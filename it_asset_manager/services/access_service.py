"""
Access management service for application and GitHub permissions.

This module contains the AccessService class that handles business logic
for managing user access to applications and GitHub repositories.
"""

from datetime import date, datetime
from typing import List, Dict, Any, Optional, Tuple
import csv
import io

from ..models.access import ApplicationAccess, GitHubAccess
from ..core.database import db


class AccessService:
    """Service class for access management business logic."""
    
    # Application Access Management
    
    @staticmethod
    def grant_application_access(
        username: str,
        application_name: str,
        access_level: str,
        remarks: Optional[str] = None
    ) -> Tuple[bool, str, Optional[ApplicationAccess]]:
        """
        Grant user access to an application.
        
        Args:
            username: Username to grant access to
            application_name: Name of the application
            access_level: Access level (Admin, Read, Write)
            remarks: Optional remarks
            
        Returns:
            Tuple of (success, message, access_object)
        """
        try:
            # Validate access level
            valid_levels = ['Admin', 'Read', 'Write']
            if access_level not in valid_levels:
                return False, f"Invalid access level. Must be one of: {', '.join(valid_levels)}", None
            
            # Check for existing active access
            existing_access = ApplicationAccess.find_user_app_access(username, application_name)
            if existing_access:
                return False, f"User {username} already has {existing_access.access_level} access to {application_name}", None
            
            # Create new access record
            access = ApplicationAccess()
            access.user_name = username
            access.application_name = application_name
            access.access_level = access_level
            access.assign_date = date.today()
            access.status = 'active'
            if remarks:
                access.remarks = remarks
            
            db.session.add(access)
            db.session.commit()
            
            return True, f"Granted {access_level} access to {application_name} for {username}", access
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error granting application access: {str(e)}", None
    
    @staticmethod
    def revoke_application_access(access_id: int, remarks: Optional[str] = None) -> Tuple[bool, str]:
        """
        Revoke application access.
        
        Args:
            access_id: ID of access record to revoke
            remarks: Optional reason for revocation
            
        Returns:
            Tuple of (success, message)
        """
        try:
            access = db.session.get(ApplicationAccess, access_id)
            if not access:
                return False, "Access record not found"
            
            if access.status == 'revoked':
                return False, "Access is already revoked"
            
            access.revoke_access(remarks)
            db.session.commit()
            
            return True, f"Revoked {access.access_level} access to {access.application_name} for {access.user_name}"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error revoking application access: {str(e)}"
    
    @staticmethod
    def update_application_access(
        access_id: int,
        new_access_level: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Update application access level.
        
        Args:
            access_id: ID of access record to update
            new_access_level: New access level
            remarks: Optional remarks
            
        Returns:
            Tuple of (success, message)
        """
        try:
            access = db.session.get(ApplicationAccess, access_id)
            if not access:
                return False, "Access record not found"
            
            if access.status != 'active':
                return False, "Cannot update inactive access record"
            
            if new_access_level:
                valid_levels = ['Admin', 'Read', 'Write']
                if new_access_level not in valid_levels:
                    return False, f"Invalid access level. Must be one of: {', '.join(valid_levels)}"
                
                old_level = access.access_level
                access.access_level = new_access_level
                
                if remarks:
                    access.remarks = remarks
                
                access.updated_at = datetime.utcnow()
                db.session.commit()
                
                return True, f"Updated access level from {old_level} to {new_access_level} for {access.user_name}"
            
            return False, "No changes specified"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating application access: {str(e)}"
    
    # GitHub Access Management
    
    @staticmethod
    def grant_github_access(
        username: str,
        organization: str,
        repo_name: str,
        access_type: str,
        remarks: Optional[str] = None
    ) -> Tuple[bool, str, Optional[GitHubAccess]]:
        """
        Grant user access to a GitHub repository.
        
        Args:
            username: Username to grant access to
            organization: GitHub organization name
            repo_name: Repository name
            access_type: Access type (Admin, Write, Read, Maintainer)
            remarks: Optional remarks
            
        Returns:
            Tuple of (success, message, access_object)
        """
        try:
            # Validate access type
            valid_types = ['Admin', 'Write', 'Read', 'Maintainer']
            if access_type not in valid_types:
                return False, f"Invalid access type. Must be one of: {', '.join(valid_types)}", None
            
            # Check for existing active access
            existing_access = GitHubAccess.find_user_repo_access(username, organization, repo_name)
            if existing_access:
                return False, f"User {username} already has {existing_access.access_type} access to {organization}/{repo_name}", None
            
            # Create new access record
            access = GitHubAccess()
            access.user_name = username
            access.organization_name = organization
            access.repo_name = repo_name
            access.access_type = access_type
            access.assign_date = date.today()
            access.status = 'active'
            if remarks:
                access.remarks = remarks
            
            db.session.add(access)
            db.session.commit()
            
            return True, f"Granted {access_type} access to {organization}/{repo_name} for {username}", access
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error granting GitHub access: {str(e)}", None
    
    @staticmethod
    def revoke_github_access(access_id: int, remarks: Optional[str] = None) -> Tuple[bool, str]:
        """
        Revoke GitHub repository access.
        
        Args:
            access_id: ID of access record to revoke
            remarks: Optional reason for revocation
            
        Returns:
            Tuple of (success, message)
        """
        try:
            access = db.session.get(GitHubAccess, access_id)
            if not access:
                return False, "Access record not found"
            
            if access.status == 'revoked':
                return False, "Access is already revoked"
            
            access.revoke_access(remarks)
            db.session.commit()
            
            return True, f"Revoked {access.access_type} access to {access.full_repo_name} for {access.user_name}"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error revoking GitHub access: {str(e)}"
    
    @staticmethod
    def update_github_access(
        access_id: int,
        new_access_type: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Update GitHub repository access type.
        
        Args:
            access_id: ID of access record to update
            new_access_type: New access type
            remarks: Optional remarks
            
        Returns:
            Tuple of (success, message)
        """
        try:
            access = db.session.get(GitHubAccess, access_id)
            if not access:
                return False, "Access record not found"
            
            if access.status != 'active':
                return False, "Cannot update inactive access record"
            
            if new_access_type:
                valid_types = ['Admin', 'Write', 'Read', 'Maintainer']
                if new_access_type not in valid_types:
                    return False, f"Invalid access type. Must be one of: {', '.join(valid_types)}"
                
                old_type = access.access_type
                access.update_access_type(new_access_type, remarks)
                db.session.commit()
                
                return True, f"Updated access type from {old_type} to {new_access_type} for {access.user_name}"
            
            return False, "No changes specified"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating GitHub access: {str(e)}"
    
    # Statistics and Reporting
    
    @staticmethod
    def get_access_statistics() -> Dict[str, Any]:
        """
        Get comprehensive access statistics.
        
        Returns:
            Dictionary containing access statistics
        """
        try:
            # Application access statistics
            total_app_access = ApplicationAccess.query.count()
            active_app_access = ApplicationAccess.query.filter_by(status='active').count()
            revoked_app_access = ApplicationAccess.query.filter_by(status='revoked').count()
            
            # GitHub access statistics
            total_github_access = GitHubAccess.query.count()
            active_github_access = GitHubAccess.query.filter_by(status='active').count()
            revoked_github_access = GitHubAccess.query.filter_by(status='revoked').count()
            
            # Access by level/type
            app_access_levels = db.session.query(
                ApplicationAccess.access_level,
                db.func.count(ApplicationAccess.id).label('count')
            ).filter_by(status='active').group_by(ApplicationAccess.access_level).all()
            
            github_access_types = db.session.query(
                GitHubAccess.access_type,
                db.func.count(GitHubAccess.id).label('count')
            ).filter_by(status='active').group_by(GitHubAccess.access_type).all()
            
            # Top applications and repositories
            top_applications = db.session.query(
                ApplicationAccess.application_name,
                db.func.count(ApplicationAccess.id).label('count')
            ).filter_by(status='active').group_by(ApplicationAccess.application_name).order_by(db.func.count(ApplicationAccess.id).desc()).limit(10).all()
            
            top_repositories = db.session.query(
                GitHubAccess.organization_name,
                GitHubAccess.repo_name,
                db.func.count(GitHubAccess.id).label('count')
            ).filter_by(status='active').group_by(GitHubAccess.organization_name, GitHubAccess.repo_name).order_by(db.func.count(GitHubAccess.id).desc()).limit(10).all()
            
            return {
                'application_access': {
                    'total': total_app_access,
                    'active': active_app_access,
                    'revoked': revoked_app_access,
                    'by_level': {item.access_level: item.count for item in app_access_levels}
                },
                'github_access': {
                    'total': total_github_access,
                    'active': active_github_access,
                    'revoked': revoked_github_access,
                    'by_type': {item.access_type: item.count for item in github_access_types}
                },
                'top_applications': [{'name': item.application_name, 'users': item.count} for item in top_applications],
                'top_repositories': [{'repo': f"{item.organization_name}/{item.repo_name}", 'users': item.count} for item in top_repositories]
            }
            
        except Exception as e:
            return {'error': f"Error getting access statistics: {str(e)}"}
    
    @staticmethod
    def export_application_access_csv() -> str:
        """
        Export application access records to CSV format.
        
        Returns:
            CSV string containing application access data
        """
        try:
            access_records = ApplicationAccess.query.all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            headers = [
                'User Name', 'Application Name', 'Access Level', 'Assign Date',
                'Remove Date', 'Status', 'Days Since Assigned', 'Remarks'
            ]
            writer.writerow(headers)
            
            # Write access data
            for access in access_records:
                row = [
                    access.user_name, access.application_name, access.access_level,
                    access.assign_date, access.remove_date, access.status,
                    access.days_since_assigned, access.remarks
                ]
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            return f"Error exporting application access: {str(e)}"
    
    @staticmethod
    def export_github_access_csv() -> str:
        """
        Export GitHub access records to CSV format.
        
        Returns:
            CSV string containing GitHub access data
        """
        try:
            access_records = GitHubAccess.query.all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            headers = [
                'User Name', 'Organization', 'Repository', 'Access Type', 'Assign Date',
                'Remove Date', 'Status', 'Days Since Assigned', 'Remarks'
            ]
            writer.writerow(headers)
            
            # Write access data
            for access in access_records:
                row = [
                    access.user_name, access.organization_name, access.repo_name,
                    access.access_type, access.assign_date, access.remove_date,
                    access.status, access.days_since_assigned, access.remarks
                ]
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            return f"Error exporting GitHub access: {str(e)}"
