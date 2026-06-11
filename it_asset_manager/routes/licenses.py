from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..services.license_service import LicenseService
from ..models.software_license import SoftwareLicense, LicenseAssignment
from ..core.database import db

licenses_bp = Blueprint('licenses', __name__, url_prefix='/licenses')


@licenses_bp.route('/')
@login_required
def list_licenses():
    try:
        licenses_list = SoftwareLicense.query.order_by(SoftwareLicense.license_name).all()
        return render_template('licenses/list.html', licenses=licenses_list)
    except Exception as e:
        flash(f'Error loading licenses: {str(e)}', 'error')
        return render_template('licenses/list.html', licenses=[])


@licenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_license():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            success, msg, lic = LicenseService.create_license(data)
            flash(msg, 'success' if success else 'error')
            if success:
                return redirect(url_for('licenses.list_licenses'))
        except Exception as e:
            flash(f'Error adding license: {str(e)}', 'error')
    return render_template('licenses/add.html')


@licenses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_license(id):
    try:
        lic = db.session.get(SoftwareLicense, id)
        if not lic:
            flash('License not found', 'error')
            return redirect(url_for('licenses.list_licenses'))
        if request.method == 'POST':
            data = request.form.to_dict()
            for field in ['license_name', 'license_key', 'publisher', 'version',
                          'license_type', 'vendor_name', 'vendor_contact', 'notes', 'status']:
                if data.get(field) is not None:
                    setattr(lic, field, data[field])
            if data.get('total_seats'):
                lic.total_seats = int(data['total_seats'])
                lic.available_seats = lic.total_seats - lic.assigned_seats
            if data.get('purchase_cost'):
                lic.purchase_cost = float(data['purchase_cost'])
            from datetime import datetime
            for field in ['purchase_date', 'expiration_date', 'support_expiry']:
                if data.get(field):
                    setattr(lic, field, datetime.strptime(data[field], '%Y-%m-%d').date())
            db.session.commit()
            flash('License updated', 'success')
            return redirect(url_for('licenses.list_licenses'))
        return render_template('licenses/edit.html', lic=lic)
    except Exception as e:
        flash(f'Error editing license: {str(e)}', 'error')
        return redirect(url_for('licenses.list_licenses'))


@licenses_bp.route('/detail/<int:id>')
@login_required
def license_detail(id):
    try:
        lic = db.session.get(SoftwareLicense, id)
        if not lic:
            flash('License not found', 'error')
            return redirect(url_for('licenses.list_licenses'))
        assignments = LicenseAssignment.query.filter_by(license_id=id).order_by(LicenseAssignment.assigned_date.desc()).all()
        return render_template('licenses/detail.html', lic=lic, assignments=assignments)
    except Exception as e:
        flash(f'Error loading license: {str(e)}', 'error')
        return redirect(url_for('licenses.list_licenses'))


@licenses_bp.route('/assign/<int:id>', methods=['POST'])
@login_required
def assign_license(id):
    try:
        user = request.form.get('assigned_to')
        if not user:
            flash('User is required', 'error')
            return redirect(url_for('licenses.license_detail', id=id))
        success, msg = LicenseService.assign_license(id, user)
        flash(msg, 'success' if success else 'error')
    except Exception as e:
        flash(f'Error assigning license: {str(e)}', 'error')
    return redirect(url_for('licenses.license_detail', id=id))


@licenses_bp.route('/revoke/<int:assignment_id>', methods=['POST'])
@login_required
def revoke_license(assignment_id):
    try:
        success, msg = LicenseService.revoke_license(assignment_id)
        flash(msg, 'success' if success else 'error')
    except Exception as e:
        flash(f'Error revoking license: {str(e)}', 'error')
    assignment = db.session.get(LicenseAssignment, assignment_id)
    lic_id = assignment.license_id if assignment else None
    return redirect(url_for('licenses.license_detail', id=lic_id) if lic_id else url_for('licenses.list_licenses'))


@licenses_bp.route('/api/stats')
@login_required
def api_license_stats():
    try:
        return jsonify(LicenseService.get_license_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
