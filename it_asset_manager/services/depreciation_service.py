from datetime import date, datetime
from typing import Dict, Any, Optional, Tuple
from ..models.depreciation import AssetDepreciation
from ..models.asset import Asset
from ..core.database import db


class DepreciationService:
    @staticmethod
    def setup_depreciation(asset_id: int, method: str, purchase_cost: float,
                           salvage_value: float, useful_life_years: int,
                           purchase_date: Optional[str] = None) -> Tuple[bool, str, Optional[AssetDepreciation]]:
        try:
            asset = db.session.get(Asset, asset_id)
            if not asset:
                return False, "Asset not found", None
            existing = AssetDepreciation.query.filter_by(asset_id=asset_id).first()
            if existing:
                return False, "Depreciation already exists for this asset", None
            dep = AssetDepreciation(
                asset_id=asset_id,
                method=method,
                purchase_cost=purchase_cost,
                salvage_value=salvage_value,
                useful_life_years=useful_life_years,
                current_book_value=purchase_cost,
                purchase_date=datetime.strptime(purchase_date, '%Y-%m-%d').date() if purchase_date else date.today()
            )
            db.session.add(dep)
            db.session.commit()
            return True, "Depreciation record created", dep
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}", None

    @staticmethod
    def run_monthly_depreciation() -> Tuple[bool, str]:
        try:
            records = AssetDepreciation.query.all()
            count = 0
            for dep in records:
                if dep.current_book_value > dep.salvage_value:
                    dep.apply_depreciation()
                    count += 1
            db.session.commit()
            return True, f"Depreciation applied to {count} assets"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_depreciation_summary() -> Dict[str, Any]:
        total_cost = db.session.query(db.func.sum(AssetDepreciation.purchase_cost)).scalar() or 0
        total_book = db.session.query(db.func.sum(AssetDepreciation.current_book_value)).scalar() or 0
        total_depreciated = total_cost - total_book
        records_count = AssetDepreciation.query.count()
        return {
            'total_purchase_cost': total_cost,
            'total_book_value': total_book,
            'total_depreciated': total_depreciated,
            'records_count': records_count
        }
