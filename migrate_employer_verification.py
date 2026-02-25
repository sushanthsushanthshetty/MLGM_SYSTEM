# =====================================================
# Migration Script: Add Employer Verification Fields
# Run this script to update the employers table with
# verification-related columns
# =====================================================

import pymysql

def migrate():
    """Add employer verification fields to the database"""
    
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='mlgms_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        cursor = connection.cursor()
        
        print("Starting migration: Adding employer verification fields...")
        
        # Add employer_id column
        try:
            cursor.execute("""
                ALTER TABLE employers 
                ADD COLUMN employer_id VARCHAR(20) UNIQUE AFTER id
            """)
            print("[OK] Added employer_id column")
        except Exception as e:
            if 'Duplicate column' in str(e):
                print("[SKIP] employer_id column already exists")
            else:
                print(f"[ERROR] adding employer_id: {e}")
        
        # Add password column
        try:
            cursor.execute("""
                ALTER TABLE employers 
                ADD COLUMN password VARCHAR(255) AFTER email
            """)
            print("[OK] Added password column")
        except Exception as e:
            if 'Duplicate column' in str(e):
                print("[SKIP] password column already exists")
            else:
                print(f"[ERROR] adding password: {e}")
        
        # Add gst_number column
        try:
            cursor.execute("""
                ALTER TABLE employers 
                ADD COLUMN gst_number VARCHAR(20) AFTER password
            """)
            print("[OK] Added gst_number column")
        except Exception as e:
            if 'Duplicate column' in str(e):
                print("[SKIP] gst_number column already exists")
            else:
                print(f"[ERROR] adding gst_number: {e}")
        
        # Add registration_number column
        try:
            cursor.execute("""
                ALTER TABLE employers 
                ADD COLUMN registration_number VARCHAR(50) AFTER gst_number
            """)
            print("[OK] Added registration_number column")
        except Exception as e:
            if 'Duplicate column' in str(e):
                print("[SKIP] registration_number column already exists")
            else:
                print(f"[ERROR] adding registration_number: {e}")
        
        # Add address column
        try:
            cursor.execute("""
                ALTER TABLE employers 
                ADD COLUMN address TEXT AFTER registration_number
            """)
            print("[OK] Added address column")
        except Exception as e:
            if 'Duplicate column' in str(e):
                print("[SKIP] address column already exists")
            else:
                print(f"[ERROR] adding address: {e}")
        
        # Add is_verified column
        try:
            cursor.execute("""
                ALTER TABLE employers 
                ADD COLUMN is_verified ENUM('pending', 'verified', 'rejected') DEFAULT 'pending' AFTER status
            """)
            print("[OK] Added is_verified column")
        except Exception as e:
            if 'Duplicate column' in str(e):
                print("[SKIP] is_verified column already exists")
            else:
                print(f"[ERROR] adding is_verified: {e}")
        
        # Add verification_notes column
        try:
            cursor.execute("""
                ALTER TABLE employers 
                ADD COLUMN verification_notes TEXT AFTER is_verified
            """)
            print("[OK] Added verification_notes column")
        except Exception as e:
            if 'Duplicate column' in str(e):
                print("[SKIP] verification_notes column already exists")
            else:
                print(f"[ERROR] adding verification_notes: {e}")
        
        # Add verified_at column
        try:
            cursor.execute("""
                ALTER TABLE employers 
                ADD COLUMN verified_at TIMESTAMP NULL AFTER verification_notes
            """)
            print("[OK] Added verified_at column")
        except Exception as e:
            if 'Duplicate column' in str(e):
                print("[SKIP] verified_at column already exists")
            else:
                print(f"[ERROR] adding verified_at: {e}")
        
        # Add verified_by column
        try:
            cursor.execute("""
                ALTER TABLE employers 
                ADD COLUMN verified_by INT AFTER verified_at
            """)
            print("[OK] Added verified_by column")
        except Exception as e:
            if 'Duplicate column' in str(e):
                print("[SKIP] verified_by column already exists")
            else:
                print(f"[ERROR] adding verified_by: {e}")
        
        # Update existing employers to be verified (for backward compatibility)
        try:
            cursor.execute("""
                UPDATE employers 
                SET is_verified = 'verified', 
                    employer_id = CONCAT('EMP', LPAD(id, 5, '0'))
                WHERE is_verified IS NULL OR is_verified = 'pending'
            """)
            print(f"[OK] Updated {cursor.rowcount} existing employers to verified status")
        except Exception as e:
            print(f"[ERROR] updating existing employers: {e}")
        
        # Add index on employer_id
        try:
            cursor.execute("""
                CREATE INDEX idx_employers_employer_id ON employers(employer_id)
            """)
            print("[OK] Added index on employer_id")
        except Exception as e:
            if 'Duplicate key name' in str(e):
                print("[SKIP] Index on employer_id already exists")
            else:
                print(f"[ERROR] adding index: {e}")
        
        # Add index on is_verified
        try:
            cursor.execute("""
                CREATE INDEX idx_employers_is_verified ON employers(is_verified)
            """)
            print("[OK] Added index on is_verified")
        except Exception as e:
            if 'Duplicate key name' in str(e):
                print("[SKIP] Index on is_verified already exists")
            else:
                print(f"[ERROR] adding index: {e}")
        
        connection.commit()
        print("\n[SUCCESS] Migration completed successfully!")
        print("\nNote: Existing employers have been auto-verified for backward compatibility.")
        print("New employer registrations will require admin verification.")
        
    except Exception as e:
        connection.rollback()
        print(f"\n[FAILED] Migration failed: {e}")
    finally:
        connection.close()


if __name__ == '__main__':
    migrate()