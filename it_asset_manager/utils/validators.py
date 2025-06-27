"""
Validation utilities for input validation and data integrity.

This module contains validation functions for various data types
used throughout the application.
"""

import re
from typing import Tuple, Optional


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 120:
        return False, "Email address is too long (max 120 characters)"
    
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength and requirements.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"
    
    # Check for at least one letter and one number (optional stronger validation)
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not has_letter:
        return False, "Password must contain at least one letter"
    
    if not has_number:
        return False, "Password must contain at least one number"
    
    return True, None


def validate_asset_tag(asset_tag: str) -> Tuple[bool, Optional[str]]:
    """
    Validate asset tag format and requirements.
    
    Args:
        asset_tag: Asset tag to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not asset_tag:
        return False, "Asset tag is required"
    
    if len(asset_tag) < 3:
        return False, "Asset tag must be at least 3 characters long"
    
    if len(asset_tag) > 50:
        return False, "Asset tag is too long (max 50 characters)"
    
    # Asset tag should contain only alphanumeric characters and hyphens
    pattern = r'^[A-Za-z0-9-]+$'
    if not re.match(pattern, asset_tag):
        return False, "Asset tag can only contain letters, numbers, and hyphens"
    
    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username format and requirements.
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 80:
        return False, "Username is too long (max 80 characters)"
    
    # Username should contain only alphanumeric characters, dots, and underscores
    pattern = r'^[A-Za-z0-9._]+$'
    if not re.match(pattern, username):
        return False, "Username can only contain letters, numbers, dots, and underscores"
    
    # Username should not start or end with dots or underscores
    if username.startswith('.') or username.startswith('_'):
        return False, "Username cannot start with a dot or underscore"
    
    if username.endswith('.') or username.endswith('_'):
        return False, "Username cannot end with a dot or underscore"
    
    return True, None


def validate_serial_number(serial_number: str) -> Tuple[bool, Optional[str]]:
    """
    Validate serial number format.
    
    Args:
        serial_number: Serial number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not serial_number:
        return False, "Serial number is required"
    
    if len(serial_number) < 3:
        return False, "Serial number must be at least 3 characters long"
    
    if len(serial_number) > 100:
        return False, "Serial number is too long (max 100 characters)"
    
    # Serial number should not contain only whitespace
    if serial_number.strip() != serial_number:
        return False, "Serial number cannot have leading or trailing whitespace"
    
    return True, None


def validate_positive_number(value: str, field_name: str) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Validate positive number input.
    
    Args:
        value: String value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message, parsed_value)
    """
    if not value:
        return True, None, None  # Optional field
    
    try:
        parsed_value = float(value)
        if parsed_value < 0:
            return False, f"{field_name} must be a positive number", None
        return True, None, parsed_value
    except ValueError:
        return False, f"{field_name} must be a valid number", None


def validate_positive_integer(value: str, field_name: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Validate positive integer input.
    
    Args:
        value: String value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message, parsed_value)
    """
    if not value:
        return True, None, None  # Optional field
    
    try:
        parsed_value = int(value)
        if parsed_value < 0:
            return False, f"{field_name} must be a positive integer", None
        return True, None, parsed_value
    except ValueError:
        return False, f"{field_name} must be a valid integer", None


def validate_date_string(date_string: str, field_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date string format (YYYY-MM-DD).
    
    Args:
        date_string: Date string to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not date_string:
        return True, None  # Optional field
    
    # Check format with regex
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_string):
        return False, f"{field_name} must be in YYYY-MM-DD format"
    
    # Try to parse the date to ensure it's valid
    try:
        from datetime import datetime
        datetime.strptime(date_string, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, f"{field_name} is not a valid date"
