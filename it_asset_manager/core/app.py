"""
Flask application factory.

This module contains the application factory function that creates
and configures the Flask application with all necessary components.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, flash
from typing import Optional

from config.settings import get_config
from .database import init_db, create_tables
from .auth import init_auth


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application instance
    """
    import os
    _base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    app = Flask(__name__, 
                template_folder=os.path.join(_base_dir, 'templates'),
                static_folder=os.path.join(_base_dir, 'static'))
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Set engine options for PostgreSQL
    engine_opts = config_class.get_engine_options()
    if engine_opts:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_opts
    
    # Initialize extensions
    init_db(app)
    init_auth(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create database tables
    create_tables(app)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize configuration
    config_class.init_app(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from ..routes.auth import auth_bp
    from ..routes.assets import assets_bp
    from ..routes.access import access_bp
    from ..routes.main import main_bp
    from ..routes.health import health_bp
    from ..routes.lifecycle import lifecycle_bp
    from ..routes.licenses import licenses_bp
    from ..routes.vendors import vendors_bp
    from ..routes.depreciation import depreciation_bp
    from ..routes.reports import reports_bp
    from ..routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(assets_bp, url_prefix='/assets')
    app.register_blueprint(access_bp, url_prefix='/access')
    app.register_blueprint(health_bp)
    app.register_blueprint(lifecycle_bp)
    app.register_blueprint(licenses_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(depreciation_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)


def setup_logging(app: Flask) -> None:
    """
    Setup application logging.
    
    Args:
        app: Flask application instance
    """
    if not app.debug and not app.testing:
        _logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
        if not os.path.exists(_logs_dir):
            os.mkdir(_logs_dir)
        
        # Setup rotating file handler
        file_handler = RotatingFileHandler(
            os.path.join(_logs_dir, 'it_asset_manager.log'),
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('IT Asset Manager startup')


def register_error_handlers(app):
    from flask_login import current_user
    from flask import request
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('base.html',
                               error='Page not found',
                               user=current_user if current_user.is_authenticated else None), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f'500 error: {e}')
        return render_template('base.html',
                               error='Internal server error. Please try again.',
                               user=current_user if current_user.is_authenticated else None), 500
