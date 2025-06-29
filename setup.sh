#!/bin/bash

# IT Asset Manager - Local Setup Script
# Author: Deepak Nemade

echo "🏢 IT Asset Manager - Local Setup"
echo "================================="

# Function to print colored output
print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.7+ first."
    echo ""
    echo "Installation instructions:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo "  Windows: Download from https://python.org"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python $python_version detected"

# Check if pip is available
if ! python3 -m pip --version &> /dev/null; then
    print_error "pip is not available. Please install pip first."
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    exit 1
fi

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    print_warning "Existing virtual environment found. Removing it..."
    rm -rf venv
fi

# Create virtual environment
print_status "Creating virtual environment..."
if ! python3 -m venv venv; then
    print_error "Failed to create virtual environment."
    echo "Try installing python3-venv: sudo apt install python3-venv"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing requirements..."
if ! pip install -r requirements.txt; then
    print_error "Failed to install requirements."
    echo "Check if requirements.txt exists and contains valid packages."
    exit 1
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p instance logs uploads backups

# Set proper permissions
chmod 755 instance logs uploads backups

print_success "Setup completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Start the application:"
echo "     python app.py"
echo ""
echo "  3. Open your browser and visit:"
echo "     http://localhost:5000"
echo ""
echo "  4. Login with default credentials:"
echo "     Username: admin"
echo "     Password: admin123"
echo ""
echo "📊 Optional - Add sample data:"
echo "  python add_sample_data.py"
echo ""
echo "🔧 Troubleshooting:"
echo "  - If port 5000 is busy: sudo lsof -i :5000"
echo "  - Check logs in: logs/ directory"
echo "  - Database file: instance/it_assets.db"
echo ""
print_warning "IMPORTANT: Change the default admin password after first login!"
