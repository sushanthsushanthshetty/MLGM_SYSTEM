# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Authentication Routes
# =====================================================

from flask import Blueprint, request, jsonify, session
from backend.models import Worker, Session
from functools import wraps

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id') or request.headers.get('Authorization')
        
        if not session_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required. Please login.'
            }), 401
        
        # Check if it's a Bearer token
        if session_id.startswith('Bearer '):
            session_id = session_id[7:]
        
        session_data = Session.get(session_id)
        
        if not session_data:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired session. Please login again.'
            }), 401
        
        # Store worker info in request context
        request.worker_id = session_data['worker_id']
        request.worker = session_data
        
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new worker"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field.replace("_", " ").title()} is required'
                }), 400
        
        # Validate phone number format
        phone = data.get('phone', '').strip()
        if not phone.isdigit() or len(phone) != 10:
            return jsonify({
                'success': False,
                'message': 'Please enter a valid 10-digit mobile number'
            }), 400
        
        # Check if phone already exists
        existing_worker = Worker.get_by_phone(phone)
        if existing_worker:
            return jsonify({
                'success': False,
                'message': 'This mobile number is already registered'
            }), 400
        
        # Validate age if provided
        age = data.get('age')
        if age:
            try:
                age = int(age)
                if age < 18 or age > 65:
                    return jsonify({
                        'success': False,
                        'message': 'Age must be between 18 and 65'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid age value'
                }), 400
        
        # Generate password from phone (for simple authentication)
        # In production, you would require a proper password
        password = data.get('password', phone)  # Default password is phone number
        
        # Prepare worker data
        worker_data = {
            'name': data.get('name', '').strip(),
            'phone': phone,
            'password': password,
            'email': data.get('email', '').strip() or None,
            'aadhaar': data.get('aadhaar', '').strip() or None,
            'skill': data.get('skill', '').strip() or None,
            'age': age,
            'gender': data.get('gender', '').strip() or None,
            'state': data.get('state', '').strip() or None,
            'district': data.get('district', '').strip() or None,
            'address': data.get('address', '').strip() or None
        }
        
        # Create worker
        result = Worker.create(worker_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'migrant_id': result['migrant_id'],
                'worker_id': result['worker_id']
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Registration failed. Please try again.',
                'error': result.get('error')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred during registration',
            'error': str(e)
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate worker and create session"""
    try:
        data = request.get_json()
        
        migrant_id = data.get('migrant_id', '').strip().upper()
        phone = data.get('phone', '').strip()
        password = data.get('password', phone)  # Default password is phone
        
        # Validate inputs
        if not migrant_id:
            return jsonify({
                'success': False,
                'message': 'Migrant ID is required'
            }), 400
        
        if not phone:
            return jsonify({
                'success': False,
                'message': 'Mobile number is required'
            }), 400
        
        # Authenticate worker
        worker = Worker.authenticate(migrant_id, phone)
        
        if not worker:
            return jsonify({
                'success': False,
                'message': 'Invalid Migrant ID or Mobile number'
            }), 401
        
        # Create session
        session_result = Session.create(
            worker_id=worker['id'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        if session_result['success']:
            # Set session in flask session
            session['session_id'] = session_result['session_id']
            session['worker_id'] = worker['id']
            session['migrant_id'] = worker['migrant_id']
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'session_id': session_result['session_id'],
                'worker': {
                    'id': worker['id'],
                    'migrant_id': worker['migrant_id'],
                    'name': worker['name'],
                    'phone': worker['phone'],
                    'skill': worker['skill']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create session'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred during login',
            'error': str(e)
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout worker and destroy session"""
    try:
        session_id = session.get('session_id') or request.headers.get('Authorization')
        
        if session_id:
            if session_id.startswith('Bearer '):
                session_id = session_id[7:]
            Session.delete(session_id)
        
        # Clear flask session
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred during logout',
            'error': str(e)
        }), 500


@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """Check if session is valid"""
    try:
        session_id = session.get('session_id') or request.headers.get('Authorization')
        
        if not session_id:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'No active session'
            }), 200
        
        if session_id.startswith('Bearer '):
            session_id = session_id[7:]
        
        session_data = Session.get(session_id)
        
        if session_data:
            return jsonify({
                'success': True,
                'authenticated': True,
                'worker': {
                    'id': session_data['worker_id'],
                    'migrant_id': session_data['migrant_id'],
                    'name': session_data['name'],
                    'phone': session_data['phone']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'Session expired'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'authenticated': False,
            'error': str(e)
        }), 500