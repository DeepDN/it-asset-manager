"""
Authentication service for user management and security.

This module contains the AuthService class that handles all authentication
related business logic including login, password management, and user operations.
"""

from datetime import datetime
from typing import Tuple, Optional
from flask_login import login_user, logout_user

from ..models.user import User
from ..core.database import db


class AuthService:
    """Service class for authentication and user management."""
    
    @staticmethod
    def authenticate_user(username: str, password: str, remember_me: bool = False) -> Tuple[bool, str, Optional[User]]:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username for authentication
            password: Password for authentication
            remember_me: Whether to remember the user session
            
        Returns:
            Tuple of (success, message, user_object)
        """
        try:
            user = User.find_by_username(username)
            
            if not user:
                return False, "Invalid username or password", None
            
            if not user.is_active:
                return False, "Account is disabled", None
            
            if not user.check_password(password):
                return False, "Invalid username or password", None
            
            # Update last login
            user.update_last_login()
            db.session.commit()
            
            # Log in user
            login_user(user, remember=remember_me)
            
            return True, "Login successful", user
            
        except Exception as e:
            return False, f"Authentication error: {str(e)}", None
    
    @staticmethod
    def logout_user_session() -> Tuple[bool, str]:
        """
        Logout current user session.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            logout_user()
            return True, "Logged out successfully"
        except Exception as e:
            return False, f"Logout error: {str(e)}"
    
    @staticmethod
    def create_user(username: str, password: str, email: Optional[str] = None) -> Tuple[bool, str, Optional[User]]:
        """
        Create a new user account.
        
        Args:
            username: Unique username
            password: User password
            email: Optional email address
            
        Returns:
            Tuple of (success, message, user_object)
        """
        try:
            # Validate input
            if not username or len(username) < 3:
                return False, "Username must be at least 3 characters long", None
            
            if not password or len(password) < 6:
                return False, "Password must be at least 6 characters long", None
            
            # Check for existing username
            if User.find_by_username(username):
                return False, "Username already exists", None
            
            # Check for existing email
            if email and User.find_by_email(email):
                return False, "Email already exists", None
            
            # Create user
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return True, f"User {username} created successfully", user
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error creating user: {str(e)}", None
    
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Change user password with current password verification.
        
        Args:
            user_id: ID of user changing password
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            # Verify current password
            if not user.check_password(current_password):
                return False, "Current password is incorrect"
            
            # Validate new password
            if not new_password or len(new_password) < 6:
                return False, "New password must be at least 6 characters long"
            
            # Set new password
            user.set_password(new_password)
            db.session.commit()
            
            return True, "Password changed successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error changing password: {str(e)}"
    
    @staticmethod
    def initiate_password_reset(username_or_email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Initiate password reset process.
        
        Args:
            username_or_email: Username or email for password reset
            
        Returns:
            Tuple of (success, message, reset_token)
        """
        try:
            # Find user by username or email
            user = User.find_by_username(username_or_email)
            if not user:
                user = User.find_by_email(username_or_email)
            
            if not user:
                return False, "User not found", None
            
            if not user.is_active:
                return False, "Account is disabled", None
            
            # Generate reset token
            reset_token = user.generate_reset_token()
            db.session.commit()
            
            return True, "Password reset token generated", reset_token
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error initiating password reset: {str(e)}", None
    
    @staticmethod
    def reset_password_with_token(token: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset password using reset token.
        
        Args:
            token: Password reset token
            new_password: New password to set
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user = User.find_by_reset_token(token)
            if not user:
                return False, "Invalid or expired reset token"
            
            if not user.verify_reset_token(token):
                return False, "Invalid or expired reset token"
            
            # Validate new password
            if not new_password or len(new_password) < 6:
                return False, "Password must be at least 6 characters long"
            
            # Set new password and clear reset token
            user.set_password(new_password)
            user.clear_reset_token()
            db.session.commit()
            
            return True, "Password reset successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error resetting password: {str(e)}"
    
    @staticmethod
    def update_user_profile(user_id: int, email: Optional[str] = None) -> Tuple[bool, str]:
        """
        Update user profile information.
        
        Args:
            user_id: ID of user to update
            email: New email address
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            # Check for existing email (excluding current user)
            if email and email != user.email:
                existing_user = User.find_by_email(email)
                if existing_user and existing_user.id != user_id:
                    return False, "Email already exists"
            
            # Update email
            if email is not None:
                user.email = email
            
            db.session.commit()
            return True, "Profile updated successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating profile: {str(e)}"
    
    @staticmethod
    def deactivate_user(user_id: int) -> Tuple[bool, str]:
        """
        Deactivate user account.
        
        Args:
            user_id: ID of user to deactivate
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            user.is_active = False
            db.session.commit()
            
            return True, f"User {user.username} deactivated successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error deactivating user: {str(e)}"
    
    @staticmethod
    def activate_user(user_id: int) -> Tuple[bool, str]:
        """
        Activate user account.
        
        Args:
            user_id: ID of user to activate
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return False, "User not found"
            
            user.is_active = True
            db.session.commit()
            
            return True, f"User {user.username} activated successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error activating user: {str(e)}"
