# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Employer Routes - Registration, Login, Dashboard
# =====================================================

from flask import Blueprint, request, jsonify, session
from backend.models import Employer, Job, JobApplication
from functools import wraps
import uuid
from datetime import datetime, timedelta
import pymysql

employer_bp = Blueprint('employer', __name__)

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


def employer_login_required(f):
    """Decorator to require employer login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        employer_session = session.get('employer_session') or request.headers.get('X-Employer-Session')
        
        if not employer_session:
            return jsonify({
                'success': False,
                'message': 'Employer authentication required. Please login.'
            }), 401
        
        # Get employer from session
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM employers WHERE employer_id = %s
            """, (employer_session,))
            employer = cursor.fetchone()
            
            if not employer:
                return jsonify({
                    'success': False,
                    'message': 'Invalid session. Please login again.'
                }), 401
            
            # Check if employer is verified
            if employer['is_verified'] != 'verified':
                return jsonify({
                    'success': False,
                    'message': 'Your account is not yet verified. Please wait for admin approval.',
                    'verification_status': employer['is_verified']
                }), 403
            
            request.employer = employer
            request.employer_id = employer['id']
            
        finally:
            conn.close()
        
        return f(*args, **kwargs)
    return decorated_function


# =====================================================
# Employer Registration
# =====================================================

@employer_bp.route('/register', methods=['POST'])
def register():
    """Register a new employer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['company_name', 'contact_person', 'phone', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field.replace("_", " ").title()} is required'
                }), 400
        
        # Validate phone number format
        phone = data.get('phone', '').strip()
        if not phone.isdigit() or len(phone) < 10:
            return jsonify({
                'success': False,
                'message': 'Please enter a valid phone number'
            }), 400
        
        # Check if email already exists
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employers WHERE email = %s", (data.get('email'),))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': 'This email is already registered'
            }), 400
        
        # Check if phone already exists
        cursor.execute("SELECT * FROM employers WHERE phone = %s", (phone,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': 'This phone number is already registered'
            }), 400
        conn.close()
        
        # Prepare employer data
        employer_data = {
            'company_name': data.get('company_name', '').strip(),
            'industry': data.get('industry', '').strip() or None,
            'location': data.get('location', '').strip() or None,
            'contact_person': data.get('contact_person', '').strip(),
            'phone': phone,
            'email': data.get('email', '').strip(),
            'password': data.get('password'),
            'gst_number': data.get('gst_number', '').strip() or None,
            'registration_number': data.get('registration_number', '').strip() or None,
            'address': data.get('address', '').strip() or None
        }
        
        # Create employer
        result = Employer.create(employer_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Registration successful. Please wait for admin verification before you can login.',
                'employer_id': result['employer_id']
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


# =====================================================
# Employer Login
# =====================================================

@employer_bp.route('/login', methods=['POST'])
def login():
    """Authenticate employer and create session"""
    try:
        data = request.get_json()
        
        employer_id = data.get('employer_id', '').strip().upper()
        password = data.get('password', '')
        
        # Validate inputs
        if not employer_id:
            return jsonify({
                'success': False,
                'message': 'Employer ID is required'
            }), 400
        
        if not password:
            return jsonify({
                'success': False,
                'message': 'Password is required'
            }), 400
        
        # Authenticate employer
        employer = Employer.authenticate(employer_id, password)
        
        if not employer:
            return jsonify({
                'success': False,
                'message': 'Invalid Employer ID or Password'
            }), 401
        
        # Check verification status
        if employer['is_verified'] == 'pending':
            return jsonify({
                'success': False,
                'message': 'Your account is pending verification. Please wait for admin approval.',
                'verification_status': 'pending'
            }), 403
        
        if employer['is_verified'] == 'rejected':
            return jsonify({
                'success': False,
                'message': 'Your account verification was rejected. Please contact support.',
                'verification_status': 'rejected'
            }), 403
        
        # Create session
        session['employer_session'] = employer['employer_id']
        session['employer_id'] = employer['id']
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'employer': {
                'id': employer['id'],
                'employer_id': employer['employer_id'],
                'company_name': employer['company_name'],
                'contact_person': employer['contact_person'],
                'email': employer['email'],
                'phone': employer['phone']
            }
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred during login',
            'error': str(e)
        }), 500


# =====================================================
# Employer Logout
# =====================================================

@employer_bp.route('/logout', methods=['POST'])
def logout():
    """Logout employer"""
    session.pop('employer_session', None)
    session.pop('employer_id', None)
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


# =====================================================
# Check Session
# =====================================================

@employer_bp.route('/check-session', methods=['GET'])
def check_session():
    """Check if employer session is valid"""
    try:
        employer_session = session.get('employer_session') or request.headers.get('X-Employer-Session')
        
        if not employer_session:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'No active session'
            }), 200
        
        employer = Employer.get_by_employer_id(employer_session)
        
        if employer and employer['is_verified'] == 'verified':
            return jsonify({
                'success': True,
                'authenticated': True,
                'employer': {
                    'id': employer['id'],
                    'employer_id': employer['employer_id'],
                    'company_name': employer['company_name'],
                    'contact_person': employer['contact_person'],
                    'email': employer['email'],
                    'phone': employer['phone']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'Session expired or account not verified'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'authenticated': False,
            'error': str(e)
        }), 500


# =====================================================
# Employer Dashboard
# =====================================================

@employer_bp.route('/dashboard', methods=['GET'])
@employer_login_required
def get_dashboard():
    """Get employer dashboard data"""
    try:
        employer = request.employer
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get job stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_jobs,
                SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_jobs,
                SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed_jobs,
                SUM(CASE WHEN status = 'filled' THEN 1 ELSE 0 END) as filled_jobs
            FROM jobs
            WHERE employer_id = %s
        """, (employer['id'],))
        job_stats = cursor.fetchone()
        
        # Get application stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_applications,
                SUM(CASE WHEN a.status = 'pending' THEN 1 ELSE 0 END) as pending_applications,
                SUM(CASE WHEN a.status = 'accepted' THEN 1 ELSE 0 END) as accepted_applications,
                SUM(CASE WHEN a.status = 'rejected' THEN 1 ELSE 0 END) as rejected_applications
            FROM job_applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE j.employer_id = %s
        """, (employer['id'],))
        app_stats = cursor.fetchone()
        
        # Get recent applications
        cursor.execute("""
            SELECT a.*, j.title as job_title, w.name as worker_name, 
                   w.migrant_id, w.phone, w.skill
            FROM job_applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN workers w ON a.worker_id = w.id
            WHERE j.employer_id = %s
            ORDER BY a.applied_at DESC
            LIMIT 10
        """, (employer['id'],))
        recent_applications = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'employer': {
                'id': employer['id'],
                'employer_id': employer['employer_id'],
                'company_name': employer['company_name'],
                'industry': employer['industry'],
                'location': employer['location'],
                'contact_person': employer['contact_person'],
                'email': employer['email'],
                'phone': employer['phone'],
                'rating': float(employer['rating']) if employer['rating'] else 0.0,
                'workers_count': employer['workers_count'] or 0
            },
            'job_stats': job_stats,
            'application_stats': app_stats,
            'recent_applications': recent_applications
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error loading dashboard',
            'error': str(e)
        }), 500


# =====================================================
# Job Management
# =====================================================

@employer_bp.route('/jobs', methods=['GET'])
@employer_login_required
def get_employer_jobs():
    """Get all jobs by employer"""
    try:
        employer_id = request.employer_id
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT j.*, 
                   COUNT(a.id) as application_count,
                   SUM(CASE WHEN a.status = 'pending' THEN 1 ELSE 0 END) as pending_count
            FROM jobs j
            LEFT JOIN job_applications a ON j.id = a.job_id
            WHERE j.employer_id = %s
            GROUP BY j.id
            ORDER BY j.created_at DESC
        """, (employer_id,))
        
        jobs = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'jobs': jobs
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching jobs',
            'error': str(e)
        }), 500


@employer_bp.route('/jobs', methods=['POST'])
@employer_login_required
def create_job():
    """Create a new job listing"""
    try:
        data = request.get_json()
        employer_id = request.employer_id
        
        # Validate required fields
        required_fields = ['title', 'skill_required', 'location']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field.replace("_", " ").title()} is required'
                }), 400
        
        job_data = {
            'employer_id': employer_id,
            'title': data.get('title'),
            'description': data.get('description'),
            'skill_required': data.get('skill_required'),
            'location': data.get('location'),
            'wage_per_day': data.get('wage_per_day'),
            'duration_days': data.get('duration_days'),
            'workers_needed': data.get('workers_needed')
        }
        
        result = Job.create(job_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Job created successfully',
                'job_id': result['job_id']
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create job',
                'error': result.get('error')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error creating job',
            'error': str(e)
        }), 500


@employer_bp.route('/jobs/<int:job_id>/close', methods=['POST'])
@employer_login_required
def close_job(job_id):
    """Close a job listing"""
    try:
        employer_id = request.employer_id
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verify job belongs to employer
        cursor.execute("SELECT * FROM jobs WHERE id = %s AND employer_id = %s", (job_id, employer_id))
        job = cursor.fetchone()
        
        if not job:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
        
        cursor.execute("UPDATE jobs SET status = 'closed' WHERE id = %s", (job_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Job closed successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error closing job',
            'error': str(e)
        }), 500


# =====================================================
# Application Management
# =====================================================

@employer_bp.route('/applications', methods=['GET'])
@employer_login_required
def get_employer_applications():
    """Get all applications for employer's jobs"""
    try:
        employer_id = request.employer_id
        status_filter = request.args.get('status')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT a.*, j.title as job_title, j.job_id, j.location, j.wage_per_day,
                   w.name as worker_name, w.migrant_id, w.phone, w.skill, w.age
            FROM job_applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN workers w ON a.worker_id = w.id
            WHERE j.employer_id = %s
        """
        params = [employer_id]
        
        if status_filter:
            query += " AND a.status = %s"
            params.append(status_filter)
        
        query += " ORDER BY a.applied_at DESC"
        
        cursor.execute(query, params)
        applications = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'applications': applications
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching applications',
            'error': str(e)
        }), 500


@employer_bp.route('/applications/<int:application_id>/accept', methods=['POST'])
@employer_login_required
def accept_application(application_id):
    """Accept a job application"""
    try:
        employer_id = request.employer_id
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verify application belongs to employer's job
        cursor.execute("""
            SELECT a.*, j.employer_id, j.id as job_id
            FROM job_applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.id = %s
        """, (application_id,))
        app = cursor.fetchone()
        
        if not app or app['employer_id'] != employer_id:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Application not found'
            }), 404
        
        # Update application status
        cursor.execute("""
            UPDATE job_applications 
            SET status = 'accepted', responded_at = NOW()
            WHERE id = %s
        """, (application_id,))
        
        # Update worker's current employer
        cursor.execute("""
            UPDATE workers 
            SET current_employer_id = %s
            WHERE id = %s
        """, (employer_id, app['worker_id']))
        
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


@employer_bp.route('/applications/<int:application_id>/reject', methods=['POST'])
@employer_login_required
def reject_application(application_id):
    """Reject a job application"""
    try:
        employer_id = request.employer_id
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verify application belongs to employer's job
        cursor.execute("""
            SELECT a.*, j.employer_id
            FROM job_applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.id = %s
        """, (application_id,))
        app = cursor.fetchone()
        
        if not app or app['employer_id'] != employer_id:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Application not found'
            }), 404
        
        # Update application status
        cursor.execute("""
            UPDATE job_applications 
            SET status = 'rejected', responded_at = NOW()
            WHERE id = %s
        """, (application_id,))
        
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
# Public Employer List (for workers)
# =====================================================

@employer_bp.route('/list', methods=['GET'])
def get_employers():
    """Get all verified employers (public)"""
    try:
        # Get status filter from query params
        status = request.args.get('status')
        
        employers = Employer.get_all(status=status, verification_status='verified')
        
        # Format employers for response
        employer_list = []
        for employer in employers:
            employer_list.append({
                'id': employer['id'],
                'employer_id': employer['employer_id'],
                'name': employer['name'],
                'type': employer['type'],
                'industry': employer['type'],
                'location': employer['location'],
                'contact_person': employer['contact_person'],
                'phone': employer['phone'],
                'email': employer['email'],
                'status': employer['status'].title() if employer['status'] else 'Active',
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
    """Get employer by ID (public)"""
    try:
        employer = Employer.get_by_id(employer_id)
        
        if not employer or employer['is_verified'] != 'verified':
            return jsonify({
                'success': False,
                'message': 'Employer not found'
            }), 404
        
        employer_detail = {
            'id': employer['id'],
            'employer_id': employer['employer_id'],
            'name': employer['name'],
            'type': employer['type'],
            'industry': employer['type'],
            'location': employer['location'],
            'contact_person': employer['contact_person'],
            'phone': employer['phone'],
            'email': employer['email'],
            'status': employer['status'].title() if employer['status'] else 'Active',
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
        all_employers = Employer.get_all(verification_status='verified')
        
        total_workers = sum(e['workers'] or 0 for e in all_employers)
        avg_rating = sum(float(e['rating'] or 0) for e in all_employers) / len(all_employers) if all_employers else 0
        
        stats = {
            'total_employers': len(all_employers),
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