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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Ensure instance directory exists
instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_dir, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', f'sqlite:///{os.path.join(instance_dir, "it_assets.db")}')
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

# Bulk Upload Routes
@app.route('/assets/bulk-upload', methods=['GET', 'POST'])
@login_required
def bulk_upload_assets():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.csv'):
            try:
                # Read CSV file
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_input = csv.reader(stream)
                
                # Skip header row
                next(csv_input)
                
                success_count = 0
                error_count = 0
                errors = []
                
                for row_num, row in enumerate(csv_input, start=2):
                    try:
                        if len(row) < 13:  # Minimum required columns
                            errors.append(f"Row {row_num}: Insufficient columns")
                            error_count += 1
                            continue
                        
                        # Check if asset tag already exists
                        existing_asset = Asset.query.filter_by(asset_tag=row[0]).first()
                        if existing_asset:
                            errors.append(f"Row {row_num}: Asset tag '{row[0]}' already exists")
                            error_count += 1
                            continue
                        
                        # Create new asset
                        asset = Asset(
                            asset_tag=row[0],
                            asset_type=row[1],
                            brand=row[2],
                            model=row[3],
                            serial_number=row[4],
                            status=row[5] if row[5] in ['assigned', 'unassigned', 'maintenance', 'retired'] else 'unassigned',
                            condition=row[6] if row[6] in ['excellent', 'good', 'fair', 'poor'] else 'good',
                            location=row[7],
                            purchase_date=row[8] if row[8] else None,
                            warranty_expiry=row[9] if row[9] else None,
                            cost=float(row[10]) if row[10] and row[10].replace('.', '').isdigit() else 0.0,
                            ownership=row[11] if row[11] in ['purchased', 'leased', 'rented'] else 'purchased',
                            vendor=row[12],
                            notes=row[13] if len(row) > 13 else ''
                        )
                        
                        db.session.add(asset)
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        error_count += 1
                
                # Commit all successful additions
                if success_count > 0:
                    db.session.commit()
                    flash(f'Successfully imported {success_count} assets', 'success')
                
                if error_count > 0:
                    flash(f'{error_count} rows had errors. Check the error log below.', 'warning')
                    for error in errors[:10]:  # Show first 10 errors
                        flash(error, 'error')
                    if len(errors) > 10:
                        flash(f'... and {len(errors) - 10} more errors', 'error')
                
                return redirect(url_for('assets'))
                
            except Exception as e:
                flash(f'Error processing CSV file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Please upload a CSV file', 'error')
            return redirect(request.url)
    
    return render_template('bulk_upload_assets.html')

@app.route('/assets/download-template')
@login_required
def download_asset_template():
    """Download CSV template for bulk asset upload"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header with all required columns
    writer.writerow([
        'asset_tag',
        'asset_type',
        'brand',
        'model',
        'serial_number',
        'status',
        'condition',
        'location',
        'purchase_date',
        'warranty_expiry',
        'cost',
        'ownership',
        'vendor',
        'notes'
    ])
    
    # Write sample data
    writer.writerow([
        'LAP001',
        'Laptop',
        'Dell',
        'Latitude 7420',
        'DL123456789',
        'assigned',
        'excellent',
        'Office Floor 1',
        '2024-01-15',
        '2027-01-15',
        '1200.00',
        'purchased',
        'Dell Technologies',
        'Sample laptop entry'
    ])
    
    writer.writerow([
        'DSK001',
        'Desktop',
        'HP',
        'EliteDesk 800',
        'HP987654321',
        'unassigned',
        'good',
        'Storage Room',
        '2023-06-10',
        '2026-06-10',
        '800.00',
        'purchased',
        'HP Inc.',
        'Sample desktop entry'
    ])
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='asset_upload_template.csv'
    )

@app.route('/app-access/bulk-upload', methods=['GET', 'POST'])
@login_required
def bulk_upload_app_access():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.csv'):
            try:
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_input = csv.reader(stream)
                
                # Skip header row
                next(csv_input)
                
                success_count = 0
                error_count = 0
                errors = []
                
                for row_num, row in enumerate(csv_input, start=2):
                    try:
                        if len(row) < 5:  # Minimum required columns
                            errors.append(f"Row {row_num}: Insufficient columns")
                            error_count += 1
                            continue
                        
                        app_access = ApplicationAccess(
                            user_name=row[0],
                            application_name=row[1],
                            access_level=row[2] if row[2] in ['read', 'write', 'admin', 'full'] else 'read',
                            granted_date=row[3] if row[3] else datetime.now().strftime('%Y-%m-%d'),
                            status=row[4] if row[4] in ['active', 'inactive', 'suspended'] else 'active',
                            notes=row[5] if len(row) > 5 else ''
                        )
                        
                        db.session.add(app_access)
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        error_count += 1
                
                if success_count > 0:
                    db.session.commit()
                    flash(f'Successfully imported {success_count} application access records', 'success')
                
                if error_count > 0:
                    flash(f'{error_count} rows had errors', 'warning')
                    for error in errors[:5]:
                        flash(error, 'error')
                
                return redirect(url_for('app_access'))
                
            except Exception as e:
                flash(f'Error processing CSV file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Please upload a CSV file', 'error')
            return redirect(request.url)
    
    return render_template('bulk_upload_app_access.html')

@app.route('/app-access/download-template')
@login_required
def download_app_access_template():
    """Download CSV template for bulk application access upload"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'user_name',
        'application_name',
        'access_level',
        'granted_date',
        'status',
        'notes'
    ])
    
    writer.writerow([
        'John Doe',
        'Microsoft Office 365',
        'full',
        '2024-01-01',
        'active',
        'Standard office suite access'
    ])
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='app_access_upload_template.csv'
    )

@app.route('/github-access/bulk-upload', methods=['GET', 'POST'])
@login_required
def bulk_upload_github_access():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.csv'):
            try:
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_input = csv.reader(stream)
                
                # Skip header row
                next(csv_input)
                
                success_count = 0
                error_count = 0
                errors = []
                
                for row_num, row in enumerate(csv_input, start=2):
                    try:
                        if len(row) < 6:  # Minimum required columns
                            errors.append(f"Row {row_num}: Insufficient columns")
                            error_count += 1
                            continue
                        
                        github_access = GitHubAccess(
                            user_name=row[0],
                            github_username=row[1],
                            repository_name=row[2],
                            access_level=row[3] if row[3] in ['read', 'write', 'admin'] else 'read',
                            granted_date=row[4] if row[4] else datetime.now().strftime('%Y-%m-%d'),
                            status=row[5] if row[5] in ['active', 'inactive', 'suspended'] else 'active',
                            notes=row[6] if len(row) > 6 else ''
                        )
                        
                        db.session.add(github_access)
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        error_count += 1
                
                if success_count > 0:
                    db.session.commit()
                    flash(f'Successfully imported {success_count} GitHub access records', 'success')
                
                if error_count > 0:
                    flash(f'{error_count} rows had errors', 'warning')
                    for error in errors[:5]:
                        flash(error, 'error')
                
                return redirect(url_for('github_access'))
                
            except Exception as e:
                flash(f'Error processing CSV file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Please upload a CSV file', 'error')
            return redirect(request.url)
    
    return render_template('bulk_upload_github_access.html')

@app.route('/github-access/download-template')
@login_required
def download_github_access_template():
    """Download CSV template for bulk GitHub access upload"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'user_name',
        'github_username',
        'repository_name',
        'access_level',
        'granted_date',
        'status',
        'notes'
    ])
    
    writer.writerow([
        'Jane Smith',
        'janesmith',
        'company-website',
        'write',
        '2024-02-01',
        'active',
        'Frontend development access'
    ])
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='github_access_upload_template.csv'
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
