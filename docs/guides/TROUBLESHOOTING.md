# 🔧 Troubleshooting Guide - IT Asset Manager

> **Comprehensive troubleshooting guide for Docker and AWS deployment issues**

---

## 🐳 **Docker Issues**

### **1. Container Won't Start**

#### **Symptoms:**
- Container exits immediately
- "docker-compose up" fails
- Application not accessible

#### **Solutions:**
```bash
# Check container logs
docker-compose logs app

# Check container status
docker-compose ps

# Rebuild without cache
docker-compose build --no-cache

# Check Docker daemon
sudo systemctl status docker

# Restart Docker service
sudo systemctl restart docker
```

### **2. Port Already in Use**

#### **Symptoms:**
- Error: "Port 5000 is already allocated"
- Cannot bind to port

#### **Solutions:**
```bash
# Find process using the port
sudo lsof -i :5000
sudo netstat -tulpn | grep :5000

# Kill the process
sudo kill -9 <PID>

# Use different port
docker-compose up -d -p 5001:5000

# Stop all containers
docker-compose down
```

### **3. Permission Denied Errors**

#### **Symptoms:**
- Cannot write to mounted volumes
- Database creation fails
- Log files not accessible

#### **Solutions:**
```bash
# Fix file ownership
sudo chown -R $USER:$USER .

# Fix directory permissions
chmod 755 logs uploads instance

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock
```

### **4. Database Issues**

#### **Symptoms:**
- Database file not found
- SQLite locked error
- Data not persisting

#### **Solutions:**
```bash
# Check database file
ls -la instance/

# Reset database (WARNING: Deletes all data)
docker-compose down -v
rm -f instance/it_assets.db
docker-compose up -d

# Fix database permissions
chmod 664 instance/it_assets.db

# Create database manually
docker-compose exec app python -c "from app import db; db.create_all()"
```

### **5. SSL Certificate Issues**

#### **Symptoms:**
- HTTPS not working
- Certificate errors
- Nginx fails to start

#### **Solutions:**
```bash
# Generate new self-signed certificate
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Check certificate validity
openssl x509 -in docker/nginx/ssl/cert.pem -text -noout

# Fix certificate permissions
chmod 644 docker/nginx/ssl/cert.pem
chmod 600 docker/nginx/ssl/key.pem
```

---

## ☁️ **AWS EC2 Issues**

### **1. Cannot Connect to Instance**

#### **Symptoms:**
- SSH connection refused
- Timeout errors
- Permission denied

#### **Solutions:**
```bash
# Check security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx

# Verify key pair permissions
chmod 400 your-key.pem

# Check instance status
aws ec2 describe-instances --instance-ids i-xxxxxxxxx

# Try different SSH port (if changed)
ssh -i your-key.pem -p 2222 ubuntu@your-ec2-ip

# Check instance logs
aws ec2 get-console-output --instance-id i-xxxxxxxxx
```

### **2. Application Not Accessible**

#### **Symptoms:**
- Cannot access via browser
- Connection timeout
- 502 Bad Gateway

#### **Solutions:**
```bash
# Check security group inbound rules
# Ensure ports 80, 443, 5000 are open

# Check application status
docker-compose ps
curl -f http://localhost:5000/

# Check nginx status
docker-compose logs nginx

# Verify EC2 instance public IP
curl -f http://YOUR_EC2_PUBLIC_IP/

# Check system resources
htop
df -h
free -h
```

### **3. SSL Certificate Issues on EC2**

#### **Symptoms:**
- HTTPS not working
- Certificate warnings
- Let's Encrypt failures

#### **Solutions:**
```bash
# Check domain DNS resolution
nslookup your-domain.com

# Verify Let's Encrypt certificate
sudo certbot certificates

# Renew certificate manually
sudo certbot renew --dry-run

# Copy certificates to Docker
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/key.pem
sudo chown ubuntu:ubuntu docker/nginx/ssl/*

# Restart nginx
docker-compose restart nginx
```

### **4. Performance Issues**

#### **Symptoms:**
- Slow response times
- High CPU/memory usage
- Application timeouts

#### **Solutions:**
```bash
# Check system resources
htop
iostat -x 1
free -h

# Monitor Docker containers
docker stats

# Scale application
docker-compose up -d --scale app=2

# Upgrade instance type
# Stop instance, change type, start instance

# Optimize database
# Consider PostgreSQL for production
```

---

## 🔍 **Application Issues**

### **1. Login Problems**

#### **Symptoms:**
- Cannot login with admin credentials
- Invalid username/password
- Session issues

#### **Solutions:**
```bash
# Reset admin password
docker-compose exec app python update_password.py

# Check admin user exists
docker-compose exec app python -c "
from app import app, User
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    print('Admin exists:', admin is not None)
"

# Create new admin user
docker-compose exec app python -c "
from app import app, db, User
with app.app_context():
    admin = User(username='admin', email='admin@example.com')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created')
"
```

### **2. Database Migration Issues**

#### **Symptoms:**
- Missing tables
- Column errors
- Migration failures

#### **Solutions:**
```bash
# Run migrations manually
docker-compose exec app python migrate_database.py
docker-compose exec app python migrate_assets.py

# Reset database schema
docker-compose exec app python -c "
from app import app, db
with app.app_context():
    db.drop_all()
    db.create_all()
    print('Database reset')
"

# Check database schema
docker-compose exec app python -c "
from app import app, db
with app.app_context():
    print(db.engine.table_names())
"
```

### **3. File Upload Issues**

#### **Symptoms:**
- Cannot upload files
- File size errors
- Permission denied

#### **Solutions:**
```bash
# Check upload directory
ls -la uploads/
mkdir -p uploads
chmod 755 uploads

# Check file size limits
# Edit .env file
MAX_CONTENT_LENGTH=16777216  # 16MB

# Fix permissions
docker-compose exec app chown -R appuser:appuser /app/uploads
```

---

## 🛠️ **Development Issues**

### **1. Code Changes Not Reflected**

#### **Symptoms:**
- Changes not visible in browser
- Old code still running
- Cache issues

#### **Solutions:**
```bash
# Restart development container
docker-compose restart app

# Rebuild container
docker-compose build app
docker-compose up -d

# Clear browser cache
# Ctrl+F5 or Cmd+Shift+R

# Check volume mounts
docker-compose exec app ls -la /app
```

### **2. Python Import Errors**

#### **Symptoms:**
- ModuleNotFoundError
- Import path issues
- Package not found

#### **Solutions:**
```bash
# Check Python path
docker-compose exec app python -c "import sys; print(sys.path)"

# Install missing packages
docker-compose exec app pip install package-name

# Rebuild with updated requirements
docker-compose build --no-cache app

# Check requirements.txt
cat requirements.txt
```

---

## 📊 **Monitoring and Debugging**

### **Health Check Commands**
```bash
# Application health
curl -f http://localhost:5000/ || echo "App down"
curl -f http://localhost/ || echo "Nginx down"

# Container health
docker-compose ps
docker inspect --format='{{.State.Health.Status}}' container-name

# System health
df -h
free -h
uptime
```

### **Log Analysis**
```bash
# Application logs
docker-compose logs -f app

# Nginx logs
docker-compose logs -f nginx

# System logs
sudo journalctl -u docker.service -f

# Container resource usage
docker stats --no-stream
```

### **Network Debugging**
```bash
# Check port connectivity
telnet localhost 5000
nc -zv localhost 80

# Check DNS resolution
nslookup your-domain.com
dig your-domain.com

# Check routing
traceroute your-domain.com
```

---

## 🔧 **Quick Fixes**

### **Complete Reset (Development)**
```bash
# WARNING: This will delete all data
docker-compose down -v --remove-orphans
docker system prune -a
rm -rf instance/ logs/ uploads/
git pull origin main
./docker-start.sh dev
```

### **Production Restart**
```bash
# Safe production restart
docker-compose -f docker-compose.prod.yml restart app
docker-compose -f docker-compose.prod.yml restart nginx
```

### **Emergency Backup**
```bash
# Quick backup before fixes
cp instance/it_assets.db backups/emergency-$(date +%Y%m%d_%H%M%S).db
tar czf emergency-backup-$(date +%Y%m%d_%H%M%S).tar.gz \
  instance/ uploads/ logs/ .env
```

---

## 📞 **Getting Help**

### **Before Asking for Help**
1. Check this troubleshooting guide
2. Review container logs: `docker-compose logs`
3. Check system resources: `htop`, `df -h`
4. Try the quick fixes above
5. Search existing GitHub issues

### **When Creating an Issue**
Include the following information:
- Operating system and version
- Docker and Docker Compose versions
- Complete error messages
- Steps to reproduce the issue
- Container logs
- System resource usage

### **Support Channels**
- **GitHub Issues**: [Create an issue](https://github.com/DeepDN/it-asset-manager/issues)
- **Documentation**: Check README.md and deployment guides
- **Author**: [Deepak Nemade on LinkedIn](https://www.linkedin.com/in/deepak-nemade/)

---

## 🎯 **Prevention Tips**

### **Best Practices**
- Always backup before making changes
- Use version control for configuration files
- Monitor system resources regularly
- Keep Docker images updated
- Use environment variables for configuration
- Test changes in development first

### **Regular Maintenance**
```bash
# Weekly maintenance script
#!/bin/bash
# Backup database
./backup.sh

# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d

# Clean up old images
docker image prune -f

# Check disk space
df -h
```

---

*Need more help? Contact [Deepak Nemade](https://www.linkedin.com/in/deepak-nemade/) for professional support.*
