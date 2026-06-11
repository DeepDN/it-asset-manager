from datetime import date, datetime
from typing import List, Dict, Any, Optional, Tuple
from ..models.software_license import SoftwareLicense, LicenseAssignment
from ..core.database import db


class LicenseService:
    @staticmethod
    def create_license(data: Dict[str, Any]) -> Tuple[bool, str, Optional[SoftwareLicense]]:
        try:
            license = SoftwareLicense()
            for field in ['license_name', 'license_key', 'publisher', 'version',
                          'license_type', 'total_seats', 'purchase_cost',
                          'vendor_name', 'vendor_contact', 'notes']:
                if data.get(field) is not None:
                    setattr(license, field, data[field])
            for field in ['purchase_date', 'expiration_date', 'support_expiry']:
                if data.get(field):
                    setattr(license, field, datetime.strptime(data[field], '%Y-%m-%d').date())
            license.total_seats = int(data.get('total_seats', 1))
            license.available_seats = license.total_seats - license.assigned_seats
            if data.get('purchase_cost'):
                license.purchase_cost = float(data['purchase_cost'])
            db.session.add(license)
            db.session.commit()
            return True, f"License '{license.license_name}' created", license
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}", None

    @staticmethod
    def assign_license(license_id: int, user: str) -> Tuple[bool, str]:
        try:
            lic = db.session.get(SoftwareLicense, license_id)
            if not lic:
                return False, "License not found"
            if lic.assigned_seats >= lic.total_seats:
                return False, "No available seats"
            assignment = LicenseAssignment(license_id=license_id, assigned_to=user)
            db.session.add(assignment)
            lic.assigned_seats += 1
            lic.available_seats = lic.total_seats - lic.assigned_seats
            db.session.commit()
            return True, f"License assigned to {user}"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def revoke_license(assignment_id: int) -> Tuple[bool, str]:
        try:
            assignment = db.session.get(LicenseAssignment, assignment_id)
            if not assignment:
                return False, "Assignment not found"
            assignment.status = 'revoked'
            assignment.revoked_date = date.today()
            lic = db.session.get(SoftwareLicense, assignment.license_id)
            if lic:
                lic.assigned_seats = max(0, lic.assigned_seats - 1)
                lic.available_seats = lic.total_seats - lic.assigned_seats
            db.session.commit()
            return True, "License revoked"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_license_stats() -> Dict[str, Any]:
        total = SoftwareLicense.query.count()
        active = SoftwareLicense.query.filter_by(status='active').count()
        expired = SoftwareLicense.query.filter_by(status='expired').count()
        total_seats = db.session.query(db.func.sum(SoftwareLicense.total_seats)).scalar() or 0
        assigned_seats = db.session.query(db.func.sum(SoftwareLicense.assigned_seats)).scalar() or 0
        return {
            'total_licenses': total,
            'active_licenses': active,
            'expired_licenses': expired,
            'total_seats': total_seats,
            'assigned_seats': assigned_seats,
            'available_seats': total_seats - assigned_seats
        }
