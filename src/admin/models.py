from src.common.database import db

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))

    doctors = db.relationship('DoctorProfile', backref='department', lazy=True)


class DoctorProfile(db.Model):
    __tablename__ = 'doctor_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False) #one-to-One 
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    specialization = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)




