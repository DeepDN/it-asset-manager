#!/usr/bin/env python3
"""
WSGI entry point for production deployment.

This module provides the WSGI application object for production servers
like Gunicorn, uWSGI, or Apache mod_wsgi.
"""

import os
from it_asset_manager.core.app import create_app
from it_asset_manager.models.user import User
from it_asset_manager.core.database import db

# Create application instance
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)


def create_default_admin():
    """Create default admin user if it doesn't exist."""
    with app.app_context():
        admin_user = User.find_by_username('admin')
        if not admin_user:
            admin_user = User()
            admin_user.username = 'admin'
            admin_user.email = 'admin@example.com'
            admin_user.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
            
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created")


# Initialize database and create admin user
with app.app_context():
    db.create_all()
    create_default_admin()

if __name__ == "__main__":
    app.run()
