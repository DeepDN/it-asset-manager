# 🚀 Installation Guide - IT Asset Manager

## **Author: Deepak Nemade**
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/deepak-nemade/)

---

## 📋 **System Requirements**

### **Minimum Requirements**
- **Operating System**: Linux, macOS, Windows 10+
- **Python**: 3.7 or higher
- **RAM**: 512 MB minimum, 1 GB recommended
- **Storage**: 100 MB for application, additional space for database
- **Network**: Internet connection for initial setup

### **Recommended Requirements**
- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / Windows 11
- **Python**: 3.9 or higher
- **RAM**: 2 GB or more
- **Storage**: 1 GB available space
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)

---

## 🛠️ **Installation Methods**

### **Method 1: Automated Setup (Recommended)**

#### **Step 1: Clone Repository**
```bash
git clone https://github.com/deepaknemade/it-asset-manager.git
cd it-asset-manager
```

#### **Step 2: Run Setup Script**
```bash
chmod +x setup.sh
./setup.sh
```

#### **Step 3: Start Application**
```bash
source venv/bin/activate
python app.py
```

#### **Step 4: Access Application**
- Open browser: http://localhost:5000
- Login: admin / admin123

---

### **Method 2: Manual Installation**

#### **Step 1: Prerequisites**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum install python3 python3-pip git

# macOS (with Homebrew)
brew install python3 git

# Windows
# Download Python from python.org
# Download Git from git-scm.com
```

#### **Step 2: Clone and Setup**
```bash
git clone https://github.com/deepaknemade/it-asset-manager.git
cd it-asset-manager

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### **Step 3: Initialize Database**
```bash
# Run migrations
python migrate_database.py
python migrate_assets.py

# Add sample data (optional)
python add_sample_data.py
```

#### **Step 4: Start Application**
```bash
python app.py
```

---

### **Method 3: Docker Installation (Advanced)**

#### **Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

#### **Build and Run**
```bash
docker build -t it-asset-manager .
docker run -p 5000:5000 -v $(pwd)/instance:/app/instance it-asset-manager
```

---

## 🔧 **Configuration**

### **Environment Variables**
Create `.env` file:
```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///it_assets.db
FLASK_ENV=production
FLASK_DEBUG=False
```

### **Database Configuration**
```python
# For PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@localhost/it_assets

# For MySQL
DATABASE_URL=mysql://user:password@localhost/it_assets
```

### **Security Configuration**
```bash
# Change default admin password
python update_password.py

# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🗄️ **Database Setup**

### **SQLite (Default)**
- **Location**: `instance/it_assets.db`
- **Auto-created**: On first run
- **Suitable for**: Small to medium deployments

### **PostgreSQL (Production)**
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb it_assets
sudo -u postgres createuser it_admin

# Update connection string
DATABASE_URL=postgresql://it_admin:password@localhost/it_assets
```

### **Migration Commands**
```bash
# User management features
python migrate_database.py

# Enhanced asset features
python migrate_assets.py

# Check migration status
python -c "
from app import app, db
with app.app_context():
    print('Database tables:', db.engine.table_names())
"
```

---

## 🚀 **First Run Setup**

### **Step 1: Start Application**
```bash
cd it-asset-manager
source venv/bin/activate
python app.py
```

### **Step 2: Initial Login**
- **URL**: http://localhost:5000
- **Username**: `admin`
- **Password**: `admin123`

### **Step 3: Change Default Password**
```bash
# Method 1: Command line
python update_password.py

# Method 2: Web interface
# Go to: http://localhost:5000/forgot-password
# Enter: admin
# Follow reset process

# Method 3: In-app
# Login → Change Password (sidebar)
```

### **Step 4: Add Sample Data (Optional)**
```bash
python add_sample_data.py
```

---

## 🔍 **Verification & Testing**

### **Health Check**
```bash
# Check application status
curl http://localhost:5000

# Expected response: 302 (redirect to login)
```

### **Database Verification**
```bash
# Check database file
ls -la instance/it_assets.db

# Check tables
sqlite3 instance/it_assets.db ".tables"
```

### **Feature Testing**
1. **Login**: Test authentication
2. **Dashboard**: View statistics
3. **Add Asset**: Create test asset
4. **Export**: Download CSV
5. **Password Reset**: Test forgot password

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Port Already in Use**
```bash
# Find process using port 5000
lsof -ti:5000

# Kill process
kill -9 $(lsof -ti:5000)

# Or use different port
python app.py --port 5001
```

#### **Permission Errors**
```bash
# Fix file permissions
chmod +x setup.sh
chmod +x *.py

# Fix directory permissions
chmod 755 instance/
```

#### **Database Errors**
```bash
# Reset database
rm instance/it_assets.db
python app.py  # Will recreate database

# Or restore from backup
cp backups/latest_backup.db instance/it_assets.db
```

#### **Python Version Issues**
```bash
# Check Python version
python --version
python3 --version

# Use specific Python version
python3.9 -m venv venv
```

#### **Virtual Environment Issues**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Log Analysis**
```bash
# Check application logs
tail -f app.log

# Check for errors
grep -i error app.log

# Check database operations
grep -i "database\|sql" app.log
```

---

## 🔄 **Backup & Recovery**

### **Automated Backup**
```bash
# Run backup script
./backup.sh

# Schedule with cron
crontab -e
# Add: 0 2 * * * /path/to/it-asset-manager/backup.sh
```

### **Manual Backup**
```bash
# Backup database
cp instance/it_assets.db backups/manual_backup_$(date +%Y%m%d).db

# Backup entire application
tar -czf it_asset_manager_backup.tar.gz \
  --exclude=venv \
  --exclude=__pycache__ \
  --exclude=*.log \
  .
```

### **Recovery Process**
```bash
# 1. Fresh installation
git clone https://github.com/deepaknemade/it-asset-manager.git
cd it-asset-manager
./setup.sh

# 2. Restore database
cp your_backup.db instance/it_assets.db

# 3. Start application
source venv/bin/activate
python app.py
```

---

## 🌐 **Production Deployment**

### **Web Server Setup (Nginx + Gunicorn)**

#### **Install Gunicorn**
```bash
pip install gunicorn
```

#### **Create Gunicorn Config**
```python
# gunicorn.conf.py
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

#### **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/it-asset-manager/static;
    }
}
```

#### **Systemd Service**
```ini
# /etc/systemd/system/it-asset-manager.service
[Unit]
Description=IT Asset Manager
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/it-asset-manager
Environment=PATH=/path/to/it-asset-manager/venv/bin
ExecStart=/path/to/it-asset-manager/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### **SSL/HTTPS Setup**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 **Performance Optimization**

### **Database Optimization**
```sql
-- Create indexes for better performance
CREATE INDEX idx_asset_tag ON asset(asset_tag);
CREATE INDEX idx_asset_type ON asset(asset_type);
CREATE INDEX idx_assigned_to ON asset(assigned_to);
CREATE INDEX idx_ownership_type ON asset(ownership_type);
```

### **Application Optimization**
```python
# Enable caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Optimize database queries
# Use pagination for large datasets
# Implement connection pooling
```

---

## 📞 **Support**

### **Getting Help**
1. **Documentation**: Check README.md and this guide
2. **GitHub Issues**: Report bugs or request features
3. **LinkedIn**: Connect with author for professional support

### **Author Contact**
**Deepak Nemade**  
*IT Asset Management Specialist*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/deepak-nemade/)

---

## ✅ **Installation Checklist**

- [ ] **System Requirements**: Python 3.7+, Git installed
- [ ] **Repository Cloned**: Code downloaded locally
- [ ] **Virtual Environment**: Created and activated
- [ ] **Dependencies**: All packages installed
- [ ] **Database**: Initialized and migrated
- [ ] **Application**: Started successfully
- [ ] **Access**: Can login with admin/admin123
- [ ] **Password**: Default password changed
- [ ] **Sample Data**: Added (optional)
- [ ] **Backup**: Backup strategy implemented
- [ ] **Documentation**: Read and understood

---

**🎉 Congratulations! Your IT Asset Manager is ready to use!**

*Installation guide created by [Deepak Nemade](https://www.linkedin.com/in/deepak-nemade/) - Making IT asset management accessible to everyone.*
