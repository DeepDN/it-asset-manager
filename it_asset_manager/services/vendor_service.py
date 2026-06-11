from typing import List, Dict, Any, Optional, Tuple
from ..models.vendor import Vendor
from ..core.database import db


class VendorService:
    @staticmethod
    def create_vendor(data: Dict[str, Any]) -> Tuple[bool, str, Optional[Vendor]]:
        try:
            vendor = Vendor()
            for field in ['vendor_name', 'contact_person', 'email', 'phone',
                          'website', 'address', 'category', 'support_contact',
                          'support_email', 'support_phone', 'notes']:
                if data.get(field) is not None:
                    setattr(vendor, field, data[field])
            db.session.add(vendor)
            db.session.commit()
            return True, f"Vendor '{vendor.vendor_name}' created", vendor
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}", None

    @staticmethod
    def update_vendor(vendor_id: int, data: Dict[str, Any]) -> Tuple[bool, str]:
        try:
            vendor = db.session.get(Vendor, vendor_id)
            if not vendor:
                return False, "Vendor not found"
            for field in ['vendor_name', 'contact_person', 'email', 'phone',
                          'website', 'address', 'category', 'support_contact',
                          'support_email', 'support_phone', 'notes', 'status']:
                if data.get(field) is not None:
                    setattr(vendor, field, data[field])
            db.session.commit()
            return True, f"Vendor '{vendor.vendor_name}' updated"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_vendor_stats() -> Dict[str, Any]:
        total = Vendor.query.count()
        active = Vendor.query.filter_by(status='active').count()
        return {'total_vendors': total, 'active_vendors': active}
