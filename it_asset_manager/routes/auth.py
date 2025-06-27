"""
Authentication routes.

This module contains all authentication related routes including
login, logout, password management, and user registration.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user

from ..services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    
    GET: Display login form
    POST: Process login credentials
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        success, message, user = AuthService.authenticate_user(username, password, remember_me)
        
        if success:
            flash(message, 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash(message, 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout route.
    
    Logs out current user and redirects to login page.
    """
    success, message = AuthService.logout_user_session()
    flash(message, 'success' if success else 'error')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change password route.
    
    GET: Display password change form
    POST: Process password change
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('change_password.html')
        
        # Change password
        success, message = AuthService.change_password(
            current_user.id, current_password, new_password
        )
        
        flash(message, 'success' if success else 'error')
        
        if success:
            return redirect(url_for('main.dashboard'))
    
    return render_template('change_password.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Forgot password route.
    
    GET: Display forgot password form
    POST: Process password reset request
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        
        if not username_or_email:
            flash('Please enter your username or email', 'error')
            return render_template('forgot_password.html')
        
        success, message, reset_token = AuthService.initiate_password_reset(username_or_email)
        
        if success:
            # In a real application, you would send this token via email
            # For now, we'll display it (not recommended for production)
            flash(f'Password reset initiated. Reset token: {reset_token}', 'info')
            return render_template('reset_instructions.html', token=reset_token)
        else:
            flash(message, 'error')
    
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token: str):
    """
    Reset password with token route.
    
    Args:
        token: Password reset token
        
    GET: Display password reset form
    POST: Process password reset
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input
        if not new_password or not confirm_password:
            flash('Both password fields are required', 'error')
            return render_template('reset_password.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        # Reset password
        success, message = AuthService.reset_password_with_token(token, new_password)
        
        flash(message, 'success' if success else 'error')
        
        if success:
            return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', token=token)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    User profile route.
    
    GET: Display user profile
    POST: Update user profile
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        success, message = AuthService.update_user_profile(current_user.id, email)
        flash(message, 'success' if success else 'error')
        
        if success:
            return redirect(url_for('auth.profile'))
    
    return render_template('profile.html', user=current_user)
