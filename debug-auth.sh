#!/bin/bash
#
# Debug Auth API - Test signup and login endpoints
#

echo "🔍 Testing Hydro-Logic Auth API on 51.21.128.226"
echo ""

BASE_URL="http://51.21.128.226"

# Test 1: Health check
echo "=== Test 1: Health Check ==="
curl -s "${BASE_URL}/health" | python3 -m json.tool 2>/dev/null || curl -s "${BASE_URL}/health"
echo ""
echo ""

# Test 2: Signup
echo "=== Test 2: Signup ==="
SIGNUP_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "debug@test.com", "password": "Test1234!"}')

echo "Response: $SIGNUP_RESPONSE"
echo ""

# Extract access token
ACCESS_TOKEN=$(echo "$SIGNUP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', 'FAILED'))" 2>/dev/null)

if [ "$ACCESS_TOKEN" != "FAILED" ] && [ -n "$ACCESS_TOKEN" ]; then
    echo "✅ Signup successful! Got access token"
    echo ""
    
    # Test 3: Protected endpoint with token
    echo "=== Test 3: Get User Profile (Protected) ==="
    curl -s "${BASE_URL}/api/auth/me" \
      -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool 2>/dev/null || echo "Failed to get profile"
    echo ""
else
    echo "❌ Signup failed or returned no token"
    echo ""
    
    # Try login instead (user might already exist)
    echo "=== Trying Login Instead ==="
    LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/login" \
      -H "Content-Type: application/json" \
      -d '{"email": "debug@test.com", "password": "Test1234!"}')
    
    echo "Response: $LOGIN_RESPONSE"
    
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', 'FAILED'))" 2>/dev/null)
    
    if [ "$ACCESS_TOKEN" != "FAILED" ] && [ -n "$ACCESS_TOKEN" ]; then
        echo "✅ Login successful!"
        echo ""
        
        echo "=== Test 3: Get User Profile (Protected) ==="
        curl -s "${BASE_URL}/api/auth/me" \
          -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool 2>/dev/null
    else
        echo "❌ Login also failed"
    fi
fi

echo ""
echo "=== Test 4: Shield Stats (Protected) ==="
if [ "$ACCESS_TOKEN" != "FAILED" ] && [ -n "$ACCESS_TOKEN" ]; then
    curl -s "${BASE_URL}/api/shield/stats" \
      -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool 2>/dev/null || echo "Shield stats failed"
else
    echo "Skipped - no token"
fi

echo ""
echo "=== Test 5: FinOps Savings (Protected) ==="
if [ "$ACCESS_TOKEN" != "FAILED" ] && [ -n "$ACCESS_TOKEN" ]; then
    curl -s "${BASE_URL}/api/finops/savings" \
      -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool 2>/dev/null || echo "FinOps failed"
else
    echo "Skipped - no token"
fi

echo ""
echo "=== Done ==="
