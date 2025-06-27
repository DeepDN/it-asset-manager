#!/usr/bin/env python3
"""
Asset Database Migration Script for IT Asset Manager
Adds comprehensive asset management fields including ownership, categories, and asset tags
"""

import sqlite3
import os
from datetime import datetime
import random
import string

def generate_asset_tag(asset_type, index):
    """Generate unique asset tag based on asset type"""
    type_prefixes = {
        'laptop': 'LAP',
        'desktop': 'DSK',
        'mobile': 'MOB',
        'tablet': 'TAB',
        'ipad': 'IPD',
        'iphone': 'IPH',
        'pendrive': 'USB',
        'harddisk': 'HDD',
        'ssd': 'SSD',
        'keyboard': 'KBD',
        'mouse': 'MSE',
        'monitor': 'MON',
        'cpu': 'CPU',
        'router': 'RTR',
        'switch': 'SWH',
        'firewall': 'FWL',
        'loadbalancer': 'LBL',
        'projector': 'PRJ',
        'printer': 'PRT',
        'television': 'TV',
        'speaker': 'SPK',
        'microphone': 'MIC',
        'connector': 'CON'
    }
    
    prefix = type_prefixes.get(asset_type.lower(), 'AST')
    return f"{prefix}{index:04d}"

def get_asset_category(asset_type):
    """Determine asset category based on type"""
    categories = {
        'laptop': 'Computing',
        'desktop': 'Computing',
        'cpu': 'Computing',
        'mobile': 'Mobile Device',
        'tablet': 'Mobile Device',
        'ipad': 'Mobile Device',
        'iphone': 'Mobile Device',
        'pendrive': 'Storage',
        'harddisk': 'Storage',
        'ssd': 'Storage',
        'keyboard': 'Peripheral',
        'mouse': 'Peripheral',
        'monitor': 'Display',
        'television': 'Display',
        'projector': 'Display',
        'router': 'Network',
        'switch': 'Network',
        'firewall': 'Network',
        'loadbalancer': 'Network',
        'printer': 'Office Equipment',
        'speaker': 'Audio/Video',
        'microphone': 'Audio/Video'
    }
    
    return categories.get(asset_type.lower(), 'Other')

def migrate_assets():
    db_path = 'instance/it_assets.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the application first to create the database.")
        return
    
    print("🔄 Starting comprehensive asset database migration...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current asset table structure
        cursor.execute("PRAGMA table_info(asset)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        
        # New columns to add (without UNIQUE constraint initially)
        new_columns = [
            ("asset_tag", "VARCHAR(50)"),
            ("asset_category", "VARCHAR(50) DEFAULT 'Other'"),
            ("ownership_type", "VARCHAR(20) DEFAULT 'purchased'"),
            ("vendor_name", "VARCHAR(100)"),
            ("rental_start_date", "DATE"),
            ("rental_end_date", "DATE"),
            ("rental_cost_monthly", "FLOAT"),
            ("purchase_date", "DATE"),
            ("purchase_cost", "FLOAT"),
            ("warranty_expiry", "DATE"),
            ("port_count", "INTEGER"),
            ("network_type", "VARCHAR(50)"),
            ("screen_size", "VARCHAR(20)"),
            ("resolution", "VARCHAR(20)"),
            ("audio_type", "VARCHAR(50)"),
            ("connector_type", "VARCHAR(50)"),
            ("location", "VARCHAR(100)"),
            ("condition", "VARCHAR(20) DEFAULT 'good'"),
            ("updated_at", "DATETIME")
        ]
        
        for column_name, column_def in new_columns:
            if column_name not in columns:
                migrations_needed.append(f"ALTER TABLE asset ADD COLUMN {column_name} {column_def}")
        
        if not migrations_needed:
            print("✅ Asset database is already up to date!")
            return
        
        print(f"📝 Applying {len(migrations_needed)} asset migrations...")
        
        # Apply migrations
        for migration in migrations_needed:
            print(f"   Executing: {migration}")
            try:
                cursor.execute(migration)
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e):
                    raise e
                print(f"   Skipped (column exists): {migration}")
        
        # Update existing assets with asset tags and categories
        cursor.execute("SELECT id, asset_type FROM asset WHERE asset_tag IS NULL OR asset_tag = ''")
        assets_to_update = cursor.fetchall()
        
        if assets_to_update:
            print(f"📋 Updating {len(assets_to_update)} existing assets with asset tags and categories...")
            
            for i, (asset_id, asset_type) in enumerate(assets_to_update, 1):
                asset_tag = generate_asset_tag(asset_type or 'other', i)
                asset_category = get_asset_category(asset_type or 'other')
                
                cursor.execute("""
                    UPDATE asset 
                    SET asset_tag = ?, 
                        asset_category = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (asset_tag, asset_category, datetime.utcnow(), asset_id))
                
                print(f"   Updated asset ID {asset_id}: {asset_tag} ({asset_category})")
        
        conn.commit()
        print("✅ Asset database migration completed successfully!")
        print("🎯 New features available:")
        print("   • Asset Tags (unique identifiers)")
        print("   • Asset Categories (Computing, Network, etc.)")
        print("   • Ownership Types (purchased, rented, leased)")
        print("   • Vendor Management for rentals")
        print("   • Enhanced asset specifications")
        print("   • Location tracking")
        print("   • Condition monitoring")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_assets()
