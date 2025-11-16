#!/bin/bash

# Learning Log Docker Deployment Script

set -e

echo "🐳 Learning Log - Docker Deployment"
echo "===================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are available"

# Check for environment file
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from example..."
    cp .env.example .env
    print_info "Please edit .env file with your configuration before continuing."
    print_info "At minimum, change the SECRET_KEY value."
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Choose deployment type
echo ""
echo "Choose deployment type:"
echo "1) PostgreSQL (recommended for production)"
echo "2) SQLite (simpler, good for small deployments)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        COMPOSE_FILE="docker-compose.yml"
        print_info "Using PostgreSQL deployment"
        ;;
    2)
        COMPOSE_FILE="docker-compose.sqlite.yml"
        print_info "Using SQLite deployment"
        # Create instance directory for SQLite
        mkdir -p instance
        ;;
    *)
        print_error "Invalid choice. Exiting."
        exit 1
        ;;
esac

print_info "Building Docker images..."
docker compose -f $COMPOSE_FILE build

print_info "Starting services..."
docker compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
print_info "Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker compose -f $COMPOSE_FILE ps | grep -q "Up"; then
    print_status "Services are running!"
    echo ""
    print_info "🌐 Application URL: http://localhost:5000"
    echo ""
    print_info "Useful commands:"
    echo "  - View logs: docker compose -f $COMPOSE_FILE logs -f"
    echo "  - Stop services: docker compose -f $COMPOSE_FILE down"
    echo "  - Restart: docker compose -f $COMPOSE_FILE restart"
    echo "  - Update: docker compose -f $COMPOSE_FILE pull && docker compose -f $COMPOSE_FILE up -d"
    echo ""
    print_status "Deployment completed successfully! 🎉"
else
    print_error "Some services failed to start. Check logs with:"
    echo "docker compose -f $COMPOSE_FILE logs"
    exit 1
fi