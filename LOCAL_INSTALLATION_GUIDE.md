# 💻 Local Python Installation Guide

## 🚀 **Quick Setup (Recommended)**

### **Method 1: Automated Setup**
```bash
# Clone repository
git clone https://github.com/DeepDN/it-asset-manager.git
cd it-asset-manager

# Run setup script
chmod +x setup.sh
./setup.sh

# Start application
source venv/bin/activate
python app.py
```

### **Method 2: Manual Setup**
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Create directories
mkdir -p instance logs uploads backups

# 4. Start application
python app.py
```

---

## 🔧 **Troubleshooting Common Issues**

### **Issue 1: Python Not Found**
```bash
# Error: python3: command not found
```

**Solutions:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL/Fedora
sudo yum install python3 python3-pip
# or
sudo dnf install python3 python3-pip

# macOS
brew install python3
# or download from https://python.org

# Windows
# Download from https://python.org
# Make sure to check "Add Python to PATH"
```

### **Issue 2: Virtual Environment Creation Failed**
```bash
# Error: No module named venv
```

**Solutions:**
```bash
# Ubuntu/Debian
sudo apt install python3-venv

# Alternative: Use virtualenv
pip3 install virtualenv
virtualenv venv
```

### **Issue 3: Permission Denied**
```bash
# Error: Permission denied
```

**Solutions:**
```bash
# Fix file permissions
chmod +x setup.sh
sudo chown -R $USER:$USER .

# Create directories with proper permissions
mkdir -p instance logs uploads backups
chmod 755 instance logs uploads backups
```

### **Issue 4: Package Installation Failed**
```bash
# Error: Failed building wheel for package
```

**Solutions:**
```bash
# Update pip and setuptools
pip install --upgrade pip setuptools wheel

# Install build dependencies (Ubuntu/Debian)
sudo apt install build-essential python3-dev

# Install packages individually
pip install Flask==2.3.3
pip install Flask-SQLAlchemy==3.0.5
pip install Flask-Login==0.6.3
pip install Werkzeug==2.3.7
```

### **Issue 5: Port Already in Use**
```bash
# Error: Address already in use
```

**Solutions:**
```bash
# Find process using port 5000
sudo lsof -i :5000
sudo netstat -tulpn | grep :5000

# Kill the process
sudo kill -9 <PID>

# Use different port
python app.py --port 5001
```

### **Issue 6: Database Issues**
```bash
# Error: No such table / Database locked
```

**Solutions:**
```bash
# Remove existing database
rm -f instance/it_assets.db

# Create fresh database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Check database file permissions
ls -la instance/
chmod 664 instance/it_assets.db
```

---

## 🧪 **Testing Your Installation**

### **Run Setup Test**
```bash
# Test if everything is working
python test_setup.py
```

### **Manual Testing**
```bash
# 1. Test Python version
python3 --version

# 2. Test virtual environment
source venv/bin/activate
which python

# 3. Test package imports
python -c "import flask; print('Flask OK')"
python -c "import flask_sqlalchemy; print('SQLAlchemy OK')"

# 4. Test app startup
python -c "from app import app; print('App import OK')"
```

---

## 📋 **System Requirements**

### **Minimum Requirements:**
- **Python**: 3.7 or higher
- **RAM**: 512MB available
- **Storage**: 100MB free space
- **OS**: Linux, macOS, Windows

### **Recommended:**
- **Python**: 3.9 or higher
- **RAM**: 1GB available
- **Storage**: 1GB free space

---

## 🐍 **Python Version Compatibility**

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.7 | ✅ Supported | Minimum version |
| 3.8 | ✅ Supported | Recommended |
| 3.9 | ✅ Supported | Recommended |
| 3.10 | ✅ Supported | Latest tested |
| 3.11 | ✅ Supported | Latest tested |
| 3.6 | ❌ Not supported | Too old |
| 2.7 | ❌ Not supported | Deprecated |

---

## 📦 **Package Dependencies**

### **Core Dependencies:**
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Werkzeug==2.3.7
```

### **Development Dependencies:**
```
pytest==7.4.3
pytest-flask==1.3.0
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
```

---

## 🔍 **Step-by-Step Debugging**

### **Step 1: Verify Python Installation**
```bash
python3 --version
python3 -c "import sys; print(sys.executable)"
```

### **Step 2: Check Virtual Environment**
```bash
python3 -m venv test_venv
source test_venv/bin/activate
which python
deactivate
rm -rf test_venv
```

### **Step 3: Test Package Installation**
```bash
pip install Flask
python -c "import flask; print(flask.__version__)"
```

### **Step 4: Test Application Import**
```bash
cd it-asset-manager
python -c "from app import app; print('Success')"
```

### **Step 5: Test Database Creation**
```bash
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database created successfully')
"
```

---

## 🚨 **Emergency Recovery**

### **Complete Reset:**
```bash
# Remove virtual environment
rm -rf venv

# Remove database
rm -f instance/it_assets.db

# Remove logs
rm -rf logs/*

# Start fresh
./setup.sh
```

### **Minimal Installation:**
```bash
# Install only essential packages
pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug

# Create minimal directories
mkdir -p instance

# Test basic functionality
python -c "from app import app; print('Basic setup OK')"
```

---

## 📞 **Getting Help**

### **If Setup Still Fails:**

1. **Run the test script:**
   ```bash
   python test_setup.py
   ```

2. **Check system logs:**
   ```bash
   # Linux
   tail -f /var/log/syslog
   
   # macOS
   tail -f /var/log/system.log
   ```

3. **Create an issue with:**
   - Operating system and version
   - Python version (`python3 --version`)
   - Complete error message
   - Output of `pip list`

### **Support Channels:**
- **GitHub Issues**: [Report installation problems](https://github.com/DeepDN/it-asset-manager/issues)
- **Documentation**: Check README.md and other guides
- **Author**: [Deepak Nemade on LinkedIn](https://www.linkedin.com/in/deepak-nemade/)

---

## ✅ **Success Checklist**

After successful installation, you should have:

- [ ] Python 3.7+ installed
- [ ] Virtual environment created and activated
- [ ] All packages installed without errors
- [ ] Directories created (instance, logs, uploads, backups)
- [ ] Database file created (instance/it_assets.db)
- [ ] Application starts without errors
- [ ] Can access http://localhost:5000
- [ ] Can login with admin/admin123

---

**🎉 Once everything is working, visit http://localhost:5000 and start managing your IT assets!**

---

*Created with ❤️ by [Deepak Nemade](https://www.linkedin.com/in/deepak-nemade/) - Making local installation simple and reliable.*
