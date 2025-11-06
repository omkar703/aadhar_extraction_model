#!/bin/bash

echo "================================================"
echo "Testing Aadhaar Extraction API"
echo "================================================"

API_URL=${1:-http://localhost:8000}

echo ""
echo "Testing API at: $API_URL"
echo ""

# Test 1: Health Check
echo "[1/2] Testing health check endpoint..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" $API_URL/)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)
BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Health check passed"
    echo "Response: $BODY"
else
    echo "✗ Health check failed (HTTP $HTTP_CODE)"
    exit 1
fi

# Test 2: Check if /docs endpoint is accessible
echo ""
echo "[2/2] Testing documentation endpoint..."
DOCS_CODE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/docs)

if [ "$DOCS_CODE" = "200" ]; then
    echo "✓ Documentation endpoint accessible"
    echo "View docs at: $API_URL/docs"
else
    echo "✗ Documentation endpoint failed (HTTP $DOCS_CODE)"
fi

echo ""
echo "================================================"
echo "Basic API Tests Complete!"
echo "================================================"
echo ""
echo "To test image extraction, run:"
echo "  curl -X POST \"$API_URL/api/v1/extract/\" \\"
echo "    -F \"image=@/path/to/aadhaar.jpg\""
echo ""
