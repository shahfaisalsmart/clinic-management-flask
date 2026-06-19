from src.auth.models import User, Role
from src.common.database import db
from src.auth.repositories import AuthRepository
from src.doctor.repositories import DoctorRepository
from flask_jwt_extended import create_access_token
from datetime import timedelta
from functools import wraps
from flask_jwt_extended import get_jwt, jwt_required
from flask import jsonify

class AuthService:

    def __init__(self):
        self.auth_repo = AuthRepository()
        self.doctor_repo = DoctorRepository()
    
    # role_name parameter accept karega jo routes se aayega
    def register_user(self, data, role_name):
        if self.auth_repo.get_user_by_email(data['email']):
            return {"error" : "Email already exist"}, 400
        
        # Database se role check karega (member, doctor, ya admin)
        role = self.auth_repo.get_role_by_name(role_name)
        if not role:
            return {"error" : f"Role '{role_name}' not found in database"}, 400

        # User create karte waat dynamic role.id pass kiya
        new_user = self.auth_repo.create_user(
            name=data['name'],
            email=data['email'],
            role_id=role.id,  # Hardcoded '1' hata kar dynamic kiya
            password=data['password']
        )

        if role_name.lower() == 'doctor':
            # Frontend data se optional fields nikalenge, agar nahi hain toh empty string bhejenge
            specialization = data.get('specialization', 'General')
            qualification = data.get('qualification', 'MBBS')
            
            # DoctorRepository ka use karke profile insert ki
            self.doctor_repo.create_profile(
                user_id=new_user.id,
                specialization=specialization,
                qualification=qualification
            )
        return {"message" : f"{role_name} registration successful"}, 201

    def login_user(self, data):
        user = self.auth_repo.get_user_by_email(data['email'])

        if not user or not user.check_password(data['password']):
            return {"error" : "wrong email or password"}, 401
        
        # SECURITY CHECK: Agar user ek Doctor hai, toh approval status check krna padega
        if user.role.name.lower() == 'doctor':
            # user.doctor_profile humne models.py ke relationship se nikala hai
            if not user.doctor_profile or not user.doctor_profile.is_approved:
                return {
                    "error": "Aapka account abhi Admin approval ke liye pending hai. Kripya thoda intezar karein."
                }, 403  # 403 Forbidden status code (Unapproved ke liye)
        
        additional_claims = {"role" : user.role.name}
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims,
            expires_delta=timedelta(days=1)
        )

        return {
            "message" : "login successful",
            "access_token" : access_token,
            "role" : user.role.name
        }, 200
