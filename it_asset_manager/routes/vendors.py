from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..services.vendor_service import VendorService
from ..models.vendor import Vendor
from ..core.database import db

vendors_bp = Blueprint('vendors', __name__, url_prefix='/vendors')


@vendors_bp.route('/')
@login_required
def list_vendors():
    try:
        vendors = Vendor.query.order_by(Vendor.vendor_name).all()
        return render_template('vendors/list.html', vendors=vendors)
    except Exception as e:
        flash(f'Error loading vendors: {str(e)}', 'error')
        return render_template('vendors/list.html', vendors=[])


@vendors_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_vendor():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            success, msg, vendor = VendorService.create_vendor(data)
            flash(msg, 'success' if success else 'error')
            if success:
                return redirect(url_for('vendors.list_vendors'))
        except Exception as e:
            flash(f'Error adding vendor: {str(e)}', 'error')
    return render_template('vendors/add.html')


@vendors_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_vendor(id):
    try:
        vendor = db.session.get(Vendor, id)
        if not vendor:
            flash('Vendor not found', 'error')
            return redirect(url_for('vendors.list_vendors'))
        if request.method == 'POST':
            data = request.form.to_dict()
            success, msg = VendorService.update_vendor(id, data)
            flash(msg, 'success' if success else 'error')
            if success:
                return redirect(url_for('vendors.list_vendors'))
        return render_template('vendors/edit.html', vendor=vendor)
    except Exception as e:
        flash(f'Error editing vendor: {str(e)}', 'error')
        return redirect(url_for('vendors.list_vendors'))


@vendors_bp.route('/api/stats')
@login_required
def api_vendor_stats():
    try:
        return jsonify(VendorService.get_vendor_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
