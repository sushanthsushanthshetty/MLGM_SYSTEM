"""
Script to fix admin password in the database
"""
import pymysql
from werkzeug.security import generate_password_hash

def fix_admin_password():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='mlgms_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    cursor = conn.cursor()
    
    # Generate proper password hash for 'admin123'
    password_hash = generate_password_hash('admin123')
    
    # Update admin password
    cursor.execute("""
        UPDATE admin 
        SET password = %s 
        WHERE username = 'admin'
    """, (password_hash,))
    
    # Check if admin exists, if not create one
    cursor.execute("SELECT * FROM admin WHERE username = 'admin'")
    admin = cursor.fetchone()
    
    if not admin:
        cursor.execute("""
            INSERT INTO admin (username, password, name, email, role)
            VALUES (%s, %s, %s, %s, %s)
        """, ('admin', password_hash, 'System Administrator', 'admin@mlgms.gov.in', 'super_admin'))
        print("Admin user created successfully!")
    else:
        print("Admin password updated successfully!")
    
    conn.commit()
    conn.close()
    
    print("Admin credentials:")
    print("  Username: admin")
    print("  Password: admin123")

if __name__ == '__main__':
    fix_admin_password()