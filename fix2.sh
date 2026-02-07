#!/bin/bash
#
# Hydro-Logic - Complete Fix Script (Handles Permissions)
# ========================================================
# Run: chmod +x fix2.sh && sudo ./fix2.sh
#

set -e

echo "🔧 Fixing Nginx configuration with proper permissions..."

# Detect the project directory
if [ -d "/home/ubuntu/HydroLogicTrustLayer" ]; then
    PROJECT_DIR="/home/ubuntu/HydroLogicTrustLayer"
    USER_NAME="ubuntu"
elif [ -d "/root/HydroLogicTrustLayer" ]; then
    PROJECT_DIR="/root/HydroLogicTrustLayer"
    USER_NAME="root"
else
    PROJECT_DIR="$(pwd)"
    USER_NAME="$(whoami)"
fi

DIST_DIR="${PROJECT_DIR}/frontend/dist"

echo "📁 Project directory: ${PROJECT_DIR}"
echo "📁 Dist directory: ${DIST_DIR}"

# Check if frontend dist exists
if [ ! -f "${DIST_DIR}/index.html" ]; then
    echo "❌ Error: ${DIST_DIR}/index.html not found!"
    echo ""
    echo "Building frontend now..."
    cd ${PROJECT_DIR}/frontend
    
    # Install deps if needed
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    npm run build
    cd ${PROJECT_DIR}
fi

# Verify dist exists now
if [ ! -f "${DIST_DIR}/index.html" ]; then
    echo "❌ Frontend build failed! Please build manually:"
    echo "   cd ${PROJECT_DIR}/frontend && npm run build"
    exit 1
fi

echo "✅ Frontend dist found"

# Fix permissions - THIS IS THE KEY!
echo "🔐 Fixing file permissions..."

# Make the entire path readable by nginx (www-data user)
chmod 755 /home 2>/dev/null || true
chmod 755 /home/ubuntu 2>/dev/null || true
chmod 755 ${PROJECT_DIR} 2>/dev/null || true
chmod 755 ${PROJECT_DIR}/frontend 2>/dev/null || true
chmod -R 755 ${DIST_DIR}

# Also make sure www-data can traverse the directories
setfacl -m u:www-data:rx /home 2>/dev/null || true
setfacl -m u:www-data:rx /home/ubuntu 2>/dev/null || true
setfacl -R -m u:www-data:rx ${PROJECT_DIR} 2>/dev/null || true

echo "✅ Permissions fixed"

# Create nginx config
echo "📝 Creating nginx configuration..."

cat > /etc/nginx/sites-available/hydro-logic << EOF
server {
    listen 80;
    server_name 51.21.128.226;

    # React SPA - serve for all frontend routes
    location / {
        root ${DIST_DIR};
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
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/hydro-logic /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

# Test nginx config
echo "🔍 Testing nginx configuration..."
nginx -t

if [ $? -ne 0 ]; then
    echo "❌ Nginx config test failed!"
    exit 1
fi

# Reload nginx  
echo "🔄 Reloading nginx..."
systemctl reload nginx

# Verify nginx can read the files
echo "🔍 Verifying nginx can access files..."
sudo -u www-data test -r ${DIST_DIR}/index.html && echo "✅ www-data can read index.html" || echo "⚠️  www-data cannot read index.html"

echo ""
echo "============================================"
echo "✅ DONE! Testing the site..."
echo "============================================"
echo ""

# Test the endpoints
sleep 2

echo "Testing /health..."
curl -s http://localhost/health | head -c 100
echo ""
echo ""

echo "Testing / (frontend)..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$RESPONSE" = "200" ]; then
    echo "✅ Frontend returns 200 OK!"
else
    echo "❌ Frontend returns HTTP $RESPONSE"
    echo ""
    echo "Checking nginx error log:"
    tail -5 /var/log/nginx/error.log
fi

echo ""
echo "============================================"
echo "🌐 Your app should be at: http://51.21.128.226"
echo "============================================"
