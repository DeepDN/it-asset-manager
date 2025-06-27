"""
Health check routes for monitoring and Docker health checks.

This module provides endpoints for application health monitoring,
database connectivity checks, and system status information.
"""

from flask import Blueprint, jsonify
from datetime import datetime
import os
import psutil

from ..core.database import db
from ..models.user import User

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        JSON response with application status
    """
    try:
        # Check database connectivity
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status,
        'version': '2.0.0'
    }), 200 if db_status == 'healthy' else 503


@health_bp.route('/health/detailed')
def detailed_health_check():
    """
    Detailed health check with system information.
    
    Returns:
        JSON response with detailed system status
    """
    try:
        # Database check
        user_count = User.query.count()
        db_status = 'healthy'
        db_info = {'user_count': user_count}
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
        db_info = {'error': str(e)}
    
    # System information
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        system_info = {
            'memory_usage_percent': memory.percent,
            'memory_available_mb': memory.available // (1024 * 1024),
            'disk_usage_percent': disk.percent,
            'disk_free_gb': disk.free // (1024 * 1024 * 1024),
            'cpu_count': psutil.cpu_count(),
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
    except Exception as e:
        system_info = {'error': str(e)}
    
    overall_status = 'healthy' if db_status == 'healthy' else 'unhealthy'
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'database': {
            'status': db_status,
            'info': db_info
        },
        'system': system_info,
        'environment': {
            'flask_env': os.environ.get('FLASK_ENV', 'unknown'),
            'python_version': os.sys.version,
            'container': os.path.exists('/.dockerenv')
        },
        'version': '2.0.0'
    }), 200 if overall_status == 'healthy' else 503


@health_bp.route('/ready')
def readiness_check():
    """
    Kubernetes-style readiness check.
    
    Returns:
        JSON response indicating if app is ready to serve traffic
    """
    try:
        # Check if database is accessible and has required tables
        db.session.execute(db.text('SELECT COUNT(*) FROM users'))
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not ready',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@health_bp.route('/live')
def liveness_check():
    """
    Kubernetes-style liveness check.
    
    Returns:
        JSON response indicating if app is alive
    """
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
