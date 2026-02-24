# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Employer Routes
# =====================================================

from flask import Blueprint, request, jsonify
from backend.models import Employer

employer_bp = Blueprint('employer', __name__)


@employer_bp.route('/list', methods=['GET'])
def get_employers():
    """Get all employers"""
    try:
        # Get status filter from query params
        status = request.args.get('status')
        
        employers = Employer.get_all(status)
        
        # Format employers for response
        employer_list = []
        for employer in employers:
            employer_list.append({
                'id': employer['id'],
                'name': employer['name'],
                'type': employer['type'],
                'industry': employer['type'],
                'location': employer['location'],
                'contact_person': employer['contact_person'],
                'phone': employer['phone'],
                'email': employer['email'],
                'status': employer['status'].title(),
                'rating': float(employer['rating']) if employer['rating'] else 0.0,
                'workers': employer['workers'] or 0,
                'created_at': employer['created_at'].isoformat() if employer['created_at'] else None
            })
        
        return jsonify({
            'success': True,
            'employers': employer_list,
            'count': len(employer_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching employers',
            'error': str(e)
        }), 500


@employer_bp.route('/<int:employer_id>', methods=['GET'])
def get_employer(employer_id):
    """Get employer by ID"""
    try:
        employer = Employer.get_by_id(employer_id)
        
        if not employer:
            return jsonify({
                'success': False,
                'message': 'Employer not found'
            }), 404
        
        employer_detail = {
            'id': employer['id'],
            'name': employer['name'],
            'type': employer['type'],
            'industry': employer['type'],
            'location': employer['location'],
            'contact_person': employer['contact_person'],
            'phone': employer['phone'],
            'email': employer['email'],
            'status': employer['status'].title(),
            'rating': float(employer['rating']) if employer['rating'] else 0.0,
            'workers': employer['workers'] or 0,
            'created_at': employer['created_at'].isoformat() if employer['created_at'] else None
        }
        
        return jsonify({
            'success': True,
            'employer': employer_detail
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching employer details',
            'error': str(e)
        }), 500


@employer_bp.route('/stats', methods=['GET'])
def get_employer_stats():
    """Get employer statistics"""
    try:
        all_employers = Employer.get_all()
        active_employers = Employer.get_all(status='active')
        
        total_workers = sum(e['workers'] or 0 for e in all_employers)
        avg_rating = sum(float(e['rating'] or 0) for e in all_employers) / len(all_employers) if all_employers else 0
        
        stats = {
            'total_employers': len(all_employers),
            'active_employers': len(active_employers),
            'inactive_employers': len(all_employers) - len(active_employers),
            'total_workers': total_workers,
            'average_rating': round(avg_rating, 2)
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching employer statistics',
            'error': str(e)
        }), 500