from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.appointments.schemas import BookAppointmentSchema, UpdateDoctorProfileAndScheduleSchema, CancelRequestSchema, DoctorApproveCancelSchema, BulkHolidaySchema
from src.appointments.services import AppointmentService
from src.common.utils.decorators import role_required
from src.common.utils.ld_client import is_feature_enabled
from marshmallow import ValidationError

appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointment')

#-----------------SCHEMAS OBEJCT MAKING ---------------------------------------------
#add_availability_schema = AddAvailabilitySchema()
update_schedule_schema = UpdateDoctorProfileAndScheduleSchema()
bulk_holiday_schema = BulkHolidaySchema()
book_appointment_schema = BookAppointmentSchema()
cancel_request_schema = CancelRequestSchema()
doctor_approve_cancel_schema = DoctorApproveCancelSchema()

#---------------- SERVICES OBJECT MAKING------------------------
appointmentServices = AppointmentService()



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
        
    response, status_code = appointmentServices.book_appointment(int(member_id), validated_data)
    return jsonify(response), status_code

@appointments_bp.route('/member/view-slots', methods=['GET'])
@role_required(['Member'])
def patient_view_slots():
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date', type=str)
    if not doctor_id or not date_str:
        return jsonify({"error": "doctor_id and date parameters are mandatory"}), 400
    response, status_code = appointmentServices.view_slots_for_patient(doctor_id, date_str)
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
    member_id = get_jwt_identity()
    claims = get_jwt()
    user_role = claims.get("role", "Member")

    isFeatureAvailable = is_feature_enabled("enable-universal-doctor-search-98128723", str(member_id), user_role);
    print(f"DEBUG FLAG STATUS FOR USER {member_id}: ", isFeatureAvailable)
    
    # FEATURE FLAG CHECK 1
    if isFeatureAvailable:
        # ON STATE: Naya Universal Dynamic Search Parameter
        search_query = request.args.get('query', '')
        if not search_query:
            return jsonify({"error" : "Search 'query' parameter is mandatory"}), 400
        
        response, status_code = appointmentServices.universal_doctor_search(search_query)
        return jsonify(response), status_code
    else:
        # ⏱️ OFF STATE: Fallback To Old Specialization Search Only
        specialization_query = request.args.get('specialization', '')
        if not specialization_query:
            return jsonify({"error" : "Old search 'specialization' parameter is mandatory"}), 400
        
        #Purana service function query hit karega
        response, status_code = AppointmentService().search_doctors_by_specialization(specialization_query)
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
        
    response, status_code = appointmentServices.set_doctor_schedule_and_generate_slots(
        int(doctor_user_id), validated_data
    )
    return jsonify(response), status_code


@appointments_bp.route('/member/my-bookings', methods=['GET'])
@role_required(['Member'])
def get_my_bookings():
    member_id = get_jwt_identity()
    response, status_code = appointmentServices.get_patient_bookings(int(member_id))
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
        
    response, status_code = appointmentServices.request_appointment_cancellation(int(member_id), validated_data)
    return jsonify(response), status_code

#Cancellation request prr Doctor ka action
@appointments_bp.route('/doctor/action-approve-cancel', methods=['POST'])
@role_required(['Doctor']) 
def doctor_approve_cancel():
    doctor_user_id = get_jwt_identity()
    try:
        validated_data = doctor_approve_cancel_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = appointmentServices.doctor_approve_cancellation(int(doctor_user_id), validated_data)
    return jsonify(response), status_code


# ----------------- PATIENT DASHBOARD ENDPOINT -----------------
@appointments_bp.route('/member/cancellation-requests', methods=['GET'])
@role_required(['Member'])
def get_member_cancellations():
    member_id = get_jwt_identity()
    response, status_code = appointmentServices.get_patient_cancellation_requests(int(member_id))
    return jsonify(response), status_code


# ------------------ Doctor DASHBOARD ENDPOINT ------------------
@appointments_bp.route('/doctor/cancellation-requests', methods=['GET'])
@role_required(['Doctor'])
def get_admin_cancellations():
    response, status_code = appointmentServices.get_doctor_cancellation_dashboard()
    return jsonify(response), status_code

#Getting ALL appointments by Admin (Full View Dashboard)
@appointments_bp.route('/admin/all-appointments', methods=['GET'])
@role_required(['Admin'])
def get_all_appointments_dashboard():
    """
    Endpoint jo admin ko saare appointments aur unka total count laakar dega
    """
    response, status_code = appointmentServices.get_all_appointments_for_admin()
    return jsonify(response), status_code

# Timing config update endpoint
@appointments_bp.route('/doctor/update-timing-config', methods=['POST'])
@role_required(['Doctor'])
def update_timing_config():
    doctor_id = get_jwt_identity()
    return appointmentServices.update_doctor_availability_config(int(doctor_id), request.get_json())

# Holiday registry endpoint
@appointments_bp.route('/doctor/mark-holiday', methods=['POST'])
@role_required(['Doctor'])
def register_holiday():
    doctor_user_id = get_jwt_identity()
    try:
        validated_data = bulk_holiday_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    response, status_code = appointmentServices.update_doctor_holidays_bulk(int(doctor_user_id), validated_data)
    return jsonify(response), status_code