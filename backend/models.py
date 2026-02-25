# =====================================================
# Migrant Labor & Grievance Management System (MLGMS)
# Database Models - Using PyMySQL
# =====================================================

import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
from flask import current_app

# Database connection pool
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


class Worker:
    """Worker model for migrant workers"""
    
    @staticmethod
    def generate_migrant_id(cursor):
        """Generate unique migrant ID"""
        cursor.execute("SELECT COALESCE(MAX(CAST(SUBSTRING(migrant_id, 4) AS UNSIGNED)), 0) as max_id FROM workers")
        result = cursor.fetchone()
        max_id = result['max_id'] if result else 0
        return f"MIG{str(max_id + 1).zfill(5)}"
    
    @staticmethod
    def create(data):
        """Create a new worker"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            migrant_id = Worker.generate_migrant_id(cursor)
            hashed_password = generate_password_hash(str(data.get('password', data.get('phone'))))
            
            cursor.execute("""
                INSERT INTO workers (migrant_id, name, email, phone, password, aadhaar, skill, age, gender, state, district, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                migrant_id,
                data.get('name'),
                data.get('email'),
                data.get('phone'),
                hashed_password,
                data.get('aadhaar'),
                data.get('skill'),
                data.get('age'),
                data.get('gender'),
                data.get('state'),
                data.get('district'),
                data.get('address')
            ))
            conn.commit()
            worker_id = cursor.lastrowid
            return {'success': True, 'worker_id': worker_id, 'migrant_id': migrant_id}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(worker_id):
        """Get worker by ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT w.*, e.company_name as current_employer_name
                FROM workers w
                LEFT JOIN employers e ON w.current_employer_id = e.id
                WHERE w.id = %s
            """, (worker_id,))
            result = cursor.fetchone()
            return result
        finally:
            conn.close()
    
    @staticmethod
    def get_by_migrant_id(migrant_id):
        """Get worker by migrant ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT w.*, e.company_name as current_employer_name
                FROM workers w
                LEFT JOIN employers e ON w.current_employer_id = e.id
                WHERE w.migrant_id = %s
            """, (migrant_id,))
            result = cursor.fetchone()
            return result
        finally:
            conn.close()
    
    @staticmethod
    def get_by_phone(phone):
        """Get worker by phone number"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workers WHERE phone = %s", (phone,))
            result = cursor.fetchone()
            return result
        finally:
            conn.close()
    
    @staticmethod
    def authenticate(migrant_id, phone):
        """Authenticate worker by migrant ID and phone"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM workers 
                WHERE migrant_id = %s AND phone = %s
            """, (migrant_id, phone))
            result = cursor.fetchone()
            return result
        finally:
            conn.close()
    
    @staticmethod
    def update(worker_id, data):
        """Update worker profile"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            update_fields = []
            update_values = []
            
            allowed_fields = ['name', 'email', 'phone', 'skill', 'age', 'gender', 'state', 'district', 'address', 'aadhaar']
            
            for field in allowed_fields:
                if field in data and data[field] is not None:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])
            
            if not update_fields:
                return {'success': False, 'error': 'No fields to update'}
            
            update_values.append(worker_id)
            
            query = f"UPDATE workers SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(query, update_values)
            conn.commit()
            
            return {'success': True, 'message': 'Profile updated successfully'}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def update_password(worker_id, old_password, new_password):
        """Update worker password"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM workers WHERE id = %s", (worker_id,))
            result = cursor.fetchone()
            
            if not result or not check_password_hash(result['password'], old_password):
                return {'success': False, 'error': 'Invalid old password'}
            
            hashed_password = generate_password_hash(new_password)
            cursor.execute("UPDATE workers SET password = %s WHERE id = %s", (hashed_password, worker_id))
            conn.commit()
            
            return {'success': True, 'message': 'Password updated successfully'}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()


class Complaint:
    """Complaint model for worker grievances"""
    
    @staticmethod
    def generate_complaint_id(cursor):
        """Generate unique complaint ID"""
        cursor.execute("SELECT COALESCE(MAX(CAST(SUBSTRING(complaint_id, 4) AS UNSIGNED)), 0) as max_id FROM complaints")
        result = cursor.fetchone()
        max_id = result['max_id'] if result else 0
        return f"CMP{str(max_id + 1).zfill(5)}"
    
    @staticmethod
    def create(data):
        """Create a new complaint"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            complaint_id = Complaint.generate_complaint_id(cursor)
            
            cursor.execute("""
                INSERT INTO complaints (complaint_id, worker_id, employer_id, category, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                complaint_id,
                data.get('worker_id'),
                data.get('employer_id'),
                data.get('category'),
                data.get('description')
            ))
            conn.commit()
            complaint_db_id = cursor.lastrowid
            return {'success': True, 'complaint_id': complaint_id, 'id': complaint_db_id}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def get_by_worker(worker_id):
        """Get all complaints by worker ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, e.company_name as employer_name
                FROM complaints c
                LEFT JOIN employers e ON c.employer_id = e.id
                WHERE c.worker_id = %s
                ORDER BY c.created_at DESC
            """, (worker_id,))
            results = cursor.fetchall()
            return results
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(complaint_id):
        """Get complaint by ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, w.name as worker_name, w.migrant_id, e.company_name as employer_name
                FROM complaints c
                JOIN workers w ON c.worker_id = w.id
                LEFT JOIN employers e ON c.employer_id = e.id
                WHERE c.id = %s OR c.complaint_id = %s
            """, (complaint_id, complaint_id))
            result = cursor.fetchone()
            return result
        finally:
            conn.close()
    
    @staticmethod
    def update_status(complaint_id, status, admin_remarks=None):
        """Update complaint status"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            resolved_at = datetime.now() if status == 'resolved' else None
            
            cursor.execute("""
                UPDATE complaints 
                SET status = %s, admin_remarks = %s, resolved_at = %s
                WHERE id = %s OR complaint_id = %s
            """, (status, admin_remarks, resolved_at, complaint_id, complaint_id))
            conn.commit()
            
            return {'success': True, 'message': 'Complaint status updated'}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def get_stats_by_worker(worker_id):
        """Get complaint statistics for a worker"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_complaints,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_complaints,
                    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_complaints,
                    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_complaints
                FROM complaints
                WHERE worker_id = %s
            """, (worker_id,))
            result = cursor.fetchone()
            return result
        finally:
            conn.close()


class Employer:
    """Employer model for companies"""
    
    @staticmethod
    def generate_employer_id(cursor):
        """Generate unique employer ID"""
        cursor.execute("SELECT COALESCE(MAX(CAST(SUBSTRING(employer_id, 4) AS UNSIGNED)), 0) as max_id FROM employers")
        result = cursor.fetchone()
        max_id = result['max_id'] if result else 0
        return f"EMP{str(max_id + 1).zfill(5)}"
    
    @staticmethod
    def create(data):
        """Create a new employer (registration)"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            employer_id = Employer.generate_employer_id(cursor)
            hashed_password = generate_password_hash(str(data.get('password')))
            
            cursor.execute("""
                INSERT INTO employers (employer_id, company_name, industry, location, 
                                       contact_person, phone, email, password, 
                                       gst_number, registration_number, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                employer_id,
                data.get('company_name'),
                data.get('industry'),
                data.get('location'),
                data.get('contact_person'),
                data.get('phone'),
                data.get('email'),
                hashed_password,
                data.get('gst_number'),
                data.get('registration_number'),
                data.get('address')
            ))
            conn.commit()
            emp_id = cursor.lastrowid
            return {'success': True, 'employer_id': employer_id, 'id': emp_id}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def authenticate(employer_id, password):
        """Authenticate employer by employer_id and password"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM employers 
                WHERE employer_id = %s
            """, (employer_id,))
            result = cursor.fetchone()
            
            if result and check_password_hash(result['password'], password):
                return result
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_employer_id(employer_id):
        """Get employer by employer_id"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM employers 
                WHERE employer_id = %s
            """, (employer_id,))
            result = cursor.fetchone()
            return result
        finally:
            conn.close()
    
    @staticmethod
    def get_all(status=None, verification_status=None):
        """Get all employers"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT id, employer_id, company_name as name, industry as type, location, 
                       contact_person, phone, email, status, is_verified, verification_notes,
                       rating, workers_count as workers, created_at
                FROM employers 
                WHERE 1=1
            """
            params = []
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            if verification_status:
                query += " AND is_verified = %s"
                params.append(verification_status)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(employer_id):
        """Get employer by ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, employer_id, company_name as name, industry as type, location, 
                       contact_person, phone, email, status, is_verified, verification_notes,
                       rating, workers_count as workers, created_at, gst_number, 
                       registration_number, address
                FROM employers 
                WHERE id = %s
            """, (employer_id,))
            result = cursor.fetchone()
            return result
        finally:
            conn.close()
    
    @staticmethod
    def update_verification(employer_id, verification_status, notes=None, admin_id=None):
        """Update employer verification status"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            if verification_status == 'verified':
                cursor.execute("""
                    UPDATE employers 
                    SET is_verified = %s, verification_notes = %s, 
                        verified_at = NOW(), verified_by = %s,
                        status = 'active'
                    WHERE id = %s
                """, (verification_status, notes, admin_id, employer_id))
            else:
                cursor.execute("""
                    UPDATE employers 
                    SET is_verified = %s, verification_notes = %s, 
                        verified_at = NOW(), verified_by = %s
                    WHERE id = %s
                """, (verification_status, notes, admin_id, employer_id))
            
            conn.commit()
            return {'success': True, 'message': 'Verification status updated'}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def get_pending_verifications():
        """Get all employers pending verification"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, employer_id, company_name, industry, location, 
                       contact_person, phone, email, gst_number, 
                       registration_number, address, created_at
                FROM employers 
                WHERE is_verified = 'pending'
                ORDER BY created_at ASC
            """)
            results = cursor.fetchall()
            return results
        finally:
            conn.close()
    
    @staticmethod
    def get_verification_stats():
        """Get employer verification statistics"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_verified = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN is_verified = 'verified' THEN 1 ELSE 0 END) as verified,
                    SUM(CASE WHEN is_verified = 'rejected' THEN 1 ELSE 0 END) as rejected
                FROM employers
            """)
            result = cursor.fetchone()
            return result
        finally:
            conn.close()


class Session:
    """Session model for user sessions"""
    
    @staticmethod
    def create(worker_id, ip_address=None, user_agent=None):
        """Create a new session"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            session_id = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(hours=1)
            
            cursor.execute("""
                INSERT INTO sessions (session_id, worker_id, ip_address, user_agent, expires_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (session_id, worker_id, ip_address, user_agent, expires_at))
            conn.commit()
            
            return {'success': True, 'session_id': session_id}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def get(session_id):
        """Get session by ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, w.migrant_id, w.name, w.phone
                FROM sessions s
                JOIN workers w ON s.worker_id = w.id
                WHERE s.session_id = %s AND s.expires_at > NOW()
            """, (session_id,))
            result = cursor.fetchone()
            return result
        finally:
            conn.close()
    
    @staticmethod
    def delete(session_id):
        """Delete session (logout)"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def delete_by_worker(worker_id):
        """Delete all sessions for a worker"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE worker_id = %s", (worker_id,))
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()


class Admin:
    """Admin model for administrators"""
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate admin"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
            result = cursor.fetchone()
            
            if result and check_password_hash(result['password'], password):
                return result
            return None
        finally:
            conn.close()
    
    @staticmethod
    def create(username, password, name, email, role='admin'):
        """Create admin user"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO admin (username, password, name, email, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, hashed_password, name, email, role))
            conn.commit()
            return {'success': True, 'admin_id': cursor.lastrowid}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()


class Job:
    """Job model for job listings"""
    
    @staticmethod
    def generate_job_id(cursor):
        """Generate unique job ID"""
        cursor.execute("SELECT COALESCE(MAX(CAST(SUBSTRING(job_id, 4) AS UNSIGNED)), 0) as max_id FROM jobs")
        result = cursor.fetchone()
        max_id = result['max_id'] if result else 0
        return f"JOB{str(max_id + 1).zfill(5)}"
    
    @staticmethod
    def create(data):
        """Create a new job listing"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            job_id = Job.generate_job_id(cursor)
            
            cursor.execute("""
                INSERT INTO jobs (job_id, employer_id, title, description, skill_required, location, wage_per_day, duration_days, workers_needed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                job_id,
                data.get('employer_id'),
                data.get('title'),
                data.get('description'),
                data.get('skill_required'),
                data.get('location'),
                data.get('wage_per_day'),
                data.get('duration_days'),
                data.get('workers_needed')
            ))
            conn.commit()
            job_db_id = cursor.lastrowid
            return {'success': True, 'job_id': job_id, 'id': job_db_id}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def get_all(status=None, skill=None):
        """Get all open jobs"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT j.*, e.company_name as employer_name, e.industry
                FROM jobs j
                JOIN employers e ON j.employer_id = e.id
            """
            conditions = []
            params = []
            
            if status:
                conditions.append("j.status = %s")
                params.append(status)
            
            if skill:
                conditions.append("(j.skill_required = %s OR j.skill_required = 'other')")
                params.append(skill)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY j.created_at DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(job_id):
        """Get job by ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT j.*, e.company_name as employer_name, e.industry, e.location as employer_location
                FROM jobs j
                JOIN employers e ON j.employer_id = e.id
                WHERE j.id = %s OR j.job_id = %s
            """, (job_id, job_id))
            result = cursor.fetchone()
            return result
        finally:
            conn.close()
    
    @staticmethod
    def update_status(job_id, status):
        """Update job status"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs SET status = %s
                WHERE id = %s OR job_id = %s
            """, (status, job_id, job_id))
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()


class JobApplication:
    """Job Application model"""
    
    @staticmethod
    def generate_application_id(cursor):
        """Generate unique application ID"""
        cursor.execute("SELECT COALESCE(MAX(CAST(SUBSTRING(application_id, 4) AS UNSIGNED)), 0) as max_id FROM job_applications")
        result = cursor.fetchone()
        max_id = result['max_id'] if result else 0
        return f"APP{str(max_id + 1).zfill(5)}"
    
    @staticmethod
    def create(job_id, worker_id):
        """Apply for a job"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if already applied
            cursor.execute("""
                SELECT * FROM job_applications 
                WHERE job_id = %s AND worker_id = %s
            """, (job_id, worker_id))
            existing = cursor.fetchone()
            
            if existing:
                return {'success': False, 'error': 'You have already applied for this job'}
            
            application_id = JobApplication.generate_application_id(cursor)
            
            cursor.execute("""
                INSERT INTO job_applications (application_id, job_id, worker_id)
                VALUES (%s, %s, %s)
            """, (application_id, job_id, worker_id))
            conn.commit()
            
            return {'success': True, 'application_id': application_id}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def get_by_worker(worker_id):
        """Get all applications by a worker"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.*, j.title, j.job_id, j.location, j.wage_per_day, j.duration_days,
                       e.company_name as employer_name
                FROM job_applications a
                JOIN jobs j ON a.job_id = j.id
                JOIN employers e ON j.employer_id = e.id
                WHERE a.worker_id = %s
                ORDER BY a.applied_at DESC
            """, (worker_id,))
            results = cursor.fetchall()
            return results
        finally:
            conn.close()
    
    @staticmethod
    def update_status(application_id, status):
        """Update application status"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE job_applications 
                SET status = %s, responded_at = NOW()
                WHERE id = %s OR application_id = %s
            """, (status, application_id, application_id))
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def get_stats_by_worker(worker_id):
        """Get application statistics for a worker"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_applications,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_applications,
                    SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted_applications,
                    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_applications
                FROM job_applications
                WHERE worker_id = %s
            """, (worker_id,))
            result = cursor.fetchone()
            return result
        finally:
            conn.close()
