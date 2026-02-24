# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Worker Routes
# =====================================================

from flask import Blueprint, request, jsonify
from backend.models import Worker, Complaint
from backend.routes.auth_routes import login_required
from datetime import datetime

worker_bp = Blueprint('worker', __name__)


@worker_bp.route('/profile/<int:worker_id>', methods=['GET'])
def get_profile(worker_id):
    """Get worker profile by ID"""
    try:
        worker = Worker.get_by_id(worker_id)
        
        if not worker:
            return jsonify({
                'success': False,
                'message': 'Worker not found'
            }), 404
        
        # Format the response
        profile = {
            'id': worker['id'],
            'migrant_id': worker['migrant_id'],
            'name': worker['name'],
            'email': worker['email'],
            'phone': worker['phone'],
            'aadhaar': worker['aadhaar'],
            'skill': worker['skill'],
            'age': worker['age'],
            'gender': worker['gender'],
            'state': worker['state'],
            'district': worker['district'],
            'address': worker['address'],
            'status': worker['status'],
            'current_employer': worker.get('current_employer_name'),
            'work_location': worker['work_location'],
            'registration_date': worker['created_at'].strftime('%d %B %Y') if worker['created_at'] else None,
            'created_at': worker['created_at'].isoformat() if worker['created_at'] else None
        }
        
        return jsonify({
            'success': True,
            'worker': profile
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching profile',
            'error': str(e)
        }), 500


@worker_bp.route('/profile', methods=['GET'])
@login_required
def get_current_profile():
    """Get current logged-in worker's profile"""
    try:
        worker_id = request.worker_id
        worker = Worker.get_by_id(worker_id)
        
        if not worker:
            return jsonify({
                'success': False,
                'message': 'Worker not found'
            }), 404
        
        # Format the response
        profile = {
            'id': worker['id'],
            'migrant_id': worker['migrant_id'],
            'name': worker['name'],
            'email': worker['email'],
            'phone': worker['phone'],
            'aadhaar': worker['aadhaar'],
            'skill': worker['skill'],
            'age': worker['age'],
            'gender': worker['gender'],
            'state': worker['state'],
            'district': worker['district'],
            'address': worker['address'],
            'status': worker['status'],
            'current_employer': worker.get('current_employer_name'),
            'work_location': worker['work_location'],
            'registration_date': worker['created_at'].strftime('%d %B %Y') if worker['created_at'] else None,
            'created_at': worker['created_at'].isoformat() if worker['created_at'] else None
        }
        
        return jsonify({
            'success': True,
            'worker': profile
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching profile',
            'error': str(e)
        }), 500


@worker_bp.route('/profile/update', methods=['PUT'])
@login_required
def update_profile():
    """Update worker profile"""
    try:
        worker_id = request.worker_id
        data = request.get_json()
        
        # Validate phone if provided
        if 'phone' in data:
            phone = data['phone']
            if phone:
                if not str(phone).isdigit() or len(str(phone)) != 10:
                    return jsonify({
                        'success': False,
                        'message': 'Please enter a valid 10-digit mobile number'
                    }), 400
                
                # Check if phone is already used by another worker
                existing = Worker.get_by_phone(phone)
                if existing and existing['id'] != worker_id:
                    return jsonify({
                        'success': False,
                        'message': 'This mobile number is already registered'
                    }), 400
        
        # Validate age if provided
        if 'age' in data and data['age']:
            try:
                age = int(data['age'])
                if age < 18 or age > 65:
                    return jsonify({
                        'success': False,
                        'message': 'Age must be between 18 and 65'
                    }), 400
                data['age'] = age
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid age value'
                }), 400
        
        # Update profile
        result = Worker.update(worker_id, data)
        
        if result['success']:
            # Fetch updated profile
            updated_worker = Worker.get_by_id(worker_id)
            
            profile = {
                'id': updated_worker['id'],
                'migrant_id': updated_worker['migrant_id'],
                'name': updated_worker['name'],
                'email': updated_worker['email'],
                'phone': updated_worker['phone'],
                'skill': updated_worker['skill'],
                'age': updated_worker['age'],
                'gender': updated_worker['gender'],
                'state': updated_worker['state'],
                'district': updated_worker['district'],
                'address': updated_worker['address'],
                'status': updated_worker['status']
            }
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'worker': profile
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Failed to update profile')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error updating profile',
            'error': str(e)
        }), 500


@worker_bp.route('/profile/password', methods=['PUT'])
@login_required
def update_password():
    """Update worker password"""
    try:
        worker_id = request.worker_id
        data = request.get_json()
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({
                'success': False,
                'message': 'Old password and new password are required'
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'New password must be at least 6 characters'
            }), 400
        
        result = Worker.update_password(worker_id, old_password, new_password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Password updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Failed to update password')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error updating password',
            'error': str(e)
        }), 500