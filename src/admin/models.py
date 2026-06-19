from src.common.database import db
from src.doctor.models import DoctorProfile

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))

    doctors = db.relationship('DoctorProfile', backref='department', lazy=True)





