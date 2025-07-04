# Production Deployment Guide

This guide covers production deployment of IT Asset Manager with security best practices and performance optimizations.

## 🚀 Quick Production Deployment

### Docker Production (Recommended)

```bash
# Clone the repository
git clone https://github.com/DeepDN/it-asset-manager.git
cd it-asset-manager

# Create production environment file
cp .env.example .env
nano .env  # Configure your production settings

# Start production environment
./docker-start.sh prod

# Access: http://your-server-ip
# Default login: admin / admin123 (CHANGE IMMEDIATELY)
```

### AWS EC2 Production Deployment

```bash
# Launch EC2 instance (t3.small recommended)
# Security Groups: Allow ports 22, 80, 443

# SSH into instance
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker ubuntu && newgrp docker

# Deploy application
git clone https://github.com/DeepDN/it-asset-manager.git
cd it-asset-manager
cp .env.example .env
nano .env  # Configure production settings
./docker-start.sh prod
```

## 🔒 Production Security Checklist

### Pre-Deployment Security

- [ ] **Change default admin password**
  ```bash
  docker-compose -f docker-compose.prod.yml exec app python update_password.py
  ```

- [ ] **Update SECRET_KEY in .env**
  ```bash
  export SECRET_KEY="$(openssl rand -base64 32)"
  echo "SECRET_KEY=$SECRET_KEY" >> .env
  ```

- [ ] **Configure SSL/HTTPS** (if using custom domain)
  ```bash
  # Generate SSL certificate
  sudo certbot certonly --standalone -d your-domain.com
  
  # Copy certificates to nginx
  sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/cert.pem
  sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/key.pem
  ```

- [ ] **Configure firewall**
  ```bash
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp    # HTTP
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw --force enable
  ```

### Post-Deployment Security

- [ ] **Test login functionality**
- [ ] **Verify SSL/HTTPS** (if configured)
- [ ] **Set up monitoring**
- [ ] **Schedule regular backups**
- [ ] **Update DNS records** (if using domain)

## 📊 Production Configuration

### Environment Variables (.env)

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
SESSION_COOKIE_SAMESITE=Lax

# Performance Settings
MAX_CONTENT_LENGTH=16777216
PERMANENT_SESSION_LIFETIME=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Docker Production Configuration

The production setup includes:
- **Nginx reverse proxy** with SSL support
- **Non-root container** execution
- **Health checks** and automatic restarts
- **Volume persistence** for data
- **Security headers** and rate limiting

## 🔧 Production Maintenance

### Regular Backups

```bash
# Automated backup (run daily via cron)
./backup.sh

# Manual backup
docker-compose -f docker-compose.prod.yml exec app \
  cp /app/instance/it_assets.db /app/backups/backup-$(date +%Y%m%d).db
```

### Updates and Patches

```bash
# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Update system packages
sudo apt update && sudo apt upgrade -y
```

### Monitoring

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check container health
docker-compose -f docker-compose.prod.yml ps

# Monitor resources
docker stats
```

## 🚨 Troubleshooting

### Common Production Issues

1. **Application won't start**
   ```bash
   # Check logs
   docker-compose -f docker-compose.prod.yml logs app
   
   # Verify environment
   docker-compose -f docker-compose.prod.yml config
   ```

2. **SSL certificate issues**
   ```bash
   # Verify certificate files
   ls -la docker/nginx/ssl/
   
   # Test SSL configuration
   openssl s_client -connect your-domain.com:443
   ```

3. **Database connection issues**
   ```bash
   # Check database file permissions
   ls -la instance/
   
   # Reset database (WARNING: Deletes data)
   rm -f instance/it_assets.db
   docker-compose -f docker-compose.prod.yml restart
   ```

### Performance Optimization

1. **Database optimization**
   - Regular VACUUM for SQLite
   - Consider PostgreSQL for large deployments
   - Implement database indexing

2. **Nginx optimization**
   - Enable gzip compression
   - Configure caching headers
   - Implement rate limiting

3. **Container optimization**
   - Set appropriate resource limits
   - Use multi-stage builds
   - Optimize image layers

## 📈 Scaling Considerations

### Single Server Scaling

- **Vertical scaling**: Increase server resources
- **Database optimization**: Tune SQLite or migrate to PostgreSQL
- **Caching**: Implement Redis for session storage
- **CDN**: Use CloudFront for static assets

### Multi-Server Scaling

- **Load balancer**: Nginx or AWS ALB
- **Shared database**: PostgreSQL or MySQL
- **Shared storage**: NFS or S3 for uploads
- **Session storage**: Redis cluster

## 🔍 Monitoring and Alerting

### Basic Monitoring

```bash
# System resources
htop
df -h
free -h

# Application health
curl -f http://localhost/health || echo "Application down"

# Docker containers
docker ps
docker stats
```

### Advanced Monitoring (Optional)

- **Prometheus + Grafana**: Metrics and dashboards
- **ELK Stack**: Log aggregation and analysis
- **Uptime monitoring**: External service monitoring
- **Alert manager**: Email/Slack notifications

## 🆘 Disaster Recovery

### Backup Strategy

1. **Database backups**: Daily automated backups
2. **Configuration backups**: Environment files and certificates
3. **Code backups**: Git repository with tags
4. **Infrastructure as Code**: Document server setup

### Recovery Procedures

1. **Application recovery**
   ```bash
   # Restore from backup
   cp backups/backup-YYYYMMDD.db instance/it_assets.db
   docker-compose -f docker-compose.prod.yml restart
   ```

2. **Full server recovery**
   ```bash
   # New server setup
   # 1. Install Docker
   # 2. Clone repository
   # 3. Restore configuration
   # 4. Restore database
   # 5. Start services
   ```

## 📞 Production Support

For production issues:

1. **Check troubleshooting guide**: [docs/guides/TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md)
2. **Review logs**: Application and system logs
3. **GitHub Issues**: [Report production issues](https://github.com/DeepDN/it-asset-manager/issues)
4. **Professional Support**: [Contact Deepak Nemade](https://www.linkedin.com/in/deepak-nemade/)

---

**🚀 Ready for production? Follow this guide step by step for a secure and reliable deployment!**
