from src.auth.models import User, Role
from src.common.database import db
from flask_jwt_extended import create_access_token
from datetime import timedelta
from functools import wraps
from flask_jwt_extended import get_jwt, jwt_required
from flask import jsonify


class AuthService:

    @staticmethod
    def register_user(data):
        if User.query.filter_by(email=data['email']).first():
            return {"error" : "Email already exist"}, 400
        
        role = Role.query.filter_by(name=data['role_name']).first()
        if not role:
            return {"error" : "role not valid"}, 400

       #new_user = User(
        #    name=data['name'],
        #   email=data['email'],
         #   role_id=role.id,
          #  password=data['password']
        #)

    
        new_user = User()
        new_user.name = data['name']
        new_user.email = data['email']
        new_user.role_id = role.id

        new_user.set_password(data['password'])

        db.session.add(new_user)
        db.session.commit()

        return {"message" : f"{data['role_name']} registration sucessful"},201

    @staticmethod
    def login_user(data):
        
        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            return {"error" : "wrong email or password"}, 401
        
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


def admin_required():
    def decorator(fn):
        @wraps(fn)
        @jwt_required() # Pehle check karega valid token hai ya nahi
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            # Token banate waqt humne additional_claims me role dala tha
            if claims.get("role") != "Admin":
                return jsonify({"error": "Access Denied! Sirf Admin hi ye kaam kar sakta hai, bhai!"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

