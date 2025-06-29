#!/usr/bin/env python3
"""
Dashboard Diagnostic Script for IT Asset Manager
This script helps diagnose dashboard display issues.
"""

import os
import sys
from flask import Flask

def check_templates():
    """Check if all required templates exist."""
    print("🔍 Checking Templates...")
    
    required_templates = [
        'base.html',
        'dashboard.html',
        'login.html'
    ]
    
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        print("❌ Templates directory not found!")
        return False
    
    missing_templates = []
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            print(f"✅ {template} - Found")
        else:
            print(f"❌ {template} - Missing")
            missing_templates.append(template)
    
    if missing_templates:
        print(f"\n⚠️ Missing templates: {', '.join(missing_templates)}")
        return False
    
    return True

def check_database():
    """Check database connection and data."""
    print("\n🗄️ Checking Database...")
    
    try:
        # Import after ensuring we're in the right directory
        sys.path.insert(0, os.path.dirname(__file__))
        from app import app, db, Asset, ApplicationAccess, GitHubAccess
        
        with app.app_context():
            # Check if tables exist
            try:
                total_assets = Asset.query.count()
                total_app_access = ApplicationAccess.query.count()
                total_github_access = GitHubAccess.query.count()
                
                print(f"✅ Database connection - OK")
                print(f"✅ Assets table - {total_assets} records")
                print(f"✅ Application Access table - {total_app_access} records")
                print(f"✅ GitHub Access table - {total_github_access} records")
                
                return True
                
            except Exception as e:
                print(f"❌ Database query error: {e}")
                return False
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_static_files():
    """Check if static files are accessible."""
    print("\n📁 Checking Static Files...")
    
    # Check if we can access external CDN resources
    import urllib.request
    import urllib.error
    
    cdn_resources = [
        "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ]
    
    for resource in cdn_resources:
        try:
            urllib.request.urlopen(resource, timeout=5)
            print(f"✅ {resource.split('/')[-1]} - Accessible")
        except urllib.error.URLError:
            print(f"❌ {resource.split('/')[-1]} - Not accessible")
        except Exception as e:
            print(f"⚠️ {resource.split('/')[-1]} - Error: {e}")

def test_dashboard_route():
    """Test the dashboard route directly."""
    print("\n🌐 Testing Dashboard Route...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test without login (should redirect)
            response = client.get('/')
            print(f"✅ Dashboard route accessible - Status: {response.status_code}")
            
            if response.status_code == 302:
                print("✅ Redirect to login working (expected behavior)")
            elif response.status_code == 200:
                print("⚠️ Dashboard accessible without login (check @login_required)")
            else:
                print(f"⚠️ Unexpected status code: {response.status_code}")
                
            return True
            
    except Exception as e:
        print(f"❌ Dashboard route error: {e}")
        return False

def check_user_authentication():
    """Check if admin user exists and can authenticate."""
    print("\n👤 Checking User Authentication...")
    
    try:
        from app import app, db, User
        from werkzeug.security import check_password_hash
        
        with app.app_context():
            admin_user = User.query.filter_by(username='admin').first()
            
            if admin_user:
                print("✅ Admin user exists")
                print(f"✅ Username: {admin_user.username}")
                print(f"✅ Email: {admin_user.email}")
                
                # Test password (assuming default password)
                if check_password_hash(admin_user.password_hash, 'admin123'):
                    print("✅ Default password works")
                else:
                    print("⚠️ Default password doesn't work (may have been changed)")
                    
                return True
            else:
                print("❌ Admin user not found")
                return False
                
    except Exception as e:
        print(f"❌ User authentication error: {e}")
        return False

def generate_test_data():
    """Generate some test data if database is empty."""
    print("\n📊 Checking Test Data...")
    
    try:
        from app import app, db, Asset
        
        with app.app_context():
            asset_count = Asset.query.count()
            
            if asset_count == 0:
                print("⚠️ No assets found. Creating test data...")
                
                # Create a test asset
                test_asset = Asset(
                    asset_tag='TEST001',
                    asset_type='Laptop',
                    brand='Test Brand',
                    model='Test Model',
                    serial_number='TEST123456',
                    status='unassigned',
                    condition='good',
                    location='Test Location',
                    purchase_date='2024-01-01',
                    warranty_expiry='2025-01-01',
                    cost=1000.00,
                    ownership='purchased',
                    vendor='Test Vendor'
                )
                
                db.session.add(test_asset)
                db.session.commit()
                
                print("✅ Test asset created")
                return True
            else:
                print(f"✅ Found {asset_count} assets in database")
                return True
                
    except Exception as e:
        print(f"❌ Test data error: {e}")
        return False

def main():
    """Run all diagnostic checks."""
    print("🏢 IT Asset Manager - Dashboard Diagnostic Tool")
    print("=" * 60)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    checks = [
        ("Templates", check_templates),
        ("Database", check_database),
        ("Static Files", check_static_files),
        ("Dashboard Route", test_dashboard_route),
        ("User Authentication", check_user_authentication),
        ("Test Data", generate_test_data)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:20} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! Dashboard should be working.")
        print("\n💡 If you're still seeing only the sidebar:")
        print("   1. Clear your browser cache")
        print("   2. Try a different browser")
        print("   3. Check browser console for JavaScript errors")
        print("   4. Ensure your EC2 security group allows the port")
    else:
        print("⚠️ Some checks failed. Please address the issues above.")
        print("\n🔧 Common fixes:")
        print("   1. Run: python app.py (to ensure database is created)")
        print("   2. Check internet connection for CDN resources")
        print("   3. Verify all files were uploaded correctly")
    
    print("\n🌐 Access your application at:")
    print("   http://YOUR_EC2_PUBLIC_IP:5000")
    print("   Username: admin")
    print("   Password: admin123")

if __name__ == "__main__":
    main()
