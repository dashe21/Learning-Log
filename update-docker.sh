#!/bin/bash

# Docker Image Update Script for Learning Log

set -e

echo "🐳 Learning Log - Docker Image Update"
echo "===================================="

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Detect which compose file is being used
COMPOSE_FILE=""
if [ -f "docker-compose.override.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
    print_info "Using docker-compose.yml (PostgreSQL setup)"
elif docker compose ps -q --filter "name=.*learning-log.*" | grep -q .; then
    if docker compose -f docker-compose.sqlite.yml ps -q 2>/dev/null | grep -q .; then
        COMPOSE_FILE="docker-compose.sqlite.yml"
        print_info "Detected SQLite deployment"
    else
        COMPOSE_FILE="docker-compose.yml"
        print_info "Detected PostgreSQL deployment"
    fi
else
    echo "Which deployment are you updating?"
    echo "1) PostgreSQL (docker-compose.yml)"
    echo "2) SQLite (docker-compose.sqlite.yml)"
    read -p "Enter choice (1 or 2): " choice
    
    case $choice in
        1) COMPOSE_FILE="docker-compose.yml" ;;
        2) COMPOSE_FILE="docker-compose.sqlite.yml" ;;
        *) print_error "Invalid choice"; exit 1 ;;
    esac
fi

print_info "Using compose file: $COMPOSE_FILE"

# Ask about data backup
echo ""
print_warning "Update Process Options:"
echo "1) Quick Update (rebuild image, keep data)"
echo "2) Full Update (rebuild image, update dependencies)"
echo "3) Clean Update (rebuild everything, keep data)"
echo "4) Fresh Start (rebuild everything, REMOVES all data)"
echo ""
read -p "Choose update type (1-4): " update_type

# Backup reminder
if [ "$update_type" != "4" ]; then
    print_warning "Backup reminder:"
    echo "For PostgreSQL: docker compose exec db pg_dump -U postgres learning_log > backup_$(date +%Y%m%d_%H%M%S).sql"
    echo "For SQLite: cp instance/learning_log.db backup_$(date +%Y%m%d_%H%M%S).db"
    echo ""
    read -p "Have you backed up your data? (y/N): " backup_confirm
    
    if [[ ! $backup_confirm =~ ^[Yy]$ ]]; then
        print_warning "Consider backing up your data first"
        read -p "Continue anyway? (y/N): " continue_anyway
        if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
            echo "Update cancelled"
            exit 0
        fi
    fi
fi

print_info "Starting update process..."

case $update_type in
    1)
        print_info "Quick Update: Rebuilding application image only"
        docker compose -f $COMPOSE_FILE build --no-cache web
        docker compose -f $COMPOSE_FILE up -d
        ;;
    2)
        print_info "Full Update: Rebuilding with latest dependencies"
        # Update base image and rebuild
        docker compose -f $COMPOSE_FILE pull
        docker compose -f $COMPOSE_FILE build --no-cache --pull web
        docker compose -f $COMPOSE_FILE up -d
        ;;
    3)
        print_info "Clean Update: Rebuilding everything (keeping data)"
        docker compose -f $COMPOSE_FILE down
        docker compose -f $COMPOSE_FILE build --no-cache --pull
        docker compose -f $COMPOSE_FILE up -d
        ;;
    4)
        print_error "Fresh Start: This will REMOVE ALL DATA"
        read -p "Are you absolutely sure? Type 'DELETE' to confirm: " confirm_delete
        if [ "$confirm_delete" = "DELETE" ]; then
            docker compose -f $COMPOSE_FILE down -v
            docker compose -f $COMPOSE_FILE build --no-cache --pull
            docker compose -f $COMPOSE_FILE up -d
            print_warning "All data has been removed"
        else
            print_info "Fresh start cancelled"
            exit 0
        fi
        ;;
esac

print_info "Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker compose -f $COMPOSE_FILE ps | grep -q "Up"; then
    print_status "Update completed successfully!"
    
    echo ""
    print_info "Service Status:"
    docker compose -f $COMPOSE_FILE ps
    
    echo ""
    print_info "Application URL: http://localhost:5000"
    print_info "View logs: docker compose -f $COMPOSE_FILE logs -f"
    print_info "Check status: docker compose -f $COMPOSE_FILE ps"
    
    # Test if application is responding
    sleep 5
    if curl -s http://localhost:5000 > /dev/null; then
        print_status "Application is responding! 🎉"
    else
        print_warning "Application may still be starting up..."
        print_info "Check logs: docker compose -f $COMPOSE_FILE logs web"
    fi
    
else
    print_error "Some services failed to start"
    print_info "Check logs: docker compose -f $COMPOSE_FILE logs"
    docker compose -f $COMPOSE_FILE ps
    exit 1
fi

echo ""
print_status "Docker image update complete! 🚀"