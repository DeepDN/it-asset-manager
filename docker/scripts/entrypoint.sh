#!/bin/bash
set -e

echo "=== AssetPulse IT Asset Manager - Entrypoint ==="

# Run DB init script
python /docker-entrypoint-init.py

echo "=== Starting application ==="
exec "$@"
