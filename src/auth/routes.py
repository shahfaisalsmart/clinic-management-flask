from flask import Blueprint, request, jsonify
from src.auth.schemas import RegisterSchema, LoginSchema
from src.auth.services import AuthService
from marshmallow import ValidationError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

register_schema = RegisterSchema()
login_schema = LoginSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Data Nahi mila"}), 400

    try:
        validated_data = register_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors" : err.messages}), 400
    

    response, status_code = AuthService.register_user(validated_data)
    return jsonify(response), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error" : "Data nahi mila"}), 400
    
    try:
        validated_data = login_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors" : err.message}), 400
    
    response, status_code = AuthService.login_user(validated_data)
    return jsonify(response), status_code

