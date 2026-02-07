#!/bin/bash
#
# Hydro-Logic - Quick Nginx Fix Script
# =====================================
# Just upload this to EC2 and run: chmod +x fix.sh && sudo ./fix.sh
#

set -e

echo "🔧 Fixing Nginx configuration..."

# Detect the project directory
if [ -d "/home/ubuntu/HydroLogicTrustLayer" ]; then
    PROJECT_DIR="/home/ubuntu/HydroLogicTrustLayer"
elif [ -d "/root/HydroLogicTrustLayer" ]; then
    PROJECT_DIR="/root/HydroLogicTrustLayer"
else
    PROJECT_DIR="$(pwd)"
fi

echo "📁 Project directory: ${PROJECT_DIR}"

# Check if frontend dist exists
if [ ! -f "${PROJECT_DIR}/frontend/dist/index.html" ]; then
    echo "❌ Error: frontend/dist/index.html not found!"
    echo "   Make sure the frontend is built. Run: cd frontend && npm run build"
    exit 1
fi

# Create nginx config
cat > /etc/nginx/sites-available/hydro-logic << EOF
server {
    listen 80;
    server_name 51.21.128.226;

    # React SPA - serve for all frontend routes
    # try_files ensures React Router handles /login, /dashboard, etc.
    location / {
        root ${PROJECT_DIR}/frontend/dist;
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
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket connections
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }

    # API Documentation
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
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        root ${PROJECT_DIR}/frontend/dist;
        expires 30d;
        add_header Cache-Control "public, immutable";
        try_files \$uri =404;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/hydro-logic /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

# Set correct permissions
chmod -R 755 ${PROJECT_DIR}/frontend/dist
chown -R www-data:www-data ${PROJECT_DIR}/frontend/dist 2>/dev/null || true

# Test nginx config
echo "🔍 Testing nginx configuration..."
nginx -t

# Reload nginx
echo "🔄 Reloading nginx..."
systemctl reload nginx

echo ""
echo "✅ SUCCESS! Nginx is now configured correctly."
echo ""
echo "🌐 Your app is available at:"
echo ""
echo "   http://51.21.128.226/            → React App (Home/Dashboard)"
echo "   http://51.21.128.226/login       → Login Page"
echo "   http://51.21.128.226/signup      → Signup Page"  
echo "   http://51.21.128.226/dashboard   → Dashboard"
echo "   http://51.21.128.226/shield      → Shield"
echo "   http://51.21.128.226/finops      → FinOps"
echo "   http://51.21.128.226/compliance  → Compliance"
echo "   http://51.21.128.226/settings    → Settings"
echo ""
echo "   http://51.21.128.226/api/        → Backend API"
echo "   http://51.21.128.226/docs        → Swagger Docs"
echo "   http://51.21.128.226/health      → Health Check"
echo ""
