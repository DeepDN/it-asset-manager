# ☁️ AWS EC2 Deployment Guide - IT Asset Manager

[![AWS](https://img.shields.io/badge/AWS-EC2-orange.svg)](https://aws.amazon.com/ec2/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-20.04+-purple.svg)](https://ubuntu.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://docker.com)

> **Complete step-by-step guide for deploying IT Asset Manager on AWS EC2 with Docker, SSL, and production-ready configuration.**

---

## 📋 **Prerequisites**

### **AWS Account Requirements**
- **AWS Account**: Active AWS account with billing enabled
- **IAM Permissions**: EC2, VPC, Security Groups, Route53 (optional)
- **Key Pair**: EC2 Key Pair for SSH access
- **Domain**: Optional domain name for SSL setup

### **Local Requirements**
- **AWS CLI**: Installed and configured
- **SSH Client**: For connecting to EC2 instance
- **Git**: For cloning the repository

---

## 🚀 **Step 1: AWS EC2 Instance Setup**

### **1.1 Launch EC2 Instance**

#### **Using AWS Console:**
1. **Login to AWS Console** → Navigate to EC2
2. **Launch Instance** → Click "Launch Instance"
3. **Choose AMI**: Ubuntu Server 22.04 LTS (Free Tier Eligible)
4. **Instance Type**: 
   - **Development**: t2.micro (1 vCPU, 1GB RAM) - Free Tier
   - **Production**: t3.small (2 vCPU, 2GB RAM) or larger
5. **Key Pair**: Select existing or create new key pair
6. **Security Group**: Create new with following rules:

```
Inbound Rules:
- SSH (22): Your IP address
- HTTP (80): 0.0.0.0/0
- HTTPS (443): 0.0.0.0/0
- Custom TCP (5000): Your IP (for development)
```

#### **Using AWS CLI:**
```bash
# Create security group
aws ec2 create-security-group \
  --group-name it-asset-manager-sg \
  --description "Security group for IT Asset Manager"

# Add inbound rules
aws ec2 authorize-security-group-ingress \
  --group-name it-asset-manager-sg \
  --protocol tcp --port 22 --cidr YOUR_IP/32

aws ec2 authorize-security-group-ingress \
  --group-name it-asset-manager-sg \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name it-asset-manager-sg \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 1 \
  --instance-type t3.small \
  --key-name your-key-pair \
  --security-groups it-asset-manager-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=IT-Asset-Manager}]'
```

### **1.2 Connect to EC2 Instance**
```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Update system packages
sudo apt update && sudo apt upgrade -y
```

---

## 🔧 **Step 2: Server Setup and Dependencies**

### **2.1 Install Docker and Docker Compose**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### **2.2 Install Additional Tools**
```bash
# Install essential tools
sudo apt install -y git curl wget unzip htop nginx-utils

# Install AWS CLI (optional)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### **2.3 Configure Firewall (UFW)**
```bash
# Enable UFW
sudo ufw enable

# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Check status
sudo ufw status
```

---

## 📦 **Step 3: Application Deployment**

### **3.1 Clone and Setup Application**
```bash
# Clone repository
git clone https://github.com/DeepDN/it-asset-manager.git
cd it-asset-manager

# Create necessary directories
mkdir -p logs uploads instance backups

# Set proper permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/it-asset-manager
chmod +x setup.sh run.py
```

### **3.2 Environment Configuration**
```bash
# Create production environment file
cp .env.example .env

# Edit environment variables
nano .env
```

**Production Environment Configuration:**
```env
# Application Settings
SECRET_KEY=your-super-secret-production-key-here
FLASK_ENV=production
FLASK_DEBUG=0

# Database Configuration
DATABASE_URL=sqlite:///instance/it_assets.db

# Admin Configuration
ADMIN_PASSWORD=your-secure-admin-password

# Security Settings
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# Server Configuration
SERVER_NAME=your-domain.com
PREFERRED_URL_SCHEME=https
```

### **3.3 SSL Certificate Setup**

#### **Option A: Let's Encrypt (Recommended for Production)**
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Create SSL directory
mkdir -p docker/nginx/ssl

# Generate certificate (replace with your domain)
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to Docker directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/key.pem
sudo chown ubuntu:ubuntu docker/nginx/ssl/*
```

#### **Option B: Self-Signed Certificate (Development/Testing)**
```bash
# Create SSL directory
mkdir -p docker/nginx/ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
```

---

## 🚀 **Step 4: Production Deployment**

### **4.1 Deploy with Docker Compose**
```bash
# Build and start production containers
docker-compose -f docker-compose.prod.yml up --build -d

# Check container status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### **4.2 Verify Deployment**
```bash
# Check application health
curl -f http://localhost:8000/ || echo "App container issue"
curl -f http://localhost/ || echo "Nginx issue"

# Check from external
curl -f http://YOUR_EC2_PUBLIC_IP/ || echo "External access issue"

# Check SSL (if configured)
curl -f https://YOUR_DOMAIN/ || echo "SSL issue"
```

### **4.3 Initialize Application**
```bash
# Add sample data (optional)
docker-compose -f docker-compose.prod.yml exec app python add_sample_data.py

# Create additional admin user (optional)
docker-compose -f docker-compose.prod.yml exec app python update_password.py
```

---

## 🌐 **Step 5: Domain and DNS Configuration**

### **5.1 Route53 Setup (if using AWS domain)**
```bash
# Create hosted zone
aws route53 create-hosted-zone --name your-domain.com --caller-reference $(date +%s)

# Create A record pointing to EC2 instance
aws route53 change-resource-record-sets --hosted-zone-id YOUR_ZONE_ID --change-batch '{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "your-domain.com",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "YOUR_EC2_PUBLIC_IP"}]
    }
  }]
}'
```

### **5.2 Update Nginx Configuration for Domain**
```bash
# Edit nginx configuration
nano docker/nginx/prod.conf

# Update server_name
server_name your-domain.com www.your-domain.com;

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 🔒 **Step 6: Security Hardening**

### **6.1 SSH Security**
```bash
# Edit SSH configuration
sudo nano /etc/ssh/sshd_config

# Recommended settings:
Port 2222                    # Change default port
PermitRootLogin no          # Disable root login
PasswordAuthentication no   # Use key-based auth only
MaxAuthTries 3             # Limit auth attempts

# Restart SSH service
sudo systemctl restart sshd

# Update security group to allow new SSH port
aws ec2 authorize-security-group-ingress \
  --group-name it-asset-manager-sg \
  --protocol tcp --port 2222 --cidr YOUR_IP/32
```

### **6.2 Fail2Ban Setup**
```bash
# Install Fail2Ban
sudo apt install -y fail2ban

# Configure Fail2Ban
sudo nano /etc/fail2ban/jail.local

# Add configuration:
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 2222

# Start Fail2Ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### **6.3 System Monitoring**
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Set up log rotation
sudo nano /etc/logrotate.d/it-asset-manager

# Add configuration:
/home/ubuntu/it-asset-manager/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
```

---

## 📊 **Step 7: Monitoring and Maintenance**

### **7.1 System Monitoring Script**
```bash
# Create monitoring script
nano monitor.sh

#!/bin/bash
echo "=== IT Asset Manager Health Check ==="
echo "Date: $(date)"
echo "Uptime: $(uptime)"
echo ""

echo "=== Docker Containers ==="
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "=== Disk Usage ==="
df -h

echo ""
echo "=== Memory Usage ==="
free -h

echo ""
echo "=== Application Health ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "Application Down"

# Make executable
chmod +x monitor.sh
```

### **7.2 Automated Backup Script**
```bash
# Create backup script
nano backup.sh

#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/ubuntu/it-asset-manager"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose -f $APP_DIR/docker-compose.prod.yml exec -T app \
  cp /app/instance/it_assets.db /app/backups/backup-${DATE}.db

# Backup configuration
tar czf $BACKUP_DIR/config-${DATE}.tar.gz \
  -C $APP_DIR .env docker/ docker-compose*.yml

# Backup uploads
tar czf $BACKUP_DIR/uploads-${DATE}.tar.gz \
  -C $APP_DIR uploads/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"

# Make executable
chmod +x backup.sh
```

### **7.3 Cron Jobs Setup**
```bash
# Edit crontab
crontab -e

# Add backup and monitoring jobs
# Daily backup at 2 AM
0 2 * * * /home/ubuntu/it-asset-manager/backup.sh >> /home/ubuntu/logs/backup.log 2>&1

# Health check every 5 minutes
*/5 * * * * /home/ubuntu/it-asset-manager/monitor.sh >> /home/ubuntu/logs/monitor.log 2>&1

# SSL certificate renewal (if using Let's Encrypt)
0 3 * * 0 sudo certbot renew --quiet && docker-compose -f /home/ubuntu/it-asset-manager/docker-compose.prod.yml restart nginx
```

---

## 🔄 **Step 8: Updates and Maintenance**

### **8.1 Application Updates**
```bash
# Create update script
nano update.sh

#!/bin/bash
cd /home/ubuntu/it-asset-manager

echo "Backing up current version..."
./backup.sh

echo "Pulling latest changes..."
git pull origin main

echo "Rebuilding containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "Restarting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "Checking health..."
sleep 10
curl -f http://localhost/ && echo "Update successful!" || echo "Update failed!"

# Make executable
chmod +x update.sh
```

### **8.2 System Updates**
```bash
# Create system update script
nano system-update.sh

#!/bin/bash
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Updating Docker images..."
docker-compose -f docker-compose.prod.yml pull

echo "Restarting containers with new images..."
docker-compose -f docker-compose.prod.yml up -d

echo "Cleaning up old Docker images..."
docker image prune -f

echo "System update completed!"

# Make executable
chmod +x system-update.sh
```

---

## 🔍 **Troubleshooting**

### **Common Issues and Solutions**

#### **1. Application Not Accessible**
```bash
# Check security group rules
aws ec2 describe-security-groups --group-names it-asset-manager-sg

# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs app
docker-compose -f docker-compose.prod.yml logs nginx
```

#### **2. SSL Certificate Issues**
```bash
# Check certificate validity
openssl x509 -in docker/nginx/ssl/cert.pem -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew --dry-run

# Update certificate in Docker
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/key.pem
docker-compose -f docker-compose.prod.yml restart nginx
```

#### **3. Database Issues**
```bash
# Check database file
ls -la instance/

# Reset database (WARNING: This will delete all data)
docker-compose -f docker-compose.prod.yml down
rm instance/it_assets.db
docker-compose -f docker-compose.prod.yml up -d

# Restore from backup
cp backups/backup-YYYYMMDD_HHMMSS.db instance/it_assets.db
docker-compose -f docker-compose.prod.yml restart app
```

#### **4. Performance Issues**
```bash
# Check system resources
htop
df -h
free -h

# Check Docker stats
docker stats

# Scale application (if needed)
docker-compose -f docker-compose.prod.yml up -d --scale app=2
```

---

## 💰 **Cost Optimization**

### **EC2 Instance Sizing**
- **t2.micro**: Free tier, suitable for testing (1 vCPU, 1GB RAM)
- **t3.small**: Production ready (2 vCPU, 2GB RAM) ~$15/month
- **t3.medium**: High traffic (2 vCPU, 4GB RAM) ~$30/month

### **Cost Monitoring**
```bash
# Set up billing alerts in AWS Console
# Use AWS Cost Explorer to monitor usage
# Consider Reserved Instances for long-term deployments
```

---

## 📈 **Scaling and Performance**

### **Vertical Scaling (Upgrade Instance)**
```bash
# Stop instance
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Change instance type
aws ec2 modify-instance-attribute --instance-id i-1234567890abcdef0 --instance-type Value=t3.medium

# Start instance
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

### **Horizontal Scaling (Load Balancer)**
```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name it-asset-manager-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678

# Create multiple EC2 instances
# Register instances with load balancer
# Update DNS to point to load balancer
```

---

## 🎯 **Production Checklist**

### **Pre-Deployment**
- [ ] EC2 instance launched with appropriate size
- [ ] Security groups configured correctly
- [ ] SSH key pair created and secured
- [ ] Domain name configured (if applicable)
- [ ] SSL certificates obtained

### **Deployment**
- [ ] Docker and Docker Compose installed
- [ ] Application cloned and configured
- [ ] Environment variables set securely
- [ ] SSL certificates configured
- [ ] Application deployed and tested
- [ ] Health checks passing

### **Post-Deployment**
- [ ] Monitoring scripts configured
- [ ] Backup scripts set up and tested
- [ ] Cron jobs scheduled
- [ ] Security hardening completed
- [ ] Performance testing done
- [ ] Documentation updated

### **Ongoing Maintenance**
- [ ] Regular backups verified
- [ ] Security updates applied
- [ ] SSL certificates renewed
- [ ] Performance monitored
- [ ] Logs reviewed regularly

---

## 📞 **Support and Resources**

### **AWS Resources**
- **AWS Documentation**: [EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- **AWS Support**: [AWS Support Center](https://console.aws.amazon.com/support/)
- **AWS Forums**: [AWS Developer Forums](https://forums.aws.amazon.com/)

### **Application Support**
- **GitHub Issues**: [Create an issue](https://github.com/DeepDN/it-asset-manager/issues)
- **Documentation**: Check README.md and other guides
- **Author**: [Deepak Nemade on LinkedIn](https://www.linkedin.com/in/deepak-nemade/)

---

## 🎉 **Congratulations!**

Your IT Asset Manager is now running on AWS EC2 with:
- ✅ Production-ready Docker deployment
- ✅ SSL/HTTPS encryption
- ✅ Automated backups
- ✅ Security hardening
- ✅ Monitoring and alerting
- ✅ Scalable architecture

**Access your application at**: https://your-domain.com or http://YOUR_EC2_PUBLIC_IP

---

*Created with ❤️ by [Deepak Nemade](https://www.linkedin.com/in/deepak-nemade/) - Empowering IT professionals with cloud-ready asset management.*
