# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Dashboard Routes
# =====================================================

from flask import Blueprint, request, jsonify
from backend.models import Worker, Complaint, Employer
from backend.routes.auth_routes import login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/<int:worker_id>', methods=['GET'])
def get_dashboard(worker_id):
    """Get dashboard data for a worker"""
    try:
        # Get worker details
        worker = Worker.get_by_id(worker_id)
        
        if not worker:
            return jsonify({
                'success': False,
                'message': 'Worker not found'
            }), 404
        
        # Get complaint statistics
        stats = Complaint.get_stats_by_worker(worker_id)
        
        # Format worker info
        worker_info = {
            'id': worker['id'],
            'migrant_id': worker['migrant_id'],
            'name': worker['name'],
            'phone': worker['phone'],
            'skill': worker['skill'],
            'status': worker['status'],
            'current_employer': worker.get('current_employer_name'),
            'work_location': worker['work_location']
        }
        
        # Format statistics
        complaint_stats = {
            'total': stats['total_complaints'] or 0,
            'pending': stats['pending_complaints'] or 0,
            'resolved': stats['resolved_complaints'] or 0,
            'in_progress': stats['in_progress_complaints'] or 0
        }
        
        return jsonify({
            'success': True,
            'worker': worker_info,
            'stats': complaint_stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching dashboard data',
            'error': str(e)
        }), 500


@dashboard_bp.route('/current', methods=['GET'])
@login_required
def get_current_dashboard():
    """Get dashboard data for current logged-in worker"""
    try:
        worker_id = request.worker_id
        
        # Get worker details
        worker = Worker.get_by_id(worker_id)
        
        if not worker:
            return jsonify({
                'success': False,
                'message': 'Worker not found'
            }), 404
        
        # Get complaint statistics
        stats = Complaint.get_stats_by_worker(worker_id)
        
        # Get recent complaints (last 5)
        complaints = Complaint.get_by_worker(worker_id)
        recent_complaints = []
        for complaint in complaints[:5]:
            recent_complaints.append({
                'id': complaint['complaint_id'],
                'type': complaint['category'],
                'status': complaint['status'].title().replace('_', ' '),
                'date': complaint['created_at'].strftime('%Y-%m-%d') if complaint['created_at'] else None
            })
        
        # Format worker info
        worker_info = {
            'id': worker['id'],
            'migrant_id': worker['migrant_id'],
            'name': worker['name'],
            'phone': worker['phone'],
            'skill': worker['skill'],
            'status': worker['status'],
            'current_employer': worker.get('current_employer_name'),
            'work_location': worker['work_location'],
            'registration_date': worker['created_at'].strftime('%d %B %Y') if worker['created_at'] else None
        }
        
        # Format statistics
        complaint_stats = {
            'total': stats['total_complaints'] or 0,
            'pending': stats['pending_complaints'] or 0,
            'resolved': stats['resolved_complaints'] or 0,
            'in_progress': stats['in_progress_complaints'] or 0
        }
        
        return jsonify({
            'success': True,
            'worker': worker_info,
            'stats': complaint_stats,
            'recent_complaints': recent_complaints
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching dashboard data',
            'error': str(e)
        }), 500


@dashboard_bp.route('/summary', methods=['GET'])
def get_system_summary():
    """Get overall system summary (public stats)"""
    try:
        # Get all employers
        employers = Employer.get_all()
        
        # Calculate stats
        total_employers = len(employers)
        active_employers = len([e for e in employers if e['status'] == 'active'])
        
        return jsonify({
            'success': True,
            'summary': {
                'total_employers': total_employers,
                'active_employers': active_employers
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching system summary',
            'error': str(e)
        }), 500