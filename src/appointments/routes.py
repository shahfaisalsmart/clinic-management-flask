from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.appointments.schemas import  BookAppointmentSchema, UpdateDoctorProfileAndScheduleSchema, CancelRequestSchema, AdminApproveCancelSchema
from src.appointments.services import AppointmentService
from src.common.utils.decorators import role_required
from marshmallow import ValidationError

appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointment')

#add_availability_schema = AddAvailabilitySchema()
book_appointment_schema = BookAppointmentSchema()
update_schedule_schema = UpdateDoctorProfileAndScheduleSchema()
cancel_request_schema = CancelRequestSchema()
admin_approve_cancel_schema = AdminApproveCancelSchema()

"""
# 1. DOCTOR ROUTE: Add Availability
@appointments_bp.route('/doctor/availability', methods=['POST'])
@role_required(['Doctor'])
def add_availability():
    doctor_user_id = get_jwt_identity() # Token se logged-in doctor ki user id milegi
    try:
        validated_data = add_availability_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = AppointmentService().add_availability(int(doctor_user_id), validated_data)
    return jsonify(response), status_code
"""

# 2. MEMBER ROUTE: Book Appointment
@appointments_bp.route('/member/booking', methods=['POST'])
@jwt_required() # Koi bhi logged-in user (Member) ise call kar sakta hai
@role_required(['Member'])
def book_appointment():
    member_id = get_jwt_identity()
    try:
        validated_data = book_appointment_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = AppointmentService().book_appointment(int(member_id), validated_data)
    return jsonify(response), status_code

"""
# 3. ADMIN ROUTE: Full View Dashboard
@appointments_bp.route('/admin/appointments-dashboard', methods=['GET'])
@role_required(['Admin'])
def admin_dashboard():
    response, status_code = AppointmentService().get_admin_dashboard()
    return jsonify(response), status_code
"""

#search for doctors (members only)
@appointments_bp.route('/doctors/search', methods=['GET'])
@role_required(['Member'])
def search_doctors():
    specialization = request.args.get('specialization', '')
    if not specialization:
        return jsonify({"error" : "specialization parameter is mandatory"})
    
    response, status_code = AppointmentService().search_doctors_by_specialization(specialization)
    return jsonify(response), status_code

#update=Schedule
@appointments_bp.route('/doctor/update-schedule', methods=['POST'])
@role_required(['Doctor'])
def update_schedule():
    doctor_user_id = get_jwt_identity()
    try:
        validated_data = update_schedule_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = AppointmentService().set_doctor_schedule_and_generate_slots(
        int(doctor_user_id), validated_data
    )
    return jsonify(response), status_code


@appointments_bp.route('/member/my-bookings', methods=['GET'])
@role_required(['Member'])
def get_my_bookings():
    member_id = get_jwt_identity()
    response, status_code = AppointmentService().get_patient_bookings(int(member_id))
    return jsonify(response), status_code

#patient Cancellation request
@appointments_bp.route('/member/cancel-request', methods=['POST'])
@role_required(['Member'])
def cancel_request():
    member_id = get_jwt_identity()
    try:
        validated_data = cancel_request_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = AppointmentService().request_appointment_cancellation(int(member_id), validated_data)
    return jsonify(response), status_code

#Cancellation request prr Admin ka action
@appointments_bp.route('/admin/action-approve-cancel', methods=['POST'])
@role_required(['Admin']) 
def admin_approve_cancel():
    admin_user_id = get_jwt_identity()
    try:
        validated_data = admin_approve_cancel_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = AppointmentService().admin_approve_cancellation(int(admin_user_id), validated_data)
    return jsonify(response), status_code


# ----------------- PATIENT DASHBOARD ENDPOINT -----------------
@appointments_bp.route('/member/cancellation-requests', methods=['GET'])
@role_required(['Member'])
def get_member_cancellations():
    member_id = get_jwt_identity()
    response, status_code = AppointmentService().get_patient_cancellation_requests(int(member_id))
    return jsonify(response), status_code


# ------------------ ADMIN DASHBOARD ENDPOINT ------------------
@appointments_bp.route('/admin/cancellation-requests', methods=['GET'])
@role_required(['Admin'])
def get_admin_cancellations():
    response, status_code = AppointmentService().get_admin_cancellation_dashboard()
    return jsonify(response), status_code

#Getting ALL appointments by Admin (Full View Dashboard)
@appointments_bp.route('/admin/all-appointments', methods=['GET'])
@role_required(['Admin'])
def get_all_appointments_dashboard():
    """
    Endpoint jo admin ko saare appointments aur unka total count laakar dega
    """
    response, status_code = AppointmentService().get_all_appointments_for_admin()
    return jsonify(response), status_code
