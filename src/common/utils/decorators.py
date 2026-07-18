from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt

"""
def admin_required():
    def decorator(fn):
        @wraps(fn)
        @jwt_required()  # पहले चेक करेगा valid token है या नहीं
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            # Token बनाते वक्त हमने additional_claims में role डाला था
            if claims.get("role") != "Admin":
                return jsonify({"error": "Access Denied! Sirf Admin hi ye kaam kar sakta hai, bhai!"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

"""

def role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()  # टोकन वैलिडिटी चेक करेगा
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get("role")  # services.py वाले additional_claims से रोल मिला

            # डेटाबेस वाले केस-सेंसिटिव रोल नाम से मैच करें
            if user_role not in allowed_roles:
                return jsonify({
                    "error": f"Access Denied! Only {', '.join(allowed_roles)} can access this resource."
                }), 403
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator


"""
def doctor_required():
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != "Doctor":
                return jsonify({"error": "Access Denied! Sirf Doctors hi apni availability manage kar sakte hain!"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
"""
