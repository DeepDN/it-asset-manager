# 🐳 Docker Deployment Guide - IT Asset Manager

[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://docker.com)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2.0+-green.svg)](https://docs.docker.com/compose/)

> **Complete guide for deploying IT Asset Manager using Docker and Docker Compose for both development and production environments.**

---

## 📋 **Prerequisites**

### **System Requirements**
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: Minimum 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### **Installation Check**
```bash
# Verify Docker installation
docker --version
docker-compose --version

# Test Docker functionality
docker run hello-world
```

---

## 🚀 **Quick Start (Development)**

### **1. Clone and Setup**
```bash
# Clone the repository
git clone https://github.com/deepaknemade/it-asset-manager.git
cd it-asset-manager

# Create environment file
cp .env.example .env.dev

# Create necessary directories
mkdir -p logs uploads instance
```

### **2. Start Development Environment**
```bash
# Build and start containers
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### **3. Access Application**
- **URL**: http://localhost:5000
- **Username**: `admin`
- **Password**: `admin123`

### **4. Stop Development Environment**
```bash
# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: This will delete data)
docker-compose down -v
```

---

## 🏭 **Production Deployment**

### **1. Environment Configuration**
```bash
# Create production environment file
cp .env.example .env

# Edit production settings
nano .env
```

**Required Environment Variables:**
```env
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production
ADMIN_PASSWORD=your-secure-admin-password
DATABASE_URL=sqlite:///instance/it_assets.db
```

### **2. SSL Certificate Setup (Optional but Recommended)**
```bash
# Create SSL directory
mkdir -p docker/nginx/ssl

# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem

# Or copy your SSL certificates
cp your-cert.pem docker/nginx/ssl/cert.pem
cp your-key.pem docker/nginx/ssl/key.pem
```

### **3. Start Production Environment**
```bash
# Build and start production containers
docker-compose -f docker-compose.prod.yml up --build -d

# Check container status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### **4. Access Production Application**
- **HTTP**: http://localhost
- **HTTPS**: https://localhost (if SSL configured)
- **Direct App**: http://localhost:8000

---

## 🔧 **Docker Commands Reference**

### **Development Commands**
```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f app

# Execute commands in container
docker-compose exec app bash
docker-compose exec app python add_sample_data.py

# Rebuild containers
docker-compose build --no-cache

# Stop and remove everything
docker-compose down -v --remove-orphans
```

### **Production Commands**
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up -d

# Scale application (multiple instances)
docker-compose -f docker-compose.prod.yml up -d --scale app=3

# Update application
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Backup database
docker-compose -f docker-compose.prod.yml exec app \
  cp /app/instance/it_assets.db /app/backups/backup-$(date +%Y%m%d).db

# View application logs
docker-compose -f docker-compose.prod.yml logs -f app

# View nginx logs
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### **Maintenance Commands**
```bash
# Clean up unused Docker resources
docker system prune -a

# Remove all containers and volumes
docker-compose down -v --remove-orphans
docker system prune -a --volumes

# Monitor resource usage
docker stats

# Inspect container details
docker inspect it-asset-manager-prod
```

---

## 📊 **Container Architecture**

### **Development Setup**
```
┌─────────────────────────────────────┐
│           Development               │
├─────────────────────────────────────┤
│  Port 5000                          │
│  ┌─────────────────────────────────┐ │
│  │     Flask Application           │ │
│  │     (Development Mode)          │ │
│  │     - Hot Reload                │ │
│  │     - Debug Mode                │ │
│  │     - SQLite Database           │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### **Production Setup**
```
┌─────────────────────────────────────────────────────────┐
│                    Production                           │
├─────────────────────────────────────────────────────────┤
│  Port 80/443                    Port 8000               │
│  ┌─────────────────────┐        ┌─────────────────────┐ │
│  │      Nginx          │───────▶│  Flask Application  │ │
│  │   Reverse Proxy     │        │   (Gunicorn WSGI)   │ │
│  │   - Load Balancer   │        │   - 4 Workers       │ │
│  │   - SSL Termination │        │   - SQLite Database │ │
│  │   - Static Files    │        │   - Health Checks   │ │
│  └─────────────────────┘        └─────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 **Troubleshooting**

### **Common Issues and Solutions**

#### **1. Port Already in Use**
```bash
# Check what's using the port
sudo lsof -i :5000
sudo lsof -i :80

# Kill the process
sudo kill -9 <PID>

# Or use different ports
docker-compose up -d --scale app=1 -p 5001:5000
```

#### **2. Permission Denied Errors**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x setup.sh run.py

# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

#### **3. Database Issues**
```bash
# Reset database
docker-compose down -v
docker-compose up -d

# Access database directly
docker-compose exec app python
>>> from app import db
>>> db.create_all()
>>> exit()
```

#### **4. Container Won't Start**
```bash
# Check container logs
docker-compose logs app

# Check container status
docker-compose ps

# Rebuild without cache
docker-compose build --no-cache
```

#### **5. SSL Certificate Issues**
```bash
# Generate new self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Check certificate
openssl x509 -in docker/nginx/ssl/cert.pem -text -noout
```

---

## 📈 **Performance Optimization**

### **Production Optimizations**
```bash
# Increase Gunicorn workers based on CPU cores
# Edit docker-compose.prod.yml
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "8", ...]

# Enable Nginx caching
# Add to nginx configuration:
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### **Database Optimization**
```bash
# For larger deployments, consider PostgreSQL
# Update docker-compose.prod.yml to include:
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: it_assets
      POSTGRES_USER: it_assets_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

---

## 🔒 **Security Best Practices**

### **Environment Security**
```bash
# Use strong passwords
ADMIN_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 64)

# Restrict file permissions
chmod 600 .env
chmod 600 docker/nginx/ssl/*

# Use non-root user in containers (already implemented)
USER appuser
```

### **Network Security**
```bash
# Use custom networks
docker network create it-asset-network --driver bridge

# Limit container capabilities
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - CHOWN
  - SETGID
  - SETUID
```

### **SSL/TLS Configuration**
```nginx
# Strong SSL configuration in nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
add_header Strict-Transport-Security "max-age=63072000" always;
```

---

## 📋 **Backup and Recovery**

### **Database Backup**
```bash
# Manual backup
docker-compose exec app cp /app/instance/it_assets.db /app/backups/backup-$(date +%Y%m%d).db

# Automated backup script
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec app cp /app/instance/it_assets.db /app/backups/backup-${DATE}.db
echo "Backup created: backup-${DATE}.db"
```

### **Full System Backup**
```bash
# Backup volumes
docker run --rm -v it-asset-manager_sqlite_prod_data:/data \
  -v $(pwd)/backups:/backup alpine \
  tar czf /backup/volume-backup-$(date +%Y%m%d).tar.gz -C /data .

# Backup configuration
tar czf config-backup-$(date +%Y%m%d).tar.gz \
  .env docker/ docker-compose*.yml
```

### **Recovery Process**
```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore database
cp backups/backup-YYYYMMDD.db instance/it_assets.db

# Restore volumes
docker run --rm -v it-asset-manager_sqlite_prod_data:/data \
  -v $(pwd)/backups:/backup alpine \
  tar xzf /backup/volume-backup-YYYYMMDD.tar.gz -C /data

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔄 **Updates and Maintenance**

### **Application Updates**
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Check health
docker-compose -f docker-compose.prod.yml ps
```

### **System Maintenance**
```bash
# Clean up old images
docker image prune -a

# Update base images
docker-compose pull
docker-compose up -d

# Monitor logs
docker-compose logs -f --tail=100
```

---

## 📞 **Support and Troubleshooting**

### **Health Checks**
```bash
# Check application health
curl -f http://localhost:5000/ || echo "App is down"
curl -f http://localhost/ || echo "Nginx is down"

# Check container health
docker-compose ps
docker inspect --format='{{.State.Health.Status}}' it-asset-manager-prod
```

### **Log Analysis**
```bash
# Application logs
docker-compose logs -f app

# Nginx access logs
docker-compose exec nginx tail -f /var/log/nginx/access.log

# Nginx error logs
docker-compose exec nginx tail -f /var/log/nginx/error.log

# System resource usage
docker stats --no-stream
```

### **Getting Help**
- **GitHub Issues**: [Create an issue](https://github.com/deepaknemade/it-asset-manager/issues)
- **Documentation**: Check README.md and other guides
- **Author**: [Deepak Nemade on LinkedIn](https://www.linkedin.com/in/deepak-nemade/)

---

## 🎯 **Next Steps**

After successful Docker deployment:

1. **Configure SSL certificates** for production
2. **Set up automated backups**
3. **Configure monitoring and alerting**
4. **Scale horizontally** if needed
5. **Consider AWS deployment** (see AWS_DEPLOYMENT.md)

---

**🚀 Your IT Asset Manager is now running in Docker! Access it at http://localhost:5000 (dev) or http://localhost (prod)**

---

*Created with ❤️ by [Deepak Nemade](https://www.linkedin.com/in/deepak-nemade/) - Making IT asset management easier with Docker.*
