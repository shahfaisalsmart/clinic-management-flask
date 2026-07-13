from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from src.member.services import MemberService
from src.member.schemas import MemberUpdateSchema
from src.common.utils.decorators import role_required  
from marshmallow import ValidationError

member_bp = Blueprint('member', __name__, url_prefix='/member')

# ========= SCHEMAS OBJECT MAKING ===================
update_schema = MemberUpdateSchema()

# ============ SERVICE OBJECT MAKING ===================
memberService = MemberService()


# 1. Member profile (members only)
@member_bp.route('/profile', methods=['GET'])
@role_required(['Member'])
def get_member_profile():
    current_user_id = get_jwt_identity()  # user id, token se mili
    response, status_code = memberService.get_profile(int(current_user_id))
    return jsonify(response), status_code

# 2. updating member profile
@member_bp.route('/profile', methods=['PUT'])
@role_required(['Member'])
def update_member_profile():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Data nahi mila"}), 400
        
    try:
        validated_data = update_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    current_user_id = get_jwt_identity()
    response, status_code = memberService.update_profile(int(current_user_id), validated_data)
    return jsonify(response), status_code
