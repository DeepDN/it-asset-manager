"""
Main application routes.

This module contains the main routes including dashboard and home page.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from ..services.asset_service import AssetService
from ..services.access_service import AccessService

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Home page route.
    
    Redirects to dashboard if user is authenticated, otherwise to login.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Main dashboard with statistics and overview.
    
    Returns:
        Rendered dashboard template with statistics
    """
    try:
        # Get asset statistics
        asset_stats = AssetService.get_asset_statistics()
        
        # Get access statistics
        access_stats = AccessService.get_access_statistics()
        
        return render_template(
            'dashboard.html',
            asset_stats=asset_stats,
            access_stats=access_stats,
            user=current_user
        )
        
    except Exception as e:
        return render_template(
            'dashboard.html',
            error=f"Error loading dashboard: {str(e)}",
            user=current_user
        )
