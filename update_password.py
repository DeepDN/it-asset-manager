#!/usr/bin/env python3
"""
Password Update Script for IT Asset Manager
Use this script to manually update user passwords
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
import getpass
import sys

def update_password():
    with app.app_context():
        print("🔐 IT Asset Manager - Password Update Tool")
        print("=" * 50)
        
        # Get username
        username = input("Enter username to update (default: admin): ").strip()
        if not username:
            username = "admin"
        
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ User '{username}' not found!")
            
            # Offer to create new user
            create_new = input("Would you like to create a new user? (y/n): ").lower()
            if create_new == 'y':
                new_password = getpass.getpass("Enter password for new user: ")
                confirm_password = getpass.getpass("Confirm password: ")
                
                if new_password != confirm_password:
                    print("❌ Passwords don't match!")
                    return
                
                # Create new user
                new_user = User(
                    username=username,
                    password_hash=generate_password_hash(new_password)
                )
                
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    print(f"✅ New user '{username}' created successfully!")
                except Exception as e:
                    print(f"❌ Error creating user: {str(e)}")
                    db.session.rollback()
            return
        
        # Update existing user password
        print(f"📝 Updating password for user: {username}")
        
        # Get new password
        new_password = getpass.getpass("Enter new password: ")
        confirm_password = getpass.getpass("Confirm new password: ")
        
        if new_password != confirm_password:
            print("❌ Passwords don't match!")
            return
        
        if len(new_password) < 6:
            print("❌ Password must be at least 6 characters long!")
            return
        
        # Update password
        try:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"✅ Password updated successfully for user '{username}'!")
            print("🎯 You can now login with the new password.")
            
        except Exception as e:
            print(f"❌ Error updating password: {str(e)}")
            db.session.rollback()

def list_users():
    """List all users in the system"""
    with app.app_context():
        users = User.query.all()
        print("\n👥 Current Users:")
        print("-" * 20)
        for user in users:
            print(f"• {user.username}")
        print()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_users()
        return
    
    try:
        update_password()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == '__main__':
    main()
