from src.admin.models import Department, DoctorProfile
from src.auth.models import User, Role
from src.common.database import db

class AdminService:
    
    @staticmethod
    def create_department(data):
        if Department.query.filter_by(name=data['name']).first():
            return {"error": "Ye Department pehle se bana hua hai!"}, 400
            
        new_dept = Department(name=data['name'], description=data.get('description', ''))
        db.session.add(new_dept)
        db.session.commit()
        return {"message": f"Department '{new_dept.name}' successfully ban gaya!", "id": new_dept.id}, 201
        
    @staticmethod
    def list_departments():
        depts = Department.query.all()
        return [{"id": d.id, "name": d.name, "description": d.description} for d in depts], 200

    @staticmethod
    def onboard_doctor(data):
        # 1. Check karo email unique hai ya nahi
        if User.query.filter_by(email=data['email']).first():
            return {"error": "Email pehle se registered hai!"}, 400
            
        # 2. Doctor Role fetch karo
        doctor_role = Role.query.filter_by(name="Doctor").first()
        
        # 3. Pehle User entry banao
        new_user = User(name=data['name'], email=data['email'], role_id=doctor_role.id)
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.flush() # Flush karne se hume new_user.id mil jayegi bina commit kiye
        
        # 4. Ab Doctor Profile entry banao
        new_doctor = DoctorProfile(
            user_id=new_user.id,
            specialization=data['specialization'],
            qualification=data['qualification'],
            department_id=data.get('department_id')
        )
        db.session.add(new_doctor)
        db.session.commit()
        
        return {"message": f"Doctor {data['name']} successfully onboard ho gaye hain!"}, 201
    
    @staticmethod
    def assign_doctor_to_department(data):
        doctor_id = data['doctor_id']
        department_id = data['department_id']
        
        # 1. Check karo doctor profile exist karti hai ya nahi
        doctor = DoctorProfile.query.get(doctor_id)
        if not doctor:
            return {"error": f"Doctor ID {doctor_id} ka koi doctor nahi mila!"}, 404
            
        # 2. Check karo department exist karta hai ya nahi
        department = Department.query.get(department_id)
        if not department:
            return {"error": f"Department ID {department_id} nahi mila!"}, 404
            
        # 3. Doctor ko department assign karo
        doctor.department_id = department_id
        db.session.commit()
        
        # User table se doctor ka naam nikalne ke liye relationship use karenge
        return {
            "message": f"Doctor {doctor.user.name} ko '{department.name}' department successfully assign kar diya gaya hai!"
        }, 200
