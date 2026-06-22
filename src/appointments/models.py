from src.common.database import db
from datetime import datetime
import enum

class AppointmentStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLATION_REQUESTED = "CANCELLATION_REQUESTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

"""
class Venue(db.Model):
    __tablename__ = 'venues'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    
    # Relationship: Is venue par kaun se slots hain
    slots = db.relationship('DoctorAvailability', backref='venue', lazy=True)
"""

"""
class DiagnosticService(db.Model):
    __tablename__ = 'diagnostic_services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    base_price = db.Column(db.Float, nullable=False, default=0.0)
"""

class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=False)
    #venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    venue_address = db.Column(db.String(255), nullable=False)

    slot_start = db.Column(db.DateTime, nullable=False) # e.g., 2026-06-25 10:00:00
    slot_end = db.Column(db.DateTime, nullable=False)   # e.g., 2026-06-25 10:30:00
    
    #is_home_visit = db.Column(db.Boolean, default=False, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    is_booked = db.Column(db.Boolean, default=False, nullable=False) # Double booking rokne ke liye

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('doctor_availability.id'), nullable=False, unique=True)
    service_id = db.Column(db.Integer, db.ForeignKey('diagnostic_services.id'), nullable=False)
    
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False)
    token_number = db.Column(db.Integer, nullable=False)
    
    cancellation_reason = db.Column(db.String(255), nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    slot = db.relationship('DoctorAvailability', backref='appointment', uselist=False)

    #cancellation dashboard banane me help karega. --> schema me .doctor  or .patient direct access milega.
    doctor = db.relationship('DoctorProfile', backref='appointments', lazy=True)
    patient = db.relationship('User', backref='appointments', lazy=True)

    # One-to-One relationship with Medical Record
    #medical_record = db.relationship('MedicalRecord', backref='appointment', uselist=False, lazy=True)

"""
class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), unique=True, nullable=False)
    
    symptoms = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=False)
    follow_up_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

"""