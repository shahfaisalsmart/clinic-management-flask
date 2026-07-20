from flask import Blueprint, request, jsonify
from src.auth.schemas import RegisterSchema, LoginSchema
from src.auth.services import AuthService
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

#-------- SCHEMAS OBJECT MAKING -----------------------
register_schema = RegisterSchema()
login_schema = LoginSchema()


# --------- SERVICES OBJECT MAKING ---------------------
authService = AuthService()

"""
#test 
@auth_bp.route('/tesing', methods=['POST'])
def testing_DB():
    json_data = request.get_json()
    response , status_code = authService.testingForDB(json_data)
    return jsonify(response), status_code
    """


# 1. Normal Member/Patient Registration (Koi bhi access kar sakta hai)
@auth_bp.route('/register', methods=['POST'])
def register_member():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Data Nahi mila"}), 400

    try:
        validated_data = register_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors" : err.messages}), 400
    
    # Humne manually 'member' role bhej diya, ab data se role_name ki zaroorat nahi hai
    response, status_code = authService.register_user(validated_data, role_name='Member')
    return jsonify(response), status_code


# 2. Doctor Registration (Ise sirf Admin ya Authorized person hi hit kar sake)
@auth_bp.route('/doctor/register', methods=['POST'])
def register_doctor():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Data Nahi mila"}), 400

    try:
        validated_data = register_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors" : err.messages}), 400
    
    # Manually pass 'doctor' role
    response, status_code = authService.register_user(validated_data, role_name='Doctor')
    return jsonify(response), status_code


# 3. Admin Registration (Super-Admin ya Initial Setup ke liye)
@auth_bp.route('/admin/register', methods=['POST'])
def register_admin():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Data Nahi mila"}), 400

    try:
        validated_data = register_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors" : err.messages}), 400
    
    # Manually pass 'Admin' role
    response, status_code = authService.register_user(validated_data, role_name='Admin')
    return jsonify(response), status_code


# 4. Login Route
@auth_bp.route('/login/v1', methods=['POST'])
def login():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error" : "Data nahi mila"}), 400
    
    try:
        validated_data = login_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors" : err.messages}), 400
    
    response, status_code = authService.login_user(validated_data)
    return jsonify(response), status_code
