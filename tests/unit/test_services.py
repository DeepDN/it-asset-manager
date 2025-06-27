"""
Unit tests for service layer.

This module contains unit tests for all service classes including
AssetService, AuthService, and AccessService.
"""

import pytest
from datetime import date

from it_asset_manager.services.asset_service import AssetService
from it_asset_manager.services.auth_service import AuthService
from it_asset_manager.services.access_service import AccessService
from it_asset_manager.models.user import User
from it_asset_manager.models.asset import Asset
from it_asset_manager.models.access import ApplicationAccess, GitHubAccess
from it_asset_manager.core.database import db


class TestAssetService:
    """Test cases for AssetService."""
    
    def test_create_asset_success(self, app):
        """Test successful asset creation."""
        with app.app_context():
            asset_data = {
                'asset_tag': 'LAP0001',
                'asset_type': 'laptop',
                'serial_number': 'SN123456789',
                'brand': 'Dell',
                'model': 'Latitude 5520',
                'ownership_type': 'purchased'
            }
            
            success, message, asset = AssetService.create_asset(asset_data)
            
            assert success is True
            assert 'created successfully' in message
            assert asset is not None
            assert asset.asset_tag == 'LAP0001'
            assert asset.asset_category == 'Computing'
    
    def test_create_asset_duplicate_tag(self, app, sample_asset):
        """Test asset creation with duplicate tag."""
        with app.app_context():
            asset_data = {
                'asset_tag': 'LAP0001',  # Same as sample_asset
                'asset_type': 'laptop',
                'serial_number': 'SN987654321'
            }
            
            success, message, asset = AssetService.create_asset(asset_data)
            
            assert success is False
            assert 'already exists' in message
            assert asset is None
    
    def test_create_asset_missing_required_field(self, app):
        """Test asset creation with missing required field."""
        with app.app_context():
            asset_data = {
                'asset_tag': 'LAP0002',
                'asset_type': 'laptop'
                # Missing serial_number
            }
            
            success, message, asset = AssetService.create_asset(asset_data)
            
            assert success is False
            assert 'Missing required field' in message
            assert asset is None
    
    def test_update_asset_success(self, app, sample_asset):
        """Test successful asset update."""
        with app.app_context():
            asset_data = {
                'brand': 'HP',
                'model': 'EliteBook 850',
                'condition': 'good'
            }
            
            success, message, updated_asset = AssetService.update_asset(
                sample_asset.id, asset_data
            )
            
            assert success is True
            assert 'updated successfully' in message
            assert updated_asset.brand == 'HP'
            assert updated_asset.model == 'EliteBook 850'
    
    def test_assign_asset_success(self, app, sample_asset):
        """Test successful asset assignment."""
        with app.app_context():
            success, message = AssetService.assign_asset(
                sample_asset.id, 'testuser', 'Office A'
            )
            
            assert success is True
            assert 'assigned to testuser' in message
            
            # Verify assignment
            db.session.refresh(sample_asset)
            assert sample_asset.assigned_to == 'testuser'
            assert sample_asset.location == 'Office A'
            assert sample_asset.status == 'assigned'
    
    def test_assign_already_assigned_asset(self, app, sample_asset):
        """Test assigning already assigned asset."""
        with app.app_context():
            # First assignment
            sample_asset.assign_to_user('user1')
            db.session.commit()
            
            # Try to assign to another user
            success, message = AssetService.assign_asset(
                sample_asset.id, 'user2'
            )
            
            assert success is False
            assert 'already assigned' in message
    
    def test_get_asset_statistics(self, app, sample_asset):
        """Test asset statistics generation."""
        with app.app_context():
            stats = AssetService.get_asset_statistics()
            
            assert 'total_assets' in stats
            assert 'assigned_assets' in stats
            assert 'unassigned_assets' in stats
            assert 'asset_types' in stats
            assert 'ownership_types' in stats
            
            assert stats['total_assets'] >= 1
            assert isinstance(stats['asset_types'], dict)


class TestAuthService:
    """Test cases for AuthService."""
    
    def test_authenticate_user_success(self, app, sample_user):
        """Test successful user authentication."""
        with app.app_context():
            success, message, user = AuthService.authenticate_user(
                'sampleuser', 'samplepass123'
            )
            
            assert success is True
            assert 'Login successful' in message
            assert user is not None
            assert user.username == 'sampleuser'
    
    def test_authenticate_user_invalid_username(self, app):
        """Test authentication with invalid username."""
        with app.app_context():
            success, message, user = AuthService.authenticate_user(
                'nonexistent', 'password'
            )
            
            assert success is False
            assert 'Invalid username or password' in message
            assert user is None
    
    def test_authenticate_user_invalid_password(self, app, sample_user):
        """Test authentication with invalid password."""
        with app.app_context():
            success, message, user = AuthService.authenticate_user(
                'sampleuser', 'wrongpassword'
            )
            
            assert success is False
            assert 'Invalid username or password' in message
            assert user is None
    
    def test_create_user_success(self, app):
        """Test successful user creation."""
        with app.app_context():
            success, message, user = AuthService.create_user(
                'newuser', 'newpass123', 'new@example.com'
            )
            
            assert success is True
            assert 'created successfully' in message
            assert user is not None
            assert user.username == 'newuser'
            assert user.email == 'new@example.com'
    
    def test_create_user_duplicate_username(self, app, sample_user):
        """Test user creation with duplicate username."""
        with app.app_context():
            success, message, user = AuthService.create_user(
                'sampleuser', 'password123'
            )
            
            assert success is False
            assert 'already exists' in message
            assert user is None
    
    def test_create_user_short_password(self, app):
        """Test user creation with short password."""
        with app.app_context():
            success, message, user = AuthService.create_user(
                'testuser', '123'  # Too short
            )
            
            assert success is False
            assert 'at least 6 characters' in message
            assert user is None
    
    def test_change_password_success(self, app, sample_user):
        """Test successful password change."""
        with app.app_context():
            success, message = AuthService.change_password(
                sample_user.id, 'samplepass123', 'newpassword123'
            )
            
            assert success is True
            assert 'Password changed successfully' in message
            
            # Verify new password works
            assert sample_user.check_password('newpassword123') is True
    
    def test_change_password_wrong_current(self, app, sample_user):
        """Test password change with wrong current password."""
        with app.app_context():
            success, message = AuthService.change_password(
                sample_user.id, 'wrongpassword', 'newpassword123'
            )
            
            assert success is False
            assert 'Current password is incorrect' in message
    
    def test_initiate_password_reset(self, app, sample_user):
        """Test password reset initiation."""
        with app.app_context():
            success, message, token = AuthService.initiate_password_reset(
                'sampleuser'
            )
            
            assert success is True
            assert 'reset token generated' in message
            assert token is not None
            assert len(token) == 32
    
    def test_reset_password_with_token(self, app, sample_user):
        """Test password reset with token."""
        with app.app_context():
            # Generate reset token
            token = sample_user.generate_reset_token()
            db.session.commit()
            
            # Reset password
            success, message = AuthService.reset_password_with_token(
                token, 'newpassword123'
            )
            
            assert success is True
            assert 'Password reset successfully' in message
            
            # Verify new password works
            db.session.refresh(sample_user)
            assert sample_user.check_password('newpassword123') is True


class TestAccessService:
    """Test cases for AccessService."""
    
    def test_grant_application_access_success(self, app):
        """Test successful application access grant."""
        with app.app_context():
            success, message, access = AccessService.grant_application_access(
                'testuser', 'TestApp', 'Read', 'Initial access'
            )
            
            assert success is True
            assert 'Granted Read access' in message
            assert access is not None
            assert access.user_name == 'testuser'
            assert access.application_name == 'TestApp'
            assert access.access_level == 'Read'
    
    def test_grant_application_access_invalid_level(self, app):
        """Test application access grant with invalid level."""
        with app.app_context():
            success, message, access = AccessService.grant_application_access(
                'testuser', 'TestApp', 'InvalidLevel'
            )
            
            assert success is False
            assert 'Invalid access level' in message
            assert access is None
    
    def test_grant_duplicate_application_access(self, app, sample_application_access):
        """Test granting duplicate application access."""
        with app.app_context():
            success, message, access = AccessService.grant_application_access(
                'testuser', 'TestApp', 'Write'
            )
            
            assert success is False
            assert 'already has' in message
            assert access is None
    
    def test_revoke_application_access_success(self, app, sample_application_access):
        """Test successful application access revocation."""
        with app.app_context():
            success, message = AccessService.revoke_application_access(
                sample_application_access.id, 'No longer needed'
            )
            
            assert success is True
            assert 'Revoked' in message
            
            # Verify revocation
            db.session.refresh(sample_application_access)
            assert sample_application_access.status == 'revoked'
    
    def test_grant_github_access_success(self, app):
        """Test successful GitHub access grant."""
        with app.app_context():
            success, message, access = AccessService.grant_github_access(
                'testuser', 'testorg', 'testrepo', 'Write', 'Development access'
            )
            
            assert success is True
            assert 'Granted Write access' in message
            assert access is not None
            assert access.user_name == 'testuser'
            assert access.organization_name == 'testorg'
            assert access.repo_name == 'testrepo'
            assert access.access_type == 'Write'
    
    def test_grant_github_access_invalid_type(self, app):
        """Test GitHub access grant with invalid type."""
        with app.app_context():
            success, message, access = AccessService.grant_github_access(
                'testuser', 'testorg', 'testrepo', 'InvalidType'
            )
            
            assert success is False
            assert 'Invalid access type' in message
            assert access is None
    
    def test_update_github_access_success(self, app, sample_github_access):
        """Test successful GitHub access update."""
        with app.app_context():
            success, message = AccessService.update_github_access(
                sample_github_access.id, 'Admin', 'Promoted to admin'
            )
            
            assert success is True
            assert 'Updated access type from Read to Admin' in message
            
            # Verify update
            db.session.refresh(sample_github_access)
            assert sample_github_access.access_type == 'Admin'
    
    def test_get_access_statistics(self, app, sample_application_access, sample_github_access):
        """Test access statistics generation."""
        with app.app_context():
            stats = AccessService.get_access_statistics()
            
            assert 'application_access' in stats
            assert 'github_access' in stats
            
            app_stats = stats['application_access']
            assert 'total' in app_stats
            assert 'active' in app_stats
            assert 'by_level' in app_stats
            
            github_stats = stats['github_access']
            assert 'total' in github_stats
            assert 'active' in github_stats
            assert 'by_type' in github_stats
