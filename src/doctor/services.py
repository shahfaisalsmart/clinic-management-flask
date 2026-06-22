from src.doctor.repositories import DoctorRepository

class DoctorService:
    
    def __init__(self):
        self.doctor_repo = DoctorRepository()

    def get_profile(self, user_id):
        user, profile = self.doctor_repo.get_doctor_profile(user_id)
        if not user:
            return {"error": "Doctor not found"}, 404
            
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.name if hasattr(user,'role') else "Doctor",
            "specialization" : profile.specialization if profile else None,
            "qualification" : profile.qualification if profile else None,
            "is_approved" : profile.is_approved if profile else False
        }, 200

    def update_profile(self, user_id, data):
        user, profile = self.doctor_repo.get_doctor_profile(user_id)
        
        if not user:
            return {"error" : "Doctor not found"}, 404
        
        #secuirty check --> unapproaved doctors are not allowed to update
        if not profile or not profile.is_approved:
            return {"error" : "Your profile is pending pr admin approval, you can't update right now"}, 403

        #all fields are Optional
        name = data.get('name')
        specialization = data.get('specialization')
        qualification = data.get('qualification')

        #validation
        if name is None and specialization is None and qualification is None:
            return {"error": "At least one field (name, specialization, or qualification) is required to update"}, 400

        #Repository 
        updated_doctor = self.doctor_repo.update_doctor_full_profile(
            user_id= user_id,
            new_name= name,
            specialization=specialization,
            qualificaiton=qualification
            )
        
        if not updated_doctor:
            return {"error": "Update failed"}, 400
            
        return {"message": "Doctor profile updated successfully"}, 200
