from flask import Blueprint, request, jsonify
from src.admin.schemas import DepartmentSchema, DoctorOnboardSchema
from src.admin.services import AdminService
from src.auth.services import admin_required
from src.admin.schemas import AssignDoctorSchema
from marshmallow import ValidationError

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

dept_schema = DepartmentSchema()
doctor_schema = DoctorOnboardSchema()

@admin_bp.route('/departments', methods=['POST'])
@admin_required() # Sirf Admin allow hoga
def create_department():
    try:
        validated_data = dept_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = AdminService.create_department(validated_data)
    return jsonify(response), status_code

# 1. LIST DEPARTMENTS ROUTE (GET)
@admin_bp.route('/departments', methods=['GET'])
@admin_required()
def list_departments():
    response, status_code = AdminService.list_departments()
    return jsonify(response), status_code


@admin_bp.route('/doctors/onboard', methods=['POST'])
@admin_required()
def onboard_doctor():
    try:
        validated_data = doctor_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = AdminService.onboard_doctor(validated_data)
    return jsonify(response), status_code


assign_doctor_schema = AssignDoctorSchema()

# 2. ASSIGN/SWITCH DOCTOR DEPARTMENT ROUTE (PUT)
@admin_bp.route('/doctors/assign', methods=['PUT'])
@admin_required()
def assign_doctor():
    try:
        validated_data = assign_doctor_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = AdminService.assign_doctor_to_department(validated_data)
    return jsonify(response), status_code