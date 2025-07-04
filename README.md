# 🏢 IT Asset Manager - Professional Edition

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **A comprehensive web-based IT Asset Management System designed for Network and System Administrators to efficiently track, manage, and monitor IT assets, user access permissions, and organizational resources.**

## 👨‍💻 **Author**

**Deepak Nemade**  
*Network & System Administrator | IT Asset Management Specialist*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/deepak-nemade/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=for-the-badge&logo=github)](https://github.com/DeepDN)

---

## 🌟 **Key Features**

### 🖥️ **Asset Management**
- **30+ Asset Types**: Laptops, Desktops, Network Equipment, Mobile Devices, Audio/Video Equipment
- **Unique Asset Tags**: Professional identification system (LAP0001, RTR0024, SWH0048)
- **Ownership Tracking**: Purchased, Rented, Leased assets with vendor management
- **Location & Condition Monitoring**: Track asset locations and condition status
- **Warranty Management**: Track warranty expiry dates and costs

### 🔐 **Access Control**
- **User Authentication**: Secure login system with password management
- **Application Access Tracking**: Monitor user permissions across applications
- **GitHub Access Management**: Repository-level permission tracking
- **Audit Trail**: Complete history of access grants and changes

### 📊 **Reporting & Export**
- **Real-time Dashboard**: Asset statistics and quick overview
- **CSV Export**: Export data for compliance and reporting
- **Advanced Filtering**: Multi-criteria search and filtering
- **Bulk Operations**: Import/export assets via CSV

---

## 🚀 **Quick Start**

### **🐳 Docker Deployment (Recommended)**

#### **Development Environment**
```bash
# Clone repository
git clone https://github.com/DeepDN/it-asset-manager.git
cd it-asset-manager

# Start development environment
./docker-start.sh dev

# Access: http://localhost:5000
# Username: admin | Password: admin123
```

#### **Production Environment**
```bash
# Start production environment with Nginx
./docker-start.sh prod

# Access: http://localhost
# Username: admin | Password: admin123
```

### **☁️ AWS EC2 Deployment**

#### **1. Launch EC2 Instance**
- **AMI**: Ubuntu Server 22.04 LTS
- **Instance Type**: t3.small (recommended) or t2.micro (free tier)
- **Security Groups**: Allow ports 22, 80, 443

#### **2. Install Docker**
```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker ubuntu && newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### **3. Deploy Application**
```bash
# Clone and deploy
git clone https://github.com/DeepDN/it-asset-manager.git
cd it-asset-manager

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Deploy production environment
./docker-start.sh prod

# Access: http://YOUR_EC2_PUBLIC_IP
```

### **💻 Local Python Installation**
```bash
# Prerequisites: Python 3.7+, pip, Git
git clone https://github.com/DeepDN/it-asset-manager.git
cd it-asset-manager

# Automated setup
chmod +x setup.sh && ./setup.sh

# Start application
source venv/bin/activate && python app.py

# Access: http://localhost:5000
# Username: admin | Password: admin123
```

**Having issues with local installation?** 
📖 **See detailed guide:** [docs/deployment/LOCAL_INSTALLATION_GUIDE.md](docs/deployment/LOCAL_INSTALLATION_GUIDE.md)

---

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file for production settings:

```env
# Application Settings
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=production
ADMIN_PASSWORD=your-secure-admin-password

# Database Configuration
SQLALCHEMY_DATABASE_URI=sqlite:///instance/it_assets.db

# Security Settings
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
```

### **SSL/HTTPS Setup (Optional)**
```bash
# Generate self-signed certificate for testing
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem

# For production, use Let's Encrypt
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com
```

---

## 📋 **Asset Types Supported**

### **Computing Devices**
- **Laptops** (LAP####): Business laptops, workstations
- **Desktops** (DSK####): Desktop computers, workstations
- **Servers** (SRV####): Physical and virtual servers

### **Network Equipment**
- **Routers** (RTR####): Network routers with specifications
- **Switches** (SWH####): Network switches (8, 16, 24, 48 port)
- **Firewalls** (FWL####): Security appliances

### **Mobile Devices**
- **Smartphones** (MOB####): Android, iOS devices
- **Tablets** (TAB####): Android tablets, iPads
- **Wearables** (WER####): Smart watches, fitness trackers

### **Audio/Video Equipment**
- **Monitors** (MON####): Computer displays with size/resolution
- **Projectors** (PRJ####): Presentation equipment
- **Speakers** (SPK####): Audio equipment

---

## 🛠️ **Docker Commands**

### **Development**
```bash
# Start development environment
./docker-start.sh dev
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### **Production**
```bash
# Start production environment
./docker-start.sh prod
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### **Maintenance**
```bash
# Add sample data
docker-compose exec app python add_sample_data.py

# Backup database
docker-compose exec app cp /app/instance/it_assets.db /app/backups/backup-$(date +%Y%m%d).db

# Update password
docker-compose exec app python update_password.py
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Port Already in Use**
```bash
# Find and kill process using port
sudo lsof -i :5000
sudo kill -9 <PID>
```

#### **Permission Denied**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x docker-start.sh setup.sh
```

#### **Database Issues**
```bash
# Reset database (WARNING: Deletes all data)
docker-compose down -v
rm -f instance/it_assets.db
docker-compose up -d
```

#### **Container Won't Start**
```bash
# Check logs
docker-compose logs app

# Rebuild without cache
docker-compose build --no-cache
```

### **Getting Help**
- **Documentation**: Check this README and deployment guides
- **Issues**: Create GitHub issues for bugs or feature requests
- **Support**: Contact [Deepak Nemade on LinkedIn](https://www.linkedin.com/in/deepak-nemade/)

---

## 📊 **System Requirements**

### **Development**
- **RAM**: 2GB minimum
- **Storage**: 5GB free space
- **OS**: Linux, macOS, Windows (with WSL2)

### **Production**
- **RAM**: 4GB recommended
- **Storage**: 20GB recommended
- **CPU**: 2 vCPU recommended
- **OS**: Ubuntu 20.04+ (recommended)

---

## 🔒 **Security Features**

- **Password Hashing**: Secure password storage with Werkzeug
- **Session Management**: Flask-Login secure sessions
- **CSRF Protection**: Built-in form protection
- **Input Validation**: Comprehensive data validation
- **SSL/HTTPS Support**: Optional SSL encryption
- **Non-root Container**: Docker security best practices

---

## 📈 **Backup & Recovery**

### **Database Backup**
```bash
# Manual backup
cp instance/it_assets.db backups/backup-$(date +%Y%m%d).db

# Automated backup script
./backup.sh
```

### **Full System Backup**
```bash
# Backup everything
tar czf it-asset-manager-backup-$(date +%Y%m%d).tar.gz \
  instance/ uploads/ logs/ .env docker-compose*.yml
```

---

## 🎯 **Production Checklist**

### **Before Deployment**
- [ ] Change default admin password
- [ ] Update SECRET_KEY in .env file
- [ ] Configure SSL certificates (if needed)
- [ ] Set up firewall rules
- [ ] Configure backup strategy

### **After Deployment**
- [ ] Test login functionality
- [ ] Verify SSL/HTTPS (if configured)
- [ ] Set up monitoring
- [ ] Schedule regular backups
- [ ] Update DNS records (if using domain)

---

## 🤝 **Contributing**

We welcome contributions from the community! IT Asset Manager is built by IT professionals, for IT professionals.

### **Quick Start for Contributors**
1. **Read our [Contributing Guidelines](CONTRIBUTING.md)**
2. **Check our [Code of Conduct](CODE_OF_CONDUCT.md)**
3. **Browse [open issues](https://github.com/DeepDN/it-asset-manager/issues)**
4. **Join [GitHub Discussions](https://github.com/DeepDN/it-asset-manager/discussions)**

### **Ways to Contribute**
- 🐛 **Report bugs** using our [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml)
- 💡 **Suggest features** using our [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml)
- 📚 **Improve documentation** 
- 🔧 **Submit code improvements**
- 🧪 **Help with testing**
- 🌍 **Translate to other languages**

### **Development Setup**
```bash
# Fork the repository and clone your fork
git clone https://github.com/YOUR_USERNAME/it-asset-manager.git
cd it-asset-manager

# Start development environment
./docker-start.sh dev

# Make your changes and submit a pull request!
```

---

## 🔒 **Security**

Security is a top priority for IT Asset Manager. We follow industry best practices and welcome security research.

### **Reporting Security Issues**
**🚨 Please DO NOT create public issues for security vulnerabilities.**

Instead, email us at: **[security@itassetmanager.com](mailto:security@itassetmanager.com)**

### **Security Features**
- 🔐 Secure password hashing (PBKDF2)
- 🛡️ CSRF protection
- 🔒 Session security
- ✅ Input validation
- 🚫 SQL injection prevention
- 🌐 XSS protection

📖 **Read our full [Security Policy](SECURITY.md)**

---

## 📞 **Support & Contact**

### **Professional Support**
**Deepak Nemade** - *IT Asset Management Specialist*
- **LinkedIn**: [Connect for professional inquiries](https://www.linkedin.com/in/deepak-nemade/)
- **GitHub**: [Follow for updates](https://github.com/DeepDN)

### **Community Support**
- **GitHub Issues**: [Report bugs or request features](https://github.com/DeepDN/it-asset-manager/issues)
- **GitHub Discussions**: [Community questions and support](https://github.com/DeepDN/it-asset-manager/discussions)
- **Documentation**: [Comprehensive guides](docs/)
- **Troubleshooting**: [Common issues and solutions](docs/guides/TROUBLESHOOTING.md)

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **Flask Community**: For the excellent web framework
- **Docker Community**: For containerization technology
- **Bootstrap Team**: For the responsive UI framework
- **Open Source Community**: For inspiration and tools

---

**🚀 Ready to streamline your IT asset management? Deploy now and take control of your IT infrastructure!**

[![Deploy Now](https://img.shields.io/badge/Deploy-Now-success?style=for-the-badge)](https://github.com/DeepDN/it-asset-manager)
[![Documentation](https://img.shields.io/badge/Read-Docs-blue?style=for-the-badge)](#-quick-start)

---

*Created with ❤️ by [Deepak Nemade](https://www.linkedin.com/in/deepak-nemade/) - Empowering IT professionals with better asset management tools.*
