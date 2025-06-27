"""
Flask application factory.

This module contains the application factory function that creates
and configures the Flask application with all necessary components.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
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
    # Create Flask app with explicit template and static folder paths
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
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
    
    return app


def register_blueprints(app: Flask) -> None:
    """
    Register all application blueprints.
    
    Args:
        app: Flask application instance
    """
    from ..routes.auth import auth_bp
    from ..routes.assets import assets_bp
    from ..routes.access import access_bp
    from ..routes.main import main_bp
    from ..routes.health import health_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(assets_bp, url_prefix='/assets')
    app.register_blueprint(access_bp, url_prefix='/access')
    app.register_blueprint(health_bp)


def setup_logging(app: Flask) -> None:
    """
    Setup application logging.
    
    Args:
        app: Flask application instance
    """
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Setup rotating file handler
        file_handler = RotatingFileHandler(
            'logs/it_asset_manager.log',
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
