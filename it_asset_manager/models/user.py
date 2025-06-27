"""
User model for authentication and user management.

This module contains the User model with authentication capabilities,
password reset functionality, and user session management.
"""

from datetime import datetime, timedelta
from typing import Optional
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

from ..core.database import db


class User(UserMixin, db.Model):
    """
    User model for authentication and session management.
    
    Attributes:
        id: Primary key
        username: Unique username for login
        email: User email address (optional)
        password_hash: Hashed password
        reset_token: Token for password reset
        reset_token_expiry: Expiry time for reset token
        created_at: Account creation timestamp
        is_active: Account status
        last_login: Last login timestamp
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True, index=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self) -> str:
        """String representation of User object."""
        return f'<User {self.username}>'
    
    def set_password(self, password: str) -> None:
        """
        Set user password with secure hashing.
        
        Args:
            password: Plain text password to hash and store
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Check if provided password matches stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self, expiry_hours: int = 24) -> str:
        """
        Generate a secure token for password reset.
        
        Args:
            expiry_hours: Hours until token expires
            
        Returns:
            Generated reset token
        """
        # Generate secure random token
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        self.reset_token = token
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=expiry_hours)
        
        return token
    
    def verify_reset_token(self, token: str) -> bool:
        """
        Verify if reset token is valid and not expired.
        
        Args:
            token: Token to verify
            
        Returns:
            True if token is valid, False otherwise
        """
        if not self.reset_token or not self.reset_token_expiry:
            return False
        
        if datetime.utcnow() > self.reset_token_expiry:
            return False
        
        return self.reset_token == token
    
    def clear_reset_token(self) -> None:
        """Clear reset token after successful password reset."""
        self.reset_token = None
        self.reset_token_expiry = None
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """
        Find user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User object if found, None otherwise
        """
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """
        Find user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User object if found, None otherwise
        """
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_reset_token(cls, token: str) -> Optional['User']:
        """
        Find user by reset token.
        
        Args:
            token: Reset token to search for
            
        Returns:
            User object if found, None otherwise
        """
        return cls.query.filter_by(reset_token=token).first()
    
    def to_dict(self) -> dict:
        """
        Convert user object to dictionary.
        
        Returns:
            Dictionary representation of user (excluding sensitive data)
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
