"""
Authentication and authorization setup.

This module handles Flask-Login configuration and user session management.
"""

from flask_login import LoginManager
from typing import Optional

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


def init_auth(app) -> None:
    """
    Initialize authentication with Flask app.
    
    Args:
        app: Flask application instance
    """
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id: str) -> Optional['User']:
    """
    Load user by ID for Flask-Login.
    
    Args:
        user_id: User ID as string
        
    Returns:
        User object if found, None otherwise
    """
    from ..models.user import User
    from .database import db
    
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None
