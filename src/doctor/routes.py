from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from src.doctor.services import DoctorService
from src.doctor.schemas import DoctorUpdateSchema
from src.common.utils.decorators import role_required
from marshmallow import ValidationError

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')
doctor_service = DoctorService()
update_schema = DoctorUpdateSchema()

# 1. डॉक्टर का प्रोफाइल देखने का रूट (सिर्फ Doctor रोल के लिए)
@doctor_bp.route('/profile', methods=['GET'])
@role_required(['Doctor'])
def get_doctor_profile():
    current_user_id = get_jwt_identity() # टोकन से यूजर ID मिली
    response, status_code = doctor_service.get_profile(int(current_user_id))
    return jsonify(response), status_code

# 2. डॉक्टर का प्रोफाइल अपडेट करने का रूट
@doctor_bp.route('/profile', methods=['PUT'])
@role_required(['Doctor'])
def update_doctor_profile():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Data nahi mila"}), 400
        
    try:
        validated_data = update_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    current_user_id = get_jwt_identity()
    response, status_code = doctor_service.update_profile(int(current_user_id), validated_data)
    return jsonify(response), status_code
