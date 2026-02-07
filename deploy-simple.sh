#!/bin/bash
#
# Hydro-Logic Trust Layer - Simple Deployment Script
# ====================================================
# Use this to deploy on a fresh EC2 instance.
#
# Prerequisites:
# 1. Upload this entire project directory to your EC2
# 2. SSH into your EC2 instance
# 3. Run: chmod +x deploy-simple.sh && sudo ./deploy-simple.sh
#

set -e

# ============ CONFIGURATION ============
PUBLIC_IP="51.21.128.226"
APP_NAME="hydro-logic"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "========================================================"
echo "🌊 HYDRO-LOGIC - SIMPLE DEPLOYMENT"
echo "========================================================"
echo "Public IP: ${PUBLIC_IP}"
echo ""

# ============ STEP 1: Install System Dependencies ============
echo -e "${YELLOW}[1/6]${NC} Installing system dependencies..."

apt-get update -y
apt-get install -y python3-pip python3-venv nodejs npm nginx

echo -e "${GREEN}✓${NC} Dependencies installed"

# ============ STEP 2: Setup Backend ============
echo -e "${YELLOW}[2/6]${NC} Setting up Python backend..."

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

echo -e "${GREEN}✓${NC} Backend ready"

# ============ STEP 3: Build Frontend ============
echo -e "${YELLOW}[3/6]${NC} Building frontend..."

cd frontend

# Create production env
cat > .env.production << EOF
VITE_API_URL=http://${PUBLIC_IP}
VITE_WS_URL=ws://${PUBLIC_IP}
EOF

npm install
npm run build

cd ..

echo -e "${GREEN}✓${NC} Frontend built"

# ============ STEP 4: Configure Nginx ============
echo -e "${YELLOW}[4/6]${NC} Configuring Nginx..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cat > /etc/nginx/sites-available/${APP_NAME} << NGINXEOF
server {
    listen 80;
    server_name ${PUBLIC_IP};

    # React SPA - serve for all frontend routes
    # try_files ensures React Router handles /login, /dashboard, etc.
    location / {
        root ${SCRIPT_DIR}/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }

    # API Docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
    }
    
    location /redoc {
        proxy_pass http://127.0.0.1:8000/redoc;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)\$ {
        root ${SCRIPT_DIR}/frontend/dist;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
NGINXEOF

# Set permissions on frontend dist
chmod -R 755 ${SCRIPT_DIR}/frontend/dist

# Enable site
ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl restart nginx

echo -e "${GREEN}✓${NC} Nginx configured"

# ============ STEP 5: Create Systemd Service ============
echo -e "${YELLOW}[5/6]${NC} Creating systemd service..."

cat > /etc/systemd/system/${APP_NAME}.service << EOF
[Unit]
Description=Hydro-Logic Trust Layer Backend
After=network.target

[Service]
User=root
WorkingDirectory=${SCRIPT_DIR}
Environment="PATH=${SCRIPT_DIR}/venv/bin"
ExecStart=${SCRIPT_DIR}/venv/bin/gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ${APP_NAME}
systemctl start ${APP_NAME}

echo -e "${GREEN}✓${NC} Service created and started"

# ============ STEP 6: Verify ============
echo -e "${YELLOW}[6/6]${NC} Verifying deployment..."

sleep 3

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓${NC} Backend is running"
else
    echo "⚠ Backend may need a moment to start..."
fi

# Check nginx
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓${NC} Nginx is running"
fi

echo ""
echo "========================================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "========================================================"
echo ""
echo "Your application is live at:"
echo ""
echo "  🌐 Frontend:  http://${PUBLIC_IP}"
echo "  🔌 API:       http://${PUBLIC_IP}/api/"
echo "  📚 API Docs:  http://${PUBLIC_IP}/docs"
echo ""
echo "Useful commands:"
echo "  View logs:     sudo journalctl -u ${APP_NAME} -f"
echo "  Restart:       sudo systemctl restart ${APP_NAME}"
echo "  Status:        sudo systemctl status ${APP_NAME}"
echo ""
echo "========================================================"
