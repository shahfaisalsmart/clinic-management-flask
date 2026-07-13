from flask import Blueprint, request, jsonify
from src.reimbursement.schemas import LaunchProductSchema, OptProductSchema, CreateMedicalRecordSchema, FileClaimSchema, ProcessClaimSchema
from src.reimbursement.services import ReimbursementService
from src.common.utils.decorators import role_required 
from flask_jwt_extended import get_jwt_identity, get_jwt
from src.common.utils.ld_client import is_feature_enabled
from marshmallow import ValidationError

reimburse_bp = Blueprint('reimbursement', __name__, url_prefix='/reimbursement')

#=================SCHEMAS OBJECT MAKING ==============================
launch_schema = LaunchProductSchema()
opt_schema = OptProductSchema()
record_schema = CreateMedicalRecordSchema()
claim_schema = FileClaimSchema()
process_schema = ProcessClaimSchema()

#======================SERVICES OBJECT MAKING========================
reimbursementServices = ReimbursementService()



#=========================== ADMIN PRODUCT LAUNCH ENDPOINTS=========================================
@reimburse_bp.route('/admin/launch-product', methods=['POST'])
@role_required(['Admin']) # Sirf health provider/admin access kar sake
def admin_launch_product():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Payload data nahi mila"}), 400
        
    try:
        validated_data = launch_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = reimbursementServices.launch_new_product(validated_data)
    return jsonify(response), status_code


@reimburse_bp.route('/admin/dashboard', methods=['GET'])
@role_required(['Admin'])
def admin_insurance_dashboard():
    response, status_code = reimbursementServices.get_admin_comprehensive_dashboard()
    return jsonify(response), status_code


# ================= MEMBER/PATIENT INSURANCE ENDPOINTS =================
@reimburse_bp.route('/member/products/search', methods=['GET'])
@role_required(['Member']) # Sirf patients access kar sakein
def patient_insurance_search():
    search_query = request.args.get('query', '')
    if not search_query:
        return jsonify({"error": "Search 'query' parameter mandatory hai"}), 400

    response, status_code = reimbursementServices.patient_universal_product_search(search_query)
    return jsonify(response), status_code


@reimburse_bp.route('/member/opt-product', methods=['POST'])
@role_required(['Member'])
def patient_opt_insurance():
    member_id = get_jwt_identity() # Current login member ki ID uthayega
    #claims = get_jwt()
    #user_role = claims.get("role", "Member")

    """
    # 🛑 FEATURE FLAG GATEKEEPER WALL
    # LaunchDarkly dashboard par flag key banayi: "enable-insurance-system"
    if not is_feature_enabled("enable-insurance-system", str(member_id), user_role):
        return jsonify({
            "error": "Feature Unavailable",
            "message": "Insurance purchase module is currently disabled by administration for system maintenance."
        }), 403
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Payload data nahi mila"}), 400

    try:
        validated_data = opt_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    response, status_code = reimbursementServices.opt_insurance_product(int(member_id), validated_data)
    return jsonify(response), status_code


@reimburse_bp.route('/member/dashboard', methods=['GET'])
@role_required(['Member'])
def patient_insurance_dashboard():
    member_id = get_jwt_identity()
    response, status_code = reimbursementServices.get_patient_insurance_dashboard(int(member_id))
    return jsonify(response), status_code


#=========== Reimbursement process============================================
#  1. DOCTOR: Log Patient Treatment Receipt
@reimburse_bp.route('/doctor/create-record', methods=['POST'])
@role_required(['Doctor'])
def doctor_log_record():
    doctor_id = get_jwt_identity()
    json_data = request.get_json()
    try:
        validated_data = record_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = reimbursementServices.doctor_create_medical_record(int(doctor_id), validated_data)
    return jsonify(response), status_code

#  2. PATIENT: Universal Search Records & File Claim
@reimburse_bp.route('/member/records/search', methods=['GET'])
@role_required(['Member'])
def patient_search_records():
    member_id = get_jwt_identity()
    query = request.args.get('query', '')
    response, status_code = reimbursementServices.patient_search_medical_records(int(member_id), query)
    return jsonify(response), status_code

@reimburse_bp.route('/member/file-claim', methods=['POST'])
@role_required(['Member'])
def patient_file_claim():
    member_id = get_jwt_identity()
    json_data = request.get_json()
    try:
        validated_data = claim_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = reimbursementServices.patient_file_reimbursement_claim(int(member_id), validated_data)
    return jsonify(response), status_code

# 3. ADMIN/HEALTH PROVIDER: Approve or Reject Claims Engine
@reimburse_bp.route('/admin/claims/<int:claim_id>/process', methods=['POST'])
@role_required(['Admin'])
def admin_process_claim(claim_id):
    json_data = request.get_json()
    try:
        validated_data = process_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    response, status_code = reimbursementServices.admin_process_reimbursement_claim(claim_id, validated_data)
    return jsonify(response), status_code