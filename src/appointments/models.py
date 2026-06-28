from src.common.database import db
from datetime import datetime
import enum

class AppointmentStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLATION_REQUESTED = "CANCELLATION_REQUESTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    APPROVE = "APPROVE"
    REJECT = "REJECT"

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

class DoctorConfig(db.Model):
    """ Doctor ka general shift timing control karne ke liye"""
    __tablename__ = 'doctor_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=False, unique=True)
    venue_address = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)  # e.g., "16:00" (4 PM)
    end_time = db.Column(db.String(5), nullable=False)    # e.g., "19:00" (7 PM)
    slot_duration_mins = db.Column(db.Integer, nullable=False, default=15) # 15 mins per slot
    fee = db.Column(db.Float, nullable=False)
    work_on_sunday = db.Column(db.Boolean, default=False, nullable=False) # Default Sunday Holiday


class DoctorHoliday(db.Model):
    """ NAYA MODEL: Doctor kis din chutti pr rhega"""
    __tablename__ = 'doctor_holidays'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=False)
    holiday_date = db.Column(db.Date, nullable=False) # Format: YYYY-MM-DD


class DoctorAvailability(db.Model):
    """🚀 HAR EK SLOT/TOKEN KA PHYSICAL STATE: Patient isi se unique entity select karega"""
    __tablename__ = 'doctor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=False)
    #venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    venue_address = db.Column(db.String(255), nullable=False)

    slot_date = db.Column(db.Date, nullable=False)
    day_name = db.Column(db.String(20), nullable=False)
    token_number = db.Column(db.Integer, nullable=False)

    slot_start_time = db.Column(db.String(10), nullable=False)    # e.g., "04:00 PM"
    slot_end_time = db.Column(db.String(10), nullable=False)      # e.g., "04:15 PM"
    
    #is_home_visit = db.Column(db.Boolean, default=False, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    is_booked = db.Column(db.Boolean, default=False, nullable=False) # Double booking rokne ke liye

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('doctor_availability.id'), nullable=False, unique=True)
    #service_id = db.Column(db.Integer, db.ForeignKey('diagnostic_services.id'), nullable=False)
    
    # Dynamic generation ke liye ab slot_id foreign key hatakar targeted booking date use karenge
    booking_date = db.Column(db.Date, nullable=False) 
    token_number = db.Column(db.Integer, nullable=False) # e.g., Token 1, Token 2

    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False)
    
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