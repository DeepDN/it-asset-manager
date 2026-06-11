from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..services.lifecycle_service import LifecycleService
from ..services.approval_service import ApprovalService
from ..models.asset import Asset
from ..models.user import User
from ..models.lifecycle import LIFECYCLE_STAGES
from ..core.database import db

lifecycle_bp = Blueprint('lifecycle', __name__, url_prefix='/lifecycle')


@lifecycle_bp.route('/timeline/<int:asset_id>')
@login_required
def asset_timeline(asset_id):
    try:
        asset = db.session.get(Asset, asset_id)
        if not asset:
            flash('Asset not found', 'error')
            return redirect(url_for('assets.list_assets'))
        entries = LifecycleService.get_asset_timeline(asset_id)
        return render_template('lifecycle/timeline.html', asset=asset, entries=entries)
    except Exception as e:
        flash(f'Error loading timeline: {str(e)}', 'error')
        return redirect(url_for('assets.list_assets'))


@lifecycle_bp.route('/transition/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def transition_asset(asset_id):
    try:
        asset = db.session.get(Asset, asset_id)
        if not asset:
            flash('Asset not found', 'error')
            return redirect(url_for('assets.list_assets'))
        if request.method == 'POST':
            new_stage = request.form.get('new_stage')
            success, msg = LifecycleService.transition_asset(asset_id, new_stage, current_user.username)
            flash(msg, 'success' if success else 'error')
            if success:
                return redirect(url_for('lifecycle.asset_timeline', asset_id=asset_id))
        allowed = Asset.ALLOWED_TRANSITIONS.get(asset.lifecycle_stage, [])
        return render_template('lifecycle/transition.html', asset=asset, allowed_stages=allowed)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('assets.list_assets'))


@lifecycle_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout_asset():
    try:
        if request.method == 'POST':
            asset_id = request.form.get('asset_id')
            assigned_user = request.form.get('assigned_user')
            expected_return = request.form.get('expected_return_date')
            condition = request.form.get('condition')
            notes = request.form.get('notes')
            success, msg = LifecycleService.checkout_asset(
                int(asset_id), assigned_user, expected_return,
                condition, current_user.username, notes
            )
            flash(msg, 'success' if success else 'error')
            if success:
                asset = Asset.query.get(int(asset_id))
                tag = asset.asset_tag if asset else f'ID:{asset_id}'
                ApprovalService.create_request(
                    request_type='asset_request',
                    requester=current_user.username,
                    description=f"Checkout of {tag} to {assigned_user}",
                    entity_type='asset',
                    entity_id=int(asset_id),
                    priority='medium'
                )
            return redirect(url_for('lifecycle.checkout_list'))
        assets = Asset.query.filter(Asset.lifecycle_stage.in_(['in_stock', 'returned'])).all()
        users = User.query.order_by(User.username).all()
        return render_template('lifecycle/checkout_form.html', assets=assets, users=users, today=__import__('datetime').date.today())
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('lifecycle.checkout_list'))


@lifecycle_bp.route('/checkin/<int:checkout_id>', methods=['GET', 'POST'])
@login_required
def checkin_asset(checkout_id):
    try:
        from ..models.lifecycle import CheckInOut
        checkout = db.session.get(CheckInOut, checkout_id)
        if not checkout:
            flash('Checkout record not found', 'error')
            return redirect(url_for('lifecycle.checkout_list'))
        if request.method == 'POST':
            condition = request.form.get('condition')
            notes = request.form.get('notes')
            success, msg = LifecycleService.checkin_asset(
                checkout.asset_id, condition, current_user.username, notes
            )
            flash(msg, 'success' if success else 'error')
            return redirect(url_for('lifecycle.checkout_list'))
        return render_template('lifecycle/checkin_form.html', checkout=checkout)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('lifecycle.checkout_list'))


@lifecycle_bp.route('/checkouts')
@login_required
def checkout_list():
    try:
        active = LifecycleService.get_active_checkouts()
        overdue = LifecycleService.get_overdue_checkouts()
        return render_template('lifecycle/checkout_list.html', active=active, overdue=overdue)
    except Exception as e:
        flash(f'Error loading checkouts: {str(e)}', 'error')
        return render_template('lifecycle/checkout_list.html', active=[], overdue=[])


@lifecycle_bp.route('/api/stats')
@login_required
def api_lifecycle_stats():
    try:
        return jsonify(LifecycleService.get_lifecycle_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
