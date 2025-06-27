"""
Core application components.

This module contains the core Flask application setup, database initialization,
and other fundamental components.
"""

from .app import create_app
from .database import db
from .auth import login_manager

__all__ = [
    'create_app',
    'db',
    'login_manager'
]
