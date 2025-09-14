# Production Deployment Guide

This guide covers deploying the Face Auth application to a production environment.

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- Node.js 16+
- Nginx
- SSL certificate
- SMTP server access

## 1. Server Setup

### Update system
```bash
sudo apt update && sudo apt upgrade -y
```

### Install dependencies
```bash
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

## 2. Application Deployment

### Clone repository
```bash
cd /var/www
sudo git clone <your-repo-url> face-auth
sudo chown -R $USER:$USER face-auth
cd face-auth
```

### Backend setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend setup
```bash
cd ../frontend
npm install
npm run build
```

## 3. Environment Configuration

### Create production environment file
```bash
cd /var/www/face-auth/backend
cp .env.example .env.production
```

### Edit production environment
```bash
nano .env.production
```

Set these variables:
```env
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-here
DATABASE_URL=sqlite:///face_auth_production.db
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-app-password
CORS_ORIGINS=https://yourdomain.com
```

## 4. Database Setup

```bash
cd /var/www/face-auth/backend
source venv/bin/activate
export FLASK_ENV=production
python run_app.py --config production &
# Stop after tables are created
```

## 5. Process Management (systemd)

### Create service file
```bash
sudo nano /etc/systemd/system/face-auth.service
```

```ini
[Unit]
Description=Face Auth Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/face-auth/backend
Environment=FLASK_ENV=production
ExecStart=/var/www/face-auth/backend/venv/bin/python run_app.py --config production --host 127.0.0.1 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and start service
```bash
sudo systemctl daemon-reload
sudo systemctl enable face-auth
sudo systemctl start face-auth
sudo systemctl status face-auth
```

## 6. Nginx Configuration

### Create Nginx config
```bash
sudo nano /etc/nginx/sites-available/face-auth
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Frontend (React build)
    root /var/www/face-auth/frontend/build;
    index index.html;
    
    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API routes
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Socket.IO
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # File upload size
    client_max_body_size 16M;
    
    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Enable site
```bash
sudo ln -s /etc/nginx/sites-available/face-auth /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 7. SSL Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 8. Firewall Configuration

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
```

## 9. Monitoring and Logs

### Application logs
```bash
sudo journalctl -u face-auth -f
```

### Nginx logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Log rotation
```bash
sudo nano /etc/logrotate.d/face-auth
```

```
/var/log/face-auth/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

## 10. Security Hardening

### Regular updates
```bash
# Create update script
sudo nano /usr/local/bin/update-face-auth.sh
```

```bash
#!/bin/bash
cd /var/www/face-auth
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ../frontend
npm install
npm run build
sudo systemctl restart face-auth
sudo systemctl reload nginx
```

```bash
sudo chmod +x /usr/local/bin/update-face-auth.sh
```

### Backup script
```bash
sudo nano /usr/local/bin/backup-face-auth.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/face-auth"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /var/www/face-auth/backend/face_auth_production.db $BACKUP_DIR/face_auth_$DATE.db

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /var/www/face-auth/backend uploads/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

```bash
sudo chmod +x /usr/local/bin/backup-face-auth.sh
```

### Cron jobs
```bash
sudo crontab -e
```

```cron
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-face-auth.sh

# Weekly updates on Sunday at 3 AM
0 3 * * 0 /usr/local/bin/update-face-auth.sh
```

## 11. Performance Optimization

### Database optimization
- Consider migrating to PostgreSQL for better performance
- Set up database connection pooling
- Implement database indexing

### Caching
- Add Redis for session storage
- Implement API response caching
- Use CDN for static assets

### Monitoring
- Set up application monitoring (e.g., Prometheus + Grafana)
- Configure error tracking (e.g., Sentry)
- Monitor server resources

## 12. Troubleshooting

### Common issues

1. **Service won't start**
   ```bash
   sudo systemctl status face-auth
   sudo journalctl -u face-auth --since "1 hour ago"
   ```

2. **Database permissions**
   ```bash
   sudo chown -R www-data:www-data /var/www/face-auth/backend/
   ```

3. **Nginx errors**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

4. **SSL certificate renewal**
   ```bash
   sudo certbot renew --dry-run
   ```

### Health check endpoint
The application includes a health check at `/api/health` for monitoring.

## Security Notes

1. Change all default passwords and keys
2. Regularly update dependencies
3. Monitor logs for suspicious activity
4. Implement rate limiting
5. Use strong SSL configuration
6. Keep backups secure and encrypted
7. Regularly test backup restoration

This deployment guide provides a solid foundation for running the Face Auth application in production. Adjust configurations based on your specific requirements and infrastructure.