"""
Unit tests for database models.

This module contains unit tests for all database models including
User, Asset, ApplicationAccess, and GitHubAccess.
"""

import pytest
from datetime import date, datetime, timedelta

from it_asset_manager.models.user import User
from it_asset_manager.models.asset import Asset
from it_asset_manager.models.access import ApplicationAccess, GitHubAccess
from it_asset_manager.core.database import db


class TestUserModel:
    """Test cases for User model."""
    
    def test_create_user(self, app):
        """Test user creation."""
        with app.app_context():
            user = User()
            user.username = 'testuser'
            user.email = 'test@example.com'
            user.set_password('testpass123')
            
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.is_active is True
            assert user.created_at is not None
    
    def test_password_hashing(self, app):
        """Test password hashing and verification."""
        with app.app_context():
            user = User()
            user.username = 'testuser'
            user.set_password('testpass123')
            
            # Password should be hashed
            assert user.password_hash != 'testpass123'
            
            # Should verify correct password
            assert user.check_password('testpass123') is True
            
            # Should not verify incorrect password
            assert user.check_password('wrongpass') is False
    
    def test_reset_token_generation(self, app):
        """Test password reset token generation."""
        with app.app_context():
            user = User()
            user.username = 'testuser'
            user.set_password('testpass123')
            
            token = user.generate_reset_token()
            
            assert token is not None
            assert len(token) == 32
            assert user.reset_token == token
            assert user.reset_token_expiry is not None
            
            # Token should be valid
            assert user.verify_reset_token(token) is True
            
            # Wrong token should be invalid
            assert user.verify_reset_token('wrongtoken') is False
    
    def test_expired_reset_token(self, app):
        """Test expired reset token validation."""
        with app.app_context():
            user = User()
            user.username = 'testuser'
            user.set_password('testpass123')
            
            # Generate token with past expiry
            token = user.generate_reset_token()
            user.reset_token_expiry = datetime.utcnow() - timedelta(hours=1)
            
            # Expired token should be invalid
            assert user.verify_reset_token(token) is False
    
    def test_find_by_username(self, app, sample_user):
        """Test finding user by username."""
        with app.app_context():
            found_user = User.find_by_username('sampleuser')
            assert found_user is not None
            assert found_user.username == 'sampleuser'
            
            # Non-existent user should return None
            not_found = User.find_by_username('nonexistent')
            assert not_found is None
    
    def test_user_to_dict(self, app, sample_user):
        """Test user dictionary conversion."""
        with app.app_context():
            user_dict = sample_user.to_dict()
            
            assert 'id' in user_dict
            assert 'username' in user_dict
            assert 'email' in user_dict
            assert 'created_at' in user_dict
            assert 'is_active' in user_dict
            
            # Password hash should not be included
            assert 'password_hash' not in user_dict


class TestAssetModel:
    """Test cases for Asset model."""
    
    def test_create_asset(self, app):
        """Test asset creation."""
        with app.app_context():
            asset = Asset()
            asset.asset_tag = 'LAP0001'
            asset.asset_type = 'laptop'
            asset.asset_category = 'Computing'
            asset.serial_number = 'SN123456789'
            asset.brand = 'Dell'
            asset.model = 'Latitude 5520'
            
            db.session.add(asset)
            db.session.commit()
            
            assert asset.id is not None
            assert asset.asset_tag == 'LAP0001'
            assert asset.asset_type == 'laptop'
            assert asset.status == 'unassigned'
            assert asset.condition == 'good'
    
    def test_asset_assignment(self, app, sample_asset):
        """Test asset assignment functionality."""
        with app.app_context():
            # Initially unassigned
            assert sample_asset.is_assigned is False
            
            # Assign to user
            sample_asset.assign_to_user('testuser', 'Office A')
            
            assert sample_asset.is_assigned is True
            assert sample_asset.assigned_to == 'testuser'
            assert sample_asset.location == 'Office A'
            assert sample_asset.status == 'assigned'
            assert sample_asset.assign_date == date.today()
    
    def test_asset_unassignment(self, app, sample_asset):
        """Test asset unassignment functionality."""
        with app.app_context():
            # First assign the asset
            sample_asset.assign_to_user('testuser')
            
            # Then unassign
            sample_asset.unassign()
            
            assert sample_asset.status == 'unassigned'
            assert sample_asset.remove_date == date.today()
    
    def test_rental_properties(self, app):
        """Test rental asset properties."""
        with app.app_context():
            asset = Asset()
            asset.asset_tag = 'LAP0002'
            asset.asset_type = 'laptop'
            asset.asset_category = 'Computing'
            asset.serial_number = 'SN987654321'
            asset.ownership_type = 'rented'
            asset.rental_start_date = date.today()
            asset.rental_end_date = date.today() + timedelta(days=30)
            
            assert asset.is_rental is True
            assert asset.rental_days_remaining == 30
    
    def test_warranty_expiry(self, app):
        """Test warranty expiry checking."""
        with app.app_context():
            asset = Asset()
            asset.asset_tag = 'LAP0003'
            asset.asset_type = 'laptop'
            asset.asset_category = 'Computing'
            asset.serial_number = 'SN111222333'
            
            # Future warranty
            asset.warranty_expiry = date.today() + timedelta(days=30)
            assert asset.is_warranty_expired is False
            
            # Expired warranty
            asset.warranty_expiry = date.today() - timedelta(days=30)
            assert asset.is_warranty_expired is True
    
    def test_find_by_tag(self, app, sample_asset):
        """Test finding asset by tag."""
        with app.app_context():
            found_asset = Asset.find_by_tag('LAP0001')
            assert found_asset is not None
            assert found_asset.asset_tag == 'LAP0001'
            
            # Non-existent tag should return None
            not_found = Asset.find_by_tag('NONEXISTENT')
            assert not_found is None
    
    def test_asset_search(self, app, sample_asset):
        """Test asset search functionality."""
        with app.app_context():
            # Search by asset tag
            results = Asset.search('LAP0001')
            assert len(results) == 1
            assert results[0].asset_tag == 'LAP0001'
            
            # Search by brand
            results = Asset.search('Dell')
            assert len(results) == 1
            assert results[0].brand == 'Dell'


class TestApplicationAccessModel:
    """Test cases for ApplicationAccess model."""
    
    def test_create_application_access(self, app):
        """Test application access creation."""
        with app.app_context():
            access = ApplicationAccess()
            access.user_name = 'testuser'
            access.application_name = 'TestApp'
            access.access_level = 'Admin'
            access.assign_date = date.today()
            access.status = 'active'
            
            db.session.add(access)
            db.session.commit()
            
            assert access.id is not None
            assert access.user_name == 'testuser'
            assert access.application_name == 'TestApp'
            assert access.access_level == 'Admin'
            assert access.is_active is True
    
    def test_revoke_access(self, app, sample_application_access):
        """Test access revocation."""
        with app.app_context():
            # Initially active
            assert sample_application_access.is_active is True
            
            # Revoke access
            sample_application_access.revoke_access('No longer needed')
            
            assert sample_application_access.status == 'revoked'
            assert sample_application_access.remove_date == date.today()
            assert sample_application_access.remarks == 'No longer needed'
            assert sample_application_access.is_active is False
    
    def test_find_by_user(self, app, sample_application_access):
        """Test finding access by user."""
        with app.app_context():
            access_records = ApplicationAccess.find_by_user('testuser')
            assert len(access_records) == 1
            assert access_records[0].user_name == 'testuser'


class TestGitHubAccessModel:
    """Test cases for GitHubAccess model."""
    
    def test_create_github_access(self, app):
        """Test GitHub access creation."""
        with app.app_context():
            access = GitHubAccess()
            access.user_name = 'testuser'
            access.organization_name = 'testorg'
            access.repo_name = 'testrepo'
            access.access_type = 'Write'
            access.assign_date = date.today()
            access.status = 'active'
            
            db.session.add(access)
            db.session.commit()
            
            assert access.id is not None
            assert access.user_name == 'testuser'
            assert access.organization_name == 'testorg'
            assert access.repo_name == 'testrepo'
            assert access.full_repo_name == 'testorg/testrepo'
            assert access.is_active is True
    
    def test_update_access_type(self, app, sample_github_access):
        """Test updating GitHub access type."""
        with app.app_context():
            # Initially Read access
            assert sample_github_access.access_type == 'Read'
            
            # Update to Write access
            sample_github_access.update_access_type('Write', 'Promoted to Write access')
            
            assert sample_github_access.access_type == 'Write'
            assert sample_github_access.remarks == 'Promoted to Write access'
    
    def test_find_by_repository(self, app, sample_github_access):
        """Test finding access by repository."""
        with app.app_context():
            access_records = GitHubAccess.find_by_repository('testorg', 'testrepo')
            assert len(access_records) == 1
            assert access_records[0].organization_name == 'testorg'
            assert access_records[0].repo_name == 'testrepo'
