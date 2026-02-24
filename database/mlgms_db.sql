-- =====================================================
-- Migrant Labor & Grievance Management System (MLGMS)
-- MySQL Database Schema
-- Database: mlgms_db
-- =====================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS mlgms_db;
USE mlgms_db;

-- =====================================================
-- Table: workers
-- Stores migrant worker information
-- =====================================================
CREATE TABLE IF NOT EXISTS workers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    migrant_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    aadhaar VARCHAR(12),
    skill VARCHAR(50),
    age INT,
    gender ENUM('male', 'female', 'other'),
    state VARCHAR(50),
    district VARCHAR(50),
    address TEXT,
    status ENUM('active', 'inactive') DEFAULT 'active',
    current_employer_id INT,
    work_location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- Table: employers
-- Stores employer/company information
-- =====================================================
CREATE TABLE IF NOT EXISTS employers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    location VARCHAR(200),
    contact_person VARCHAR(100),
    phone VARCHAR(15),
    email VARCHAR(100),
    status ENUM('active', 'inactive') DEFAULT 'active',
    rating DECIMAL(3,2) DEFAULT 0.00,
    workers_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- Table: complaints
-- Stores worker complaints/grievances
-- =====================================================
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(20) UNIQUE NOT NULL,
    worker_id INT NOT NULL,
    employer_id INT,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('pending', 'in_progress', 'resolved', 'rejected') DEFAULT 'pending',
    admin_remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE,
    FOREIGN KEY (employer_id) REFERENCES employers(id) ON DELETE SET NULL
);

-- =====================================================
-- Table: admin
-- Stores administrator accounts
-- =====================================================
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100),
    role ENUM('super_admin', 'admin', 'moderator') DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- Table: sessions
-- Stores user session data
-- =====================================================
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    worker_id INT,
    admin_id INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES admin(id) ON DELETE CASCADE
);

-- =====================================================
-- Indexes for better performance
-- =====================================================
CREATE INDEX idx_workers_migrant_id ON workers(migrant_id);
CREATE INDEX idx_workers_phone ON workers(phone);
CREATE INDEX idx_workers_status ON workers(status);
CREATE INDEX idx_complaints_worker_id ON complaints(worker_id);
CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_complaints_created_at ON complaints(created_at);
CREATE INDEX idx_employers_status ON employers(status);
CREATE INDEX idx_sessions_session_id ON sessions(session_id);

-- =====================================================
-- Sample Data: Employers
-- =====================================================
INSERT INTO employers (company_name, industry, location, contact_person, phone, email, status, rating, workers_count) VALUES
('ABC Construction Pvt Ltd', 'Construction', 'Mumbai, Maharashtra', 'Rajesh Sharma', '02212345678', 'hr@abcconstruction.com', 'active', 4.50, 150),
('XYZ Manufacturing Co', 'Manufacturing', 'Pune, Maharashtra', 'Amit Patel', '02298765432', 'contact@xyzmanufacturing.com', 'active', 4.00, 200),
('LMN Textiles', 'Textile', 'Surat, Gujarat', 'Suresh Kumar', '02614567890', 'info@lmntextiles.com', 'inactive', 3.50, 80),
('PQR Infrastructure', 'Infrastructure', 'Delhi NCR', 'Vikram Singh', '01123456789', 'hr@pqrinfra.com', 'active', 4.80, 300),
('EFG Hospitality Services', 'Hospitality', 'Bangalore, Karnataka', 'Priya Nair', '08012345678', 'jobs@efghospitality.com', 'active', 4.20, 120),
('HIJ Agricultural Farms', 'Agriculture', 'Nashik, Maharashtra', 'Mahesh Deshmukh', '02534567890', 'contact@hijfarms.com', 'active', 3.80, 50);

-- =====================================================
-- Sample Data: Admin
-- Default password: admin123 (will be hashed by application)
-- =====================================================
INSERT INTO admin (username, password, name, email, role) VALUES
('admin', 'pbkdf2:sha256:600000$placeholder$placeholder', 'System Administrator', 'admin@mlgms.gov.in', 'super_admin');

-- =====================================================
-- Stored Procedure: Generate Migrant ID
-- =====================================================
DELIMITER //
CREATE PROCEDURE GenerateMigrantID(OUT new_migrant_id VARCHAR(20))
BEGIN
    DECLARE max_id INT DEFAULT 0;
    SELECT COALESCE(MAX(CAST(SUBSTRING(migrant_id, 4) AS UNSIGNED)), 0) INTO max_id FROM workers;
    SET new_migrant_id = CONCAT('MIG', LPAD(max_id + 1, 5, '0'));
END //
DELIMITER ;

-- =====================================================
-- Stored Procedure: Generate Complaint ID
-- =====================================================
DELIMITER //
CREATE PROCEDURE GenerateComplaintID(OUT new_complaint_id VARCHAR(20))
BEGIN
    DECLARE max_id INT DEFAULT 0;
    SELECT COALESCE(MAX(CAST(SUBSTRING(complaint_id, 4) AS UNSIGNED)), 0) INTO max_id FROM complaints;
    SET new_complaint_id = CONCAT('CMP', LPAD(max_id + 1, 5, '0'));
END //
DELIMITER ;

-- =====================================================
-- Trigger: Auto-generate Migrant ID before insert
-- =====================================================
DELIMITER //
CREATE TRIGGER before_worker_insert
BEFORE INSERT ON workers
FOR EACH ROW
BEGIN
    DECLARE max_id INT;
    IF NEW.migrant_id IS NULL OR NEW.migrant_id = '' THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING(migrant_id, 4) AS UNSIGNED)), 0) INTO max_id FROM workers;
        SET NEW.migrant_id = CONCAT('MIG', LPAD(max_id + 1, 5, '0'));
    END IF;
END //
DELIMITER ;

-- =====================================================
-- Trigger: Auto-generate Complaint ID before insert
-- =====================================================
DELIMITER //
CREATE TRIGGER before_complaint_insert
BEFORE INSERT ON complaints
FOR EACH ROW
BEGIN
    DECLARE max_id INT;
    IF NEW.complaint_id IS NULL OR NEW.complaint_id = '' THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING(complaint_id, 4) AS UNSIGNED)), 0) INTO max_id FROM complaints;
        SET NEW.complaint_id = CONCAT('CMP', LPAD(max_id + 1, 5, '0'));
    END IF;
END //
DELIMITER ;

-- =====================================================
-- View: Worker Dashboard Stats
-- =====================================================
CREATE OR REPLACE VIEW v_worker_dashboard AS
SELECT 
    w.id AS worker_id,
    w.migrant_id,
    w.name,
    w.phone,
    w.skill,
    w.status,
    COUNT(c.id) AS total_complaints,
    SUM(CASE WHEN c.status = 'pending' THEN 1 ELSE 0 END) AS pending_complaints,
    SUM(CASE WHEN c.status = 'resolved' THEN 1 ELSE 0 END) AS resolved_complaints,
    SUM(CASE WHEN c.status = 'in_progress' THEN 1 ELSE 0 END) AS in_progress_complaints
FROM workers w
LEFT JOIN complaints c ON w.id = c.worker_id
GROUP BY w.id;

-- =====================================================
-- View: Employer Summary
-- =====================================================
CREATE OR REPLACE VIEW v_employer_summary AS
SELECT 
    e.id,
    e.company_name AS name,
    e.industry AS type,
    e.location,
    e.contact_person,
    e.phone,
    e.email,
    e.status,
    e.rating,
    e.workers_count AS workers,
    e.created_at
FROM employers e;

-- =====================================================
-- Table: jobs
-- Stores job listings from employers
-- =====================================================
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
);

-- =====================================================
-- Table: job_applications
-- Stores worker applications for jobs
-- =====================================================
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
);

-- =====================================================
-- Indexes for jobs and applications
-- =====================================================
CREATE INDEX idx_jobs_employer ON jobs(employer_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_skill ON jobs(skill_required);
CREATE INDEX idx_applications_worker ON job_applications(worker_id);
CREATE INDEX idx_applications_job ON job_applications(job_id);
CREATE INDEX idx_applications_status ON job_applications(status);

-- =====================================================
-- Trigger: Auto-generate Job ID before insert
-- =====================================================
DELIMITER //
CREATE TRIGGER before_job_insert
BEFORE INSERT ON jobs
FOR EACH ROW
BEGIN
    DECLARE max_id INT;
    IF NEW.job_id IS NULL OR NEW.job_id = '' THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING(job_id, 4) AS UNSIGNED)), 0) INTO max_id FROM jobs;
        SET NEW.job_id = CONCAT('JOB', LPAD(max_id + 1, 5, '0'));
    END IF;
END //
DELIMITER ;

-- =====================================================
-- Trigger: Auto-generate Application ID before insert
-- =====================================================
DELIMITER //
CREATE TRIGGER before_application_insert
BEFORE INSERT ON job_applications
FOR EACH ROW
BEGIN
    DECLARE max_id INT;
    IF NEW.application_id IS NULL OR NEW.application_id = '' THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING(application_id, 4) AS UNSIGNED)), 0) INTO max_id FROM job_applications;
        SET NEW.application_id = CONCAT('APP', LPAD(max_id + 1, 5, '0'));
    END IF;
END //
DELIMITER ;

-- =====================================================
-- Sample Data: Jobs
-- =====================================================
INSERT INTO jobs (job_id, employer_id, title, description, skill_required, location, wage_per_day, duration_days, workers_needed, status) VALUES
('JOB00001', 1, 'Electrician for Building Construction', 'Need experienced electrician for wiring work in new residential building', 'electrician', 'Mumbai, Maharashtra', 800.00, 30, 5, 'open'),
('JOB00002', 2, 'Factory Worker - Manufacturing', 'General factory work including machine operation and quality checking', 'other', 'Pune, Maharashtra', 500.00, 60, 20, 'open'),
('JOB00003', 4, 'Construction Workers Needed', 'Masons and laborers needed for infrastructure project', 'mason', 'Delhi NCR', 600.00, 90, 50, 'open'),
('JOB00004', 5, 'Hotel Staff - Cook and Cleaners', 'Need cooks and housekeeping staff for hotel', 'cook', 'Bangalore, Karnataka', 450.00, 180, 10, 'open'),
('JOB00005', 6, 'Agricultural Workers', 'Farm workers needed for harvest season', 'other', 'Nashik, Maharashtra', 400.00, 15, 30, 'open'),
('JOB00006', 1, 'Plumber for Maintenance Work', 'Experienced plumber for maintenance work in commercial complex', 'plumber', 'Mumbai, Maharashtra', 700.00, 15, 3, 'open'),
('JOB00007', 3, 'Textile Worker', 'Workers needed for textile manufacturing', 'other', 'Surat, Gujarat', 450.00, 30, 15, 'closed');

-- =====================================================
-- Grant privileges (adjust username as needed)
-- =====================================================
-- GRANT ALL PRIVILEGES ON mlgms_db.* TO 'root'@'localhost';
-- FLUSH PRIVILEGES;

SELECT 'Database mlgms_db created successfully!' AS Message;
