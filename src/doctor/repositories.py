from src.common.database import db
from src.auth.models import User, Role
from src.admin.models import DoctorProfile


class DoctorRepository:
    def get_by_id(self, doctor_id):
        return DoctorProfile.query.get(doctor_id)

    def get_by_user_id(self, user_id):
        return DoctorProfile.query.filter_by(user_id=user_id).first()

    def create_profile(self, user_id, specialization, qualification):
        new_doctor = DoctorProfile(
            user_id=user_id,
            specialization=specialization,
            qualification=qualification,
            is_approved=False  # Default False rahega
        )
        db.session.add(new_doctor)
        db.session.commit()
        return new_doctor
    
    def get_doctor_profile(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        profile = DoctorProfile.query.filter_by(user_id=user_id).first()
        return user, profile
    

    def update_doctor_full_profile(self, user_id, new_name=None, specialization=None, qualification=None, bio=None, treatment_services=None):
        user =  User.query.filter_by(id=user_id).first()
        if not user:
            return None
        
        #new_name is not mandatory to update
        if new_name is not None:
            user.name = new_name
        
        #updating DoctorProfile
        profile = DoctorProfile.query.filter_by(user_id=user_id).first()
        if profile: 
            if specialization is not None:
                profile.specialization = specialization
            if qualification is not None:  
                profile.qualification = qualification
            if bio is not None:
                profile.bio = bio
            if treatment_services is not None:
                profile.treatment_services = treatment_services
            
        db.session.commit()
        return user, profile

    def get_all_doctors(self):
        return  User.query.join(Role).filter(Role.name == 'Doctor').all()
    
    def update_approval_status(self, doctor_profile, status):
        doctor_profile.is_approved = status
        db.session.commit()
        return doctor_profile
    

    def update_doctor_name(self, user_id, new_name):
        user = User.query.filter_by(id=user_id).first()
        if user:
            user.name = new_name
            db.session.commit()
            return user
        return None

    def save(self):
        #changes ko commit krte time jaise ki department assign karte time
        db.session.commit()