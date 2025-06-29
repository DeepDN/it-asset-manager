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

if __name__ == "__main__":
    app.run()
