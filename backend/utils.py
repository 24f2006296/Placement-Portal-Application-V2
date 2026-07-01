from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user = get_jwt_identity()
            if user.get('role') != 'admin':
                return jsonify({"error": "Admin access required!"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def company_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user = get_jwt_identity()
            if user.get('role') != 'company':
                return jsonify({"error": "Company access required!"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def student_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user = get_jwt_identity()
            if user.get('role') != 'student':
                return jsonify({"error": "Student access required!"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper