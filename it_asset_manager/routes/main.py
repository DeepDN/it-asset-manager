from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import login_required, current_user

from ..services.asset_service import AssetService
from ..services.access_service import AccessService
from ..services.license_service import LicenseService
from ..services.vendor_service import VendorService
from ..services.lifecycle_service import LifecycleService
from ..services.report_service import ReportService
from ..models.asset import Asset
from ..models.lifecycle import CheckInOut
from ..models.software_license import SoftwareLicense
from ..models.vendor import Vendor
from ..core.database import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/asset/<asset_tag>')
def public_asset_view(asset_tag):
    try:
        asset = Asset.query.filter_by(asset_tag=asset_tag).first()
        if not asset:
            abort(404)
        return render_template('public_asset.html', asset=asset)
    except Exception as e:
        return render_template('public_asset.html', asset=None, error=str(e))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        total_assets = Asset.query.count()
        assigned_assets = Asset.query.filter_by(lifecycle_stage='assigned').count()
        in_stock = Asset.query.filter_by(lifecycle_stage='in_stock').count()
        under_maintenance = Asset.query.filter_by(lifecycle_stage='under_maintenance').count()
        retired = Asset.query.filter_by(lifecycle_stage='retired').count()

        total_licenses = SoftwareLicense.query.count()
        total_vendors = Vendor.query.count()
        active_checkouts = CheckInOut.query.filter_by(status='checked_out').count()
        from datetime import date
        overdue_checkouts = CheckInOut.query.filter(
            CheckInOut.status == 'checked_out',
            CheckInOut.expected_return_date.isnot(None),
            CheckInOut.expected_return_date < date.today()
        ).count()

        warranty_expiring = Asset.query.filter(
            Asset.warranty_expiry.isnot(None),
            Asset.warranty_expiry >= date.today()
        ).count()

        asset_stats = AssetService.get_asset_statistics()
        access_stats = AccessService.get_access_statistics()

        recent = CheckInOut.query.order_by(CheckInOut.created_at.desc()).limit(5).all()
        recent_activity = []
        for c in recent:
            action = 'Check Out' if c.status == 'checked_out' else 'Check In'
            recent_activity.append({
                'action': f'{action}: {c.asset_tag or "N/A"}',
                'description': f'by {c.checked_out_by or "unknown"}',
                'time': c.created_at.strftime('%d %b %Y') if c.created_at else '',
                'color': 'success' if c.status == 'checked_out' else 'info'
            })

        return render_template(
            'dashboard.html',
            total_assets=total_assets,
            assigned_assets=assigned_assets,
            in_stock=in_stock,
            under_maintenance=under_maintenance,
            retired=retired,
            total_licenses=total_licenses,
            total_vendors=total_vendors,
            active_checkouts=active_checkouts,
            overdue_checkouts=overdue_checkouts,
            warranty_expiring=warranty_expiring,
            asset_stats=asset_stats,
            access_stats=access_stats,
            recent_activity=recent_activity,
            user=current_user
        )
    except Exception as e:
        return render_template(
            'dashboard.html',
            error=f"Error loading dashboard: {str(e)}",
            user=current_user
        )
