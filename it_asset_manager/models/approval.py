from datetime import datetime
from typing import Optional, List, Dict, Any
from ..core.database import db


APPROVAL_STATUSES = ['pending', 'approved', 'rejected', 'cancelled']
APPROVAL_TYPES = ['asset_request', 'asset_assignment', 'access_request', 'purchase_request']


class ApprovalRequest(db.Model):
    __tablename__ = 'approval_requests'

    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(50), nullable=False, index=True)
    requester = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    priority = db.Column(db.String(20), default='medium')
    # Polymorphic reference to the entity being requested
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    # Currently assigned approver
    current_approver = db.Column(db.String(100))
    # Approval chain
    approval_chain = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApprovalAction(db.Model):
    __tablename__ = 'approval_actions'

    id = db.Column(db.Integer, primary_key=True)
    approval_id = db.Column(db.Integer, db.ForeignKey('approval_requests.id'), nullable=False, index=True)
    approver = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    approval = db.relationship('ApprovalRequest', backref=db.backref('actions', lazy='dynamic'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'approval_id': self.approval_id,
            'approver': self.approver,
            'action': self.action,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
