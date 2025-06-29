#!/usr/bin/env python3
"""
WSGI entry point for production deployment.

This module provides the WSGI application object for production servers
like Gunicorn, uWSGI, or Apache mod_wsgi.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app from app.py
from app import app

# Create default admin user if it doesn't exist
def create_default_admin():
    """Create default admin user if it doesn't exist."""
    from app import db, User
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User()
            admin_user.username = 'admin'
            admin_user.email = 'admin@example.com'
            admin_user.password_hash = generate_password_hash(
                os.environ.get('ADMIN_PASSWORD', 'admin123')
            )
            
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created")

# Import password hashing function
from werkzeug.security import generate_password_hash

# Initialize database and create admin user
create_default_admin()

if __name__ == "__main__":
    app.run()
