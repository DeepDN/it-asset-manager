from datetime import date, datetime
from typing import List, Dict, Any, Optional, Tuple
from ..models.asset import Asset
from ..models.lifecycle import AssetTimeline, CheckInOut
from ..core.database import db


class LifecycleService:
    @staticmethod
    def add_timeline_entry(asset_id: int, action: str, description: Optional[str] = None,
                           performed_by: Optional[str] = None,
                           previous_status: Optional[str] = None,
                           new_status: Optional[str] = None) -> Tuple[bool, str]:
        try:
            entry = AssetTimeline(
                asset_id=asset_id,
                action=action,
                description=description,
                performed_by=performed_by,
                previous_status=previous_status,
                new_status=new_status
            )
            db.session.add(entry)
            db.session.commit()
            return True, "Timeline entry added"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_asset_timeline(asset_id: int) -> List[AssetTimeline]:
        return AssetTimeline.query.filter_by(asset_id=asset_id).order_by(AssetTimeline.created_at.desc()).all()

    @staticmethod
    def transition_asset(asset_id: int, new_stage: str, user: Optional[str] = None) -> Tuple[bool, str]:
        try:
            asset = db.session.get(Asset, asset_id)
            if not asset:
                return False, "Asset not found"
            old_stage = asset.lifecycle_stage
            if not asset.transition_to(new_stage, user):
                return False, f"Cannot transition from {old_stage} to {new_stage}"
            db.session.commit()
            LifecycleService.add_timeline_entry(
                asset_id, f"Status changed to {new_stage}",
                f"Transitioned from {old_stage} to {new_stage}",
                user, old_stage, new_stage
            )
            return True, f"Asset transitioned from {old_stage} to {new_stage}"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def checkout_asset(asset_id: int, assigned_user: str, expected_return: Optional[str] = None,
                       condition: Optional[str] = None, checked_by: Optional[str] = None,
                       notes: Optional[str] = None) -> Tuple[bool, str]:
        try:
            asset = db.session.get(Asset, asset_id)
            if not asset:
                return False, "Asset not found"
            if asset.lifecycle_stage not in ['in_stock', 'returned']:
                return False, f"Asset is in '{asset.lifecycle_stage}' stage and cannot be checked out"
            checkout = CheckInOut(
                asset_id=asset_id,
                assigned_user=assigned_user,
                expected_return_date=datetime.strptime(expected_return, '%Y-%m-%d').date() if expected_return else None,
                condition_at_checkout=condition,
                checked_out_by=checked_by,
                notes=notes
            )
            asset.assign_to_user(assigned_user)
            db.session.add(checkout)
            db.session.commit()
            LifecycleService.add_timeline_entry(
                asset_id, "Asset checked out",
                f"Checked out to {assigned_user}", checked_by,
                'in_stock', 'assigned'
            )
            return True, f"Asset checked out to {assigned_user}"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def checkin_asset(asset_id: int, condition: Optional[str] = None,
                      checked_by: Optional[str] = None, notes: Optional[str] = None) -> Tuple[bool, str]:
        try:
            asset = db.session.get(Asset, asset_id)
            if not asset:
                return False, "Asset not found"
            active_checkout = CheckInOut.query.filter_by(
                asset_id=asset_id, status='checked_out'
            ).first()
            if not active_checkout:
                return False, "No active checkout found for this asset"
            active_checkout.check_in(condition, checked_by, notes)
            asset.unassign()
            if condition:
                asset.condition = condition
            db.session.commit()
            LifecycleService.add_timeline_entry(
                asset_id, "Asset checked in",
                f"Returned by {active_checkout.assigned_user}", checked_by,
                'assigned', 'in_stock'
            )
            return True, "Asset checked in successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_active_checkouts() -> List[CheckInOut]:
        return CheckInOut.query.filter_by(status='checked_out').order_by(CheckInOut.assignment_date.desc()).all()

    @staticmethod
    def get_overdue_checkouts() -> List[CheckInOut]:
        today = date.today()
        return CheckInOut.query.filter(
            CheckInOut.status == 'checked_out',
            CheckInOut.expected_return_date.isnot(None),
            CheckInOut.expected_return_date < today
        ).order_by(CheckInOut.expected_return_date.asc()).all()

    @staticmethod
    def get_lifecycle_stats() -> Dict[str, Any]:
        stages = db.session.query(
            Asset.lifecycle_stage,
            db.func.count(Asset.id).label('count')
        ).group_by(Asset.lifecycle_stage).all()
        active_checkouts = CheckInOut.query.filter_by(status='checked_out').count()
        overdue = len(LifecycleService.get_overdue_checkouts())
        return {
            'by_stage': {item.lifecycle_stage: item.count for item in stages},
            'active_checkouts': active_checkouts,
            'overdue_checkouts': overdue
        }
