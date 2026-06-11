from datetime import datetime
from typing import Optional, List, Dict, Any
from ..core.database import db


ROLES = ['super_admin', 'it_admin', 'asset_manager', 'auditor', 'dept_manager', 'employee']


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Role {self.name}>'

    def get_permissions_list(self) -> List[str]:
        if self.permissions:
            return [p.strip() for p in self.permissions.split(',')]
        return []

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.get_permissions_list()
        }


ROLE_PERMISSIONS = {
    'super_admin': 'assets.create,assets.read,assets.update,assets.delete,assets.assign,'
                   'users.create,users.read,users.update,users.delete,'
                   'licenses.create,licenses.read,licenses.update,licenses.delete,'
                   'vendors.create,vendors.read,vendors.update,vendors.delete,'
                   'reports.create,reports.read,reports.export,'
                   'settings.read,settings.update,'
                   'access.create,access.read,access.update,access.delete,'
                   'lifecycle.create,lifecycle.read,lifecycle.update,lifecycle.delete,'
                   'approval.create,approval.read,approval.approve',
    'it_admin': 'assets.create,assets.read,assets.update,assets.assign,'
                'users.read,users.update,'
                'licenses.create,licenses.read,licenses.update,'
                'vendors.read,'
                'reports.read,reports.export,'
                'access.create,access.read,access.update,'
                'lifecycle.create,lifecycle.read,lifecycle.update',
    'asset_manager': 'assets.create,assets.read,assets.update,assets.assign,'
                     'licenses.read,licenses.update,'
                     'vendors.read,'
                     'reports.read,reports.export,'
                     'lifecycle.read,lifecycle.update',
    'auditor': 'assets.read,'
               'users.read,'
               'licenses.read,'
               'vendors.read,'
               'reports.read,reports.export,'
               'access.read,'
               'lifecycle.read',
    'dept_manager': 'assets.read,'
                    'licenses.read,'
                    'reports.read,'
                    'access.read',
    'employee': 'assets.read(own),'
                'access.read(own)'
}
