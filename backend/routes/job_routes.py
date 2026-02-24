# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Job Routes
# =====================================================

from flask import Blueprint, request, jsonify
from backend.models import Job, JobApplication, Worker
from backend.routes.auth_routes import login_required

job_bp = Blueprint('job', __name__)


@job_bp.route('/list', methods=['GET'])
def get_jobs():
    """Get all open jobs"""
    try:
        status = request.args.get('status', 'open')
        skill = request.args.get('skill')
        
        jobs = Job.get_all(status=status, skill=skill)
        
        # Format jobs for response
        job_list = []
        for job in jobs:
            job_list.append({
                'id': job['id'],
                'job_id': job['job_id'],
                'title': job['title'],
                'description': job['description'],
                'skill_required': job['skill_required'],
                'location': job['location'],
                'wage_per_day': float(job['wage_per_day']) if job['wage_per_day'] else 0,
                'duration_days': job['duration_days'],
                'workers_needed': job['workers_needed'],
                'status': job['status'],
                'employer_name': job['employer_name'],
                'industry': job['industry'],
                'created_at': job['created_at'].isoformat() if job['created_at'] else None
            })
        
        return jsonify({
            'success': True,
            'jobs': job_list,
            'count': len(job_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching jobs',
            'error': str(e)
        }), 500


@job_bp.route('/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get job details"""
    try:
        job = Job.get_by_id(job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
        
        job_detail = {
            'id': job['id'],
            'job_id': job['job_id'],
            'title': job['title'],
            'description': job['description'],
            'skill_required': job['skill_required'],
            'location': job['location'],
            'wage_per_day': float(job['wage_per_day']) if job['wage_per_day'] else 0,
            'duration_days': job['duration_days'],
            'workers_needed': job['workers_needed'],
            'status': job['status'],
            'employer_name': job['employer_name'],
            'industry': job['industry'],
            'employer_location': job.get('employer_location'),
            'created_at': job['created_at'].isoformat() if job['created_at'] else None
        }
        
        return jsonify({
            'success': True,
            'job': job_detail
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching job details',
            'error': str(e)
        }), 500


@job_bp.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply_for_job(job_id):
    """Apply for a job"""
    try:
        worker_id = request.worker_id
        
        # Check if job exists and is open
        job = Job.get_by_id(job_id)
        if not job:
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
        
        if job['status'] != 'open':
            return jsonify({
                'success': False,
                'message': 'This job is no longer accepting applications'
            }), 400
        
        # Create application
        result = JobApplication.create(job_id, worker_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Application submitted successfully',
                'application_id': result['application_id']
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Failed to submit application')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error submitting application',
            'error': str(e)
        }), 500


@job_bp.route('/applications', methods=['GET'])
@login_required
def get_my_applications():
    """Get all applications for current worker"""
    try:
        worker_id = request.worker_id
        
        applications = JobApplication.get_by_worker(worker_id)
        
        # Format applications for response
        app_list = []
        for app in applications:
            app_list.append({
                'id': app['id'],
                'application_id': app['application_id'],
                'job_id': app['job_id'],
                'job_title': app['title'],
                'location': app['location'],
                'wage_per_day': float(app['wage_per_day']) if app['wage_per_day'] else 0,
                'duration_days': app['duration_days'],
                'employer_name': app['employer_name'],
                'status': app['status'].title(),
                'applied_at': app['applied_at'].isoformat() if app['applied_at'] else None
            })
        
        return jsonify({
            'success': True,
            'applications': app_list,
            'count': len(app_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching applications',
            'error': str(e)
        }), 500


@job_bp.route('/applications/stats', methods=['GET'])
@login_required
def get_application_stats():
    """Get application statistics for current worker"""
    try:
        worker_id = request.worker_id
        
        stats = JobApplication.get_stats_by_worker(worker_id)
        
        return jsonify({
            'success': True,
            'stats': {
                'total': stats['total_applications'] or 0,
                'pending': stats['pending_applications'] or 0,
                'accepted': stats['accepted_applications'] or 0,
                'rejected': stats['rejected_applications'] or 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching application statistics',
            'error': str(e)
        }), 500