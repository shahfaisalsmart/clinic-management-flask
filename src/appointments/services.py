# BILAL_TEST_12345
from src.appointments.models import DoctorAvailability, Appointment, AppointmentStatus, DoctorHoliday, DoctorConfig
from src.appointments.schemas import cancellation_dashboard_list_schema, CancellationDashboardSchema, admin_all_appointments_list_schema
from src.appointments.repositories import AppointmentRepository
from datetime import datetime, timedelta, time
from src.common.database import db
from sqlalchemy import or_


class AppointmentService:

    def __init__(self):
        self.appoint_repo = AppointmentRepository()
    
    def set_doctor_schedule_and_generate_slots(self, doctor_user_id, data):
        doctor_profile = self.appoint_repo.get_doctor_profile_by_user_id(doctor_user_id)
        if not doctor_profile:
            return {"error": "Doctor profile nahi mili"}, 404
        
        doctor_profile.treatment_services = data['treatment_services']
        
        # 1. Update config settings inside doctor_configs table
        config = self.appoint_repo.get_doctor_config(doctor_profile.id)
        if not config:
            config = DoctorConfig(doctor_id=doctor_profile.id)
        
        config.venue_address = data['venue_address']
        config.start_time = data['start_time']
        config.end_time = data['end_time']
        config.slot_duration_mins = data['slot_duration_mins']
        config.fee = data['fee']
        config.work_on_sunday = data.get('work_on_sunday', False)
        self.appoint_repo.save_doctor_config(config)
        
        # 2. Delete old unbooked future slots
        self.appoint_repo.delete_future_unbooked_slots(doctor_profile.id)
        
        # 3. Fetch doctor holidays
        holiday_set = self.appoint_repo.get_doctor_holidays_set(doctor_profile.id)
        
        start_h, start_m = map(int, data['start_time'].split(':'))
        end_h, end_m = map(int, data['end_time'].split(':'))
        slot_duration = timedelta(minutes=data['slot_duration_mins'])
        
        generated_slots = []
        today = datetime.now().date()

        # Generates array sequences for the next 90 days efficiently
        for i in range(90):
            current_date = today + timedelta(days=i)
            day_name = current_date.strftime("%A")
            
            if day_name == 'Sunday' and not config.work_on_sunday:
                continue
            if current_date in holiday_set:
                continue
                
            start_datetime = datetime.combine(current_date, time(start_h, start_m))
            end_datetime = datetime.combine(current_date, time(end_h, end_m))
            
            temp_start = start_datetime
            token_counter = 1
            
            while temp_start + slot_duration <= end_datetime:
                new_slot = DoctorAvailability(
                    doctor_id=doctor_profile.id,
                    venue_address=data['venue_address'],
                    slot_date=current_date,
                    day_name=day_name,
                    token_number=token_counter,
                    slot_start_time=temp_start.strftime('%I:%M %p'),
                    slot_end_time=(temp_start + slot_duration).strftime('%I:%M %p'),
                    fee=data['fee'],
                    is_booked=False
                )
                generated_slots.append(new_slot)
                temp_start += slot_duration
                token_counter += 1

        if generated_slots:
            self.appoint_repo.bulk_add_slots(generated_slots)
            
        self.appoint_repo.commit_changes()
        return {"message": f"Schedule set! Generated {len(generated_slots)} slots without Sundays/Holidays."}, 200

    def update_doctor_holidays_bulk(self, doctor_user_id, data):
        doctor_profile = self.appoint_repo.get_doctor_profile_by_user_id(doctor_user_id)
        if not doctor_profile:
            return {"error": "Doctor profile nahi mili"}, 404
            
        # 1. Purani holidays saaf karein
        self.appoint_repo.delete_all_holidays_for_doctor(doctor_profile.id)
        
        # 2. Nayi holidays insert karein aur database objects taiyar karein
        holiday_objects = []
        parsed_dates = [] 
        for date_str in data['holiday_dates']:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            parsed_dates.append(parsed_date)
            holiday_objects.append(DoctorHoliday(doctor_id=doctor_profile.id, holiday_date=parsed_date))
            
        self.appoint_repo.bulk_add_holidays(holiday_objects)
        
        #  3. FIXED: Booked aur Unbooked dono slots ka perfect cancellation treatment
        from src.appointments.models import DoctorAvailability, Appointment, AppointmentStatus
        from src.common.database import db
        #from sqlalchemy import cast
        
        # Safe checkpoint to instantly clear any locked threads
        db.session.commit()

        for p_date in parsed_dates:
            #date_iso_str = p_date.strftime('%Y-%m-%d')
            # A. Pehle un appointments ko dhoondo jo is chutti wali date ke slots par booked hain
            print("========== DEBUG ==========", flush=True)
            print("p_date:", repr(p_date), flush=True)
            print("type :", type(p_date), flush=True)
            print("===========================", flush=True)
            booked_slots_query = db.session.query(DoctorAvailability.id).filter(
                DoctorAvailability.doctor_id == doctor_profile.id,
                DoctorAvailability.is_booked == True,
                DoctorAvailability.slot_date == p_date
            ).subquery()
            

            db.session.query(Appointment).filter(
                    Appointment.slot_id.in_(booked_slots_query)
            ).update(
                    {
                        "status": AppointmentStatus.CANCELLED,
                        "cancellation_reason": "Doctor unavailable due to sudden holiday/emergency leave.",
                        "cancelled_at": datetime.utcnow()
                    }, 
                    synchronize_session=False
                )


            # B. Un sabhi appointments ka status 'CANCELLED' karo aur reason daalo
            #db.session.query(Appointment).filter(
               # Appointment.slot_id.in_(booked_slots_query)
            #).update(
                #{
                    #"status": AppointmentStatus.CANCELLED,
                    #"cancellation_reason": "Doctor unavailable due to sudden holiday/emergency leave.",
                    #"cancelled_at": datetime.utcnow()
                #}, 
                #synchronize_session=False
            #)
            
            # C. Ab database se is date ke SAARE SLOTS (Chahe booked ho ya unbooked) delete kar do
            db.session.execute(
                db.text("""
                    DELETE FROM doctor_availability 
                    WHERE doctor_id = :doc_id 
                      AND slot_date = :s_date
                """),
                {"doc_id": doctor_profile.id, "s_date": p_date}
            )
            
        db.session.commit()

        return {
            "message": f"Successfully updated {len(holiday_objects)} holidays. All pending slots cleared and affected patients notified/cancelled!"
        }, 200

    def view_slots_for_patient(self, doctor_id, date_str):
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        slots = self.appoint_repo.get_slots_by_date(doctor_id, target_date)
        
        if not slots:
            return {"message": "Doctor is din available nahi hain!"}, 404
            
        slots_array = []
        available_count = 0
        for s in slots:
            status_label = "Booked" if s.is_booked else "Available"
            if not s.is_booked:
                available_count += 1
            slots_array.append({
                "slot_id": s.id,
                "token_display": f"Token {s.token_number} : {s.slot_start_time} se {s.slot_end_time}",
                "status": status_label
            })
            
        return {
            "date": date_str,
            "day": target_date.strftime('%A'),
            "tokens_available": available_count,
            "slots": slots_array
        }, 200

    def universal_doctor_search(self, search_query: str):
        doctors = self.appoint_repo.get_doctors_by_universal_search(search_query)
        if not doctors:
            return {"message": "Doctor not found matching your search query"}, 404
            
        result = []
        for doc in doctors:
            slots_data = []
            available_slots = self.appoint_repo.get_upcoming_free_slots(doc.id)
            
            for slot in available_slots:
                slots_data.append({
                    "slot_id": slot.id,
                    "day": slot.slot_date.strftime("%A") if slot.slot_date else "", 
                    "start_time": f"{slot.slot_date} {slot.slot_start_time}",
                    "end_time": f"{slot.slot_date} {slot.slot_end_time}",
                    "venue_address": slot.venue_address,
                    "fee": slot.fee,
                })
                
            result.append({
                "doctor_id": doc.id,
                "doctor_name": doc.user.name if doc.user else "Unknown Doctor",
                "specialization": doc.specialization,
                "qualification": doc.qualification,
                "bio_achievements": doc.bio or "Experienced specialist.",
                "treatment_services": doc.treatment_services or [],
                "available_slots": slots_data
            })
        return result, 200

    def get_patient_bookings(self, member_id):
        # Repository se optimized join data fetch karega
        records = self.appoint_repo.get_patient_bookings_with_details(member_id)
        if not records:
            return {"message": "Aapki koi booking nahi mili!"}, 200
            
        bookings_list = []
        for a, s, d in records:
            doctor_name = d.user.name if d and d.user else "Unknown Doctor"
            
            # FIXED: Safe parsing taaki bad/incomplete data par AttributeError na aaye
            slot_date_str = s.slot_date.strftime('%Y-%m-%d') if (s and s.slot_date) else "N/A"
            slot_start_str = s.slot_start_time if s else "N/A"
            slot_end_str = s.slot_end_time if s else "N/A"
            clinic_address = s.venue_address if s else "N/A"
            consultation_fee = s.fee if s else 0.0
            
            bookings_list.append({
                "appointment_id": a.id, 
                "token_number": a.token_number, 
                "status": a.status.value if hasattr(a.status, 'value') else a.status,
                "schedule_details": {
                    "date": slot_date_str, 
                    "time": f"{slot_start_str} - {slot_end_str}", 
                    "clinic": clinic_address,
                    "fee": consultation_fee
                }
            })
        return bookings_list, 200

    def request_appointment_cancellation(self, member_id, data):
        appt = self.appoint_repo.get_appointment_by_id(data['appointment_id'])
        if not appt or appt.member_id != member_id:
            return {"error": "Access denied/Not found"}, 404
        appt.status = AppointmentStatus.CANCELLATION_REQUESTED
        appt.cancellation_reason = data['cancellation_reason']
        self.appoint_repo.commit_changes()
        return {"message": "Cancellation request submitted."}, 200

    def doctor_approve_cancellation(self, doctor_user_id, data):
        appt = self.appoint_repo.get_appointment_by_id(data['appointment_id'])
        if not appt:
            return {"error": "Not found"}, 404
        action = data['action'].upper()
        if action == AppointmentStatus.APPROVE.value:
            appt.status = AppointmentStatus.CANCELLED
            appt.cancelled_at = datetime.utcnow()
            if appt.slot:
                appt.slot.is_booked = False
            msg = "Cancelled successfully."
        else:
            appt.status = AppointmentStatus.CONFIRMED
            msg = "Rejected cancellation."
        self.appoint_repo.commit_changes()
        return {"message": msg}, 200

    def get_patient_cancellation_requests(self, member_id):
        requests = self.appoint_repo.get_patient_cancellation_requests(member_id)
        return CancellationDashboardSchema(many=True, exclude=("patient_details",)).dump(requests), 200

    def get_doctor_cancellation_dashboard(self):
        requests = self.appoint_repo.get_doctor_cancellation_requests()
        return cancellation_dashboard_list_schema.dump(requests), 200
    
    def get_all_appointments_for_admin(self):
        query_results = self.appoint_repo.get_all_appointments_with_names_for_admin()
        formatted_list = []
        for appt, p_name, d_name in query_results:
            appt.patient_name = p_name
            appt.doctor_name = d_name
            formatted_list.append(appt)
        return {"metadata": {"total_appointments_count": len(formatted_list)}, "appointments": admin_all_appointments_list_schema.dump(formatted_list)}, 200


    #====== LAST PHASE TO MODIFICATION ============
    def update_doctor_availability_config(self, doctor_user_id, data):
        # Doctor user_id se internal profile extract default assume model layer context
        doctor_id = doctor_user_id  # Map internally as required
        
        config = self.appoint_repo.get_doctor_config(doctor_id)
        if not config:
            config = DoctorConfig(doctor_id=doctor_id)
            
        config.venue_address = data['venue_address']
        config.start_time = data['start_time'] # "16:00"
        config.end_time = data['end_time']     # "19:00"
        config.slot_duration_mins = data['slot_duration_mins'] # 15
        config.fee = data['fee']
        config.work_on_sunday = data.get('work_on_sunday', False)

        self.appoint_repo.save_doctor_config(config)
        return {"message": "Doctor general availability constraints successfully updated!"}, 200

    def mark_doctor_holiday(self, doctor_user_id, data):
        doctor_id = doctor_user_id
        holiday_date = datetime.strptime(data['holiday_date'], '%Y-%m-%d').date()

        new_holiday = DoctorHoliday(doctor_id=doctor_id, holiday_date=holiday_date)
        self.appoint_repo.add_holiday(new_holiday)
        return {"message": f"Date {data['holiday_date']} successfully marked as Holiday!"}, 201

    def book_appointment(self, member_id, data):
        slot_id = data['slot_id']
        doctor_id = data['doctor_id']
        
        # 1. Row ko update ke liye lock karenge concurreny rokne ke liye
        slot = self.appoint_repo.get_slot_for_update(slot_id)
        
        if not slot or slot.doctor_id != doctor_id:
            return {"error": "Invalid target slot payload matching"}, 400
        if slot.is_booked:
            return {"error": "Ye slot pehle se hi book ho chuka hai!"}, 400
            
        # 2. Slot ko booked mark karo
        slot.is_booked = True
        
        # 3. Dynamic token format setup (Existing table size ke according token count)
        from src.appointments.models import Appointment, AppointmentStatus
        from src.common.database import db
        
        existing_count = db.session.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.slot_id == slot_id
        ).count()
        token_number = slot.token_number # Hum standard configured token assign karenge

        new_appointment = Appointment(
            member_id=member_id,
            doctor_id=doctor_id,
            slot_id=slot.id,
            token_number=token_number,
            status=AppointmentStatus.CONFIRMED
        )
        self.appoint_repo.create_appointment(new_appointment)
        
        return {
            "booking_status": "SUCCESS", 
            "message": "Aapka slot book ho chuka hai aur dashboard pr inject ho gaya h!"
        }, 201
    


