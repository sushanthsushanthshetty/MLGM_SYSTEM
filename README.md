# Migrant Labor & Grievance Management System (MLGMS)

## 🌟 Overview

The **Migrant Labor & Grievance Management System (MLGMS)** is a comprehensive government portal designed to protect the rights of migrant workers, facilitate their registration, manage their profiles, file and track grievances, and connect them with verified employers. This system aims to bring transparency, accountability, and efficiency to the migrant labor ecosystem.

---

## 🔴 Real-World Problem Statement

### The Migrant Labor Crisis

Migrant workers are among the most vulnerable populations in any country. They face numerous challenges:

#### 1. **Lack of Legal Identity & Documentation**
- Many migrant workers lack proper registration with local authorities
- No centralized database exists to track their employment history
- Absence of legal documentation makes them invisible to the system

#### 2. **Exploitation & Abuse**
- **Wage Theft**: Employers often withhold wages or pay below minimum wage
- **Excessive Working Hours**: Workers are forced to work overtime without compensation
- **Unsafe Working Conditions**: Lack of safety equipment and protocols
- **Contract Violations**: Terms of employment are frequently violated

#### 3. **No Grievance Redressal Mechanism**
- Workers have no formal channel to report abuses
- Fear of retaliation prevents complaints
- No tracking system for complaint status
- Bureaucratic hurdles discourage reporting

#### 4. **Information Asymmetry**
- Workers don't know their rights
- No access to verified employer information
- Lack of awareness about available government schemes

#### 5. **Humanitarian Crisis During Emergencies**
- The COVID-19 pandemic exposed the plight of migrant workers
- Millions were stranded without support, money, or food
- No system to identify and reach affected workers

### How MLGMS Solves These Problems

| Problem | MLGMS Solution |
|---------|----------------|
| No legal identity | Unique Migrant ID upon registration |
| Wage theft & exploitation | Formal complaint filing with tracking |
| No grievance mechanism | Multi-category complaint system with status updates |
| Information asymmetry | Verified employer database with ratings |
| Lack of support | Centralized dashboard for all services |

---

## ✨ Features

### 1. **Worker Registration**
- Simple registration form capturing essential details
- Unique Migrant ID generation
- Skill categorization for better job matching
- Mobile number verification

### 2. **Profile Management**
- View and update personal information
- Track employment history
- View registration status
- Access to important documents

### 3. **Grievance Filing System**
- Multiple complaint categories:
  - Non-Payment of Wages
  - Safety Issues
  - Workplace Harassment
  - Accommodation Problems
  - Excessive Working Hours
  - Contract Violation
- Real-time complaint tracking
- Status updates via SMS

### 4. **Complaint Tracking Dashboard**
- View all filed complaints
- Track status (Pending/Resolved)
- Historical complaint records
- Response timeline

### 5. **Employer Directory**
- Database of verified employers
- Employer ratings and reviews
- Worker count and industry type
- Active/Inactive status indicators

### 6. **User Dashboard**
- Centralized access to all services
- Quick navigation to important features
- Profile overview
- Recent activity summary

---

## 🛠️ Technology Stack

| Category | Technology |
|----------|------------|
| **Frontend Framework** | AngularJS 1.8.2 |
| **Routing** | Angular Route (ngRoute) |
| **UI Framework** | Bootstrap 5.3.2 |
| **Styling** | Custom CSS |
| **Architecture** | Single Page Application (SPA) |

---

## 📁 Project Structure

```
MLGM_SYSTEM/
├── index.html              # Main entry point (SPA shell)
├── README.md               # Project documentation
├── css/
│   └── style.css           # Custom styles
├── js/
│   ├── app.js              # AngularJS module & route configuration
│   └── controllers.js      # Application controllers
└── pages/
    ├── home.html           # Landing page
    ├── register.html       # Worker registration form
    ├── login.html          # Login page
    ├── dashboard.html      # User dashboard
    ├── profile.html        # Profile management
    ├── complaint.html      # File new complaint
    ├── complaints.html     # View complaints list
    └── employers.html      # Employer directory
```

---

## 🚀 Installation & Setup

### Prerequisites
- A modern web browser (Chrome, Firefox, Edge, Safari)
- Python 3.x (for local development server) OR Node.js

### Option 1: Python HTTP Server

```bash
# Navigate to project directory
cd c:\MLGM_SYSTEM

# Start local server
python -m http.server 8000

# Open in browser
# http://localhost:8000
```

### Option 2: Node.js HTTP Server

```bash
# Navigate to project directory
cd c:\MLGM_SYSTEM

# Start server using npx
npx http-server -p 8000

# Open in browser
# http://localhost:8000
```

### Option 3: VS Code Live Server

1. Install "Live Server" extension in VS Code
2. Right-click `index.html`
3. Select "Open with Live Server"

---

## 📱 Application Routes

| Route | Page | Description |
|-------|------|-------------|
| `#!/` | Home | Landing page with system overview |
| `#!/register` | Register | New worker registration |
| `#!/login` | Login | Worker login portal |
| `#!/dashboard` | Dashboard | User control panel |
| `#!/profile` | Profile | View/edit profile details |
| `#!/complaint` | File Complaint | Submit new grievance |
| `#!/complaints` | My Complaints | View complaint history |
| `#!/employers` | Employers | Browse verified employers |

---

## 🎯 Target Users

1. **Migrant Workers**
   - Register themselves in the system
   - File and track complaints
   - Access verified employer information

2. **Government Officials**
   - Monitor worker registrations
   - Process and resolve complaints
   - Maintain employer database

3. **Employers**
   - Register their organizations
   - Access skilled worker database
   - Maintain compliance records

4. **Labor Department**
   - Generate reports and analytics
   - Track grievance resolution
   - Policy decision support

---

## 🔮 Future Enhancements

### Phase 2 Features
- [ ] Backend API integration (Node.js/Express or Python/Django)
- [ ] Database integration (MongoDB/PostgreSQL)
- [ ] SMS/Email notifications
- [ ] Multi-language support (Hindi, Tamil, Bengali, etc.)
- [ ] Mobile responsive improvements
- [ ] Biometric authentication

### Phase 3 Features
- [ ] Mobile application (React Native/Flutter)
- [ ] Integration with Aadhaar (Indian national ID)
- [ ] AI-powered complaint categorization
- [ ] Blockchain-based document verification
- [ ] Real-time chat support
- [ ] Integration with other government portals

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is developed for government use and is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

For support or queries:
- **Helpline**: 1800-XXX-XXXX (Toll Free)
- **Email**: support@mlgms.gov.in
- **Working Hours**: Monday to Saturday, 9:00 AM - 6:00 PM

---

## 👨‍💻 Author

**Government Portal Development Team**

---

> *"Empowering Migrant Workers, Ensuring Dignity and Justice"*