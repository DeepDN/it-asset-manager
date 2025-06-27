"""
Access management models for application and GitHub permissions.

This module contains models for tracking user access to applications
and GitHub repositories with comprehensive audit trails.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import and_, or_

from ..core.database import db


class ApplicationAccess(db.Model):
    """
    Model for tracking user access to applications.
    
    Tracks permissions, access levels, and provides audit trail
    for application access management.
    """
    
    __tablename__ = 'application_access'
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False, index=True)
    application_name = db.Column(db.String(100), nullable=False, index=True)
    access_level = db.Column(db.String(50), nullable=False, index=True)  # Admin, Read, Write
    assign_date = db.Column(db.Date, nullable=False)
    remove_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active', nullable=False, index=True)  # active, revoked
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        """String representation of ApplicationAccess object."""
        return f'<ApplicationAccess {self.user_name}@{self.application_name}:{self.access_level}>'
    
    @property
    def is_active(self) -> bool:
        """Check if access is currently active."""
        return self.status == 'active' and (not self.remove_date or self.remove_date >= date.today())
    
    @property
    def days_since_assigned(self) -> int:
        """Calculate days since access was assigned."""
        return (date.today() - self.assign_date).days
    
    def revoke_access(self, remarks: Optional[str] = None) -> None:
        """
        Revoke user access to application.
        
        Args:
            remarks: Optional reason for revocation
        """
        self.status = 'revoked'
        self.remove_date = date.today()
        if remarks:
            self.remarks = remarks
        self.updated_at = datetime.utcnow()
    
    def reactivate_access(self, remarks: Optional[str] = None) -> None:
        """
        Reactivate previously revoked access.
        
        Args:
            remarks: Optional reason for reactivation
        """
        self.status = 'active'
        self.remove_date = None
        if remarks:
            self.remarks = remarks
        self.updated_at = datetime.utcnow()
    
    @classmethod
    def find_by_user(cls, username: str, active_only: bool = True) -> List['ApplicationAccess']:
        """
        Find all application access records for a user.
        
        Args:
            username: Username to search for
            active_only: If True, return only active access records
            
        Returns:
            List of ApplicationAccess objects
        """
        query = cls.query.filter_by(user_name=username)
        if active_only:
            query = query.filter_by(status='active')
        return query.all()
    
    @classmethod
    def find_by_application(cls, application_name: str, active_only: bool = True) -> List['ApplicationAccess']:
        """
        Find all users with access to a specific application.
        
        Args:
            application_name: Application name to search for
            active_only: If True, return only active access records
            
        Returns:
            List of ApplicationAccess objects
        """
        query = cls.query.filter_by(application_name=application_name)
        if active_only:
            query = query.filter_by(status='active')
        return query.all()
    
    @classmethod
    def find_user_app_access(cls, username: str, application_name: str) -> Optional['ApplicationAccess']:
        """
        Find specific user's access to an application.
        
        Args:
            username: Username to search for
            application_name: Application name to search for
            
        Returns:
            ApplicationAccess object if found, None otherwise
        """
        return cls.query.filter_by(
            user_name=username,
            application_name=application_name,
            status='active'
        ).first()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert access record to dictionary.
        
        Returns:
            Dictionary representation of access record
        """
        return {
            'id': self.id,
            'user_name': self.user_name,
            'application_name': self.application_name,
            'access_level': self.access_level,
            'assign_date': self.assign_date.isoformat() if self.assign_date else None,
            'remove_date': self.remove_date.isoformat() if self.remove_date else None,
            'status': self.status,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'days_since_assigned': self.days_since_assigned
        }


class GitHubAccess(db.Model):
    """
    Model for tracking user access to GitHub repositories.
    
    Provides comprehensive tracking of GitHub repository permissions
    with organization and repository level granularity.
    """
    
    __tablename__ = 'github_access'
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False, index=True)
    organization_name = db.Column(db.String(100), nullable=False, index=True)
    repo_name = db.Column(db.String(100), nullable=False, index=True)
    access_type = db.Column(db.String(50), nullable=False, index=True)  # Admin, Write, Read, Maintainer
    assign_date = db.Column(db.Date, nullable=False)
    remove_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active', nullable=False, index=True)  # active, revoked
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        """String representation of GitHubAccess object."""
        return f'<GitHubAccess {self.user_name}@{self.organization_name}/{self.repo_name}:{self.access_type}>'
    
    @property
    def is_active(self) -> bool:
        """Check if GitHub access is currently active."""
        return self.status == 'active' and (not self.remove_date or self.remove_date >= date.today())
    
    @property
    def days_since_assigned(self) -> int:
        """Calculate days since GitHub access was assigned."""
        return (date.today() - self.assign_date).days
    
    @property
    def full_repo_name(self) -> str:
        """Get full repository name in org/repo format."""
        return f"{self.organization_name}/{self.repo_name}"
    
    def revoke_access(self, remarks: Optional[str] = None) -> None:
        """
        Revoke user's GitHub repository access.
        
        Args:
            remarks: Optional reason for revocation
        """
        self.status = 'revoked'
        self.remove_date = date.today()
        if remarks:
            self.remarks = remarks
        self.updated_at = datetime.utcnow()
    
    def reactivate_access(self, remarks: Optional[str] = None) -> None:
        """
        Reactivate previously revoked GitHub access.
        
        Args:
            remarks: Optional reason for reactivation
        """
        self.status = 'active'
        self.remove_date = None
        if remarks:
            self.remarks = remarks
        self.updated_at = datetime.utcnow()
    
    def update_access_type(self, new_access_type: str, remarks: Optional[str] = None) -> None:
        """
        Update user's access type for the repository.
        
        Args:
            new_access_type: New access level (Admin, Write, Read, Maintainer)
            remarks: Optional reason for change
        """
        self.access_type = new_access_type
        if remarks:
            self.remarks = remarks
        self.updated_at = datetime.utcnow()
    
    @classmethod
    def find_by_user(cls, username: str, active_only: bool = True) -> List['GitHubAccess']:
        """
        Find all GitHub access records for a user.
        
        Args:
            username: Username to search for
            active_only: If True, return only active access records
            
        Returns:
            List of GitHubAccess objects
        """
        query = cls.query.filter_by(user_name=username)
        if active_only:
            query = query.filter_by(status='active')
        return query.all()
    
    @classmethod
    def find_by_repository(cls, organization: str, repo_name: str, active_only: bool = True) -> List['GitHubAccess']:
        """
        Find all users with access to a specific repository.
        
        Args:
            organization: GitHub organization name
            repo_name: Repository name
            active_only: If True, return only active access records
            
        Returns:
            List of GitHubAccess objects
        """
        query = cls.query.filter_by(organization_name=organization, repo_name=repo_name)
        if active_only:
            query = query.filter_by(status='active')
        return query.all()
    
    @classmethod
    def find_by_organization(cls, organization: str, active_only: bool = True) -> List['GitHubAccess']:
        """
        Find all access records for a GitHub organization.
        
        Args:
            organization: GitHub organization name
            active_only: If True, return only active access records
            
        Returns:
            List of GitHubAccess objects
        """
        query = cls.query.filter_by(organization_name=organization)
        if active_only:
            query = query.filter_by(status='active')
        return query.all()
    
    @classmethod
    def find_user_repo_access(cls, username: str, organization: str, repo_name: str) -> Optional['GitHubAccess']:
        """
        Find specific user's access to a repository.
        
        Args:
            username: Username to search for
            organization: GitHub organization name
            repo_name: Repository name
            
        Returns:
            GitHubAccess object if found, None otherwise
        """
        return cls.query.filter_by(
            user_name=username,
            organization_name=organization,
            repo_name=repo_name,
            status='active'
        ).first()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert GitHub access record to dictionary.
        
        Returns:
            Dictionary representation of GitHub access record
        """
        return {
            'id': self.id,
            'user_name': self.user_name,
            'organization_name': self.organization_name,
            'repo_name': self.repo_name,
            'full_repo_name': self.full_repo_name,
            'access_type': self.access_type,
            'assign_date': self.assign_date.isoformat() if self.assign_date else None,
            'remove_date': self.remove_date.isoformat() if self.remove_date else None,
            'status': self.status,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'days_since_assigned': self.days_since_assigned
        }
