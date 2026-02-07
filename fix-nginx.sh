#!/bin/bash
#
# Fix Nginx 500 Error - Quick Fix Script
# Run this on your EC2 instance: sudo ./fix-nginx.sh
#

set -e

PUBLIC_IP="51.21.128.226"
APP_NAME="hydro-logic"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Fixing Nginx configuration..."

# Update Nginx config to proxy root to backend
cat > /etc/nginx/sites-available/${APP_NAME} << 'EOF'
server {
    listen 80;
    server_name 51.21.128.226;

    # Landing page - proxy to backend
    location = / {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # React App - serve from dist folder
    location /app {
        alias /opt/hydro-logic/frontend/dist;
        index index.html;
        try_files $uri $uri/ /app/index.html;
    }

    # Static assets for React app
    location /assets {
        alias /opt/hydro-logic/frontend/dist/assets;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
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
}
EOF

# Copy frontend dist to /opt/hydro-logic if not exists
if [ -d "${SCRIPT_DIR}/frontend/dist" ]; then
    mkdir -p /opt/hydro-logic/frontend
    cp -r ${SCRIPT_DIR}/frontend/dist /opt/hydro-logic/frontend/
    chown -R www-data:www-data /opt/hydro-logic
    echo "✓ Frontend files copied to /opt/hydro-logic"
fi

# Test and reload nginx
nginx -t && systemctl reload nginx

echo ""
echo "✅ Nginx fixed!"
echo ""
echo "Try accessing:"
echo "  🌐 Landing Page:  http://${PUBLIC_IP}"
echo "  📱 React App:     http://${PUBLIC_IP}/app"
echo "  📚 API Docs:      http://${PUBLIC_IP}/docs"
echo ""
