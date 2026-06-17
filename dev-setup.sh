#!/bin/bash

# IT Asset Manager - Development Setup Script
# Author: Deepak Nemade
# LinkedIn: https://www.linkedin.com/in/deepak-nemade/

set -e

echo "🚀 IT Asset Manager - Development Environment Setup"
echo "=================================================="

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
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating development directories..."
mkdir -p logs uploads backups instance

# Copy environment file
if [ ! -f .env ]; then
    print_status "Creating development environment file..."
    cp .env.dev .env
    print_success "Environment file created from .env.dev"
else
    print_warning "Environment file already exists. Skipping..."
fi

# Build development containers
print_status "Building development containers..."
docker-compose -f docker-compose.dev.yml build

# Start development environment
print_status "Starting development environment..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for application to be ready
print_status "Waiting for application to be ready..."
sleep 10

# Check if application is running
if curl -f http://localhost:5000/ > /dev/null 2>&1; then
    print_success "Application is running successfully!"
else
    print_warning "Application might still be starting up..."
fi

# Install development dependencies in virtual environment (optional)
if command -v python3 &> /dev/null; then
    print_status "Setting up local Python virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements-dev.txt
    print_success "Development dependencies installed in virtual environment"
fi

# Setup pre-commit hooks
if [ -f "venv/bin/pre-commit" ]; then
    print_status "Installing pre-commit hooks..."
    source venv/bin/activate
    pre-commit install
    print_success "Pre-commit hooks installed"
fi

echo ""
echo "🎉 Development Environment Setup Complete!"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo "  1. Access the application: http://localhost:5000"
echo "  2. Login with: admin / admin123"
echo "  3. Start developing!"
echo ""
echo "🔧 Development Commands:"
echo "  • View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "  • Stop: docker-compose -f docker-compose.dev.yml down"
echo "  • Restart: docker-compose -f docker-compose.dev.yml restart"
echo "  • Shell access: docker-compose -f docker-compose.dev.yml exec app bash"
echo ""
echo "🧪 Testing Commands:"
echo "  • Run tests: make test"
echo "  • Code quality: make lint"
echo "  • Security scan: make security-check"
echo ""
echo "📚 Documentation:"
echo "  • Contributing: CONTRIBUTING.md"
echo "  • Troubleshooting: docs/guides/TROUBLESHOOTING.md"
echo ""
print_success "Happy coding! 🚀"
