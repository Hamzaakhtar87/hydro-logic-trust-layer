# 🚀 AWS EC2 Deployment Guide

## Quick Deploy (5 Minutes)

### Prerequisites

1. **AWS EC2 Instance** with:
   - Ubuntu 22.04 LTS
   - At least t2.medium (2GB RAM)
   - 20GB disk space

2. **Security Group** with these inbound rules:
   | Port | Protocol | Source | Purpose |
   |------|----------|--------|---------|
   | 22 | TCP | Your IP | SSH access |
   | 80 | TCP | 0.0.0.0/0 | HTTP (frontend) |
   | 443 | TCP | 0.0.0.0/0 | HTTPS (optional) |

3. **Gemini API Key** from [AI Studio](https://aistudio.google.com/)

---

## Deployment Steps

### Step 1: Connect to Your EC2

```bash
ssh -i your-key.pem ubuntu@51.21.128.226
```

### Step 2: Clone/Upload the Project

**Option A: Git Clone**
```bash
git clone https://github.com/YOUR_USERNAME/HydroLogicTrustLayer.git
cd HydroLogicTrustLayer
```

**Option B: SCP Upload**
```bash
# From your local machine:
scp -i your-key.pem -r ./HydroLogicTrustLayer ubuntu@51.21.128.226:~/
```

### Step 3: Configure Environment

```bash
# Create .env file with your API key
cp .env.example .env
nano .env
```

Add your Gemini API key:
```
GEMINI_API_KEY=AIzaSy...your_key_here
DATABASE_URL=sqlite:///./hydro_logic.db
JWT_SECRET=your-secret-key-change-in-production
```

### Step 4: Run Deployment Script

```bash
chmod +x deploy-simple.sh
sudo ./deploy-simple.sh
```

The script will:
1. ✅ Install Python, Node.js, Nginx
2. ✅ Set up Python virtual environment
3. ✅ Build the React frontend
4. ✅ Configure Nginx reverse proxy
5. ✅ Create and start systemd service

### Step 5: Verify Deployment

Visit in your browser:
- **Frontend:** http://51.21.128.226
- **API Docs:** http://51.21.128.226/docs
- **Health Check:** http://51.21.128.226/health

---

## Post-Deployment

### View Logs

```bash
# Backend logs
sudo journalctl -u hydro-logic -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Restart Services

```bash
# Restart backend
sudo systemctl restart hydro-logic

# Restart Nginx
sudo systemctl restart nginx

# Restart both
sudo systemctl restart hydro-logic nginx
```

### Check Status

```bash
# Backend status
sudo systemctl status hydro-logic

# Nginx status
sudo systemctl status nginx

# Test health endpoint
curl http://localhost:8000/health
```

---

## Enable HTTPS (Recommended)

### Using Let's Encrypt (Free SSL)

You'll need a domain name pointing to your IP first.

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
sudo journalctl -u hydro-logic -n 50

# Common issues:
# 1. Missing .env file
# 2. Wrong GEMINI_API_KEY
# 3. Port 8000 already in use

# Kill process on port 8000
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Nginx errors

```bash
# Test config
sudo nginx -t

# Common issues:
# 1. Frontend not built (run npm run build)
# 2. Wrong paths in nginx config

# Check error log
sudo tail -f /var/log/nginx/error.log
```

### Frontend shows blank page

```bash
# Rebuild frontend
cd frontend
npm run build

# Check if dist folder exists
ls -la dist/
```

### API returns CORS errors

```bash
# Check ALLOWED_ORIGINS in .env
# Should include: http://51.21.128.226

# Restart backend after changes
sudo systemctl restart hydro-logic
```

---

## Architecture Overview

```
                    Internet
                       │
                       ▼
              ┌────────────────┐
              │    Nginx       │ Port 80/443
              │  Reverse Proxy │
              └───────┬────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────┐          ┌────────────────┐
│   Frontend    │          │    Backend     │
│  (Static)     │          │  (FastAPI)     │
│  /frontend/   │          │  Port 8000     │
│    dist/      │          └───────┬────────┘
└───────────────┘                  │
                                   ▼
                           ┌────────────────┐
                           │    Database    │
                           │   (SQLite)     │
                           │ hydro_logic.db │
                           └────────────────┘
```

---

## Security Checklist

- [ ] Change JWT_SECRET in .env to a strong random string
- [ ] Enable HTTPS with Let's Encrypt
- [ ] Restrict SSH access to your IP only
- [ ] Set up firewall (UFW)
- [ ] Enable automatic security updates
- [ ] Set up regular backups

### Quick Security Hardening

```bash
# Enable UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Enable auto updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

---

## Scaling (Future)

For production scaling:

1. **Database:** Switch from SQLite to PostgreSQL
   ```bash
   # In .env
   DATABASE_URL=postgresql://user:pass@host/db
   ```

2. **Load Balancing:** Use AWS ALB

3. **Caching:** Add Redis for session storage

4. **CDN:** CloudFront for static assets

---

## Support

If you encounter issues:
1. Check the logs first
2. Verify all ports are open in Security Group
3. Ensure .env file has correct values
4. Restart services after any changes

---

**Happy Deploying! 🌊**
