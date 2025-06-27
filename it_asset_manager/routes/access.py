"""
Access management routes.

This module contains all routes related to application and GitHub access management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required
import io

from ..services.access_service import AccessService
from ..models.access import ApplicationAccess, GitHubAccess
from ..core.database import db

access_bp = Blueprint('access', __name__)


# Application Access Routes

@access_bp.route('/applications')
@login_required
def list_application_access():
    """
    List all application access records.
    
    Returns:
        Rendered application access list template
    """
    try:
        # Get filter parameters
        username = request.args.get('user', '')
        application = request.args.get('app', '')
        status = request.args.get('status', '')
        
        # Build query
        query = ApplicationAccess.query
        
        if username:
            query = query.filter(ApplicationAccess.user_name.ilike(f'%{username}%'))
        
        if application:
            query = query.filter(ApplicationAccess.application_name.ilike(f'%{application}%'))
        
        if status:
            query = query.filter_by(status=status)
        
        access_records = query.order_by(ApplicationAccess.created_at.desc()).all()
        
        # Get unique values for filters
        users = db.session.query(ApplicationAccess.user_name).distinct().all()
        applications = db.session.query(ApplicationAccess.application_name).distinct().all()
        
        return render_template(
            'app_access.html',
            access_records=access_records,
            users=[u[0] for u in users],
            applications=[a[0] for a in applications],
            current_user=username,
            current_app=application,
            current_status=status
        )
        
    except Exception as e:
        flash(f"Error loading application access: {str(e)}", 'error')
        return render_template('app_access.html', access_records=[])


@access_bp.route('/applications/add', methods=['GET', 'POST'])
@login_required
def add_application_access():
    """
    Add new application access route.
    
    GET: Display add access form
    POST: Process new access creation
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        application_name = request.form.get('application_name', '').strip()
        access_level = request.form.get('access_level', '').strip()
        remarks = request.form.get('remarks', '').strip()
        
        if not all([username, application_name, access_level]):
            flash('Username, application name, and access level are required', 'error')
            return render_template('add_app_access.html')
        
        success, message, access = AccessService.grant_application_access(
            username, application_name, access_level, remarks
        )
        
        flash(message, 'success' if success else 'error')
        
        if success:
            return redirect(url_for('access.list_application_access'))
    
    return render_template('add_app_access.html')


@access_bp.route('/applications/revoke/<int:access_id>', methods=['POST'])
@login_required
def revoke_application_access(access_id: int):
    """
    Revoke application access route.
    
    Args:
        access_id: ID of access record to revoke
    """
    remarks = request.form.get('remarks', '').strip()
    
    success, message = AccessService.revoke_application_access(access_id, remarks)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('access.list_application_access'))


@access_bp.route('/applications/update/<int:access_id>', methods=['POST'])
@login_required
def update_application_access(access_id: int):
    """
    Update application access route.
    
    Args:
        access_id: ID of access record to update
    """
    new_access_level = request.form.get('access_level', '').strip()
    remarks = request.form.get('remarks', '').strip()
    
    if not new_access_level:
        flash('Access level is required', 'error')
        return redirect(url_for('access.list_application_access'))
    
    success, message = AccessService.update_application_access(
        access_id, new_access_level, remarks
    )
    flash(message, 'success' if success else 'error')
    return redirect(url_for('access.list_application_access'))


# GitHub Access Routes

@access_bp.route('/github')
@login_required
def list_github_access():
    """
    List all GitHub access records.
    
    Returns:
        Rendered GitHub access list template
    """
    try:
        # Get filter parameters
        username = request.args.get('user', '')
        organization = request.args.get('org', '')
        repository = request.args.get('repo', '')
        status = request.args.get('status', '')
        
        # Build query
        query = GitHubAccess.query
        
        if username:
            query = query.filter(GitHubAccess.user_name.ilike(f'%{username}%'))
        
        if organization:
            query = query.filter(GitHubAccess.organization_name.ilike(f'%{organization}%'))
        
        if repository:
            query = query.filter(GitHubAccess.repo_name.ilike(f'%{repository}%'))
        
        if status:
            query = query.filter_by(status=status)
        
        access_records = query.order_by(GitHubAccess.created_at.desc()).all()
        
        # Get unique values for filters
        users = db.session.query(GitHubAccess.user_name).distinct().all()
        organizations = db.session.query(GitHubAccess.organization_name).distinct().all()
        repositories = db.session.query(GitHubAccess.repo_name).distinct().all()
        
        return render_template(
            'github_access.html',
            access_records=access_records,
            users=[u[0] for u in users],
            organizations=[o[0] for o in organizations],
            repositories=[r[0] for r in repositories],
            current_user=username,
            current_org=organization,
            current_repo=repository,
            current_status=status
        )
        
    except Exception as e:
        flash(f"Error loading GitHub access: {str(e)}", 'error')
        return render_template('github_access.html', access_records=[])


@access_bp.route('/github/add', methods=['GET', 'POST'])
@login_required
def add_github_access():
    """
    Add new GitHub access route.
    
    GET: Display add GitHub access form
    POST: Process new GitHub access creation
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        organization = request.form.get('organization', '').strip()
        repo_name = request.form.get('repo_name', '').strip()
        access_type = request.form.get('access_type', '').strip()
        remarks = request.form.get('remarks', '').strip()
        
        if not all([username, organization, repo_name, access_type]):
            flash('All fields except remarks are required', 'error')
            return render_template('add_github_access.html')
        
        success, message, access = AccessService.grant_github_access(
            username, organization, repo_name, access_type, remarks
        )
        
        flash(message, 'success' if success else 'error')
        
        if success:
            return redirect(url_for('access.list_github_access'))
    
    return render_template('add_github_access.html')


@access_bp.route('/github/revoke/<int:access_id>', methods=['POST'])
@login_required
def revoke_github_access(access_id: int):
    """
    Revoke GitHub access route.
    
    Args:
        access_id: ID of access record to revoke
    """
    remarks = request.form.get('remarks', '').strip()
    
    success, message = AccessService.revoke_github_access(access_id, remarks)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('access.list_github_access'))


@access_bp.route('/github/update/<int:access_id>', methods=['POST'])
@login_required
def update_github_access(access_id: int):
    """
    Update GitHub access route.
    
    Args:
        access_id: ID of access record to update
    """
    new_access_type = request.form.get('access_type', '').strip()
    remarks = request.form.get('remarks', '').strip()
    
    if not new_access_type:
        flash('Access type is required', 'error')
        return redirect(url_for('access.list_github_access'))
    
    success, message = AccessService.update_github_access(
        access_id, new_access_type, remarks
    )
    flash(message, 'success' if success else 'error')
    return redirect(url_for('access.list_github_access'))


# Export Routes

@access_bp.route('/applications/export')
@login_required
def export_application_access():
    """
    Export application access to CSV file.
    
    Returns:
        CSV file download
    """
    try:
        csv_data = AccessService.export_application_access_csv()
        
        # Create file-like object
        output = io.StringIO(csv_data)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='application_access_export.csv'
        )
        
    except Exception as e:
        flash(f"Error exporting application access: {str(e)}", 'error')
        return redirect(url_for('access.list_application_access'))


@access_bp.route('/github/export')
@login_required
def export_github_access():
    """
    Export GitHub access to CSV file.
    
    Returns:
        CSV file download
    """
    try:
        csv_data = AccessService.export_github_access_csv()
        
        # Create file-like object
        output = io.StringIO(csv_data)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='github_access_export.csv'
        )
        
    except Exception as e:
        flash(f"Error exporting GitHub access: {str(e)}", 'error')
        return redirect(url_for('access.list_github_access'))


# API Routes

@access_bp.route('/api/statistics')
@login_required
def api_access_statistics():
    """
    API endpoint for access statistics.
    
    Returns:
        JSON response with access statistics
    """
    try:
        stats = AccessService.get_access_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
