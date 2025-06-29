#!/usr/bin/env python3
"""
Test script to verify IT Asset Manager setup.
Run this to check if everything is working correctly.
"""

import sys
import os

def test_python_version():
    """Test Python version compatibility."""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+")
        return False

def test_imports():
    """Test if all required packages can be imported."""
    print("\n📦 Testing package imports...")
    packages = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'SQLAlchemy'),
        ('flask_login', 'LoginManager'),
        ('werkzeug.security', 'generate_password_hash'),
    ]
    
    all_good = True
    for package, item in packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError as e:
            print(f"❌ {package} - MISSING ({e})")
            all_good = False
    
    return all_good

def test_directories():
    """Test if required directories exist."""
    print("\n📁 Testing directories...")
    directories = ['instance', 'logs', 'uploads', 'backups']
    
    all_good = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}/ - EXISTS")
        else:
            print(f"❌ {directory}/ - MISSING")
            all_good = False
    
    return all_good

def test_database():
    """Test database connection."""
    print("\n🗄️ Testing database...")
    try:
        from app import app, db
        with app.app_context():
            # Try to create tables
            db.create_all()
            print("✅ Database connection - OK")
            print("✅ Database tables created - OK")
            return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_app_startup():
    """Test if the app can start."""
    print("\n🚀 Testing app startup...")
    try:
        from app import app
        # Test if app can be created
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code in [200, 302]:  # 302 for redirect to login
                print("✅ App startup - OK")
                return True
            else:
                print(f"❌ App returned status code: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ App startup error: {e}")
        return False

def main():
    """Run all tests."""
    print("🏢 IT Asset Manager - Setup Test")
    print("=" * 40)
    
    tests = [
        test_python_version,
        test_imports,
        test_directories,
        test_database,
        test_app_startup
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📊 Test Summary:")
    
    if all(results):
        print("🎉 All tests passed! Your setup is working correctly.")
        print("\n🚀 You can now start the application with:")
        print("   python app.py")
        print("\n🌐 Then visit: http://localhost:5000")
        print("👤 Login: admin / admin123")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n🔧 Common solutions:")
        print("   1. Run: pip install -r requirements.txt")
        print("   2. Create directories: mkdir -p instance logs uploads backups")
        print("   3. Check Python version: python3 --version")
        
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
