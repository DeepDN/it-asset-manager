# Docker Deployment Guide - IT Asset Manager

## Overview

This guide covers Docker deployment options for the IT Asset Manager application, including development and production environments with comprehensive monitoring and backup solutions.

## 🐳 **Docker Architecture**

### **Multi-Stage Dockerfile**
- **Base Stage**: Common dependencies and user setup
- **Development Stage**: Development tools and hot-reload support
- **Production Stage**: Optimized for production with Gunicorn

### **Service Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Flask App     │    │   PostgreSQL    │
│  Load Balancer  │────│   (Gunicorn)    │────│    Database     │
│   & SSL Term    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │     Redis       │              │
         └──────────────│   Cache/Session │──────────────┘
                        │                 │
                        └─────────────────┘
```

## 🚀 **Quick Start**

### **Development Environment**

1. **Clone and Setup**
   ```bash
   git clone https://github.com/DeepDN/it-asset-manager.git
   cd it-asset-manager
   cp .env.example .env.dev
   ```

2. **Start Development Stack**
   ```bash
   docker-compose up -d
   ```

3. **Access Application**
   - **Application**: http://localhost:5000
   - **Nginx Proxy**: http://localhost:80
   - **PostgreSQL**: localhost:5432
   - **Redis**: localhost:6379

4. **View Logs**
   ```bash
   docker-compose logs -f app-dev
   ```

### **Production Environment**

1. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Generate SSL Certificates**
   ```bash
   mkdir -p docker/nginx/ssl
   # Add your SSL certificates
   ```

3. **Start Production Stack**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Access Application**
   - **Application**: https://your-domain.com
   - **Monitoring**: http://localhost:3000 (Grafana)
   - **Metrics**: http://localhost:9090 (Prometheus)

## 📋 **Detailed Configuration**

### **Environment Variables**

#### **Required Variables**
```bash
# Security
SECRET_KEY=your-super-secret-key
ADMIN_PASSWORD=secure-admin-password

# Database
POSTGRES_PASSWORD=secure-database-password
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis (Production)
REDIS_PASSWORD=secure-redis-password
REDIS_URL=redis://:password@host:port/db
```

#### **Optional Variables**
```bash
# Application
FLASK_ENV=production
LOG_LEVEL=INFO
MAX_CONTENT_LENGTH=16777216

# Monitoring
GRAFANA_PASSWORD=grafana-password
WEBHOOK_URL=https://hooks.slack.com/webhook

# Email (Future)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=email@domain.com
MAIL_PASSWORD=app-password
```

### **Volume Configuration**

#### **Development Volumes**
```yaml
volumes:
  - .:/app                    # Source code (hot-reload)
  - sqlite_data:/app/instance # SQLite persistence
  - ./logs:/app/logs          # Log files
```

#### **Production Volumes**
```yaml
volumes:
  - ./logs:/app/logs          # Application logs
  - ./uploads:/app/uploads    # File uploads
  - postgres_prod_data:/var/lib/postgresql/data  # Database
  - redis_prod_data:/data     # Redis persistence
```

## 🔧 **Service Configuration**

### **Flask Application**

#### **Development Configuration**
```yaml
app-dev:
  build:
    target: development
  ports:
    - "5000:5000"
  environment:
    - FLASK_ENV=development
    - FLASK_DEBUG=1
  volumes:
    - .:/app  # Hot-reload support
```

#### **Production Configuration**
```yaml
app:
  build:
    target: production
  environment:
    - FLASK_ENV=production
  deploy:
    replicas: 2
    resources:
      limits:
        cpus: '1.0'
        memory: 512M
```

### **PostgreSQL Database**

#### **Configuration**
```yaml
postgres:
  image: postgres:15-alpine
  environment:
    - POSTGRES_DB=it_assets_prod
    - POSTGRES_USER=it_assets_user
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
  volumes:
    - postgres_prod_data:/var/lib/postgresql/data
    - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
```

#### **Performance Tuning**
The `init.sql` script creates optimized indexes:
- User table indexes for username, email lookups
- Asset table indexes for tag, serial number, type searches
- Composite indexes for common query patterns

### **Redis Cache**

#### **Development**
```yaml
redis-dev:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

#### **Production**
```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
  volumes:
    - redis_prod_data:/data
```

### **Nginx Reverse Proxy**

#### **Features**
- SSL termination
- Load balancing
- Rate limiting
- Static file serving
- Security headers
- Gzip compression

#### **Rate Limiting**
```nginx
# Login protection
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

# API protection
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

## 🔍 **Health Checks**

### **Application Health Check**
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### **Health Check Endpoints**
- `/health` - Basic health check
- `/health/detailed` - Detailed system information
- `/ready` - Kubernetes-style readiness check
- `/live` - Kubernetes-style liveness check

### **Database Health Check**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U it_assets_user -d it_assets_prod"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 💾 **Backup and Recovery**

### **Automated Backups**

#### **Backup Service**
```yaml
postgres-backup:
  image: postgres:15-alpine
  volumes:
    - ./backups/postgres:/backups
    - ./docker/scripts/backup.sh:/backup.sh
  command: /bin/sh -c "chmod +x /backup.sh && crond -f"
```

#### **Backup Features**
- Daily automated backups
- Multiple backup formats (custom and SQL)
- Compression for space efficiency
- Retention policy (7 days default)
- Backup verification
- Notification support

#### **Manual Backup**
```bash
# Create backup
docker-compose exec postgres-backup /backup.sh

# List backups
docker-compose exec postgres-backup ls -la /backups/

# Restore from backup
docker-compose exec postgres pg_restore -h postgres -U it_assets_user -d it_assets_prod /backups/backup_file.custom
```

### **Data Recovery**

#### **Database Recovery**
```bash
# Stop application
docker-compose down

# Restore database
docker-compose exec postgres pg_restore \
  -h postgres -U it_assets_user -d it_assets_prod \
  --clean --if-exists /backups/backup_file.custom

# Start application
docker-compose up -d
```

#### **Volume Recovery**
```bash
# Backup volumes
docker run --rm -v it-asset-manager_postgres_prod_data:/data \
  -v $(pwd)/backups:/backup alpine \
  tar czf /backup/postgres_volume_backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v it-asset-manager_postgres_prod_data:/data \
  -v $(pwd)/backups:/backup alpine \
  tar xzf /backup/postgres_volume_backup.tar.gz -C /data
```

## 📊 **Monitoring and Logging**

### **Prometheus Monitoring**

#### **Enable Monitoring**
```bash
docker-compose -f docker-compose.prod.yml --profile monitoring up -d
```

#### **Metrics Available**
- Application performance metrics
- Database connection metrics
- System resource usage
- Custom business metrics

### **Grafana Dashboards**

#### **Access Grafana**
- URL: http://localhost:3000
- Username: admin
- Password: ${GRAFANA_PASSWORD}

#### **Pre-configured Dashboards**
- Application Overview
- Database Performance
- System Resources
- Business Metrics

### **Log Management**

#### **Log Locations**
```bash
# Application logs
./logs/it_asset_manager.log

# Nginx logs
./logs/nginx/access.log
./logs/nginx/error.log

# Container logs
docker-compose logs app
docker-compose logs postgres
docker-compose logs nginx
```

#### **Log Rotation**
```bash
# Configure logrotate
cat > /etc/logrotate.d/it-asset-manager << EOF
/path/to/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 appuser appuser
}
EOF
```

## 🔒 **Security Configuration**

### **SSL/TLS Setup**

#### **Generate Self-Signed Certificate (Development)**
```bash
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

#### **Production SSL Certificate**
```bash
# Using Let's Encrypt
certbot certonly --standalone -d your-domain.com
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/key.pem
```

### **Security Headers**
Nginx configuration includes:
- HSTS (HTTP Strict Transport Security)
- X-Frame-Options
- X-XSS-Protection
- X-Content-Type-Options
- Content Security Policy

### **Network Security**
```yaml
networks:
  it-asset-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 🚀 **Deployment Strategies**

### **Blue-Green Deployment**

#### **Setup**
```bash
# Deploy new version (green)
docker-compose -f docker-compose.prod.yml up -d --scale app=4

# Test new version
curl -f https://your-domain.com/health

# Switch traffic (update nginx config)
# Remove old containers
docker-compose -f docker-compose.prod.yml up -d --scale app=2
```

### **Rolling Updates**

#### **Update Application**
```bash
# Build new image
docker-compose -f docker-compose.prod.yml build app

# Rolling update
docker-compose -f docker-compose.prod.yml up -d --no-deps app
```

### **Scaling**

#### **Horizontal Scaling**
```bash
# Scale application containers
docker-compose -f docker-compose.prod.yml up -d --scale app=4

# Scale with resource limits
docker-compose -f docker-compose.prod.yml up -d \
  --scale app=4 \
  --scale postgres=1 \
  --scale redis=1
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **Application Won't Start**
```bash
# Check logs
docker-compose logs app

# Check health
docker-compose exec app curl -f http://localhost:8000/health

# Check database connection
docker-compose exec app python -c "from it_asset_manager.core.database import db; print('DB OK')"
```

#### **Database Connection Issues**
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U it_assets_user

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U it_assets_user -d it_assets_prod -c "SELECT version();"
```

#### **Performance Issues**
```bash
# Check resource usage
docker stats

# Check application metrics
curl http://localhost:8000/health/detailed

# Check database performance
docker-compose exec postgres psql -U it_assets_user -d it_assets_prod -c "SELECT * FROM pg_stat_activity;"
```

### **Debug Mode**

#### **Enable Debug Logging**
```bash
# Update environment
echo "LOG_LEVEL=DEBUG" >> .env

# Restart with debug
docker-compose -f docker-compose.prod.yml up -d
```

#### **Interactive Debugging**
```bash
# Access container shell
docker-compose exec app /bin/bash

# Run Python shell
docker-compose exec app python -c "from it_asset_manager.core.app import create_app; app = create_app(); print('App created')"
```

## 📈 **Performance Optimization**

### **Application Optimization**
- Multi-worker Gunicorn setup
- Connection pooling
- Redis caching
- Static file optimization

### **Database Optimization**
- Optimized indexes
- Connection pooling
- Query optimization
- Regular maintenance

### **Infrastructure Optimization**
- Resource limits and reservations
- Health check optimization
- Log rotation
- Monitoring and alerting

## 🔄 **Maintenance**

### **Regular Maintenance Tasks**

#### **Daily**
- Check application health
- Monitor resource usage
- Review error logs

#### **Weekly**
- Update security patches
- Review backup integrity
- Performance analysis

#### **Monthly**
- Update base images
- Security audit
- Capacity planning

### **Update Procedures**

#### **Application Updates**
```bash
# Pull latest code
git pull origin main

# Build and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

#### **System Updates**
```bash
# Update base images
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

This comprehensive Docker setup provides a production-ready deployment with monitoring, backup, security, and scalability features for the IT Asset Manager application.
