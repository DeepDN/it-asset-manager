from .main import main_bp
from .auth import auth_bp
from .assets import assets_bp
from .access import access_bp
from .health import health_bp
from .admin import admin_bp
from .lifecycle import lifecycle_bp
from .licenses import licenses_bp
from .vendors import vendors_bp
from .depreciation import depreciation_bp
from .reports import reports_bp

__all__ = [
    'main_bp', 'auth_bp', 'assets_bp', 'access_bp', 'health_bp',
    'admin_bp', 'lifecycle_bp', 'licenses_bp', 'vendors_bp',
    'depreciation_bp', 'reports_bp',
]
