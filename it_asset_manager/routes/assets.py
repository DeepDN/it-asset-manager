"""
Asset management routes.

This module contains all routes related to asset management including
CRUD operations, assignment, and reporting.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required
import io

from ..services.asset_service import AssetService
from ..models.asset import Asset
from ..core.database import db

assets_bp = Blueprint('assets', __name__)


@assets_bp.route('/')
@login_required
def list_assets():
    """
    List all assets with filtering and search capabilities.
    
    Returns:
        Rendered assets list template
    """
    try:
        # Get filter parameters
        asset_type = request.args.get('type', '')
        status = request.args.get('status', '')
        search = request.args.get('search', '')
        
        # Build query
        query = Asset.query
        
        if asset_type:
            query = query.filter_by(asset_type=asset_type)
        
        if status:
            query = query.filter_by(status=status)
        
        if search:
            assets = Asset.search(search)
        else:
            assets = query.all()
        
        # Get unique asset types and statuses for filters
        asset_types = db.session.query(Asset.asset_type).distinct().all()
        asset_statuses = db.session.query(Asset.status).distinct().all()
        
        return render_template(
            'assets.html',
            assets=assets,
            asset_types=[t[0] for t in asset_types],
            asset_statuses=[s[0] for s in asset_statuses],
            current_type=asset_type,
            current_status=status,
            current_search=search
        )
        
    except Exception as e:
        flash(f"Error loading assets: {str(e)}", 'error')
        return render_template('assets.html', assets=[])


@assets_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_asset():
    """
    Add new asset route.
    
    GET: Display add asset form
    POST: Process new asset creation
    """
    if request.method == 'POST':
        # Get form data
        asset_data = {
            'asset_tag': request.form.get('asset_tag', '').strip(),
            'asset_type': request.form.get('asset_type', '').strip(),
            'serial_number': request.form.get('serial_number', '').strip(),
            'ownership_type': request.form.get('ownership_type', 'purchased'),
            'vendor_name': request.form.get('vendor_name', '').strip(),
            'brand': request.form.get('brand', '').strip(),
            'model': request.form.get('model', '').strip(),
            'processor': request.form.get('processor', '').strip(),
            'ram_gb': request.form.get('ram_gb', ''),
            'storage_gb': request.form.get('storage_gb', ''),
            'storage_type': request.form.get('storage_type', '').strip(),
            'port_count': request.form.get('port_count', ''),
            'network_type': request.form.get('network_type', '').strip(),
            'screen_size': request.form.get('screen_size', '').strip(),
            'resolution': request.form.get('resolution', '').strip(),
            'audio_type': request.form.get('audio_type', '').strip(),
            'connector_type': request.form.get('connector_type', '').strip(),
            'location': request.form.get('location', '').strip(),
            'condition': request.form.get('condition', 'good'),
            'remarks': request.form.get('remarks', '').strip(),
            'purchase_date': request.form.get('purchase_date', ''),
            'purchase_cost': request.form.get('purchase_cost', ''),
            'warranty_expiry': request.form.get('warranty_expiry', ''),
            'rental_start_date': request.form.get('rental_start_date', ''),
            'rental_end_date': request.form.get('rental_end_date', ''),
            'rental_cost_monthly': request.form.get('rental_cost_monthly', '')
        }
        
        # Create asset
        success, message, asset = AssetService.create_asset(asset_data)
        
        flash(message, 'success' if success else 'error')
        
        if success:
            return redirect(url_for('assets.list_assets'))
    
    return render_template('add_asset.html')


@assets_bp.route('/edit/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def edit_asset(asset_id: int):
    """
    Edit asset route.
    
    Args:
        asset_id: ID of asset to edit
        
    GET: Display edit asset form
    POST: Process asset updates
    """
    asset = db.session.get(Asset, asset_id)
    if not asset:
        flash('Asset not found', 'error')
        return redirect(url_for('assets.list_assets'))
    
    if request.method == 'POST':
        # Get form data (same as add_asset)
        asset_data = {
            'asset_tag': request.form.get('asset_tag', '').strip(),
            'asset_type': request.form.get('asset_type', '').strip(),
            'serial_number': request.form.get('serial_number', '').strip(),
            'ownership_type': request.form.get('ownership_type', 'purchased'),
            'vendor_name': request.form.get('vendor_name', '').strip(),
            'brand': request.form.get('brand', '').strip(),
            'model': request.form.get('model', '').strip(),
            'processor': request.form.get('processor', '').strip(),
            'ram_gb': request.form.get('ram_gb', ''),
            'storage_gb': request.form.get('storage_gb', ''),
            'storage_type': request.form.get('storage_type', '').strip(),
            'port_count': request.form.get('port_count', ''),
            'network_type': request.form.get('network_type', '').strip(),
            'screen_size': request.form.get('screen_size', '').strip(),
            'resolution': request.form.get('resolution', '').strip(),
            'audio_type': request.form.get('audio_type', '').strip(),
            'connector_type': request.form.get('connector_type', '').strip(),
            'location': request.form.get('location', '').strip(),
            'condition': request.form.get('condition', 'good'),
            'remarks': request.form.get('remarks', '').strip(),
            'purchase_date': request.form.get('purchase_date', ''),
            'purchase_cost': request.form.get('purchase_cost', ''),
            'warranty_expiry': request.form.get('warranty_expiry', ''),
            'rental_start_date': request.form.get('rental_start_date', ''),
            'rental_end_date': request.form.get('rental_end_date', ''),
            'rental_cost_monthly': request.form.get('rental_cost_monthly', '')
        }
        
        # Update asset
        success, message, updated_asset = AssetService.update_asset(asset_id, asset_data)
        
        flash(message, 'success' if success else 'error')
        
        if success:
            return redirect(url_for('assets.list_assets'))
    
    return render_template('edit_asset.html', asset=asset)


@assets_bp.route('/delete/<int:asset_id>', methods=['POST'])
@login_required
def delete_asset(asset_id: int):
    """
    Delete asset route.
    
    Args:
        asset_id: ID of asset to delete
    """
    success, message = AssetService.delete_asset(asset_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('assets.list_assets'))


@assets_bp.route('/assign/<int:asset_id>', methods=['POST'])
@login_required
def assign_asset(asset_id: int):
    """
    Assign asset to user route.
    
    Args:
        asset_id: ID of asset to assign
    """
    username = request.form.get('username', '').strip()
    location = request.form.get('location', '').strip()
    
    if not username:
        flash('Username is required for assignment', 'error')
        return redirect(url_for('assets.list_assets'))
    
    success, message = AssetService.assign_asset(asset_id, username, location)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('assets.list_assets'))


@assets_bp.route('/unassign/<int:asset_id>', methods=['POST'])
@login_required
def unassign_asset(asset_id: int):
    """
    Unassign asset from user route.
    
    Args:
        asset_id: ID of asset to unassign
    """
    success, message = AssetService.unassign_asset(asset_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('assets.list_assets'))


@assets_bp.route('/export')
@login_required
def export_assets():
    """
    Export assets to CSV file.
    
    Returns:
        CSV file download
    """
    try:
        csv_data = AssetService.export_assets_csv()
        
        # Create file-like object
        output = io.StringIO(csv_data)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='assets_export.csv'
        )
        
    except Exception as e:
        flash(f"Error exporting assets: {str(e)}", 'error')
        return redirect(url_for('assets.list_assets'))


@assets_bp.route('/api/statistics')
@login_required
def api_statistics():
    """
    API endpoint for asset statistics.
    
    Returns:
        JSON response with asset statistics
    """
    try:
        stats = AssetService.get_asset_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
