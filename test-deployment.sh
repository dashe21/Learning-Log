#!/bin/bash

# Test deployment script for Learning Log

echo "🧪 Testing Learning Log Docker Deployment"
echo "========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }

# Test if containers are running
echo "Testing container status..."
if docker compose ps | grep -q "Up"; then
    print_success "Containers are running"
else
    print_error "Containers are not running"
    exit 1
fi

# Test web application response
echo "Testing web application..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000)
if [ "$response" = "200" ]; then
    print_success "Web application is responding (HTTP $response)"
else
    print_error "Web application not responding (HTTP $response)"
fi

# Test database connection (for PostgreSQL)
if docker compose ps | grep -q "db.*Up"; then
    echo "Testing database connection..."
    if docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        print_success "Database is ready"
    else
        print_error "Database connection failed"
    fi
fi

# Test application pages
echo "Testing application pages..."
pages=("/" "/auth/login" "/auth/register")
for page in "${pages[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000$page)
    if [ "$response" = "200" ]; then
        print_success "Page $page: HTTP $response"
    else
        print_warning "Page $page: HTTP $response"
    fi
done

echo ""
print_success "Deployment test completed!"
echo ""
echo "🌐 Access your application at: http://localhost:5000"
echo "📊 Monitor with: docker compose logs -f"