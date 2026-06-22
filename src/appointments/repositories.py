from src.appointments.models import DoctorAvailability, Appointment
from src.auth.models import User
from src.admin.models import DoctorProfile
from src.common.database import db
from datetime import datetime, timezone

class AppointmentRepository:
    def get_user_by_id(self,user_id):
        return User.query.get(user_id)
        
    #def get_diagnostic_service_by_id(self, service_id):
    #    return DiagnosticService.query.get(service_id)

    def add_availability_slot(self, slot_obj):
        db.session.add(slot_obj)
        db.session.commit()
        return slot_obj

    def get_slot_for_update(self, slot_id):
        # Concurrency control (SELECT FOR UPDATE) --> preventing Double booking
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

    # --- Patient Centric Search Queries ---
    def get_doctors_by_specialization(self, specialization_query: str):
        search_term = f"%{specialization_query}%"
        return DoctorProfile.query.filter(DoctorProfile.specialization.ilike(search_term)).all()

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