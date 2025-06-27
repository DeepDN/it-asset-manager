#!/bin/bash

# IT Asset Manager Backup Script
# Creates timestamped backup of database and exports

BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="it_assets_backup_${TIMESTAMP}"

echo "🔄 Creating backup: ${BACKUP_NAME}"

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

# Create backup folder
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

# Copy database
if [ -f "it_assets.db" ]; then
    cp it_assets.db "${BACKUP_DIR}/${BACKUP_NAME}/"
    echo "✅ Database backed up"
else
    echo "⚠️  Database file not found"
fi

# Export data to CSV (if application is running)
echo "📊 Attempting to export CSV data..."

# Create a simple Python script to export data
cat > temp_export.py << 'EOF'
from app import app, db, Asset, ApplicationAccess, GitHubAccess
import csv
import sys
import os

def export_to_csv():
    backup_dir = sys.argv[1] if len(sys.argv) > 1 else 'backups/temp'
    
    with app.app_context():
        try:
            # Export Assets
            with open(f'{backup_dir}/assets.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Asset Type', 'Brand', 'Model', 'Serial Number', 'Processor', 
                               'RAM (GB)', 'Storage (GB)', 'Storage Type', 'Assigned To', 
                               'Assign Date', 'Remove Date', 'Status', 'Remarks'])
                
                assets = Asset.query.all()
                for asset in assets:
                    writer.writerow([
                        asset.asset_type, asset.brand, asset.model, asset.serial_number,
                        asset.processor, asset.ram_gb, asset.storage_gb, asset.storage_type,
                        asset.assigned_to, asset.assign_date, asset.remove_date,
                        asset.status, asset.remarks
                    ])
            
            # Export Application Access
            with open(f'{backup_dir}/app_access.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['User Name', 'Application Name', 'Access Level', 'Assign Date', 
                               'Remove Date', 'Status', 'Remarks'])
                
                accesses = ApplicationAccess.query.all()
                for access in accesses:
                    writer.writerow([
                        access.user_name, access.application_name, access.access_level,
                        access.assign_date, access.remove_date, access.status, access.remarks
                    ])
            
            # Export GitHub Access
            with open(f'{backup_dir}/github_access.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['User Name', 'Organization Name', 'Repo Name', 'Access Type', 
                               'Assign Date', 'Remove Date', 'Status', 'Remarks'])
                
                accesses = GitHubAccess.query.all()
                for access in accesses:
                    writer.writerow([
                        access.user_name, access.organization_name, access.repo_name,
                        access.access_type, access.assign_date, access.remove_date,
                        access.status, access.remarks
                    ])
            
            print("✅ CSV exports completed")
            
        except Exception as e:
            print(f"❌ Export error: {str(e)}")

if __name__ == '__main__':
    export_to_csv()
EOF

# Run export if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
    python temp_export.py "${BACKUP_DIR}/${BACKUP_NAME}"
    rm temp_export.py
else
    echo "⚠️  Virtual environment not found, skipping CSV export"
fi

# Create backup info file
cat > "${BACKUP_DIR}/${BACKUP_NAME}/backup_info.txt" << EOF
IT Asset Manager Backup
Created: $(date)
Backup Name: ${BACKUP_NAME}
Contents:
- it_assets.db (SQLite database)
- assets.csv (Asset export)
- app_access.csv (Application access export)
- github_access.csv (GitHub access export)

To restore:
1. Copy it_assets.db back to application directory
2. Or import CSV files into new installation
EOF

# Create archive
cd ${BACKUP_DIR}
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"
cd ..

echo "✅ Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "📁 Backup contains:"
echo "   • Database file"
echo "   • CSV exports"
echo "   • Backup information"

# Clean up old backups (keep last 10)
cd ${BACKUP_DIR}
ls -t *.tar.gz | tail -n +11 | xargs -r rm
cd ..

echo "🧹 Old backups cleaned up (keeping last 10)"
echo "🎯 Backup process complete!"
