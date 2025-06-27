#!/bin/bash

echo "🚀 Setting up IT Asset Manager..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

# Create templates directory if it doesn't exist
mkdir -p templates

echo "✅ Setup complete!"
echo ""
echo "🎯 To start the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the application: python app.py"
echo "3. Open browser and go to: http://localhost:5000"
echo "4. Login with: admin / admin123"
echo ""
echo "📊 Features available:"
echo "   • IT Asset Management (laptops, desktops, mobiles, tablets)"
echo "   • User Access Management for applications"
echo "   • GitHub Access Tracking"
echo "   • Data Export (CSV format)"
echo "   • Filtering and Search capabilities"
echo ""
echo "🔒 Security: Change default admin password after first login!"
