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
    def get_all(status=None):
        """Get all employers"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if status:
                cursor.execute("""
                    SELECT id, company_name as name, industry as type, location, 
                           contact_person, phone, email, status, rating, 
                           workers_count as workers, created_at
                    FROM employers 
                    WHERE status = %s
                    ORDER BY rating DESC
                """, (status,))
            else:
                cursor.execute("""
                    SELECT id, company_name as name, industry as type, location, 
                           contact_person, phone, email, status, rating, 
                           workers_count as workers, created_at
                    FROM employers 
                    ORDER BY rating DESC
                """)
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
                SELECT id, company_name as name, industry as type, location, 
                       contact_person, phone, email, status, rating, 
                       workers_count as workers, created_at
                FROM employers 
                WHERE id = %s
            """, (employer_id,))
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