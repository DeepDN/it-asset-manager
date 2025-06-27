"""
Pytest configuration and fixtures for IT Asset Manager tests.

This module contains shared fixtures and configuration for all tests.
"""

import pytest
import tempfile
import os
from datetime import date

from it_asset_manager.core.app import create_app
from it_asset_manager.core.database import db
from it_asset_manager.models.user import User
from it_asset_manager.models.asset import Asset
from it_asset_manager.models.access import ApplicationAccess, GitHubAccess


@pytest.fixture
def app():
    """Create application for testing."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Create authentication headers for API requests."""
    # Create test user and login
    with client.application.app_context():
        user = User()
        user.username = 'testuser'
        user.email = 'test@example.com'
        user.set_password('testpass123')
        
        db.session.add(user)
        db.session.commit()
    
    # Login
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    })
    
    return {'Content-Type': 'application/json'}


@pytest.fixture
def sample_user():
    """Create sample user for testing."""
    user = User()
    user.username = 'sampleuser'
    user.email = 'sample@example.com'
    user.set_password('samplepass123')
    
    db.session.add(user)
    db.session.commit()
    
    return user


@pytest.fixture
def sample_asset():
    """Create sample asset for testing."""
    asset = Asset()
    asset.asset_tag = 'LAP0001'
    asset.asset_type = 'laptop'
    asset.asset_category = 'Computing'
    asset.serial_number = 'SN123456789'
    asset.brand = 'Dell'
    asset.model = 'Latitude 5520'
    asset.ownership_type = 'purchased'
    asset.purchase_date = date.today()
    asset.purchase_cost = 1200.00
    asset.condition = 'excellent'
    asset.status = 'unassigned'
    
    db.session.add(asset)
    db.session.commit()
    
    return asset


@pytest.fixture
def sample_application_access():
    """Create sample application access for testing."""
    access = ApplicationAccess()
    access.user_name = 'testuser'
    access.application_name = 'TestApp'
    access.access_level = 'Read'
    access.assign_date = date.today()
    access.status = 'active'
    
    db.session.add(access)
    db.session.commit()
    
    return access


@pytest.fixture
def sample_github_access():
    """Create sample GitHub access for testing."""
    access = GitHubAccess()
    access.user_name = 'testuser'
    access.organization_name = 'testorg'
    access.repo_name = 'testrepo'
    access.access_type = 'Read'
    access.assign_date = date.today()
    access.status = 'active'
    
    db.session.add(access)
    db.session.commit()
    
    return access


@pytest.fixture
def authenticated_user(client, sample_user):
    """Login user and return authenticated client."""
    client.post('/auth/login', data={
        'username': sample_user.username,
        'password': 'samplepass123'
    })
    return client


class AuthActions:
    """Helper class for authentication actions in tests."""
    
    def __init__(self, client):
        self._client = client
    
    def login(self, username='testuser', password='testpass123'):
        """Login with given credentials."""
        return self._client.post('/auth/login', data={
            'username': username,
            'password': password
        })
    
    def logout(self):
        """Logout current user."""
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """Authentication helper fixture."""
    return AuthActions(client)
