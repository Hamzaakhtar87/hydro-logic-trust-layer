#!/bin/bash
#
# Complete Nginx Fix - Handles Backend Landing + React SPA
# Run on EC2: sudo ./fix-nginx-complete.sh
#

set -e

PUBLIC_IP="51.21.128.226"
APP_NAME="hydro-logic"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Fixing Nginx configuration (complete fix)..."

# Check if frontend dist exists
if [ ! -d "${SCRIPT_DIR}/frontend/dist" ]; then
    echo "❌ Frontend dist folder not found!"
    echo "   Building frontend..."
    cd ${SCRIPT_DIR}/frontend
    npm install
    npm run build
    cd ${SCRIPT_DIR}
fi

# Create nginx config
cat > /etc/nginx/sites-available/${APP_NAME} << NGINXEOF
server {
    listen 80;
    server_name ${PUBLIC_IP};

    # Frontend React App - for all frontend routes
    # React routes: /login, /signup, /dashboard, /shield, /finops, /compliance, /settings
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
        root ${SCRIPT_DIR}/frontend/dist;
        expires 30d;
        add_header Cache-Control "public, immutable";
        try_files \$uri =404;
    }
}
NGINXEOF

# Set correct permissions
chown -R www-data:www-data ${SCRIPT_DIR}/frontend/dist 2>/dev/null || true
chmod -R 755 ${SCRIPT_DIR}/frontend/dist 2>/dev/null || true

# Test and reload nginx
nginx -t
systemctl reload nginx

echo ""
echo "✅ Nginx configuration fixed!"
echo ""
echo "Frontend Routes (React SPA):"
echo "  📱 http://${PUBLIC_IP}/              → Dashboard (root)"
echo "  🔐 http://${PUBLIC_IP}/login         → Login page"
echo "  ✏️  http://${PUBLIC_IP}/signup        → Signup page"
echo "  📊 http://${PUBLIC_IP}/dashboard     → Dashboard"
echo "  🛡️  http://${PUBLIC_IP}/shield        → Shield"
echo "  💰 http://${PUBLIC_IP}/finops        → FinOps"
echo "  📋 http://${PUBLIC_IP}/compliance    → Compliance"
echo "  ⚙️  http://${PUBLIC_IP}/settings      → Settings"
echo ""
echo "Backend API:"
echo "  🔌 http://${PUBLIC_IP}/api/          → API endpoints"
echo "  📚 http://${PUBLIC_IP}/docs          → Swagger docs"
echo "  ❤️  http://${PUBLIC_IP}/health        → Health check"
echo ""
