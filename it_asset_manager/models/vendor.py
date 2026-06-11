from datetime import datetime, date
from typing import Optional, List, Dict, Any
from ..core.database import db


class Vendor(db.Model):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    website = db.Column(db.String(200))
    address = db.Column(db.Text)
    category = db.Column(db.String(50))
    support_contact = db.Column(db.String(200))
    support_email = db.Column(db.String(120))
    support_phone = db.Column(db.String(50))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='active', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Vendor {self.vendor_name}>'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'vendor_name': self.vendor_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'address': self.address,
            'category': self.category,
            'support_contact': self.support_contact,
            'support_email': self.support_email,
            'support_phone': self.support_phone,
            'notes': self.notes,
            'status': self.status
        }
