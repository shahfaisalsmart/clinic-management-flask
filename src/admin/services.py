from src.admin.models import Department
from src.doctor.models import DoctorProfile
from src.auth.models import User, Role
from src.common.database import db
from src.admin.repositories import (
    DepartmentRepository,
    RoleRepository,
    UserRepository,
    )
from src.doctor.repositories import DoctorRepository

class AdminService:

    #initializing the repositories
    def __init__(self):
        self.department_repo = DepartmentRepository()
        self.role_repo = RoleRepository()
        self.user_repo = UserRepository()
        self.doctor_repo = DoctorRepository()

    #@staticmethod
    def create_department(self,data):
        if self.department_repo.get_by_name(data['name']):
            return {"error": "Ye Department pehle se bana hua hai!"}, 400
            
        new_dept = self.department_repo.create(
            name = data['name'],
            description= data.get('description', '')
        )
        return {"message": f"Department '{new_dept.name}' successfully ban gaya!", "id": new_dept.id}, 201
        
    #@staticmethod
    def list_departments(self):
        depts = self.department_repo.get_all()
        return [{"id": d.id, "name": d.name, "description": d.description} for d in depts], 200

    #@staticmethod
    def onboard_doctor(self, data):
        # 1. Check karo email unique hai ya nahi
        if self.user_repo.get_by_email(data['email']):
            return {"error": "Email pehle se registered hai!"}, 400
            
        # 2. Doctor Role fetch karo
        doctor_role = self.role_repo.get_by_name("Doctor")
        if not doctor_role:
            return {"error": "Doctor role system me nahi mila!"}, 500

        # 3. Pehle User entry banao
        new_user = self.user_repo.create_user(
            name=data['name'], 
            email=data['email'], 
            role_id=doctor_role.id, 
            password=data['password']
        )
        # ZAROORI FIX: UserRepository me flush() use hua hai, hum commit isliye karenge 
        # taaki new_user.id foreign key bante waqt SQLite error na de
        db.session.commit()

        # 4. Ab Doctor Profile entry banao
        self.doctor_repo.create_profile(
            user_id=new_user.id,
            specialization=data['specialization'],
            qualification=data['qualification'],
           #department_id=data.get('department_id')
        )
        return {"message": f"Doctor {data['name']} successfully onboard ho gaye hain!"}, 201
    
  
    def assign_doctor_to_department(self, data):
        doctor_id = data['doctor_id']
        department_id = data['department_id']
        
        # 1. Check karo doctor profile exist karti hai ya nahi
        doctor = self.doctor_repo.get_by_user_id(doctor_id)
        if not doctor:
            return {"error": f"Doctor ID {doctor_id} ka koi doctor nahi mila!"}, 404
            
        # 2. Check karo department exist karta hai ya nahi
        department = self.department_repo.get_by_id(department_id)
        if not department:
            return {"error": f"Department ID {department_id} nahi mila!"}, 404
            
        # 3. Doctor ko department assign karo
        doctor.department_id = department_id
        self.doctor_repo.save()
        
        # User table se doctor ka naam nikalne ke liye relationship use karenge
        return {
            "message": f"Doctor {doctor.user.name} ko '{department.name}' department successfully assign kar diya gaya hai!"
        }, 200
    
    def view_all_doctors(self):
        doctors = self.doctor_repo.get_all_doctors()
        
        # अगर कोई डॉक्टर ऑनबोर्ड नहीं है
        if not doctors:
            return {"message": "No doctors found"}, 200
            
        doctors_list = []
        for doc in doctors:
            
            doc_data = {
                "id": doc.id,
                "name": doc.name,
                "email": doc.email,
                "onboarded_at": doc.created_at.strftime("%Y-%m-%d"),
                "profile_details": None
            }
            
            
            if doc.doctor_profile:
                doc_data["profile_details"] = {
                    "id": doc.doctor_profile.id,
                    "specialization": doc.doctor_profile.specialization,
                    "qualification": doc.doctor_profile.qualification
                }
                
            doctors_list.append(doc_data)
            
        return {"doctors": doctors_list}, 200
    
    # Jo doctor ke status ko true/false karega
    def verify_doctor_status(self, data):
        user_id = data.get('user_id')
        status = data.get('is_approved') # True ya False boolean value

        # Check karenge ki kya is user_id ki koi doctor profile exist karti hai
        doctor_profile = self.doctor_repo.get_by_user_id(user_id)
        if not doctor_profile:
            return {"error": "Doctor profile not found for this user"}, 404

        # Status ko repository ke through update karenge
        self.doctor_repo.update_approval_status(doctor_profile, status)

        status_text = "Approved" if status else "Rejected/Pending"
        return {"message": f"Doctor status successfully updated to {status_text}"}, 200
