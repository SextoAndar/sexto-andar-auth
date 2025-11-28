#!/bin/bash
# Test runner script for sexto-andar-auth

set -e

echo "========================================="
echo "  Running Tests for Auth Service"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if test database exists
echo "📋 Checking test database..."
DB_EXISTS=$(docker exec sexto-andar-postgres psql -U sexto_andar_user -lqt | cut -d \| -f 1 | grep -w sexto_andar_test_db | wc -l)

if [ "$DB_EXISTS" -eq 0 ]; then
    echo "📦 Creating test database..."
    docker exec sexto-andar-postgres psql -U sexto_andar_user -c "CREATE DATABASE sexto_andar_test_db;"
    echo -e "${GREEN}✅ Test database created${NC}"
else
    echo -e "${GREEN}✅ Test database already exists${NC}"
fi
echo ""

# Install test dependencies if needed
echo "📦 Installing test dependencies..."
./venv/bin/python -m pip install -q pytest pytest-asyncio pytest-cov httpx
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Run tests
echo "🧪 Running tests..."
echo ""

if ./venv/bin/python -m pytest "$@"; then
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}  ✅ All tests passed!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}  ❌ Some tests failed${NC}"
    echo -e "${RED}=========================================${NC}"
    exit 1
fi
