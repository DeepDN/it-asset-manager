from typing import List, Optional, Tuple
from ..models.user import User
from ..models.rbac import Role, ROLE_PERMISSIONS


class RBACService:
    @staticmethod
    def user_has_permission(user: User, permission: str) -> bool:
        role_name = user.role or 'employee'
        perms = ROLE_PERMISSIONS.get(role_name, '')
        return permission in perms

    @staticmethod
    def get_role_permissions(role_name: str) -> List[str]:
        perms = ROLE_PERMISSIONS.get(role_name, '')
        return [p.strip() for p in perms.split(',') if p.strip()]

    @staticmethod
    def update_user_role(user_id: int, new_role: str) -> Tuple[bool, str]:
        try:
            from ..core.database import db
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found"
            valid_roles = ['super_admin', 'it_admin', 'asset_manager', 'auditor', 'dept_manager', 'employee']
            if new_role not in valid_roles:
                return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            user.role = new_role
            db.session.commit()
            return True, f"User {user.username} role updated to {new_role}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_users_by_role(role_name: str) -> List[User]:
        return User.query.filter_by(role=role_name).all()
