#!/usr/bin/env python3
import os
from it_asset_manager.core.app import create_app

if __name__ == '__main__':
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    debug_mode = app.config.get('DEBUG', False)
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
