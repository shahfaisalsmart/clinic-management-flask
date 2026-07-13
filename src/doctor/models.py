from src.common.database import db


class DoctorProfile(db.Model):
    __tablename__ = 'doctor_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False) #one-to-One 
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    specialization = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)

    #TREATMENT jo ki Doctor provide krta hai
    treatment_services = db.Column(db.JSON, nullable=True) 

    # Default False rahega, Admin approve karega tab True hoga
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
