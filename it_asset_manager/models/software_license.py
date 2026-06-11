from datetime import datetime, date
from typing import Optional, List, Dict, Any
from ..core.database import db


class SoftwareLicense(db.Model):
    __tablename__ = 'software_licenses'

    id = db.Column(db.Integer, primary_key=True)
    license_name = db.Column(db.String(200), nullable=False, index=True)
    license_key = db.Column(db.String(500))
    publisher = db.Column(db.String(100))
    version = db.Column(db.String(50))
    license_type = db.Column(db.String(50), nullable=False, default='perpetual')
    total_seats = db.Column(db.Integer, default=1)
    assigned_seats = db.Column(db.Integer, default=0)
    available_seats = db.Column(db.Integer, default=1)
    purchase_date = db.Column(db.Date)
    purchase_cost = db.Column(db.Float)
    expiration_date = db.Column(db.Date)
    support_expiry = db.Column(db.Date)
    vendor_name = db.Column(db.String(100))
    vendor_contact = db.Column(db.String(200))
    status = db.Column(db.String(20), default='active', index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignments = db.relationship('LicenseAssignment', backref='license', lazy='dynamic')

    def __repr__(self):
        return f'<SoftwareLicense {self.license_name}>'

    @property
    def is_expired(self) -> bool:
        if self.expiration_date:
            return date.today() > self.expiration_date
        return False

    @property
    def utilization_percent(self) -> float:
        if self.total_seats <= 0:
            return 0.0
        return round((self.assigned_seats / self.total_seats) * 100, 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'license_name': self.license_name,
            'license_key': self.license_key,
            'publisher': self.publisher,
            'version': self.version,
            'license_type': self.license_type,
            'total_seats': self.total_seats,
            'assigned_seats': self.assigned_seats,
            'available_seats': self.total_seats - self.assigned_seats,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_cost': self.purchase_cost,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'support_expiry': self.support_expiry.isoformat() if self.support_expiry else None,
            'vendor_name': self.vendor_name,
            'vendor_contact': self.vendor_contact,
            'status': self.status,
            'notes': self.notes,
            'is_expired': self.is_expired,
            'utilization_percent': self.utilization_percent
        }


class LicenseAssignment(db.Model):
    __tablename__ = 'license_assignments'

    id = db.Column(db.Integer, primary_key=True)
    license_id = db.Column(db.Integer, db.ForeignKey('software_licenses.id'), nullable=False, index=True)
    assigned_to = db.Column(db.String(100), nullable=False, index=True)
    assigned_date = db.Column(db.Date, nullable=False, default=date.today)
    revoked_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active', index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<LicenseAssignment {self.license_id} -> {self.assigned_to}>'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'license_id': self.license_id,
            'assigned_to': self.assigned_to,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'revoked_date': self.revoked_date.isoformat() if self.revoked_date else None,
            'status': self.status,
            'notes': self.notes
        }
