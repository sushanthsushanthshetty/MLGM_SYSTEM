# Database Migration Script for MLGMS
# Run this script to add jobs and job_applications tables

import pymysql

def migrate():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='mlgms_db',
        autocommit=True
    )
    
    cursor = conn.cursor()
    
    print("Running database migration...")
    
    # Create jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_id VARCHAR(20) UNIQUE NOT NULL,
            employer_id INT NOT NULL,
            title VARCHAR(150) NOT NULL,
            description TEXT,
            skill_required VARCHAR(50),
            location VARCHAR(200),
            wage_per_day DECIMAL(10,2),
            duration_days INT,
            workers_needed INT,
            status ENUM('open', 'closed', 'filled') DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (employer_id) REFERENCES employers(id) ON DELETE CASCADE
        )
    """)
    print("[OK] Created jobs table")
    
    # Create job_applications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            application_id VARCHAR(20) UNIQUE NOT NULL,
            job_id INT NOT NULL,
            worker_id INT NOT NULL,
            status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            responded_at TIMESTAMP NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE
        )
    """)
    print("[OK] Created job_applications table")
    
    # Create indexes
    try:
        cursor.execute("CREATE INDEX idx_jobs_employer ON jobs(employer_id)")
        cursor.execute("CREATE INDEX idx_jobs_status ON jobs(status)")
        cursor.execute("CREATE INDEX idx_jobs_skill ON jobs(skill_required)")
        cursor.execute("CREATE INDEX idx_applications_worker ON job_applications(worker_id)")
        cursor.execute("CREATE INDEX idx_applications_job ON job_applications(job_id)")
        cursor.execute("CREATE INDEX idx_applications_status ON job_applications(status)")
        print("[OK] Created indexes")
    except Exception as e:
        print(f"  Indexes may already exist: {e}")
    
    # Check if sample jobs exist
    cursor.execute("SELECT COUNT(*) FROM jobs")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insert sample jobs
        sample_jobs = [
            ('JOB00001', 1, 'Electrician for Building Construction', 'Need experienced electrician for wiring work in new residential building', 'electrician', 'Mumbai, Maharashtra', 800.00, 30, 5, 'open'),
            ('JOB00002', 2, 'Factory Worker - Manufacturing', 'General factory work including machine operation and quality checking', 'other', 'Pune, Maharashtra', 500.00, 60, 20, 'open'),
            ('JOB00003', 4, 'Construction Workers Needed', 'Masons and laborers needed for infrastructure project', 'mason', 'Delhi NCR', 600.00, 90, 50, 'open'),
            ('JOB00004', 5, 'Hotel Staff - Cook and Cleaners', 'Need cooks and housekeeping staff for hotel', 'cook', 'Bangalore, Karnataka', 450.00, 180, 10, 'open'),
            ('JOB00005', 6, 'Agricultural Workers', 'Farm workers needed for harvest season', 'other', 'Nashik, Maharashtra', 400.00, 15, 30, 'open'),
            ('JOB00006', 1, 'Plumber for Maintenance Work', 'Experienced plumber for maintenance work in commercial complex', 'plumber', 'Mumbai, Maharashtra', 700.00, 15, 3, 'open'),
            ('JOB00007', 3, 'Textile Worker', 'Workers needed for textile manufacturing', 'other', 'Surat, Gujarat', 450.00, 30, 15, 'closed'),
        ]
        
        cursor.executemany("""
            INSERT INTO jobs (job_id, employer_id, title, description, skill_required, location, wage_per_day, duration_days, workers_needed, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, sample_jobs)
        print("[OK] Inserted sample jobs")
    else:
        print(f"  Jobs table already has {count} records")
    
    conn.close()
    print("\n[SUCCESS] Migration completed successfully!")

if __name__ == '__main__':
    migrate()