# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Admin Routes - For managing applications and complaints
# =====================================================

from flask import Blueprint, request, jsonify
from backend.models import JobApplication, Complaint, Worker, Job
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

admin_bp = Blueprint('admin', __name__)

def get_connection():
    """Get database connection"""
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='mlgms_db',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )


def admin_required(f):
    """Decorator to check admin authentication"""
    def decorated_function(*args, **kwargs):
        # Simple admin check - in production use proper session/auth
        admin_id = request.headers.get('X-Admin-ID')
        if not admin_id:
            return jsonify({
                'success': False,
                'message': 'Admin authentication required'
            }), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


# =====================================================
# Admin Authentication
# =====================================================

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if admin and check_password_hash(admin['password'], password):
            return jsonify({
                'success': True,
                'message': 'Admin login successful',
                'admin': {
                    'id': admin['id'],
                    'username': admin['username'],
                    'name': admin['name'],
                    'role': admin['role']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error during login',
            'error': str(e)
        }), 500


# =====================================================
# Job Applications Management
# =====================================================

@admin_bp.route('/applications', methods=['GET'])
def get_all_applications():
    """Get all job applications (for admin)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        status_filter = request.args.get('status')
        
        query = """
            SELECT a.*, j.title as job_title, j.location, j.wage_per_day,
                   w.name as worker_name, w.migrant_id, w.phone, w.skill,
                   e.company_name as employer_name
            FROM job_applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN workers w ON a.worker_id = w.id
            JOIN employers e ON j.employer_id = e.id
        """
        
        if status_filter:
            query += " WHERE a.status = %s"
            cursor.execute(query, (status_filter,))
        else:
            query += " ORDER BY a.applied_at DESC"
            cursor.execute(query)
        
        applications = cursor.fetchall()
        conn.close()
        
        # Format applications
        app_list = []
        for app in applications:
            app_list.append({
                'id': app['id'],
                'application_id': app['application_id'],
                'job_title': app['job_title'],
                'employer_name': app['employer_name'],
                'location': app['location'],
                'wage_per_day': float(app['wage_per_day']) if app['wage_per_day'] else 0,
                'worker_name': app['worker_name'],
                'migrant_id': app['migrant_id'],
                'phone': app['phone'],
                'skill': app['skill'],
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


@admin_bp.route('/applications/<application_id>/accept', methods=['POST'])
def accept_application(application_id):
    """Accept a job application"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update application status
        cursor.execute("""
            UPDATE job_applications 
            SET status = 'accepted', responded_at = NOW()
            WHERE id = %s OR application_id = %s
        """, (application_id, application_id))
        
        # Get the application details
        cursor.execute("""
            SELECT a.*, j.id as job_id, w.id as worker_id
            FROM job_applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN workers w ON a.worker_id = w.id
            WHERE a.id = %s OR a.application_id = %s
        """, (application_id, application_id))
        
        app = cursor.fetchone()
        
        if app:
            # Update worker's current employer
            cursor.execute("""
                UPDATE workers 
                SET current_employer_id = (SELECT employer_id FROM jobs WHERE id = %s)
                WHERE id = %s
            """, (app['job_id'], app['worker_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Application accepted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error accepting application',
            'error': str(e)
        }), 500


@admin_bp.route('/applications/<application_id>/reject', methods=['POST'])
def reject_application(application_id):
    """Reject a job application"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE job_applications 
            SET status = 'rejected', responded_at = NOW()
            WHERE id = %s OR application_id = %s
        """, (application_id, application_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Application rejected'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error rejecting application',
            'error': str(e)
        }), 500


# =====================================================
# Complaints Management
# =====================================================

@admin_bp.route('/complaints', methods=['GET'])
def get_all_complaints():
    """Get all complaints (for admin)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        status_filter = request.args.get('status')
        
        query = """
            SELECT c.*, w.name as worker_name, w.migrant_id, w.phone,
                   e.company_name as employer_name
            FROM complaints c
            JOIN workers w ON c.worker_id = w.id
            LEFT JOIN employers e ON c.employer_id = e.id
        """
        
        if status_filter:
            query += " WHERE c.status = %s ORDER BY c.created_at DESC"
            cursor.execute(query, (status_filter,))
        else:
            query += " ORDER BY c.created_at DESC"
            cursor.execute(query)
        
        complaints = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'complaints': complaints,
            'count': len(complaints)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching complaints',
            'error': str(e)
        }), 500


@admin_bp.route('/complaints/<complaint_id>/resolve', methods=['POST'])
def resolve_complaint(complaint_id):
    """Resolve a complaint"""
    try:
        data = request.get_json()
        remarks = data.get('remarks', '')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE complaints 
            SET status = 'resolved', admin_remarks = %s, resolved_at = NOW()
            WHERE id = %s OR complaint_id = %s
        """, (remarks, complaint_id, complaint_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Complaint resolved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error resolving complaint',
            'error': str(e)
        }), 500


# =====================================================
# Dashboard Stats
# =====================================================

@admin_bp.route('/stats', methods=['GET'])
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Workers count
        cursor.execute("SELECT COUNT(*) as count FROM workers WHERE status = 'active'")
        stats['total_workers'] = cursor.fetchone()['count']
        
        # Jobs count
        cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE status = 'open'")
        stats['open_jobs'] = cursor.fetchone()['count']
        
        # Applications stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM job_applications
        """)
        app_stats = cursor.fetchone()
        stats['applications'] = app_stats
        
        # Complaints stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved
            FROM complaints
        """)
        complaint_stats = cursor.fetchone()
        stats['complaints'] = complaint_stats
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching stats',
            'error': str(e)
        }), 500