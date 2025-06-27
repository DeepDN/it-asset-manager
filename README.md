# 🏢 IT Asset Manager - Professional Edition

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)](https://sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **A comprehensive web-based IT Asset Management System designed for Network and System Administrators to efficiently track, manage, and monitor IT assets, user access permissions, and organizational resources.**

## 👨‍💻 **Author**

**Deepak Nemade**  
*Network & System Administrator | IT Asset Management Specialist*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/deepak-nemade/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=for-the-badge&logo=github)](https://github.com/deepaknemade)

---

## 🌟 **Features Overview**

### 🖥️ **Comprehensive Asset Management**
- **30+ Asset Types**: Laptops, Desktops, Network Equipment, Mobile Devices, Audio/Video Equipment
- **Unique Asset Tags**: Professional identification system (LAP0001, RTR0024, SWH0048)
- **Ownership Tracking**: Purchased, Rented, Leased assets with vendor management
- **Technical Specifications**: Detailed specs for each asset category
- **Location Management**: Track asset locations and assignments
- **Condition Monitoring**: Asset condition tracking (Excellent to Damaged)
- **Warranty Management**: Track warranty expiry dates
- **Financial Tracking**: Purchase costs and rental fees

### 🔐 **User Access Management**
- **Application Access Control**: Track user permissions across applications
- **GitHub Access Tracker**: Repository-level permission management
- **Access Levels**: Admin, Read, Write, Maintainer permissions
- **Audit Trail**: Complete history of access grants and revocations
- **Multi-Organization Support**: Handle multiple GitHub organizations

### 🔑 **Advanced Security Features**
- **Multi-Method Password Management**: Manual, Web-based, and In-app password reset
- **Secure Token System**: Time-limited password reset tokens
- **Session Management**: Secure user authentication with Flask-Login
- **Password Validation**: Strength requirements and confirmation
- **Account Recovery**: Comprehensive forgot password functionality

### 📊 **Professional Dashboard & Reporting**
- **Real-time Statistics**: Asset counts, assignments, access permissions
- **Advanced Filtering**: Multi-criteria search and filtering
- **Data Export**: CSV exports for compliance and reporting
- **Professional UI**: Modern, responsive design with animations
- **Mobile Responsive**: Works seamlessly on all devices

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.7 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### **Installation**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/deepaknemade/it-asset-manager.git
   cd it-asset-manager
   ```

2. **Run Setup Script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Start the Application**
   ```bash
   source venv/bin/activate
   python run.py
   ```

4. **Access the Application**
   - **URL**: http://localhost:5000
   - **Username**: `admin`
   - **Password**: `admin123`

### **Add Sample Data (Optional)**
```bash
python add_sample_data.py
```

---

## 📋 **Detailed Setup Instructions**

### **Manual Installation**

1. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Database**
   ```bash
   python run.py  # This will create the database automatically
   ```

4. **Run Database Migrations (if needed)**
   ```bash
   python migrate_database.py      # For user management features
   python migrate_assets.py        # For enhanced asset features
   ```

### **Environment Configuration**

Create a `.env` file for production settings:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///it_assets.db
FLASK_ENV=production
```

---

## 🗄️ **Data Storage & Backup**

### **Database Location**
- **File**: `instance/it_assets.db`
- **Type**: SQLite database
- **Auto-created**: On first application run

### **Database Schema**
```sql
-- Main Tables
- users          # User authentication
- asset          # IT assets with comprehensive fields
- application_access  # Application permissions
- github_access  # GitHub repository access

-- Key Asset Fields
- asset_tag      # Unique identifier (LAP0001, RTR0024)
- ownership_type # purchased, rented, leased
- asset_category # Computing, Network, Display, etc.
- specifications # Technical details per asset type
- location       # Physical location tracking
- condition      # Asset condition monitoring
```

### **Backup & Recovery**

#### **Automated Backup**
```bash
./backup.sh  # Creates timestamped backup with CSV exports
```

#### **Manual Backup**
```bash
# Copy database file
cp instance/it_assets.db backups/it_assets_$(date +%Y%m%d).db

# Export data to CSV
python -c "
from app import app, db, Asset, ApplicationAccess, GitHubAccess
import csv
with app.app_context():
    # Export logic here
"
```

#### **Recovery from Scratch**
1. **Database Recovery**: Replace `instance/it_assets.db` with backup file
2. **CSV Recovery**: Import CSV files into new installation
3. **Migration Recovery**: Run migration scripts to update schema

#### **Disaster Recovery Steps**
```bash
# 1. Fresh installation
git clone https://github.com/deepaknemade/it-asset-manager.git
cd it-asset-manager
./setup.sh

# 2. Restore database
cp your-backup.db instance/it_assets.db

# 3. Start application
source venv/bin/activate
python app.py
```

---

## 🎯 **Asset Types & Categories**

### **Computing Devices**
- **Laptops** (LAP####): Business laptops, workstations
- **Desktops** (DSK####): Desktop computers, workstations
- **CPUs** (CPU####): Computer towers, servers

### **Mobile Devices**
- **Mobile Phones** (MOB####): Android, iOS devices
- **Tablets** (TAB####): Android tablets, Windows tablets
- **iPads** (IPD####): Apple iPad devices
- **iPhones** (IPH####): Apple iPhone devices

### **Network Infrastructure**
- **Routers** (RTR####): Network routers with port specifications
- **Switches** (SWH####): Network switches (8, 16, 24, 48 port)
- **Firewalls** (FWL####): Security appliances
- **Load Balancers** (LBL####): Traffic distribution devices

### **Display & Audio/Video**
- **Monitors** (MON####): Computer monitors with size/resolution
- **Televisions** (TV#####): Conference room displays
- **Projectors** (PRJ####): Presentation equipment
- **Speakers** (SPK####): Audio equipment
- **Microphones** (MIC####): Recording equipment

### **Storage & Peripherals**
- **USB Drives** (USB####): Pen drives, flash storage
- **External HDDs** (HDD####): External hard drives
- **External SSDs** (SSD####): External solid state drives
- **Keyboards** (KBD####): Input devices
- **Mice** (MSE####): Pointing devices

### **Connectors & Cables**
- **HDMI Cables** (HDM####): Video connectors
- **USB-C Cables** (USC####): Modern connectors
- **Lightning Cables** (LTG####): Apple connectors
- **Ethernet Cables** (ETH####): Network cables

---

## 🔧 **Advanced Features**

### **Password Management**
- **Manual Update**: Command-line password tool
- **Web Reset**: Forgot password with secure tokens
- **In-App Change**: Authenticated password updates

### **Asset Ownership**
- **Purchased**: Track purchase date, cost, warranty
- **Rented**: Vendor management, monthly costs, rental periods
- **Leased**: Lease terms, vendor details, end dates

### **Technical Specifications**
- **Computing**: CPU, RAM, Storage specifications
- **Network**: Port counts, network types (Ethernet, WiFi, Fiber)
- **Display**: Screen sizes, resolutions (HD, Full HD, 2K, 4K)
- **Audio/Video**: Equipment types, connector specifications

### **Location & Condition Tracking**
- **Location**: Floor, room, desk assignments
- **Condition**: Excellent, Good, Fair, Poor, Damaged
- **Assignment**: User assignments with dates
- **History**: Complete audit trail

---

## 📊 **Usage Examples**

### **Adding a Network Switch**
```
Asset Tag: SWH0024
Asset Type: Switch
Category: Network (auto-filled)
Brand: Cisco
Model: Catalyst 2960
Port Count: 24
Network Type: Ethernet
Ownership: Purchased
Location: Server Room A, Rack 3
```

### **Adding a Rental Laptop**
```
Asset Tag: LAP0156
Asset Type: Laptop
Category: Computing (auto-filled)
Brand: Dell
Model: Latitude 5520
Ownership: Rented
Vendor: TechRent Solutions
Monthly Cost: $85.00
Rental Period: 2024-01-01 to 2024-12-31
```

### **Managing User Access**
```
User: john.doe
Application: GitHub
Access Level: Admin
Organization: company-org
Repository: main-application
Assign Date: 2024-01-15
Status: Active
```

---

## 🛠️ **Development & Customization**

### **Project Structure**
```
it-asset-manager/
├── it_asset_manager/           # Main application package
│   ├── core/                   # Core application components
│   │   ├── app.py             # Application factory
│   │   ├── database.py        # Database initialization
│   │   └── auth.py            # Authentication setup
│   ├── models/                 # Database models
│   │   ├── user.py            # User authentication model
│   │   ├── asset.py           # Asset management model
│   │   └── access.py          # Access control models
│   ├── services/               # Business logic layer
│   │   ├── asset_service.py   # Asset management logic
│   │   ├── auth_service.py    # Authentication logic
│   │   └── access_service.py  # Access management logic
│   ├── routes/                 # Flask route blueprints
│   │   ├── main.py            # Dashboard routes
│   │   ├── auth.py            # Authentication routes
│   │   ├── assets.py          # Asset management routes
│   │   └── access.py          # Access management routes
│   ├── utils/                  # Utility functions
│   │   ├── validators.py      # Input validation
│   │   ├── formatters.py      # Data formatting
│   │   └── generators.py      # ID generation
│   ├── templates/              # HTML templates
│   └── static/                 # Static files (CSS, JS, images)
├── config/                     # Configuration management
│   └── settings.py            # Environment-based settings
├── tests/                      # Comprehensive test suite
│   ├── conftest.py            # Pytest fixtures
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── docs/                       # Documentation
├── run.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── pytest.ini                 # Test configuration
└── setup.cfg                  # Package configuration
```

### **Adding New Asset Types**
1. Update `add_asset.html` template with new options
2. Add category mapping in JavaScript
3. Update database migration if needed
4. Add appropriate icons and styling

### **Customizing UI**
- **Colors**: Modify CSS variables in `base.html`
- **Branding**: Update logos and company information
- **Layout**: Customize Bootstrap components
- **Features**: Add new routes and templates

---

## 🔒 **Security Considerations**

### **Production Deployment**
1. **Change Default Credentials**: Update admin password immediately
2. **Environment Variables**: Use `.env` file for sensitive data
3. **HTTPS**: Enable SSL/TLS encryption
4. **Database Security**: Use PostgreSQL for production
5. **Access Control**: Implement role-based permissions
6. **Backup Strategy**: Regular automated backups
7. **Monitoring**: Log access and changes

### **Security Features**
- **Password Hashing**: Werkzeug secure password hashing
- **Session Management**: Flask-Login secure sessions
- **CSRF Protection**: Built-in form protection
- **Input Validation**: Comprehensive data validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection

---

## 📈 **Performance & Scalability**

### **Current Capacity**
- **Assets**: Handles thousands of assets efficiently
- **Users**: Multiple concurrent users supported
- **Database**: SQLite suitable for small to medium deployments
- **Response Time**: Sub-second response times

### **Scaling Options**
- **Database**: Migrate to PostgreSQL for larger deployments
- **Caching**: Add Redis for improved performance
- **Load Balancing**: Multiple application instances
- **CDN**: Static asset delivery optimization

---

## 🧪 **Testing**

### **Manual Testing**
```bash
# Test asset creation
curl -X POST http://localhost:5000/assets/add \
  -d "asset_tag=TEST001&asset_type=laptop&serial_number=TEST123"

# Test authentication
curl -X POST http://localhost:5000/login \
  -d "username=admin&password=admin123"
```

### **Database Testing**
```bash
# Test migrations
python migrate_database.py
python migrate_assets.py

# Test sample data
python add_sample_data.py
```

---

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### **Contribution Guidelines**
- Follow PEP 8 Python style guide
- Add comments for complex logic
- Update documentation for new features
- Test all changes before submitting
- Maintain backward compatibility

---

## 📞 **Support & Contact**

### **Author Contact**
**Deepak Nemade**  
*IT Asset Management Specialist*

- **LinkedIn**: [https://www.linkedin.com/in/deepak-nemade/](https://www.linkedin.com/in/deepak-nemade/)
- **GitHub**: [https://github.com/deepaknemade](https://github.com/deepaknemade)
- **Email**: Available on LinkedIn profile

### **Getting Help**
1. **Documentation**: Check this README and additional docs
2. **Issues**: Create GitHub issues for bugs or feature requests
3. **Discussions**: Use GitHub Discussions for questions
4. **LinkedIn**: Connect for professional inquiries

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **Flask Community**: For the excellent web framework
- **Bootstrap Team**: For the responsive UI framework
- **FontAwesome**: For the professional icons
- **SQLAlchemy**: For the robust ORM
- **Open Source Community**: For inspiration and tools

---

## 🔄 **Version History**

### **v2.0.0** - Enhanced Professional Edition
- ✅ 30+ Asset types with comprehensive specifications
- ✅ Asset ownership management (purchased/rented/leased)
- ✅ Unique asset tagging system
- ✅ Advanced password management
- ✅ Professional UI with animations
- ✅ Enhanced database schema
- ✅ Comprehensive documentation

### **v1.0.0** - Initial Release
- ✅ Basic asset management
- ✅ User access tracking
- ✅ GitHub access management
- ✅ CSV export functionality
- ✅ Authentication system

---

## 🎯 **Roadmap**

### **Upcoming Features**
- [ ] **API Integration**: RESTful API for external integrations
- [ ] **Mobile App**: Native mobile application
- [ ] **Advanced Reporting**: Custom report builder
- [ ] **Notification System**: Email alerts and reminders
- [ ] **Multi-tenant Support**: Multiple organization support
- [ ] **Advanced Analytics**: Usage statistics and trends
- [ ] **Integration Hub**: Connect with popular IT tools

### **Long-term Vision**
- Enterprise-grade scalability
- Cloud deployment options
- Advanced automation features
- Machine learning insights
- IoT device integration

---

**🚀 Ready to revolutionize your IT asset management? Get started today!**

[![Deploy](https://img.shields.io/badge/Deploy-Now-success?style=for-the-badge)](https://github.com/deepaknemade/it-asset-manager)
[![Documentation](https://img.shields.io/badge/Read-Docs-blue?style=for-the-badge)](README.md)
[![LinkedIn](https://img.shields.io/badge/Connect-LinkedIn-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/deepak-nemade/)

---

*Created with ❤️ by [Deepak Nemade](https://www.linkedin.com/in/deepak-nemade/) - Empowering IT professionals with better asset management tools.*
