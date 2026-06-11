from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from ..models.approval import ApprovalRequest, ApprovalAction
from ..core.database import db


class ApprovalService:
    @staticmethod
    def create_request(request_type: str, requester: str, description: str,
                       entity_type: Optional[str] = None, entity_id: Optional[int] = None,
                       priority: str = 'medium') -> Tuple[bool, str, Optional[ApprovalRequest]]:
        try:
            req = ApprovalRequest(
                request_type=request_type,
                requester=requester,
                description=description,
                entity_type=entity_type,
                entity_id=entity_id,
                priority=priority
            )
            db.session.add(req)
            db.session.commit()
            return True, "Approval request created", req
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}", None

    @staticmethod
    def approve_request(approval_id: int, approver: str, comment: Optional[str] = None) -> Tuple[bool, str]:
        return ApprovalService._take_action(approval_id, approver, 'approved', comment)

    @staticmethod
    def reject_request(approval_id: int, approver: str, comment: Optional[str] = None) -> Tuple[bool, str]:
        return ApprovalService._take_action(approval_id, approver, 'rejected', comment)

    @staticmethod
    def _take_action(approval_id: int, approver: str, action: str, comment: Optional[str] = None) -> Tuple[bool, str]:
        try:
            req = db.session.get(ApprovalRequest, approval_id)
            if not req:
                return False, "Request not found"
            if req.status != 'pending':
                return False, f"Request is already {req.status}"
            action_record = ApprovalAction(
                approval_id=approval_id,
                approver=approver,
                action=action,
                comment=comment
            )
            req.status = action
            db.session.add(action_record)
            db.session.commit()
            return True, f"Request {action}"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_pending_requests() -> List[ApprovalRequest]:
        return ApprovalRequest.query.filter_by(status='pending').order_by(ApprovalRequest.created_at.desc()).all()

    @staticmethod
    def get_requests_by_user(username: str) -> List[ApprovalRequest]:
        return ApprovalRequest.query.filter_by(requester=username).order_by(ApprovalRequest.created_at.desc()).all()
