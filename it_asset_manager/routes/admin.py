from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models.user import User
from ..models.rbac import ROLES
from ..models.location import Location
from ..models.approval import ApprovalRequest, APPROVAL_STATUSES, APPROVAL_TYPES
from ..services.rbac_service import RBACService
from ..services.approval_service import ApprovalService
from ..core.database import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/users')
@login_required
def list_users():
    if current_user.role not in ['super_admin', 'it_admin']:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    try:
        users = User.query.order_by(User.username).all()
        return render_template('admin/users.html', users=users, roles=ROLES)
    except Exception as e:
        flash(f'Error loading users: {str(e)}', 'error')
        return render_template('admin/users.html', users=[], roles=ROLES)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role not in ['super_admin', 'it_admin']:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        try:
            from ..services.auth_service import AuthService
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            email = request.form.get('email', '').strip()
            role = request.form.get('role', 'employee')
            department = request.form.get('department', '').strip()
            phone = request.form.get('phone', '').strip()
            success, msg, user = AuthService.create_user(username, password, email or None)
            if success:
                if role:
                    RBACService.update_user_role(user.id, role)
                user.department = department or None
                user.phone = phone or None
                db.session.commit()
                flash(msg, 'success')
                return redirect(url_for('admin.list_users'))
            else:
                flash(msg, 'error')
        except Exception as e:
            flash(f'Error adding user: {str(e)}', 'error')
    return render_template('admin/add_user.html', roles=ROLES)


@admin_bp.route('/users/update-role/<int:user_id>', methods=['POST'])
@login_required
def update_user_role(user_id):
    if current_user.role not in ['super_admin', 'it_admin']:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    try:
        new_role = request.form.get('role')
        success, msg = RBACService.update_user_role(user_id, new_role)
        flash(msg, 'success' if success else 'error')
    except Exception as e:
        flash(f'Error updating role: {str(e)}', 'error')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/toggle/<int:user_id>', methods=['POST'])
@login_required
def toggle_user(user_id):
    if current_user.role not in ['super_admin', 'it_admin']:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    try:
        user = db.session.get(User, user_id)
        if user:
            user.is_active = not user.is_active
            db.session.commit()
            flash(f"User {'activated' if user.is_active else 'deactivated'}", 'success')
        else:
            flash('User not found', 'error')
    except Exception as e:
        flash(f'Error toggling user: {str(e)}', 'error')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/reset-password/<int:user_id>', methods=['POST'])
@login_required
def reset_user_password(user_id):
    if current_user.role not in ['super_admin', 'it_admin']:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    try:
        user = db.session.get(User, user_id)
        if not user:
            flash('User not found', 'error')
        elif user.username == 'admin':
            flash('Cannot reset password for admin user', 'error')
        else:
            from ..services.auth_service import AuthService
            new_password = request.form.get('new_password', '')
            if not new_password or len(new_password) < 6:
                flash('Password must be at least 6 characters', 'error')
            else:
                user.set_password(new_password)
                db.session.commit()
                flash(f'Password reset for {user.username}', 'success')
    except Exception as e:
        flash(f'Error resetting password: {str(e)}', 'error')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/locations')
@login_required
def list_locations():
    try:
        locations = Location.query.order_by(Location.full_path).all()
        return render_template('admin/locations.html', locations=locations)
    except Exception as e:
        flash(f'Error loading locations: {str(e)}', 'error')
        return render_template('admin/locations.html', locations=[])


@admin_bp.route('/locations/add', methods=['POST'])
@login_required
def add_location():
    if current_user.role not in ['super_admin', 'it_admin']:
        flash('Access denied', 'error')
        return redirect(url_for('admin.list_locations'))
    try:
        parts = [
            request.form.get('country', ''),
            request.form.get('region', ''),
            request.form.get('office', ''),
            request.form.get('building', ''),
            request.form.get('floor', ''),
            request.form.get('room', '')
        ]
        full_path = ' / '.join(p for p in parts if p)
        loc = Location(
            country=request.form.get('country'),
            region=request.form.get('region'),
            office=request.form.get('office'),
            building=request.form.get('building'),
            floor=request.form.get('floor'),
            room=request.form.get('room'),
            full_path=full_path
        )
        db.session.add(loc)
        db.session.commit()
        flash('Location added', 'success')
    except Exception as e:
        flash(f'Error adding location: {str(e)}', 'error')
    return redirect(url_for('admin.list_locations'))


@admin_bp.route('/approvals/create', methods=['POST'])
@login_required
def create_approval():
    try:
        request_type = request.form.get('request_type', '').strip()
        requester = request.form.get('requester', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        entity_type = request.form.get('entity_type', '').strip()
        entity_id = request.form.get('entity_id', '').strip()

        if not request_type or not requester or not description:
            flash('Request type, requester, and description are required', 'error')
            return redirect(url_for('admin.list_approvals'))

        success, msg, req = ApprovalService.create_request(
            request_type, requester, description,
            entity_type or None,
            int(entity_id) if entity_id else None,
            priority
        )
        flash(msg, 'success' if success else 'error')
    except Exception as e:
        flash(f'Error creating approval: {str(e)}', 'error')
    return redirect(url_for('admin.list_approvals'))


@admin_bp.route('/approvals')
@login_required
def list_approvals():
    try:
        if current_user.role in ['super_admin', 'it_admin', 'asset_manager']:
            requests = ApprovalRequest.query.order_by(ApprovalRequest.created_at.desc()).all()
        else:
            requests = ApprovalRequest.query.filter_by(requester=current_user.username).order_by(ApprovalRequest.created_at.desc()).all()
        users = User.query.order_by(User.username).all()
        return render_template('admin/approvals.html', requests=requests, users=users, approval_types=APPROVAL_TYPES)
    except Exception as e:
        flash(f'Error loading approvals: {str(e)}', 'error')
        return render_template('admin/approvals.html', requests=[], users=[], approval_types=APPROVAL_TYPES)


@admin_bp.route('/approvals/action/<int:approval_id>/<action>', methods=['POST'])
@login_required
def approval_action(approval_id, action):
    try:
        comment = request.form.get('comment', '')
        if action == 'approve':
            success, msg = ApprovalService.approve_request(approval_id, current_user.username, comment)
        elif action == 'reject':
            success, msg = ApprovalService.reject_request(approval_id, current_user.username, comment)
        else:
            flash('Invalid action', 'error')
            return redirect(url_for('admin.list_approvals'))
        flash(msg, 'success' if success else 'error')
    except Exception as e:
        flash(f'Error processing approval: {str(e)}', 'error')
    return redirect(url_for('admin.list_approvals'))
