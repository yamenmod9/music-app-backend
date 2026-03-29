from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def json_response(data, status=200):
    """Helper to create JSON responses"""
    return jsonify(data), status


def error_response(message, status=400):
    """Helper to create error responses"""
    return jsonify({'error': True, 'message': message}), status


def success_response(message='Success', data=None, status=200):
    """Helper to create success responses"""
    response = {'success': True, 'message': message}
    if data is not None:
        response['data'] = data
    return jsonify(response), status


def jwt_required_custom(fn):
    """Custom JWT required decorator with better error handling"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return error_response(str(e), 401)
    return wrapper
