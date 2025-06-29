#!/usr/bin/env python3
"""
Dashboard Display Fix Script for IT Asset Manager
This script fixes common dashboard display issues.
"""

import os
import sys

def fix_css_loading_issue():
    """Fix potential CSS loading issues by creating a simple CSS fallback."""
    print("🎨 Fixing CSS loading issues...")
    
    # Create static directory if it doesn't exist
    static_dir = 'static'
    css_dir = os.path.join(static_dir, 'css')
    os.makedirs(css_dir, exist_ok=True)
    
    # Create a fallback CSS file
    fallback_css = """
/* Fallback CSS for IT Asset Manager */
.main-content {
    margin-left: 280px !important;
    padding: 20px !important;
    min-height: 100vh;
}

@media (max-width: 768px) {
    .main-content {
        margin-left: 0 !important;
    }
}

.sidebar {
    position: fixed !important;
    top: 0;
    left: 0;
    width: 280px;
    height: 100vh;
    background: #2c3e50 !important;
    z-index: 1000;
}

.card {
    margin-bottom: 20px;
    border: 1px solid #dee2e6;
    border-radius: 8px;
}

.card-body {
    padding: 1.5rem;
}

.row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -15px;
}

.col-xl-3, .col-md-6 {
    flex: 0 0 25%;
    max-width: 25%;
    padding: 0 15px;
}

@media (max-width: 768px) {
    .col-xl-3, .col-md-6 {
        flex: 0 0 50%;
        max-width: 50%;
    }
}

@media (max-width: 576px) {
    .col-xl-3, .col-md-6 {
        flex: 0 0 100%;
        max-width: 100%;
    }
}

.h2 {
    font-size: 2rem;
    font-weight: 700;
}

.text-muted {
    color: #6c757d !important;
}

.mb-4 {
    margin-bottom: 1.5rem !important;
}

.p-4 {
    padding: 1.5rem !important;
}
"""
    
    css_file_path = os.path.join(css_dir, 'fallback.css')
    with open(css_file_path, 'w') as f:
        f.write(fallback_css)
    
    print(f"✅ Created fallback CSS: {css_file_path}")
    return True

def update_base_template():
    """Update base template to include fallback CSS."""
    print("📝 Updating base template...")
    
    base_template_path = 'templates/base.html'
    
    if not os.path.exists(base_template_path):
        print("❌ base.html template not found")
        return False
    
    # Read the current template
    with open(base_template_path, 'r') as f:
        content = f.read()
    
    # Check if fallback CSS is already included
    if 'fallback.css' in content:
        print("✅ Fallback CSS already included")
        return True
    
    # Add fallback CSS link before closing </head>
    fallback_css_link = '    <link href="{{ url_for(\'static\', filename=\'css/fallback.css\') }}" rel="stylesheet">\n</head>'
    
    if '</head>' in content:
        content = content.replace('</head>', fallback_css_link)
        
        # Write back to file
        with open(base_template_path, 'w') as f:
            f.write(content)
        
        print("✅ Added fallback CSS to base template")
        return True
    else:
        print("⚠️ Could not find </head> tag in base template")
        return False

def create_sample_data():
    """Create sample data if database is empty."""
    print("📊 Creating sample data...")
    
    try:
        from app import app, db, Asset, ApplicationAccess, GitHubAccess
        
        with app.app_context():
            # Check if we already have data
            if Asset.query.count() > 0:
                print("✅ Sample data already exists")
                return True
            
            # Create sample assets
            sample_assets = [
                {
                    'asset_tag': 'LAP001',
                    'asset_type': 'Laptop',
                    'brand': 'Dell',
                    'model': 'Latitude 7420',
                    'serial_number': 'DL123456789',
                    'status': 'assigned',
                    'condition': 'excellent',
                    'location': 'Office Floor 1',
                    'purchase_date': '2024-01-15',
                    'warranty_expiry': '2027-01-15',
                    'cost': 1200.00,
                    'ownership': 'purchased',
                    'vendor': 'Dell Technologies'
                },
                {
                    'asset_tag': 'DSK001',
                    'asset_type': 'Desktop',
                    'brand': 'HP',
                    'model': 'EliteDesk 800',
                    'serial_number': 'HP987654321',
                    'status': 'unassigned',
                    'condition': 'good',
                    'location': 'Storage Room',
                    'purchase_date': '2023-06-10',
                    'warranty_expiry': '2026-06-10',
                    'cost': 800.00,
                    'ownership': 'purchased',
                    'vendor': 'HP Inc.'
                },
                {
                    'asset_tag': 'MON001',
                    'asset_type': 'Monitor',
                    'brand': 'Samsung',
                    'model': '27" 4K Display',
                    'serial_number': 'SM456789123',
                    'status': 'assigned',
                    'condition': 'excellent',
                    'location': 'Office Floor 2',
                    'purchase_date': '2024-03-20',
                    'warranty_expiry': '2027-03-20',
                    'cost': 350.00,
                    'ownership': 'purchased',
                    'vendor': 'Samsung Electronics'
                }
            ]
            
            for asset_data in sample_assets:
                asset = Asset(**asset_data)
                db.session.add(asset)
            
            # Create sample application access
            app_access = ApplicationAccess(
                user_name='John Doe',
                application_name='Microsoft Office 365',
                access_level='full',
                granted_date='2024-01-01',
                status='active',
                notes='Standard office suite access'
            )
            db.session.add(app_access)
            
            # Create sample GitHub access
            github_access = GitHubAccess(
                user_name='Jane Smith',
                github_username='janesmith',
                repository_name='company-website',
                access_level='write',
                granted_date='2024-02-01',
                status='active',
                notes='Frontend development access'
            )
            db.session.add(github_access)
            
            db.session.commit()
            print("✅ Sample data created successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def fix_responsive_layout():
    """Fix responsive layout issues."""
    print("📱 Fixing responsive layout...")
    
    # Create a JavaScript file to fix layout issues
    static_dir = 'static'
    js_dir = os.path.join(static_dir, 'js')
    os.makedirs(js_dir, exist_ok=True)
    
    layout_fix_js = """
// Layout fix for IT Asset Manager
document.addEventListener('DOMContentLoaded', function() {
    // Ensure main content is visible
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.style.display = 'block';
        mainContent.style.visibility = 'visible';
    }
    
    // Fix sidebar toggle on mobile
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('[data-bs-toggle="collapse"]');
    
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    // Ensure cards are visible
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.style.display = 'block';
        card.style.visibility = 'visible';
    });
    
    console.log('IT Asset Manager layout fixes applied');
});
"""
    
    js_file_path = os.path.join(js_dir, 'layout-fix.js')
    with open(js_file_path, 'w') as f:
        f.write(layout_fix_js)
    
    print(f"✅ Created layout fix JavaScript: {js_file_path}")
    return True

def update_template_with_js():
    """Add JavaScript fix to base template."""
    print("🔧 Adding JavaScript fixes to template...")
    
    base_template_path = 'templates/base.html'
    
    if not os.path.exists(base_template_path):
        print("❌ base.html template not found")
        return False
    
    with open(base_template_path, 'r') as f:
        content = f.read()
    
    # Check if layout fix JS is already included
    if 'layout-fix.js' in content:
        print("✅ Layout fix JavaScript already included")
        return True
    
    # Add JavaScript before closing </body>
    js_include = '    <script src="{{ url_for(\'static\', filename=\'js/layout-fix.js\') }}"></script>\n</body>'
    
    if '</body>' in content:
        content = content.replace('</body>', js_include)
        
        with open(base_template_path, 'w') as f:
            f.write(content)
        
        print("✅ Added layout fix JavaScript to base template")
        return True
    else:
        print("⚠️ Could not find </body> tag in base template")
        return False

def main():
    """Run all fixes."""
    print("🔧 IT Asset Manager - Dashboard Display Fix")
    print("=" * 50)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    fixes = [
        ("CSS Loading Fix", fix_css_loading_issue),
        ("Base Template Update", update_base_template),
        ("Responsive Layout Fix", fix_responsive_layout),
        ("JavaScript Template Update", update_template_with_js),
        ("Sample Data Creation", create_sample_data)
    ]
    
    results = []
    
    for fix_name, fix_func in fixes:
        try:
            print(f"\n🔄 Running: {fix_name}")
            result = fix_func()
            results.append((fix_name, result))
        except Exception as e:
            print(f"❌ {fix_name} failed: {e}")
            results.append((fix_name, False))
    
    print("\n" + "=" * 50)
    print("📋 FIX SUMMARY")
    print("=" * 50)
    
    for fix_name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{fix_name:25} {status}")
    
    print("\n🎉 Dashboard display fixes completed!")
    print("\n📝 Next steps:")
    print("1. Restart your application:")
    print("   python app.py")
    print("2. Clear your browser cache")
    print("3. Access: http://YOUR_EC2_PUBLIC_IP:5000")
    print("4. Login with: admin / admin123")
    
    print("\n💡 If issues persist:")
    print("1. Check browser console for errors (F12)")
    print("2. Try a different browser")
    print("3. Ensure EC2 security group allows port 5000")

if __name__ == "__main__":
    main()
