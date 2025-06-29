#!/bin/bash

# IT Asset Manager - Docker Startup Script
# Author: Deepak Nemade

set -e

echo "🏢 IT Asset Manager - Docker Deployment Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check for docker compose (new version) or docker-compose (old version)
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
        print_success "Docker and Docker Compose (new version) are installed"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
        print_success "Docker and Docker Compose (legacy version) are installed"
    else
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs uploads instance backups docker/nginx/ssl
    print_success "Directories created"
}

# Setup environment file
setup_environment() {
    if [ ! -f .env ]; then
        print_status "Creating environment file..."
        cp .env.example .env
        print_warning "Please edit .env file with your production settings"
    else
        print_success "Environment file already exists"
    fi
}

# Generate SSL certificates (self-signed for development)
generate_ssl() {
    if [ ! -f docker/nginx/ssl/cert.pem ]; then
        print_status "Generating self-signed SSL certificate..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout docker/nginx/ssl/key.pem \
            -out docker/nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=IT-Asset-Manager/CN=localhost" \
            2>/dev/null
        print_success "SSL certificate generated"
    else
        print_success "SSL certificate already exists"
    fi
}

# Start development environment
start_development() {
    print_status "Starting development environment..."
    $DOCKER_COMPOSE_CMD up --build -d
    
    # Wait for containers to be ready
    print_status "Waiting for containers to be ready..."
    sleep 10
    
    # Check if application is running
    if curl -f http://localhost:5000/ &>/dev/null; then
        print_success "Development environment started successfully!"
        echo ""
        echo "🎉 Application is running at:"
        echo "   📱 URL: http://localhost:5000"
        echo "   👤 Username: admin"
        echo "   🔑 Password: admin123"
        echo ""
        echo "📊 Useful commands:"
        echo "   View logs: $DOCKER_COMPOSE_CMD logs -f"
        echo "   Stop: $DOCKER_COMPOSE_CMD down"
        echo "   Add sample data: $DOCKER_COMPOSE_CMD exec app python add_sample_data.py"
    else
        print_error "Failed to start development environment"
        echo "Check logs with: $DOCKER_COMPOSE_CMD logs"
        exit 1
    fi
}

# Start production environment
start_production() {
    print_status "Starting production environment..."
    $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml up --build -d
    
    # Wait for containers to be ready
    print_status "Waiting for containers to be ready..."
    sleep 15
    
    # Check if application is running
    if curl -f http://localhost/ &>/dev/null; then
        print_success "Production environment started successfully!"
        echo ""
        echo "🎉 Application is running at:"
        echo "   🌐 HTTP: http://localhost"
        echo "   🔒 HTTPS: https://localhost (self-signed certificate)"
        echo "   🎯 Direct: http://localhost:8000"
        echo "   👤 Username: admin"
        echo "   🔑 Password: Check your .env file for ADMIN_PASSWORD"
        echo ""
        echo "📊 Useful commands:"
        echo "   View logs: $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml logs -f"
        echo "   Stop: $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml down"
        echo "   Add sample data: $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml exec app python add_sample_data.py"
    else
        print_error "Failed to start production environment"
        echo "Check logs with: $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml logs"
        exit 1
    fi
}

# Show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  dev, development    Start development environment (default)"
    echo "  prod, production    Start production environment"
    echo "  stop               Stop all containers"
    echo "  restart            Restart containers"
    echo "  logs               Show container logs"
    echo "  status             Show container status"
    echo "  clean              Clean up containers and images"
    echo "  help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Start development environment"
    echo "  $0 dev             # Start development environment"
    echo "  $0 prod            # Start production environment"
    echo "  $0 stop            # Stop all containers"
}

# Stop containers
stop_containers() {
    print_status "Stopping containers..."
    $DOCKER_COMPOSE_CMD down 2>/dev/null || true
    $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml down 2>/dev/null || true
    print_success "Containers stopped"
}

# Restart containers
restart_containers() {
    print_status "Restarting containers..."
    stop_containers
    sleep 2
    if [ "$1" = "prod" ] || [ "$1" = "production" ]; then
        start_production
    else
        start_development
    fi
}

# Show logs
show_logs() {
    if $DOCKER_COMPOSE_CMD ps | grep -q "it-asset-manager-prod"; then
        $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml logs -f
    else
        $DOCKER_COMPOSE_CMD logs -f
    fi
}

# Show status
show_status() {
    print_status "Container status:"
    $DOCKER_COMPOSE_CMD ps 2>/dev/null || true
    $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml ps 2>/dev/null || true
}

# Clean up
clean_up() {
    print_warning "This will remove all containers, images, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up..."
        $DOCKER_COMPOSE_CMD down -v --remove-orphans 2>/dev/null || true
        $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || true
        docker system prune -f
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Main script logic
main() {
    case "${1:-dev}" in
        "dev"|"development"|"")
            check_docker
            create_directories
            setup_environment
            generate_ssl
            start_development
            ;;
        "prod"|"production")
            check_docker
            create_directories
            setup_environment
            generate_ssl
            start_production
            ;;
        "stop")
            stop_containers
            ;;
        "restart")
            restart_containers "${2:-dev}"
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "clean")
            clean_up
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
