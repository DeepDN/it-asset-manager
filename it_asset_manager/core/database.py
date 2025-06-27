"""
Database initialization and configuration.

This module handles SQLAlchemy database setup and provides
database utilities for the application.
"""

from flask_sqlalchemy import SQLAlchemy
from typing import Any

# Initialize SQLAlchemy instance
db = SQLAlchemy()


def init_db(app) -> None:
    """
    Initialize database with Flask app.
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)


def create_tables(app) -> None:
    """
    Create all database tables.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.create_all()


def drop_tables(app) -> None:
    """
    Drop all database tables.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()


def reset_database(app) -> None:
    """
    Reset database by dropping and recreating all tables.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
