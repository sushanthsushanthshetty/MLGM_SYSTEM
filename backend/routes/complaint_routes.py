# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Complaint Routes
# =====================================================

from flask import Blueprint, request, jsonify
from backend.models import Complaint, Worker
from backend.routes.auth_routes import login_required
from datetime import datetime

complaint_bp = Blueprint('complaint', __name__)


# Complaint type mapping
COMPLAINT_TYPES = {
    'wages': 'Non-Payment of Wages',
    'safety': 'Safety Issues',
    'harassment': 'Workplace Harassment',
    'accommodation': 'Accommodation Problems',
    'working_hours': 'Excessive Working Hours',
    'contract': 'Contract Violation',
    'other': 'Other'
}


@complaint_bp.route('/add', methods=['POST'])
@login_required
def add_complaint():
    """Submit a new complaint"""
    try:
        worker_id = request.worker_id
        data = request.get_json()
        
        # Validate required fields
        category = data.get('type') or data.get('category')
        description = data.get('description')
        
        if not category:
            return jsonify({
                'success': False,
                'message': 'Complaint type is required'
            }), 400
        
        if not description or len(description.strip()) < 10:
            return jsonify({
                'success': False,
                'message': 'Please provide a detailed description (at least 10 characters)'
            }), 400
        
        # Map category to full name if needed
        if category in COMPLAINT_TYPES:
            category_full = COMPLAINT_TYPES[category]
        else:
            category_full = category
        
        # Prepare complaint data
        complaint_data = {
            'worker_id': worker_id,
            'employer_id': data.get('employer_id'),
            'category': category_full,
            'description': description.strip()
        }
        
        # Create complaint
        result = Complaint.create(complaint_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Complaint submitted successfully',
                'complaint_id': result['complaint_id']
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to submit complaint. Please try again.',
                'error': result.get('error')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error submitting complaint',
            'error': str(e)
        }), 500


@complaint_bp.route('/list', methods=['GET'])
@login_required
def list_complaints():
    """Get all complaints for current worker"""
    try:
        worker_id = request.worker_id
        
        complaints = Complaint.get_by_worker(worker_id)
        
        # Format complaints for response
        complaint_list = []
        for complaint in complaints:
            complaint_list.append({
                'id': complaint['complaint_id'],
                'db_id': complaint['id'],
                'type': complaint['category'],
                'description': complaint['description'],
                'status': complaint['status'].title().replace('_', ' '),
                'employer_name': complaint.get('employer_name'),
                'admin_remarks': complaint.get('admin_remarks'),
                'date': complaint['created_at'].strftime('%Y-%m-%d') if complaint['created_at'] else None,
                'created_at': complaint['created_at'].isoformat() if complaint['created_at'] else None,
                'resolved_at': complaint['resolved_at'].isoformat() if complaint.get('resolved_at') else None
            })
        
        return jsonify({
            'success': True,
            'complaints': complaint_list,
            'count': len(complaint_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching complaints',
            'error': str(e)
        }), 500


@complaint_bp.route('/<int:worker_id>', methods=['GET'])
def get_complaints_by_worker(worker_id):
    """Get all complaints for a specific worker by ID"""
    try:
        complaints = Complaint.get_by_worker(worker_id)
        
        # Format complaints for response
        complaint_list = []
        for complaint in complaints:
            complaint_list.append({
                'id': complaint['complaint_id'],
                'db_id': complaint['id'],
                'type': complaint['category'],
                'description': complaint['description'],
                'status': complaint['status'].title().replace('_', ' '),
                'employer_name': complaint.get('employer_name'),
                'admin_remarks': complaint.get('admin_remarks'),
                'date': complaint['created_at'].strftime('%Y-%m-%d') if complaint['created_at'] else None,
                'created_at': complaint['created_at'].isoformat() if complaint['created_at'] else None,
                'resolved_at': complaint['resolved_at'].isoformat() if complaint.get('resolved_at') else None
            })
        
        return jsonify({
            'success': True,
            'complaints': complaint_list,
            'count': len(complaint_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching complaints',
            'error': str(e)
        }), 500


@complaint_bp.route('/detail/<complaint_id>', methods=['GET'])
def get_complaint_detail(complaint_id):
    """Get complaint details by ID"""
    try:
        complaint = Complaint.get_by_id(complaint_id)
        
        if not complaint:
            return jsonify({
                'success': False,
                'message': 'Complaint not found'
            }), 404
        
        complaint_detail = {
            'id': complaint['complaint_id'],
            'db_id': complaint['id'],
            'type': complaint['category'],
            'description': complaint['description'],
            'status': complaint['status'].title().replace('_', ' '),
            'worker_name': complaint.get('worker_name'),
            'migrant_id': complaint.get('migrant_id'),
            'employer_name': complaint.get('employer_name'),
            'admin_remarks': complaint.get('admin_remarks'),
            'date': complaint['created_at'].strftime('%Y-%m-%d') if complaint['created_at'] else None,
            'created_at': complaint['created_at'].isoformat() if complaint['created_at'] else None,
            'resolved_at': complaint['resolved_at'].isoformat() if complaint.get('resolved_at') else None
        }
        
        return jsonify({
            'success': True,
            'complaint': complaint_detail
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching complaint details',
            'error': str(e)
        }), 500


@complaint_bp.route('/update_status', methods=['PUT'])
@login_required
def update_complaint_status():
    """Update complaint status (for admin use)"""
    try:
        data = request.get_json()
        
        complaint_id = data.get('complaint_id')
        status = data.get('status')
        admin_remarks = data.get('admin_remarks')
        
        if not complaint_id:
            return jsonify({
                'success': False,
                'message': 'Complaint ID is required'
            }), 400
        
        valid_statuses = ['pending', 'in_progress', 'resolved', 'rejected']
        if status not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Valid statuses are: {", ".join(valid_statuses)}'
            }), 400
        
        result = Complaint.update_status(complaint_id, status, admin_remarks)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Complaint status updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Failed to update status')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error updating complaint status',
            'error': str(e)
        }), 500


@complaint_bp.route('/stats/<int:worker_id>', methods=['GET'])
def get_complaint_stats(worker_id):
    """Get complaint statistics for a worker"""
    try:
        stats = Complaint.get_stats_by_worker(worker_id)
        
        return jsonify({
            'success': True,
            'stats': {
                'total': stats['total_complaints'] or 0,
                'pending': stats['pending_complaints'] or 0,
                'resolved': stats['resolved_complaints'] or 0,
                'in_progress': stats['in_progress_complaints'] or 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching complaint statistics',
            'error': str(e)
        }), 500