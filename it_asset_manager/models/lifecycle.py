from datetime import datetime, date
from typing import Optional, List, Dict, Any
from ..core.database import db


LIFECYCLE_STAGES = [
    'requested', 'purchased', 'in_stock', 'assigned',
    'under_maintenance', 'returned', 'retired', 'disposed'
]


class AssetTimeline(db.Model):
    __tablename__ = 'asset_timeline'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    performed_by = db.Column(db.String(100))
    previous_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    asset = db.relationship('Asset', backref=db.backref('timeline_entries', lazy='dynamic'))

    def __repr__(self):
        return f'<AssetTimeline {self.asset_id}: {self.action}>'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'action': self.action,
            'description': self.description,
            'performed_by': self.performed_by,
            'previous_status': self.previous_status,
            'new_status': self.new_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CheckInOut(db.Model):
    __tablename__ = 'check_in_out'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False, index=True)
    assigned_user = db.Column(db.String(100), nullable=False, index=True)
    assignment_date = db.Column(db.Date, nullable=False, default=date.today)
    expected_return_date = db.Column(db.Date)
    actual_return_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='checked_out', nullable=False)
    condition_at_checkout = db.Column(db.String(20))
    condition_at_return = db.Column(db.String(20))
    notes = db.Column(db.Text)
    checked_out_by = db.Column(db.String(100))
    checked_in_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asset = db.relationship('Asset', backref=db.backref('checkinout_entries', lazy='dynamic'))

    def __repr__(self):
        return f'<CheckInOut {self.asset_id} -> {self.assigned_user}>'

    @property
    def is_overdue(self) -> bool:
        if self.status == 'checked_out' and self.expected_return_date:
            return date.today() > self.expected_return_date
        return False

    @property
    def duration_days(self) -> Optional[int]:
        start = self.assignment_date
        end = self.actual_return_date or date.today()
        return (end - start).days

    def check_in(self, condition: Optional[str] = None, checked_by: Optional[str] = None, notes: Optional[str] = None):
        self.status = 'returned'
        self.actual_return_date = date.today()
        if condition:
            self.condition_at_return = condition
        if checked_by:
            self.checked_in_by = checked_by
        if notes:
            self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'assigned_user': self.assigned_user,
            'assignment_date': self.assignment_date.isoformat() if self.assignment_date else None,
            'expected_return_date': self.expected_return_date.isoformat() if self.expected_return_date else None,
            'actual_return_date': self.actual_return_date.isoformat() if self.actual_return_date else None,
            'status': self.status,
            'condition_at_checkout': self.condition_at_checkout,
            'condition_at_return': self.condition_at_return,
            'notes': self.notes,
            'checked_out_by': self.checked_out_by,
            'checked_in_by': self.checked_in_by,
            'is_overdue': self.is_overdue,
            'duration_days': self.duration_days
        }
