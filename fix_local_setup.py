#!/usr/bin/env python3
"""
Quick fix script for common local installation issues.
Run this if you're having problems with the local Python setup.
"""

import os
import sys
import subprocess
import shutil

def run_command(command, description):
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def fix_permissions():
    """Fix file and directory permissions."""
    print("\n📁 Fixing permissions...")
    
    # Make scripts executable
    scripts = ['setup.sh', 'docker-start.sh', 'backup.sh']
    for script in scripts:
        if os.path.exists(script):
            os.chmod(script, 0o755)
            print(f"✅ Made {script} executable")
    
    # Create directories with proper permissions
    directories = ['instance', 'logs', 'uploads', 'backups']
    for directory in directories:
        os.makedirs(directory, mode=0o755, exist_ok=True)
        print(f"✅ Created/fixed {directory}/ directory")

def fix_virtual_environment():
    """Recreate virtual environment."""
    print("\n🐍 Fixing virtual environment...")
    
    # Remove existing venv if it exists
    if os.path.exists('venv'):
        print("🗑️ Removing existing virtual environment...")
        shutil.rmtree('venv')
    
    # Create new virtual environment
    if run_command('python3 -m venv venv', 'Creating virtual environment'):
        return True
    else:
        # Try alternative method
        return run_command('virtualenv venv', 'Creating virtual environment (alternative)')

def fix_dependencies():
    """Install dependencies with error handling."""
    print("\n📦 Fixing dependencies...")
    
    # Activate virtual environment and install packages
    commands = [
        'source venv/bin/activate && pip install --upgrade pip',
        'source venv/bin/activate && pip install --upgrade setuptools wheel',
        'source venv/bin/activate && pip install -r requirements.txt'
    ]
    
    for command in commands:
        if not run_command(command, f"Running: {command.split('&&')[-1].strip()}"):
            # Try installing packages individually
            print("🔄 Trying individual package installation...")
            individual_packages = [
                'Flask==2.3.3',
                'Flask-SQLAlchemy==3.0.5',
                'Flask-Login==0.6.3',
                'Werkzeug==2.3.7'
            ]
            
            for package in individual_packages:
                run_command(f'source venv/bin/activate && pip install {package}', f'Installing {package}')

def fix_database():
    """Fix database issues."""
    print("\n🗄️ Fixing database...")
    
    # Remove existing database if corrupted
    db_file = 'instance/it_assets.db'
    if os.path.exists(db_file):
        print("🗑️ Removing existing database file...")
        os.remove(db_file)
    
    # Create fresh database
    create_db_script = '''
from app import app, db
with app.app_context():
    db.create_all()
    print("Database created successfully!")
'''
    
    with open('temp_create_db.py', 'w') as f:
        f.write(create_db_script)
    
    success = run_command('source venv/bin/activate && python temp_create_db.py', 'Creating database')
    
    # Clean up temporary file
    if os.path.exists('temp_create_db.py'):
        os.remove('temp_create_db.py')
    
    return success

def check_port():
    """Check if port 5000 is available."""
    print("\n🔌 Checking port availability...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("⚠️ Port 5000 is in use. You may need to:")
            print("   1. Kill the process: sudo lsof -i :5000")
            print("   2. Use a different port")
            return False
        else:
            print("✅ Port 5000 is available")
            return True
    except Exception as e:
        print(f"❌ Error checking port: {e}")
        return False

def main():
    """Run all fixes."""
    print("🔧 IT Asset Manager - Local Setup Fix")
    print("=" * 50)
    
    fixes = [
        ("File Permissions", fix_permissions),
        ("Virtual Environment", fix_virtual_environment),
        ("Dependencies", fix_dependencies),
        ("Database", fix_database),
        ("Port Check", check_port)
    ]
    
    results = []
    for name, fix_func in fixes:
        try:
            result = fix_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} fix failed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Fix Summary:")
    
    all_good = True
    for name, result in results:
        status = "✅ FIXED" if result else "❌ FAILED"
        print(f"   {name}: {status}")
        if not result:
            all_good = False
    
    if all_good:
        print("\n🎉 All fixes applied successfully!")
        print("\n🚀 Try starting the application now:")
        print("   source venv/bin/activate")
        print("   python app.py")
        print("\n🌐 Then visit: http://localhost:5000")
    else:
        print("\n⚠️ Some fixes failed. Please check the errors above.")
        print("\n📖 For more help, see: LOCAL_INSTALLATION_GUIDE.md")
        print("🐛 Or create an issue: https://github.com/DeepDN/it-asset-manager/issues")

if __name__ == "__main__":
    main()
