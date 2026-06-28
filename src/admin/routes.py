from flask import Blueprint, request, jsonify
from src.admin.schemas import DepartmentSchema, DoctorOnboardSchema
from src.admin.services import AdminService
from src.common.utils.decorators import role_required
from src.admin.schemas import AssignDoctorSchema
from marshmallow import ValidationError

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


#-------- SCHEMAS Object making ------------------------
dept_schema = DepartmentSchema()
doctor_schema = DoctorOnboardSchema()
assign_doctor_schema = AssignDoctorSchema()

#-------SERVICES OBJECT MAKING--------------
adminService = AdminService()

@admin_bp.route('/departments', methods=['POST'])
@role_required(['Admin']) # Sirf Admin allow hoga
def create_department():
    try:
        validated_data = dept_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = adminService.create_department(validated_data)
    return jsonify(response), status_code

# 1. LIST DEPARTMENTS ROUTE (GET)
@admin_bp.route('/departments', methods=['GET'])
@role_required(['Admin'])
def list_departments():
    response, status_code = adminService.list_departments()
    return jsonify(response), status_code


@admin_bp.route('/doctors/onboard', methods=['POST'])
@role_required(['Admin'])
def onboard_doctor():
    try:
        validated_data = doctor_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = adminService.onboard_doctor(validated_data)
    return jsonify(response), status_code




# 2. ASSIGN/SWITCH DOCTOR DEPARTMENT ROUTE (PUT)
@admin_bp.route('/doctors/assign', methods=['PUT'])
@role_required(['Admin'])
def assign_doctor():
    try:
        validated_data = assign_doctor_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = adminService.assign_doctor_to_department(validated_data)
    return jsonify(response), status_code

#list of all doctors
@admin_bp.route('/doctors', methods=['GET'])
@role_required(['Admin'])
def get_all_doctors_list():
        response, status_code = adminService.view_all_doctors()
        return jsonify(response), status_code


# DOCTOR APPROVAL/VERIFICATION ROUTE (PUT)
@admin_bp.route('/doctors/verify', methods=['PUT'])
@role_required(['Admin'])  
def verify_doctor():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Data nahi mila"}), 400
    
    if 'user_id' not in json_data or 'is_approved' not in json_data:
        return jsonify({"error": "user_id aur is_approved fields zaroori hain"}), 400
        
    response, status_code = adminService.verify_doctor_status(json_data)
    return jsonify(response), status_code