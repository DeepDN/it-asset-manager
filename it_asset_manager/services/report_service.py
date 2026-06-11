from datetime import date, datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import func
from ..models.asset import Asset
from ..models.access import ApplicationAccess, GitHubAccess
from ..models.lifecycle import CheckInOut, AssetTimeline
from ..models.software_license import SoftwareLicense
from ..models.vendor import Vendor
from ..models.depreciation import AssetDepreciation
from ..core.database import db


class ReportService:
    @staticmethod
    def get_executive_dashboard() -> Dict[str, Any]:
        total_assets = Asset.query.count()
        active_assets = Asset.query.filter(Asset.lifecycle_stage.in_(['assigned', 'in_stock'])).count()
        assigned_assets = Asset.query.filter_by(lifecycle_stage='assigned').count()
        in_repair = Asset.query.filter_by(lifecycle_stage='under_maintenance').count()
        warranty_expiring = Asset.query.filter(
            Asset.warranty_expiry.isnot(None),
            Asset.warranty_expiry >= date.today(),
            Asset.warranty_expiry <= date.today() + timedelta(days=90)
        ).count()
        licenses_expiring = SoftwareLicense.query.filter(
            SoftwareLicense.expiration_date.isnot(None),
            SoftwareLicense.expiration_date >= date.today(),
            SoftwareLicense.expiration_date <= date.today() + timedelta(days=90)
        ).count()

        assets_by_dept = db.session.query(
            Asset.assigned_to, func.count(Asset.id)
        ).filter(Asset.lifecycle_stage == 'assigned').group_by(Asset.assigned_to).all()

        assets_by_location = db.session.query(
            Asset.location, func.count(Asset.id)
        ).filter(Asset.location.isnot(None)).group_by(Asset.location).all()

        assets_by_category = db.session.query(
            Asset.asset_category, func.count(Asset.id)
        ).group_by(Asset.asset_category).all()

        assets_by_type = db.session.query(
            Asset.asset_type, func.count(Asset.id)
        ).group_by(Asset.asset_type).all()

        return {
            'total_assets': total_assets,
            'active_assets': active_assets,
            'assigned_assets': assigned_assets,
            'in_repair': in_repair,
            'warranty_expiring': warranty_expiring,
            'licenses_expiring': licenses_expiring,
            'assets_by_department': dict(assets_by_dept),
            'assets_by_location': dict(assets_by_location),
            'assets_by_category': dict(assets_by_category),
            'assets_by_type': dict(assets_by_type)
        }

    @staticmethod
    def get_warranty_report() -> List[Dict[str, Any]]:
        assets = Asset.query.filter(Asset.warranty_expiry.isnot(None)).order_by(Asset.warranty_expiry.asc()).all()
        return [{
            'asset_tag': a.asset_tag,
            'brand': a.brand,
            'model': a.model,
            'serial_number': a.serial_number,
            'warranty_expiry': a.warranty_expiry.isoformat() if a.warranty_expiry else None,
            'days_remaining': (a.warranty_expiry - date.today()).days if a.warranty_expiry else None,
            'status': 'expired' if a.is_warranty_expired else 'active'
        } for a in assets]

    @staticmethod
    def get_financial_report() -> Dict[str, Any]:
        purchase_total = db.session.query(func.sum(Asset.purchase_cost)).scalar() or 0
        lease_monthly = db.session.query(func.sum(Asset.rental_cost_monthly)).scalar() or 0
        assets_with_cost = Asset.query.filter(Asset.purchase_cost.isnot(None)).count()
        dep_summary = DepreciationService.get_depreciation_summary() if 'DepreciationService' in dir() else {}
        return {
            'total_purchase_value': purchase_total,
            'monthly_lease_cost': lease_monthly,
            'assets_with_cost': assets_with_cost,
            'depreciation': dep_summary
        }

    @staticmethod
    def get_audit_report() -> Dict[str, Any]:
        return {
            'total_assets': Asset.query.count(),
            'assigned': Asset.query.filter_by(lifecycle_stage='assigned').count(),
            'unassigned': Asset.query.filter_by(lifecycle_stage='in_stock').count(),
            'maintenance': Asset.query.filter_by(lifecycle_stage='under_maintenance').count(),
            'retired': Asset.query.filter_by(lifecycle_stage='retired').count(),
            'active_app_access': ApplicationAccess.query.filter_by(status='active').count(),
            'active_github_access': GitHubAccess.query.filter_by(status='active').count(),
            'total_licenses': SoftwareLicense.query.count(),
            'active_checkouts': CheckInOut.query.filter_by(status='checked_out').count(),
            'overdue_checkouts': CheckInOut.query.filter(
                CheckInOut.status == 'checked_out',
                CheckInOut.expected_return_date.isnot(None),
                CheckInOut.expected_return_date < date.today()
            ).count()
        }

    @staticmethod
    def get_utilization_report() -> Dict[str, Any]:
        total = Asset.query.count() or 1
        assigned = Asset.query.filter_by(lifecycle_stage='assigned').count()
        in_stock = Asset.query.filter_by(lifecycle_stage='in_stock').count()
        return {
            'utilization_rate': round((assigned / total) * 100, 1),
            'total_assets': total,
            'in_use': assigned,
            'available': in_stock,
            'license_utilization': ReportService._get_license_utilization()
        }

    @staticmethod
    def _get_license_utilization() -> Dict[str, Any]:
        total_seats = db.session.query(func.sum(SoftwareLicense.total_seats)).scalar() or 0
        assigned_seats = db.session.query(func.sum(SoftwareLicense.assigned_seats)).scalar() or 0
        return {
            'total_seats': total_seats,
            'assigned_seats': assigned_seats,
            'utilization': round((assigned_seats / total_seats) * 100, 1) if total_seats > 0 else 0
        }


from .depreciation_service import DepreciationService
