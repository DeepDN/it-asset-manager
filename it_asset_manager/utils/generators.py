"""
Generator utilities for creating unique identifiers and codes.

This module contains functions for generating asset tags, tokens,
and other unique identifiers used throughout the application.
"""

import secrets
import string
from typing import Optional
from datetime import datetime


def generate_asset_tag(asset_type: str, sequence_number: Optional[int] = None) -> str:
    """
    Generate asset tag based on asset type and sequence number.
    
    Args:
        asset_type: Type of asset
        sequence_number: Optional sequence number
        
    Returns:
        Generated asset tag
    """
    # Asset type prefixes
    type_prefixes = {
        'laptop': 'LAP',
        'desktop': 'DSK',
        'cpu': 'CPU',
        'server': 'SRV',
        'mobile': 'MOB',
        'tablet': 'TAB',
        'ipad': 'IPD',
        'iphone': 'IPH',
        'router': 'RTR',
        'switch': 'SWH',
        'firewall': 'FWL',
        'load_balancer': 'LBL',
        'access_point': 'APT',
        'monitor': 'MON',
        'television': 'TV',
        'projector': 'PRJ',
        'speaker': 'SPK',
        'microphone': 'MIC',
        'headset': 'HDS',
        'camera': 'CAM',
        'usb_drive': 'USB',
        'external_hdd': 'HDD',
        'external_ssd': 'SSD',
        'keyboard': 'KBD',
        'mouse': 'MSE',
        'hdmi_cable': 'HDM',
        'usb_cable': 'USC',
        'ethernet_cable': 'ETH',
        'lightning_cable': 'LTG'
    }
    
    # Get prefix for asset type
    prefix = type_prefixes.get(asset_type.lower(), 'GEN')  # GEN for generic
    
    # Generate sequence number if not provided
    if sequence_number is None:
        # Use timestamp-based sequence
        timestamp = datetime.now()
        sequence_number = int(timestamp.strftime('%m%d%H%M'))
    
    # Format with leading zeros
    return f"{prefix}{sequence_number:04d}"


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token.
    
    Args:
        length: Length of token to generate
        
    Returns:
        Generated secure token
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_password_reset_token() -> str:
    """
    Generate secure token for password reset.
    
    Returns:
        Generated password reset token
    """
    return generate_secure_token(32)


def generate_session_id() -> str:
    """
    Generate secure session ID.
    
    Returns:
        Generated session ID
    """
    return generate_secure_token(64)


def generate_api_key() -> str:
    """
    Generate API key for external integrations.
    
    Returns:
        Generated API key
    """
    # API key format: prefix + timestamp + random
    prefix = 'itam'
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = generate_secure_token(16)
    
    return f"{prefix}_{timestamp}_{random_part}"


def generate_backup_filename(prefix: str = 'backup') -> str:
    """
    Generate filename for backup files.
    
    Args:
        prefix: Prefix for filename
        
    Returns:
        Generated backup filename
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}"


def generate_export_filename(export_type: str) -> str:
    """
    Generate filename for data exports.
    
    Args:
        export_type: Type of export (assets, users, etc.)
        
    Returns:
        Generated export filename
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{export_type}_export_{timestamp}.csv"


def generate_unique_serial_number(prefix: str = 'SN') -> str:
    """
    Generate unique serial number.
    
    Args:
        prefix: Prefix for serial number
        
    Returns:
        Generated serial number
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = generate_secure_token(6).upper()
    
    return f"{prefix}{timestamp}{random_suffix}"


def generate_qr_code_data(asset_tag: str, base_url: str = 'https://assets.company.com') -> str:
    """
    Generate QR code data for asset tracking.
    
    Args:
        asset_tag: Asset tag to encode
        base_url: Base URL for asset lookup
        
    Returns:
        QR code data string
    """
    return f"{base_url}/asset/{asset_tag}"


def generate_barcode_data(asset_tag: str) -> str:
    """
    Generate barcode data for asset tracking.
    
    Args:
        asset_tag: Asset tag to encode
        
    Returns:
        Barcode data string
    """
    # Simple barcode format: asset tag with checksum
    checksum = sum(ord(c) for c in asset_tag) % 10
    return f"{asset_tag}{checksum}"
