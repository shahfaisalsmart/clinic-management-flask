from src.appointments.models import DoctorAvailability, Appointment, AppointmentStatus
from src.appointments.schemas import cancellation_dashboard_list_schema, CancellationDashboardSchema
from src.auth.models import User
from src.common.database import db
from src.appointments.repositories import AppointmentRepository
from datetime import datetime, timedelta, time, timezone
from sqlalchemy.orm import aliased
from src.doctor.models import DoctorProfile
from src.appointments.schemas import admin_all_appointments_list_schema

class AppointmentService:

    def __init__(self):
        self.appoint_repo = AppointmentRepository()
    
    def set_doctor_schedule_and_generate_slots(self, doctor_user_id, data):
        # checking doctor profile
        user = self.appoint_repo.get_user_by_id(doctor_user_id)
        if not user or not user.doctor_profile:
            return {"error": "Doctor profile nahi mili"}, 404
        
        doctor_profile = user.doctor_profile

        doctor_profile.treatment_services = data['treatment_services']
        
        self.appoint_repo.delete_future_unbooked_slots(doctor_profile.id)

    
        generated_slots = []
        today = datetime.now().date()
        weekly_schedule = data['weekly_schedule']

        # next 1 year 
        for i in range(365):
            current_date = today + timedelta(days=i)
            day_name = current_date.strftime("%A") 
            
            # checking ki doctor ne is din ka time diya h yaa nhi 
            day_config = next((item for item in weekly_schedule if item['day_of_week'] == day_name), None)
            

            if day_config:
                start_h, start_m = map(int, day_config['start_time'].split(':'))
                end_h, end_m = map(int, day_config['end_time'].split(':'))
                
                start_datetime = datetime.combine(current_date, time(start_h, start_m))
                end_datetime = datetime.combine(current_date, time(end_h, end_m))
                slot_duration = timedelta(minutes=day_config['slot_duration_mins'])
                
                temp_start = start_datetime
                while temp_start + slot_duration <= end_datetime:
                    new_slot = DoctorAvailability(
                        doctor_id=doctor_profile.id,
                        venue_address=data['venue_address'],
                        slot_start=temp_start,
                        slot_end=temp_start + slot_duration,
                        fee=data['fee'],
                        is_booked=False
                    )
                    generated_slots.append(new_slot)
                    temp_start += slot_duration

        # loading database in bulk 
        if generated_slots:
            self.appoint_repo.bulk_add_slots(generated_slots)
            
        self.appoint_repo.commit_changes()

        return {
            "message": f"Schedule perfectly updated! Generated {len(generated_slots)} slots for the next 365 days.",
            "venue_registered": data['venue_address'],
            "services_registered": doctor_profile.treatment_services
        }, 200

    def add_availability(self,doctor_user_id, data):
        #fetching Doctor PROFILE
        user = self.appoint_repo.get_user_by_id(doctor_user_id)
        if not user or not user.doctor_profile:
            return {"error": "Doctor profile nahi mili"}, 404
            
        doctor_profile_id = user.doctor_profile.id
        
        # Venue exist or not
        if not self.appoint_repo.get_venue_by_id(data['venue_id']):
            return {"error": "Venue NOT found in Database"}, 404

        # creating new Slot
        new_slot = DoctorAvailability(
            doctor_id=doctor_profile_id,
            venue_id=data['venue_id'],
            slot_start=data['slot_start'],
            slot_end=data['slot_end'],
            #is_home_visit=data['is_home_visit'],
            fee=data['fee']
        )
        self.appoint_repo.add_availability_slot(new_slot)
        return {"message": "Availability slot successfully Added"}, 201
    
    def search_doctors_by_specialization(self, specialization_query: str):
        doctors = self.appoint_repo.get_doctors_by_specialization(specialization_query)
        if not doctors:
            return {"message": "Doctor not found w.r.t. required specialisation"}, 404
            
        result = []
        for doc in doctors:
            slots_data = []
            available_slots = self.appoint_repo.get_upcoming_free_slots(doc.id)
            
            for slot in available_slots:
                slots_data.append({
                    "slot_id": slot.id,
                    "day": slot.slot_start.strftime("%A"), 
                    "start_time": slot.slot_start.strftime("%Y-%m-%d %I:%M %p"),
                    "end_time": slot.slot_end.strftime("%Y-%m-%d %I:%M %p"),
                    "venue_address": slot.venue_address,
                    "fee": slot.fee,
                    #"is_home_visit": slot.is_home_visit
                })
                
            result.append({
                "doctor_id": doc.id,
                "doctor_name": doc.user.name,
                "specialization": doc.specialization,
                "qualification": doc.qualification,
                "bio_achievements": doc.bio or "Experienced specialist.",
                "treatment_services": doc.treatment_services or [],
                "available_slots": slots_data
            })
        return result, 200

    def book_appointment(self, member_id, data):
        slot_id = data['slot_id']
        doctor_id = data['doctor_id']
        
        #patient name slip me dikhane ke liye chaiye
        member_user = self.appoint_repo.get_user_by_id(member_id)
        if not member_user:
            return {"error": "Patient NOT FOUND !"}, 404

        # 2. Race condition prevention ke liye 'SELECT FOR UPDATE' ke sath slot lock kre.
        slot = self.appoint_repo.get_slot_for_update(slot_id)
        
        if not slot:
            return {"error": "Maafi chahenge, ye slot available nahi hai!"}, 404
            
        if slot.is_booked:
            return {"error": "Ye slot pehle se hi book ho chuka hai! Double booking allowed nahi hai."}, 400
            
        if slot.doctor_id != doctor_id:
            return {"error": "Mismatched Data: Ye slot is doctor ka nahi hai!"}, 400

        # 3. slot registeration starts 
        today_start = datetime.combine(slot.slot_start.date(), datetime.min.time())
        today_end = datetime.combine(slot.slot_start.date(), datetime.max.time())
        
        existing_appointments_count = self.appoint_repo.count_doctor_appointments_for_day(
            slot.doctor_id,
            today_start,
            today_end
        )
        token_number = existing_appointments_count + 1


        new_appointment = Appointment(
            member_id=member_id,
            doctor_id=doctor_id,
            slot_id=slot.id,
            service_id=1, 
            status=AppointmentStatus.CONFIRMED,
            token_number=token_number
        )
        
        # slot booking mark
        slot.is_booked = True
        
        #database me saved
        self.appoint_repo.create_appointment(new_appointment)
        
        doctor_prof = DoctorProfile.query.get(slot.doctor_id)

        doctor_name = "Unknown Doctor"
        doctor_spec = "Specialist"
        
        if doctor_prof and doctor_prof.user:
            doctor_name = doctor_prof.user.name
            doctor_spec = doctor_prof.specialization #real doctor name present here

        # 5. a Detailed Appointment slip created
        appointment_slip = {
            "booking_status": "SUCCESS",
            "message": "Appointment successfully booked!",
            "appointment_details": {
                "appointment_id": new_appointment.id,
                "token_number": token_number,
                "status": new_appointment.status.value,
                "booked_at": new_appointment.created_at.strftime("%Y-%m-%d %I:%M %p")
            },
            "patient_details": {
                "patient_id": member_user.id,
                "patient_name": member_user.name
            },
            "doctor_details": {
                "doctor_id": slot.doctor_id,
                "doctor_name": doctor_name,
                "specialization": doctor_spec 
            },
            "schedule_details": {
                "day": slot.slot_start.strftime("%A"),
                "date": slot.slot_start.strftime("%Y-%m-%d"),
                "start_time": slot.slot_start.strftime("%I:%M %p"),
                "end_time": slot.slot_end.strftime("%I:%M %p"),
                "clinic_address": slot.venue_address,
                "consultation_fee": slot.fee
            }
        }
        return appointment_slip, 201

    def get_patient_bookings(self, member_id):
        appointments = Appointment.query.filter_by(member_id=member_id).order_by(Appointment.created_at.desc()).all()
        
        if not appointments:
            return {"message": "Aapki koi booking nahi mili!"}, 200
            
        bookings_list = []
        for appt in appointments:
            #slot = appt.slot  # Relationship से सीधे स्लॉट निकाला   (kisi kaam ki nhi ye line)
            slot = DoctorAvailability.query.get(appt.slot_id)
            doctor_prof = DoctorProfile.query.get(appt.doctor_id)
            doctor_name = doctor_prof.user.name if doctor_prof and doctor_prof.user else "Unknown Doctor"
            
            bookings_list.append({
                "appointment_id": appt.id,
                "token_number": appt.token_number,
                "status": appt.status.value,
                "booked_at": appt.created_at.strftime("%Y-%m-%d %I:%M %p"),
                "doctor_details": {
                    "doctor_id": appt.doctor_id,
                    "doctor_name": doctor_name,
                    "specialization": doctor_prof.specialization if doctor_prof else "Specialist"
                },
                "schedule_details": {
                    "date": slot.slot_start.strftime("%Y-%m-%d") if slot else "N/A",
                    "time": f"{slot.slot_start.strftime('%I:%M %p')} se {slot.slot_end.strftime('%I:%M %p')}" if slot else "N/A",
                    "clinic_address": slot.venue_address if slot else "N/A",
                    "fee": slot.fee if slot else 0.0
                }
            })
        return bookings_list, 200

    # 2. patient slot cancellation request
    def request_appointment_cancellation(self, member_id, data):
        appt = Appointment.query.get(data['appointment_id'])
        
        if not appt:
            return {"error": "Appointment nahi mila!"}, 404
        if appt.member_id != member_id:
            return {"error": "Aap sirf apni hi booking cancel karne ki request daal sakte hain!"}, 403
        if appt.status in [AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]:
            return {"error": f"Ye appointment pehle se hi {appt.status.value} hai!, aap dubara request nahi bhej sakte!"}, 400


        appt.status = AppointmentStatus.CANCELLATION_REQUESTED
        appt.cancellation_reason = data['cancellation_reason']
        
        db.session.commit()
        return {"message": "Cancellation request successfully Admin ko bhej di gayi hai. Status pending hai."}, 200

    # 3. ADMINISTRATIVE WORK: Admin hi Request ko handle krega
    def admin_approve_cancellation(self, admin_user_id, data):
        appt = Appointment.query.get(data['appointment_id'])
        
        if not appt:
            return {"error": "Appointment nahi mila!"}, 404
            
        # Sirf pending request par hi action liya ja sakta hai
        if appt.status != AppointmentStatus.CANCELLATION_REQUESTED:
            return {"error": "Is appointment ke liye koi cancellation request pending nahi hai!"}, 400

        action = data['action'].upper()

        if action == "APPROVE":
            # 1. Appointment FINALLY cancel ho gaya
            appt.status = AppointmentStatus.CANCELLED
            appt.cancelled_at = datetime.utcnow()
            
            # 2. Slot ko dobara open kiya taaki koi aur book kar sake
            if appt.slot:
                appt.slot.is_booked = False
                
            msg = f"Admin ne appointment ID {appt.id} successfully CANCEL kar diya hai aur slot wapas OPEN ho chuka hai."

        elif action == "REJECT":
            # 1. Request kharij hui, appointment wapas CONFIRMED ho gaya
            appt.status = AppointmentStatus.CONFIRMED
            
            # Note: Slot booked hi rahega (appt.slot.is_booked = True), isliye slot ko as it rehne dete hain
            msg = f"Admin ne cancellation request REJECT kar di hai. Appointment abhi bhi CONFIRMED hai."

        db.session.commit()
        return {"message": msg}, 200

    """
    def get_admin_dashboard(self):
        # Admin poora data dekh sakta hai pure joins ke sath
        appointments = Appointment.query.all()
        result = []
        for appt in appointments:
            member_user = self.appoint_repo.get_user_by_id(appt.member_id)
            service = self.appoint_repo.get_diagnostic_service_by_id(appt.service_id)
            
            result.append({
            "appointment_id": appt.id,
            "member_name": member_user.name if member_user else "Unknown",
            "doctor_name": appt.doctor_profile.user.name if appt.doctor_profile and appt.doctor_profile.user else "Unknown",
            "venue": appt.slot.venue.name if appt.slot and appt.slot.venue else "Unknown",
            "time": f"{appt.slot.slot_start} se {appt.slot.slot_end}" if appt.slot else "Unknown",
            "service": service.name if service else "Unknown",
            "status": appt.status.value,
            "token_number": appt.token_number
        })
        return result, 200 
    """

    def get_patient_cancellation_requests(self, member_id):
        """
        Sirf logged-in patient ki cancellation requests fetch karega.
        Isme CANCELLATION_REQUESTED aur CANCELLED dono statuses dikhenge.
        """
        requests = Appointment.query.filter(
            Appointment.member_id == member_id,
            Appointment.status.in_([
                AppointmentStatus.CANCELLATION_REQUESTED, 
                AppointmentStatus.CANCELLED
            ])
        ).order_by(Appointment.created_at.desc()).all()
        
        # Patient khud ki API dekh raha hai toh patient_details hide kar dete hain redundancy bachane ke liye
        schema = CancellationDashboardSchema(many=True, exclude=("patient_details",))
        return schema.dump(requests), 200

    def get_admin_cancellation_dashboard(self):
        """
        Admin ke liye saari pending cancellation requests lekar aayega 
        jisme Doctor aur Patient dono ki details mapped hongi.
        """
        requests = Appointment.query.filter(
            Appointment.status == AppointmentStatus.CANCELLATION_REQUESTED
        ).order_by(Appointment.created_at.desc()).all()
        
        return cancellation_dashboard_list_schema.dump(requests), 200
    
    def get_all_appointments_for_admin(self):
        """
        Admin ke liye saari appointments ki list, details, 
        Patient Name, Doctor Name aur Total Counts fetch karega.
        """
        # Aliases banayenge taaki Patient User aur Doctor User me confusion na ho
        patient_user = aliased(User)
        doctor_user = aliased(User)

        # High-performance join query
        query_results = db.session.query(
            Appointment,
            patient_user.name.label("patient_name"),
            doctor_user.name.label("doctor_name")
        ).join(
            patient_user, Appointment.member_id == patient_user.id
        ).join(
            DoctorProfile, Appointment.doctor_id == DoctorProfile.id
        ).join(
            doctor_user, DoctorProfile.user_id == doctor_user.id
        ).order_by(Appointment.created_at.desc()).all()

        # Total count nikalne ke liye list ki length use karenge
        total_appointments = len(query_results)

        # Data ko structured format me parse karenge
        formatted_list = []
        for appt, p_name, d_name in query_results:
            # appt object me dynamically names bind kar rahe hain taaki schema read kar sake
            appt.patient_name = p_name
            appt.doctor_name = d_name
            formatted_list.append(appt)

        # Final Payload Structure (Upskilling standard wrapper)
        response_payload = {
            "metadata": {
                "total_appointments_count": total_appointments
            },
            "appointments": admin_all_appointments_list_schema.dump(formatted_list)
        }

        return response_payload, 200