#!/usr/bin/env python3
"""
Main application entry point for IT Asset Manager.

This script creates and runs the Flask application using the application factory pattern.
"""

import os
from it_asset_manager.core.app import create_app
from it_asset_manager.models.user import User
from it_asset_manager.core.database import db


def create_default_admin():
    """Create default admin user if it doesn't exist."""
    with app.app_context():
        admin_user = User.find_by_username('admin')
        if not admin_user:
            admin_user = User()
            admin_user.username = 'admin'
            admin_user.email = 'admin@example.com'
            admin_user.set_password('admin123')
            
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created (username: admin, password: admin123)")
        else:
            print("Admin user already exists")


if __name__ == '__main__':
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask application
    app = create_app(config_name)
    
    # Create default admin user
    create_default_admin()
    
    # Run application
    debug_mode = app.config.get('DEBUG', False)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode
    )
