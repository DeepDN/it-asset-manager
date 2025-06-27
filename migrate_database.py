#!/usr/bin/env python3
"""
Database Migration Script for IT Asset Manager
Adds new columns for password reset functionality
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    db_path = 'instance/it_assets.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the application first to create the database.")
        return
    
    print("🔄 Starting database migration...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        
        if 'email' not in columns:
            migrations_needed.append("ALTER TABLE user ADD COLUMN email VARCHAR(120)")
            
        if 'reset_token' not in columns:
            migrations_needed.append("ALTER TABLE user ADD COLUMN reset_token VARCHAR(100)")
            
        if 'reset_token_expiry' not in columns:
            migrations_needed.append("ALTER TABLE user ADD COLUMN reset_token_expiry DATETIME")
            
        if 'created_at' not in columns:
            migrations_needed.append("ALTER TABLE user ADD COLUMN created_at DATETIME")
        
        if not migrations_needed:
            print("✅ Database is already up to date!")
            return
        
        print(f"📝 Applying {len(migrations_needed)} migrations...")
        
        for migration in migrations_needed:
            print(f"   Executing: {migration}")
            cursor.execute(migration)
        
        # Update existing admin user with email if it doesn't have one
        cursor.execute("SELECT id, email FROM user WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user and not admin_user[1]:  # If admin exists but has no email
            cursor.execute(
                "UPDATE user SET email = ?, created_at = ? WHERE username = 'admin'",
                ('admin@itassetmanager.local', datetime.utcnow())
            )
            print("   Updated admin user with default email")
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        print("🎯 You can now use the password reset functionality.")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
