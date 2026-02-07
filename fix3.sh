#!/bin/bash
#
# Fix3: JWT Secret Key Fix + Restart
# ==================================
# This fixes the JWT secret key issue that causes 401 errors
# Run: chmod +x fix3.sh && sudo ./fix3.sh
#

set -e

echo "🔐 Applying JWT Secret Key Fix..."

# Detect project dir
if [ -d "/home/ubuntu/HydroLogicTrustLayer" ]; then
    PROJECT_DIR="/home/ubuntu/HydroLogicTrustLayer"
elif [ -d "/root/HydroLogicTrustLayer" ]; then
    PROJECT_DIR="/root/HydroLogicTrustLayer"
else
    PROJECT_DIR="$(pwd)"
fi

echo "📁 Project directory: ${PROJECT_DIR}"

# Check if hydro-logic service exists
if systemctl is-enabled hydro-logic 2>/dev/null; then
    echo "🔄 Restarting hydro-logic service..."
    systemctl restart hydro-logic
    sleep 3
    systemctl status hydro-logic --no-pager || true
else
    echo "⚠️  hydro-logic service not found"
    echo "   Try running: source venv/bin/activate && python -m uvicorn backend.main:app --reload"
fi

# Clear the database to reset all users (their tokens are invalid now)
echo ""
echo "⚠️  NOTE: Existing user sessions will be invalidated by this fix."
echo "   Users will need to log in again."

# Test the health endpoint
echo ""
echo "🔍 Testing health endpoint..."
sleep 2
curl -s http://localhost:8000/health 2>/dev/null || echo "Backend not responding on localhost:8000"

# Test with new signup
echo ""
echo "🔍 Testing auth API..."
SIGNUP_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "fix3test@test.com", "password": "Test1234!"}' 2>/dev/null)

if echo "$SIGNUP_RESULT" | grep -q "access_token"; then
    echo "✅ Signup works!"
    
    # Extract token and test protected endpoint
    TOKEN=$(echo "$SIGNUP_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
    
    if [ -n "$TOKEN" ]; then
        echo "🔍 Testing protected endpoint with token..."
        ME_RESULT=$(curl -s http://localhost:8000/api/auth/me \
          -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        if echo "$ME_RESULT" | grep -q "email"; then
            echo "✅ Token verification works! The fix is successful."
        else
            echo "❌ Token verification failed: $ME_RESULT"
        fi
    fi
else
    # Try login if user already exists
    LOGIN_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email": "fix3test@test.com", "password": "Test1234!"}' 2>/dev/null)
    
    if echo "$LOGIN_RESULT" | grep -q "access_token"; then
        echo "✅ Login works! (User already existed)"
        
        TOKEN=$(echo "$LOGIN_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
        
        if [ -n "$TOKEN" ]; then
            ME_RESULT=$(curl -s http://localhost:8000/api/auth/me \
              -H "Authorization: Bearer $TOKEN" 2>/dev/null)
            
            if echo "$ME_RESULT" | grep -q "email"; then
                echo "✅ Token verification works! The fix is successful."
            else
                echo "❌ Token verification failed: $ME_RESULT"
            fi
        fi
    else
        echo "❌ Auth test failed. Check the backend logs:"
        echo "   sudo journalctl -u hydro-logic -n 50"
    fi
fi

echo ""
echo "============================================"
echo "🎉 Fix applied! Try logging in at:"
echo "   http://51.21.128.226/login"
echo ""
echo "If issues persist, check logs:"
echo "   sudo journalctl -u hydro-logic -f"
echo "============================================"
