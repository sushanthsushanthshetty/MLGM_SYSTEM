# Migrant Labor & Grievance Management System (MLGMS)

A comprehensive government portal for migrant workers to register, manage profiles, file complaints, and connect with employers.

## 🏗️ Project Structure

```
MLGM_SYSTEM/
├── index.html                 # Main HTML file
├── css/
│   └── style.css             # Custom styles
├── js/
│   ├── app.js                # AngularJS app configuration
│   └── controllers.js        # AngularJS controllers (connected to Flask API)
├── pages/
│   ├── home.html             # Home page
│   ├── register.html         # Worker registration
│   ├── login.html            # Worker login
│   ├── dashboard.html        # Worker dashboard
│   ├── profile.html          # Profile view/edit
│   ├── complaint.html        # File complaint
│   ├── complaints.html       # View complaints list
│   └── employers.html        # Employer directory
├── backend/
│   ├── __init__.py           # Backend package init
│   ├── app.py                # Flask main application
│   ├── config.py             # Configuration settings
│   ├── models.py             # Database models
│   └── routes/
│       ├── __init__.py       # Routes package init
│       ├── auth_routes.py    # Authentication routes
│       ├── worker_routes.py  # Worker profile routes
│       ├── complaint_routes.py # Complaint routes
│       ├── employer_routes.py  # Employer routes
│       └── dashboard_routes.py # Dashboard routes
├── database/
│   └── mlgms_db.sql          # MySQL database schema
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🛠️ Technology Stack

### Frontend
- AngularJS 1.8.2
- HTML5, CSS3
- Bootstrap 5.3.2
- ngRoute for routing

### Backend
- Python Flask
- Flask-MySQLdb
- Flask-CORS
- Werkzeug (password hashing)

### Database
- MySQL (XAMPP phpMyAdmin)

## 📋 Prerequisites

1. **XAMPP** - For MySQL database
   - Download from: https://www.apachefriends.org/
   - Install and start Apache & MySQL

2. **Python 3.8+**
   - Download from: https://www.python.org/downloads/

3. **pip** (comes with Python)

## 🚀 Installation & Setup

### Step 1: Clone/Download the Project

```bash
cd c:\MLGM_SYSTEM
```

### Step 2: Setup MySQL Database

1. Start XAMPP Control Panel
2. Start Apache and MySQL services
3. Open phpMyAdmin: http://localhost/phpmyadmin
4. Go to "SQL" tab
5. Copy and paste the contents of `database/mlgms_db.sql`
6. Click "Go" to execute

**Or use MySQL command line:**
```bash
mysql -u root < database/mlgms_db.sql
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

If you encounter issues with mysqlclient, try:
```bash
pip install mysqlclient
# If that fails, try:
pip install pymysql
```

### Step 4: Configure Database Connection

Edit `backend/config.py` if your MySQL credentials are different:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''  # Default XAMPP has no password
MYSQL_DB = 'mlgms_db'
```

### Step 5: Run the Flask Backend

```bash
cd backend
python app.py
```

You should see:
```
============================================================
Migrant Labor & Grievance Management System (MLGMS)
============================================================
Environment: development
Server running on: http://localhost:5000
API Base URL: http://localhost:5000/api
============================================================
```

### Step 6: Access the Application

Open your browser and go to:
```
http://localhost:5000
```

Or open `index.html` directly in a browser (requires Flask running for API calls).

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register new worker |
| POST | `/api/login` | Worker login |
| POST | `/api/logout` | Worker logout |
| GET | `/api/check-session` | Check session validity |

### Worker Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile` | Get current worker profile |
| GET | `/api/profile/<worker_id>` | Get worker by ID |
| PUT | `/api/profile/update` | Update profile |

### Complaints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/complaint/add` | Submit new complaint |
| GET | `/api/complaint/list` | Get worker's complaints |
| GET | `/api/complaint/<worker_id>` | Get complaints by worker ID |
| PUT | `/api/complaint/update_status` | Update complaint status |

### Employers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employers/list` | Get all employers |
| GET | `/api/employers/<id>` | Get employer by ID |
| GET | `/api/employers/stats` | Get employer statistics |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/current` | Get current worker dashboard |
| GET | `/api/dashboard/<worker_id>` | Get worker dashboard by ID |

## 🔐 Authentication Flow

1. **Register**: User fills registration form → Gets unique Migrant ID (e.g., MIG00001)
2. **Login**: Enter Migrant ID + Mobile Number → Session created
3. **Session**: Stored in localStorage and database
4. **Protected Routes**: Require valid session token in Authorization header

## 📝 Usage Guide

### Worker Registration
1. Click "Register" on home page
2. Fill in details (Name, Mobile, Age, Gender, Skill)
3. Submit form
4. **Note your Migrant ID** (e.g., MIG00001) - This is your login credential!

### Worker Login
1. Click "Login" on home page
2. Enter your Migrant ID (e.g., MIG00001)
3. Enter your registered mobile number
4. Click Login

### File a Complaint
1. Login and go to Dashboard
2. Click "File Complaint"
3. Select complaint type
4. Describe your issue
5. Submit

### View Profile
1. Login and go to Dashboard
2. Click "My Profile"
3. View/Edit your details

## 🔧 Troubleshooting

### Database Connection Error
```
Error: Can't connect to MySQL server
```
**Solution:**
- Ensure MySQL is running in XAMPP
- Check credentials in `backend/config.py`

### CORS Error
```
Access-Control-Allow-Origin error
```
**Solution:**
- Flask-CORS is configured, but ensure Flask server is running
- Access app via `http://localhost:5000` not `file://`

### Module Not Found
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:**
```bash
pip install -r requirements.txt
```

### mysqlclient Installation Error (Windows)
```bash
# Try alternative:
pip install pymysql

# Then add to backend/models.py:
import pymysql
pymysql.install_as_MySQLdb()
```

## 🧪 Testing the API

### Test Registration
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","phone":"9876543210","age":30,"gender":"male","skill":"electrician"}'
```

### Test Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"migrant_id":"MIG00001","phone":"9876543210"}'
```

### Test Health Check
```bash
curl http://localhost:5000/api/health
```

## 📊 Database Schema

### workers table
| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary Key |
| migrant_id | VARCHAR(20) | Unique ID (MIG00001) |
| name | VARCHAR(100) | Worker name |
| phone | VARCHAR(15) | Mobile number |
| password | VARCHAR(255) | Hashed password |
| skill | VARCHAR(50) | Primary skill |
| age | INT | Age |
| gender | ENUM | male/female/other |
| status | ENUM | active/inactive |

### complaints table
| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary Key |
| complaint_id | VARCHAR(20) | Unique ID (CMP00001) |
| worker_id | INT | Foreign Key |
| category | VARCHAR(50) | Complaint type |
| description | TEXT | Issue details |
| status | ENUM | pending/resolved |

### employers table
| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary Key |
| company_name | VARCHAR(150) | Company name |
| industry | VARCHAR(100) | Industry type |
| location | VARCHAR(200) | Location |
| rating | DECIMAL(3,2) | Rating (0-5) |
| status | ENUM | active/inactive |

## 🔒 Security Features

- Password hashing with Werkzeug (pbkdf2:sha256)
- Session-based authentication
- CORS protection
- Input validation
- SQL injection prevention (parameterized queries)

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify database connection
3. Check Flask console for errors

## 📄 License

Government Portal - Migrant Labor & Grievance Management System

---

**Developed for the welfare of migrant workers**