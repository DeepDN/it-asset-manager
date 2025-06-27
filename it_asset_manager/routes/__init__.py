"""
Flask route blueprints.

This module contains all Flask route blueprints organized by functionality.
"""

from .main import main_bp
from .auth import auth_bp
from .assets import assets_bp
from .access import access_bp

__all__ = [
    'main_bp',
    'auth_bp',
    'assets_bp',
    'access_bp'
]
