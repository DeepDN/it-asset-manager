from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from ..services.depreciation_service import DepreciationService
from ..models.depreciation import AssetDepreciation
from ..models.asset import Asset
from ..core.database import db

depreciation_bp = Blueprint('depreciation', __name__, url_prefix='/depreciation')


@depreciation_bp.route('/')
@login_required
def list_depreciation():
    try:
        records = AssetDepreciation.query.order_by(AssetDepreciation.purchase_date.desc()).all()
        summary = DepreciationService.get_depreciation_summary()
        return render_template('depreciation/list.html', records=records, summary=summary)
    except Exception as e:
        flash(f'Error loading depreciation: {str(e)}', 'error')
        return render_template('depreciation/list.html', records=[], summary={})


@depreciation_bp.route('/setup/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def setup_depreciation(asset_id):
    try:
        asset = db.session.get(Asset, asset_id)
        if not asset:
            flash('Asset not found', 'error')
            return redirect(url_for('assets.list_assets'))
        if request.method == 'POST':
            method = request.form.get('method', 'straight_line')
            purchase_cost = float(request.form.get('purchase_cost', 0))
            salvage_value = float(request.form.get('salvage_value', 0))
            useful_life = int(request.form.get('useful_life_years', 1))
            purchase_date = request.form.get('purchase_date')
            success, msg, dep = DepreciationService.setup_depreciation(
                asset_id, method, purchase_cost, salvage_value, useful_life, purchase_date
            )
            flash(msg, 'success' if success else 'error')
            if success:
                return redirect(url_for('depreciation.list_depreciation'))
        return render_template('depreciation/setup.html', asset=asset)
    except Exception as e:
        flash(f'Error setting up depreciation: {str(e)}', 'error')
        return redirect(url_for('assets.list_assets'))


@depreciation_bp.route('/run', methods=['POST'])
@login_required
def run_depreciation():
    try:
        success, msg = DepreciationService.run_monthly_depreciation()
        flash(msg, 'success' if success else 'error')
    except Exception as e:
        flash(f'Error running depreciation: {str(e)}', 'error')
    return redirect(url_for('depreciation.list_depreciation'))


@depreciation_bp.route('/api/summary')
@login_required
def api_depreciation_summary():
    try:
        return jsonify(DepreciationService.get_depreciation_summary())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
