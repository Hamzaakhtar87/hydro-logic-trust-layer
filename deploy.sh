#!/bin/bash
#
# Hydro-Logic Trust Layer - AWS EC2 Deployment Script
# =====================================================
# This script automates the complete deployment process.
#
# Usage: chmod +x deploy.sh && sudo ./deploy.sh
#
# Requirements:
# - Ubuntu 22.04+ EC2 instance
# - At least 2GB RAM, 20GB disk
# - Security group with ports 22, 80, 443, 8000 open
#

set -e  # Exit on error

# ============ CONFIGURATION ============
PUBLIC_IP="51.21.128.226"
APP_DIR="/opt/hydro-logic"
BACKEND_PORT=8000
FRONTEND_PORT=3000
DOMAIN="${PUBLIC_IP}"  # Use IP directly, or set domain name

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============ PRE-FLIGHT CHECKS ============
echo ""
echo "========================================================"
echo "🌊 HYDRO-LOGIC TRUST LAYER - AWS EC2 DEPLOYMENT"
echo "========================================================"
echo ""
echo "Public IP: ${PUBLIC_IP}"
echo "App Directory: ${APP_DIR}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (sudo ./deploy.sh)"
    exit 1
fi

# Check for .env file with API key
if [ ! -f ".env" ]; then
    log_error ".env file not found! Create it with your GEMINI_API_KEY"
    echo ""
    echo "Create .env file:"
    echo "  cp .env.example .env"
    echo "  nano .env  # Add your GEMINI_API_KEY"
    exit 1
fi

# Verify API key is set
if ! grep -q "GEMINI_API_KEY=AIza" .env 2>/dev/null; then
    log_warning "GEMINI_API_KEY may not be set correctly in .env"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ============ STEP 1: SYSTEM UPDATE ============
log_info "Step 1/8: Updating system packages..."

apt-get update -y
apt-get upgrade -y
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nodejs \
    npm \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    wget \
    htop \
    supervisor

log_success "System packages installed"

# ============ STEP 2: CREATE APP DIRECTORY ============
log_info "Step 2/8: Setting up application directory..."

# Create app directory
mkdir -p ${APP_DIR}
mkdir -p ${APP_DIR}/logs

# Copy application files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r ${SCRIPT_DIR}/* ${APP_DIR}/
cp ${SCRIPT_DIR}/.env ${APP_DIR}/.env 2>/dev/null || true

# Set permissions
chown -R www-data:www-data ${APP_DIR}
chmod -R 755 ${APP_DIR}

log_success "Application files copied to ${APP_DIR}"

# ============ STEP 3: PYTHON BACKEND SETUP ============
log_info "Step 3/8: Setting up Python backend..."

cd ${APP_DIR}

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

log_success "Python backend configured"

# ============ STEP 4: FRONTEND BUILD ============
log_info "Step 4/8: Building frontend..."

cd ${APP_DIR}/frontend

# Install Node.js dependencies
npm install

# Update API URL for production
cat > .env.production << EOF
VITE_API_URL=http://${PUBLIC_IP}:${BACKEND_PORT}
VITE_WS_URL=ws://${PUBLIC_IP}:${BACKEND_PORT}
EOF

# Build for production
npm run build

log_success "Frontend built successfully"

# ============ STEP 5: CONFIGURE SUPERVISOR ============
log_info "Step 5/8: Configuring Supervisor for process management..."

# Backend service
cat > /etc/supervisor/conf.d/hydro-logic-backend.conf << EOF
[program:hydro-logic-backend]
command=${APP_DIR}/venv/bin/gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${BACKEND_PORT}
directory=${APP_DIR}
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=${APP_DIR}/logs/backend.log
stderr_logfile=${APP_DIR}/logs/backend-error.log
environment=PATH="${APP_DIR}/venv/bin:%(ENV_PATH)s"
EOF

# Reload supervisor
supervisorctl reread
supervisorctl update

log_success "Supervisor configured"

# ============ STEP 6: CONFIGURE NGINX ============
log_info "Step 6/8: Configuring Nginx reverse proxy..."

cat > /etc/nginx/sites-available/hydro-logic << EOF
# Hydro-Logic Trust Layer - Nginx Configuration

# Rate limiting
limit_req_zone \$binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} ${PUBLIC_IP};

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Frontend - serve static files
    location / {
        root ${APP_DIR}/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API - proxy to FastAPI
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:${BACKEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket for real-time updates
    location /ws/ {
        proxy_pass http://127.0.0.1:${BACKEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }

    # API Documentation
    location /docs {
        proxy_pass http://127.0.0.1:${BACKEND_PORT}/docs;
        proxy_set_header Host \$host;
    }

    location /redoc {
        proxy_pass http://127.0.0.1:${BACKEND_PORT}/redoc;
        proxy_set_header Host \$host;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:${BACKEND_PORT}/health;
        access_log off;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/hydro-logic /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload nginx
nginx -t
systemctl reload nginx

log_success "Nginx configured"

# ============ STEP 7: START SERVICES ============
log_info "Step 7/8: Starting services..."

# Start backend via supervisor
supervisorctl start hydro-logic-backend

# Enable nginx on boot
systemctl enable nginx

log_success "Services started"

# ============ STEP 8: VERIFY DEPLOYMENT ============
log_info "Step 8/8: Verifying deployment..."

sleep 5  # Wait for services to start

# Check backend health
if curl -s http://localhost:${BACKEND_PORT}/health > /dev/null; then
    log_success "Backend is running"
else
    log_warning "Backend may still be starting..."
fi

# Check nginx
if systemctl is-active --quiet nginx; then
    log_success "Nginx is running"
else
    log_error "Nginx failed to start"
fi

# ============ DEPLOYMENT COMPLETE ============
echo ""
echo "========================================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "========================================================"
echo ""
echo "Your Hydro-Logic Trust Layer is now live at:"
echo ""
echo "  🌐 Frontend:     http://${PUBLIC_IP}"
echo "  🔌 Backend API:  http://${PUBLIC_IP}/api/"
echo "  📚 API Docs:     http://${PUBLIC_IP}/docs"
echo ""
echo "Admin Commands:"
echo "  View logs:       sudo tail -f ${APP_DIR}/logs/backend.log"
echo "  Restart backend: sudo supervisorctl restart hydro-logic-backend"
echo "  Restart nginx:   sudo systemctl restart nginx"
echo "  Check status:    sudo supervisorctl status"
echo ""
echo "To enable HTTPS (recommended):"
echo "  sudo certbot --nginx -d your-domain.com"
echo ""
echo "========================================================"
echo ""
