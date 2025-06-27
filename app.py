from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import csv
import io
import os
import secrets
import string
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///it_assets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(120), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(50), unique=True, nullable=False)  # Unique asset tag
    asset_type = db.Column(db.String(50), nullable=False)  # laptop, desktop, mobile, etc.
    asset_category = db.Column(db.String(50), nullable=False)  # Computing, Network, Audio/Video, etc.
    ownership_type = db.Column(db.String(20), nullable=False, default='purchased')  # purchased, rented, leased
    vendor_name = db.Column(db.String(100))  # For rented/leased assets
    rental_start_date = db.Column(db.Date)  # For rented assets
    rental_end_date = db.Column(db.Date)  # For rented assets
    rental_cost_monthly = db.Column(db.Float)  # Monthly rental cost
    purchase_date = db.Column(db.Date)  # For purchased assets
    purchase_cost = db.Column(db.Float)  # Purchase cost
    warranty_expiry = db.Column(db.Date)  # Warranty expiry date
    brand = db.Column(db.String(50))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    processor = db.Column(db.String(100))
    ram_gb = db.Column(db.Integer)
    storage_gb = db.Column(db.Integer)
    storage_type = db.Column(db.String(20))  # SSD, HDD
    # Network device specific fields
    port_count = db.Column(db.Integer)  # For switches, routers
    network_type = db.Column(db.String(50))  # Ethernet, WiFi, etc.
    # Display specific fields
    screen_size = db.Column(db.String(20))  # For monitors, TVs
    resolution = db.Column(db.String(20))  # 1920x1080, 4K, etc.
    # Audio/Video specific fields
    audio_type = db.Column(db.String(50))  # Microphone, Speaker, Headset
    connector_type = db.Column(db.String(50))  # HDMI, USB-C, Lightning, etc.
    # General fields
    assigned_to = db.Column(db.String(100))
    assign_date = db.Column(db.Date)
    remove_date = db.Column(db.Date)
    location = db.Column(db.String(100))  # Office location, floor, room
    status = db.Column(db.String(20), default='unassigned')  # assigned, unassigned, maintenance, retired
    condition = db.Column(db.String(20), default='good')  # excellent, good, fair, poor, damaged
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ApplicationAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    application_name = db.Column(db.String(100), nullable=False)
    access_level = db.Column(db.String(50), nullable=False)  # Admin, Read, Write
    assign_date = db.Column(db.Date, nullable=False)
    remove_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')  # active, revoked
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GitHubAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    organization_name = db.Column(db.String(100), nullable=False)
    repo_name = db.Column(db.String(100), nullable=False)
    access_type = db.Column(db.String(50), nullable=False)  # Admin, Write, Read, Maintainer
    assign_date = db.Column(db.Date, nullable=False)
    remove_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')  # active, revoked
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
@app.route('/')
@login_required
def dashboard():
    total_assets = Asset.query.count()
    assigned_assets = Asset.query.filter_by(status='assigned').count()
    unassigned_assets = Asset.query.filter_by(status='unassigned').count()
    total_app_access = ApplicationAccess.query.filter_by(status='active').count()
    total_github_access = GitHubAccess.query.filter_by(status='active').count()
    
    return render_template('dashboard.html', 
                         total_assets=total_assets,
                         assigned_assets=assigned_assets,
                         unassigned_assets=unassigned_assets,
                         total_app_access=total_app_access,
                         total_github_access=total_github_access)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Generate reset token
            reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            user.reset_token = reset_token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
            
            try:
                db.session.commit()
                
                # In a real application, you would send this via email
                # For now, we'll show it on screen (for demo purposes)
                session['reset_info'] = {
                    'username': username,
                    'token': reset_token,
                    'expiry': user.reset_token_expiry.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                flash('Password reset instructions have been generated. Check below for your reset link.', 'success')
                return redirect(url_for('reset_instructions'))
                
            except Exception as e:
                flash(f'Error generating reset token: {str(e)}', 'error')
        else:
            flash('Username not found', 'error')
    
    return render_template('forgot_password.html')

@app.route('/reset-instructions')
def reset_instructions():
    reset_info = session.get('reset_info')
    if not reset_info:
        return redirect(url_for('forgot_password'))
    
    return render_template('reset_instructions.html', reset_info=reset_info)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired reset token', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('reset_password.html', token=token)
        
        # Update password and clear reset token
        user.password_hash = generate_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        
        try:
            db.session.commit()
            flash('Password has been reset successfully! You can now login with your new password.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error resetting password: {str(e)}', 'error')
    
    return render_template('reset_password.html', token=token, user=user)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Verify current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect', 'error')
            return render_template('change_password.html')
        
        # Validate new password
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('change_password.html')
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error changing password: {str(e)}', 'error')
    
    return render_template('change_password.html')

# Asset Management Routes
@app.route('/assets')
@login_required
def assets():
    asset_type = request.args.get('asset_type', '')
    assigned_user = request.args.get('assigned_user', '')
    status = request.args.get('status', '')
    
    query = Asset.query
    
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if assigned_user:
        query = query.filter(Asset.assigned_to.contains(assigned_user))
    if status:
        query = query.filter(Asset.status == status)
    
    assets = query.all()
    asset_types = db.session.query(Asset.asset_type).distinct().all()
    
    return render_template('assets.html', assets=assets, asset_types=asset_types)

@app.route('/assets/add', methods=['GET', 'POST'])
@login_required
def add_asset():
    if request.method == 'POST':
        # Basic Information
        asset_tag = request.form['asset_tag']
        asset_type = request.form['asset_type']
        asset_category = request.form['asset_category']
        serial_number = request.form['serial_number']
        brand = request.form['brand']
        model = request.form['model']
        
        # Ownership Information
        ownership_type = request.form['ownership_type']
        vendor_name = request.form['vendor_name'] if request.form['vendor_name'] else None
        purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date() if request.form['purchase_date'] else None
        purchase_cost = float(request.form['purchase_cost']) if request.form['purchase_cost'] else None
        rental_start_date = datetime.strptime(request.form['rental_start_date'], '%Y-%m-%d').date() if request.form['rental_start_date'] else None
        rental_end_date = datetime.strptime(request.form['rental_end_date'], '%Y-%m-%d').date() if request.form['rental_end_date'] else None
        rental_cost_monthly = float(request.form['rental_cost_monthly']) if request.form['rental_cost_monthly'] else None
        warranty_expiry = datetime.strptime(request.form['warranty_expiry'], '%Y-%m-%d').date() if request.form['warranty_expiry'] else None
        condition = request.form['condition']
        
        # Technical Specifications
        processor = request.form['processor'] if request.form['processor'] else None
        ram_gb = int(request.form['ram_gb']) if request.form['ram_gb'] else None
        storage_gb = int(request.form['storage_gb']) if request.form['storage_gb'] else None
        storage_type = request.form['storage_type'] if request.form['storage_type'] else None
        port_count = int(request.form['port_count']) if request.form['port_count'] else None
        network_type = request.form['network_type'] if request.form['network_type'] else None
        screen_size = request.form['screen_size'] if request.form['screen_size'] else None
        resolution = request.form['resolution'] if request.form['resolution'] else None
        audio_type = request.form['audio_type'] if request.form['audio_type'] else None
        connector_type = request.form['connector_type'] if request.form['connector_type'] else None
        
        # Assignment & Location
        assigned_to = request.form['assigned_to'] if request.form['assigned_to'] else None
        assign_date = datetime.strptime(request.form['assign_date'], '%Y-%m-%d').date() if request.form['assign_date'] else None
        location = request.form['location'] if request.form['location'] else None
        
        # Additional Information
        remarks = request.form['remarks']
        
        # Determine status
        status = 'assigned' if assigned_to and not request.form.get('remove_date') else 'unassigned'
        
        asset = Asset(
            asset_tag=asset_tag,
            asset_type=asset_type,
            asset_category=asset_category,
            ownership_type=ownership_type,
            vendor_name=vendor_name,
            rental_start_date=rental_start_date,
            rental_end_date=rental_end_date,
            rental_cost_monthly=rental_cost_monthly,
            purchase_date=purchase_date,
            purchase_cost=purchase_cost,
            warranty_expiry=warranty_expiry,
            brand=brand,
            model=model,
            serial_number=serial_number,
            processor=processor,
            ram_gb=ram_gb,
            storage_gb=storage_gb,
            storage_type=storage_type,
            port_count=port_count,
            network_type=network_type,
            screen_size=screen_size,
            resolution=resolution,
            audio_type=audio_type,
            connector_type=connector_type,
            assigned_to=assigned_to,
            assign_date=assign_date,
            location=location,
            status=status,
            condition=condition,
            remarks=remarks
        )
        
        try:
            db.session.add(asset)
            db.session.commit()
            flash('Asset added successfully!', 'success')
            return redirect(url_for('assets'))
        except Exception as e:
            flash(f'Error adding asset: {str(e)}', 'error')
    
    return render_template('add_asset.html')

@app.route('/assets/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_asset(id):
    asset = Asset.query.get_or_404(id)
    
    if request.method == 'POST':
        asset.asset_type = request.form['asset_type']
        asset.brand = request.form['brand']
        asset.model = request.form['model']
        asset.serial_number = request.form['serial_number']
        asset.processor = request.form['processor']
        asset.ram_gb = int(request.form['ram_gb']) if request.form['ram_gb'] else None
        asset.storage_gb = int(request.form['storage_gb']) if request.form['storage_gb'] else None
        asset.storage_type = request.form['storage_type']
        asset.assigned_to = request.form['assigned_to'] if request.form['assigned_to'] else None
        asset.assign_date = datetime.strptime(request.form['assign_date'], '%Y-%m-%d').date() if request.form['assign_date'] else None
        asset.remove_date = datetime.strptime(request.form['remove_date'], '%Y-%m-%d').date() if request.form['remove_date'] else None
        asset.status = 'assigned' if request.form['assigned_to'] and not request.form['remove_date'] else 'unassigned'
        asset.remarks = request.form['remarks']
        
        try:
            db.session.commit()
            flash('Asset updated successfully!')
            return redirect(url_for('assets'))
        except Exception as e:
            flash(f'Error updating asset: {str(e)}')
    
    return render_template('edit_asset.html', asset=asset)

# Application Access Routes
@app.route('/app-access')
@login_required
def app_access():
    user_name = request.args.get('user_name', '')
    application = request.args.get('application', '')
    status = request.args.get('status', '')
    
    query = ApplicationAccess.query
    
    if user_name:
        query = query.filter(ApplicationAccess.user_name.contains(user_name))
    if application:
        query = query.filter(ApplicationAccess.application_name.contains(application))
    if status:
        query = query.filter(ApplicationAccess.status == status)
    
    accesses = query.all()
    applications = db.session.query(ApplicationAccess.application_name).distinct().all()
    
    return render_template('app_access.html', accesses=accesses, applications=applications)

@app.route('/app-access/add', methods=['GET', 'POST'])
@login_required
def add_app_access():
    if request.method == 'POST':
        access = ApplicationAccess(
            user_name=request.form['user_name'],
            application_name=request.form['application_name'],
            access_level=request.form['access_level'],
            assign_date=datetime.strptime(request.form['assign_date'], '%Y-%m-%d').date(),
            remove_date=datetime.strptime(request.form['remove_date'], '%Y-%m-%d').date() if request.form['remove_date'] else None,
            status='revoked' if request.form['remove_date'] else 'active',
            remarks=request.form['remarks']
        )
        
        try:
            db.session.add(access)
            db.session.commit()
            flash('Application access added successfully!')
            return redirect(url_for('app_access'))
        except Exception as e:
            flash(f'Error adding application access: {str(e)}')
    
    return render_template('add_app_access.html')

# GitHub Access Routes
@app.route('/github-access')
@login_required
def github_access():
    user_name = request.args.get('user_name', '')
    organization = request.args.get('organization', '')
    repo = request.args.get('repo', '')
    status = request.args.get('status', '')
    
    query = GitHubAccess.query
    
    if user_name:
        query = query.filter(GitHubAccess.user_name.contains(user_name))
    if organization:
        query = query.filter(GitHubAccess.organization_name.contains(organization))
    if repo:
        query = query.filter(GitHubAccess.repo_name.contains(repo))
    if status:
        query = query.filter(GitHubAccess.status == status)
    
    accesses = query.all()
    organizations = db.session.query(GitHubAccess.organization_name).distinct().all()
    
    return render_template('github_access.html', accesses=accesses, organizations=organizations)

@app.route('/github-access/add', methods=['GET', 'POST'])
@login_required
def add_github_access():
    if request.method == 'POST':
        access = GitHubAccess(
            user_name=request.form['user_name'],
            organization_name=request.form['organization_name'],
            repo_name=request.form['repo_name'],
            access_type=request.form['access_type'],
            assign_date=datetime.strptime(request.form['assign_date'], '%Y-%m-%d').date(),
            remove_date=datetime.strptime(request.form['remove_date'], '%Y-%m-%d').date() if request.form['remove_date'] else None,
            status='revoked' if request.form['remove_date'] else 'active',
            remarks=request.form['remarks']
        )
        
        try:
            db.session.add(access)
            db.session.commit()
            flash('GitHub access added successfully!')
            return redirect(url_for('github_access'))
        except Exception as e:
            flash(f'Error adding GitHub access: {str(e)}')
    
    return render_template('add_github_access.html')

# Export Routes
@app.route('/export/assets')
@login_required
def export_assets():
    assets = Asset.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Asset Type', 'Brand', 'Model', 'Serial Number', 'Processor', 
                    'RAM (GB)', 'Storage (GB)', 'Storage Type', 'Assigned To', 
                    'Assign Date', 'Remove Date', 'Status', 'Remarks'])
    
    # Write data
    for asset in assets:
        writer.writerow([
            asset.asset_type, asset.brand, asset.model, asset.serial_number,
            asset.processor, asset.ram_gb, asset.storage_gb, asset.storage_type,
            asset.assigned_to, asset.assign_date, asset.remove_date,
            asset.status, asset.remarks
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'assets_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/export/app-access')
@login_required
def export_app_access():
    accesses = ApplicationAccess.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['User Name', 'Application Name', 'Access Level', 'Assign Date', 
                    'Remove Date', 'Status', 'Remarks'])
    
    # Write data
    for access in accesses:
        writer.writerow([
            access.user_name, access.application_name, access.access_level,
            access.assign_date, access.remove_date, access.status, access.remarks
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'app_access_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/export/github-access')
@login_required
def export_github_access():
    accesses = GitHubAccess.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['User Name', 'Organization Name', 'Repo Name', 'Access Type', 
                    'Assign Date', 'Remove Date', 'Status', 'Remarks'])
    
    # Write data
    for access in accesses:
        writer.writerow([
            access.user_name, access.organization_name, access.repo_name,
            access.access_type, access.assign_date, access.remove_date,
            access.status, access.remarks
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'github_access_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

def create_admin_user():
    """Create default admin user if it doesn't exist"""
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@itassetmanager.local',  # Default email
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: username=admin, password=admin123")
        print("⚠️  IMPORTANT: Change the default password immediately!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
