from src.appointments.models import DoctorAvailability, Appointment, AppointmentStatus, DoctorConfig, DoctorHoliday
from src.auth.models import User
from src.doctor.models import DoctorProfile
from src.common.database import db
from datetime import datetime
from sqlalchemy.orm import aliased
from sqlalchemy import or_

class AppointmentRepository:
    
    def get_user_by_id(self, user_id):
        return User.query.get(user_id)

    def get_doctor_profile_by_user_id(self, user_id):
        return DoctorProfile.query.filter_by(user_id=user_id).first()

    def get_doctor_profile_by_id(self, doctor_id):
        return DoctorProfile.query.get(doctor_id)

    def save_doctor_config(self, config_obj):
        db.session.add(config_obj)
        db.session.commit()
        return config_obj

    def get_doctor_config(self, doctor_id):
        return DoctorConfig.query.filter_by(doctor_id=doctor_id).first()

    def delete_all_holidays_for_doctor(self, doctor_id):
        DoctorHoliday.query.filter_by(doctor_id=doctor_id).delete()
        db.session.commit()

    def bulk_add_holidays(self, holiday_objects):
        db.session.add_all(holiday_objects)
        db.session.commit()

    def get_doctor_holidays_set(self, doctor_id):
        holidays = DoctorHoliday.query.filter_by(doctor_id=doctor_id).all()
        return {h.holiday_date for h in holidays}

    def delete_future_unbooked_slots(self, doctor_id):
        current_date = datetime.now().date()
        DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.is_booked == False,
            DoctorAvailability.slot_date >= current_date
        ).delete(synchronize_session=False)
        db.session.commit()

    def bulk_add_slots(self, slots_list):
        db.session.add_all(slots_list)
        db.session.commit()

    def get_slots_by_date(self, doctor_id, target_date):
        return DoctorAvailability.query.filter_by(doctor_id=doctor_id, slot_date=target_date).order_by(DoctorAvailability.token_number).all()

    def get_slot_for_update(self, slot_id):
        return db.session.query(DoctorAvailability).filter(DoctorAvailability.id == slot_id).with_for_update().first()

    def create_appointment(self, appointment_obj):
        db.session.add(appointment_obj)
        db.session.commit()
        return appointment_obj

    def get_appointment_by_id(self, appointment_id):
        return Appointment.query.get(appointment_id)

    def commit_changes(self):
        db.session.commit()

    def get_doctors_by_universal_search(self, search_query: str):
        #  SINGLE LINE CLEAN POWER QUERY (With Join, Filter and OR Constraints)
        return DoctorProfile.query.join(User, DoctorProfile.user_id == User.id).filter(or_(User.name.ilike(f"%{search_query}%"), 
                                                                                           DoctorProfile.specialization.ilike(f"%{search_query}%"), 
                                                                                           DoctorProfile.qualification.ilike(f"%{search_query}%"), 
                                                                                           DoctorProfile.bio.ilike(f"%{search_query}%"), 
                                                                                           DoctorProfile.treatment_services.cast(db.String).ilike(f"%{search_query}%"))).all()

    def get_upcoming_free_slots(self, doctor_id: int):
        """WAPAS JODA: Doctor ke aage aane wale saare khaali slots nikalne ke liye"""
        from datetime import datetime
        current_date = datetime.now().date()
        
        return DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.is_booked == False,
            DoctorAvailability.slot_date >= current_date
        ).order_by(DoctorAvailability.slot_date, DoctorAvailability.token_number).all()

    def get_patient_bookings_with_details(self, member_id):
        return db.session.query(Appointment, DoctorAvailability, DoctorProfile).\
            join(DoctorAvailability, Appointment.slot_id == DoctorAvailability.id).\
            join(DoctorProfile, Appointment.doctor_id == DoctorProfile.id).\
            filter(Appointment.member_id == member_id).\
            order_by(Appointment.created_at.desc()).all()

    def get_patient_cancellation_requests(self, member_id):
        return Appointment.query.filter(
            Appointment.member_id == member_id,
            Appointment.status.in_([AppointmentStatus.CANCELLATION_REQUESTED, AppointmentStatus.CANCELLED])
        ).order_by(Appointment.created_at.desc()).all()

    def get_doctor_cancellation_requests(self):
        return Appointment.query.filter(Appointment.status == AppointmentStatus.CANCELLATION_REQUESTED).order_by(Appointment.created_at.desc()).all()

    def get_all_appointments_with_names_for_admin(self):
        patient_user = aliased(User)
        doctor_user = aliased(User)
        return db.session.query(Appointment, patient_user.name.label("patient_name"), doctor_user.name.label("doctor_name")).\
            join(patient_user, Appointment.member_id == patient_user.id).\
            join(DoctorProfile, Appointment.doctor_id == DoctorProfile.id).\
            join(doctor_user, DoctorProfile.user_id == doctor_user.id).\
            order_by(Appointment.created_at.desc()).all()



"""
from src.appointments.models import DoctorAvailability, Appointment, AppointmentStatus, DoctorConfig, DoctorHoliday
from src.auth.models import User
from src.doctor.models import DoctorProfile  # Fixed path based on services.py imports
from src.common.database import db
from datetime import datetime, timezone
from sqlalchemy.orm import aliased

class AppointmentRepository:
    
    def get_user_by_id(self, user_id):
        return User.query.get(user_id)

    def add_availability_slot(self, slot_obj):
        db.session.add(slot_obj)
        db.session.commit()
        return slot_obj

    def get_slot_for_update(self, slot_id):
        return db.session.query(DoctorAvailability).filter(DoctorAvailability.id == slot_id).with_for_update().first()

    def count_doctor_appointments_for_day(self, doctor_id, start_time, end_time):
        return Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.created_at >= start_time,
            Appointment.created_at <= end_time
        ).count()

    def create_appointment(self, appointment_obj):
        db.session.add(appointment_obj)
        db.session.commit()
        return appointment_obj

    def get_all_appointments(self):
        return Appointment.query.all()

    def get_doctors_by_specialization(self, specialization_query: str):
        search_term = f"%{specialization_query}%"
        return DoctorProfile.query.filter(
            (DoctorProfile.specialization.ilike(search_term))
        ).all()

    def get_upcoming_free_slots(self, doctor_id: int):
        current_time = datetime.now(timezone.utc)
        return DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.is_booked == False,
            DoctorAvailability.slot_start > current_time
        ).all()
    
    def delete_future_unbooked_slots(self, doctor_id):
        current_time = datetime.now()
        DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.is_booked == False,
            DoctorAvailability.slot_start > current_time
        ).delete(synchronize_session=False)
        db.session.commit()

    def bulk_add_slots(self, slots_list):
        db.session.add_all(slots_list)

    def commit_changes(self):
        db.session.commit()

    # --- NAYE REPOSITORY METHODS (Jo services.py se extract kiye hain) ---

    def get_appointment_by_id(self, appointment_id):
        #Service layer se direct query hatane ke liye
        return Appointment.query.get(appointment_id)

    def get_doctor_profile_by_id(self, doctor_id):
        #Doctor profile fetch karne ke liye
        return DoctorProfile.query.get(doctor_id)

    def get_patient_bookings_with_details(self, member_id):
        #EFFICIENT JOIN QUERY: Loop ke andar queries karne ke bajay 
        #ek baar me hi Appointment, Slot aur Doctor details fetch karega (Solves N+1 Problem).
        return db.session.query(Appointment, DoctorAvailability, DoctorProfile).\
            join(DoctorAvailability, Appointment.slot_id == DoctorAvailability.id).\
            join(DoctorProfile, Appointment.doctor_id == DoctorProfile.id).\
            filter(Appointment.member_id == member_id).\
            order_by(Appointment.created_at.desc()).all()

    def get_patient_cancellation_requests(self, member_id):
        #Patient ki cancellation requests fetch karne ki query
        return Appointment.query.filter(
            Appointment.member_id == member_id,
            Appointment.status.in_([
                AppointmentStatus.CANCELLATION_REQUESTED, 
                AppointmentStatus.CANCELLED
            ])
        ).order_by(Appointment.created_at.desc()).all()

    def get_admin_cancellation_requests(self):
        #Admin ke liye saari pending cancellation requests
        return Appointment.query.filter(
            Appointment.status == AppointmentStatus.CANCELLATION_REQUESTED
        ).order_by(Appointment.created_at.desc()).all()

    def get_all_appointments_with_names_for_admin(self):
        #Admin ka mega join query jo complete appointments data laata hai
        patient_user = aliased(User)
        doctor_user = aliased(User)

        return db.session.query(
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
    

    def save_doctor_config(self, config_obj):
        db.session.add(config_obj)
        db.session.commit()
        return config_obj

    def get_doctor_config(self, doctor_id):
        return DoctorConfig.query.filter_by(doctor_id=doctor_id).first()

    def add_holiday(self, holiday_obj):
        db.session.add(holiday_obj)
        db.session.commit()
        return holiday_obj

    def is_doctor_on_holiday(self, doctor_id, target_date):
        return DoctorHoliday.query.filter_by(doctor_id=doctor_id, holiday_date=target_date).first() is not None

    def get_appointments_count_for_date(self, doctor_id, target_date):
        return Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.booking_date == target_date,
            Appointment.status != 'CANCELLED'
        ).count() 

"""