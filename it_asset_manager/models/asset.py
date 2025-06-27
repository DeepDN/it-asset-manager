"""
Asset model for IT asset management.

This module contains the Asset model with comprehensive fields for tracking
various types of IT assets including computers, network equipment, and peripherals.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import and_, or_
from flask_sqlalchemy import SQLAlchemy

from ..core.database import db


class Asset(db.Model):
    """
    Asset model for comprehensive IT asset tracking.
    
    Supports various asset types including:
    - Computing devices (laptops, desktops, servers)
    - Network equipment (routers, switches, firewalls)
    - Mobile devices (phones, tablets)
    - Display equipment (monitors, TVs, projectors)
    - Audio/Video equipment
    - Storage devices and peripherals
    """
    
    __tablename__ = 'assets'
    
    # Primary identification
    id = db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(50), unique=True, nullable=False, index=True)
    asset_type = db.Column(db.String(50), nullable=False, index=True)
    asset_category = db.Column(db.String(50), nullable=False, index=True)
    
    # Ownership and financial information
    ownership_type = db.Column(db.String(20), nullable=False, default='purchased', index=True)
    vendor_name = db.Column(db.String(100))
    rental_start_date = db.Column(db.Date)
    rental_end_date = db.Column(db.Date)
    rental_cost_monthly = db.Column(db.Float)
    purchase_date = db.Column(db.Date)
    purchase_cost = db.Column(db.Float)
    warranty_expiry = db.Column(db.Date)
    
    # Basic asset information
    brand = db.Column(db.String(50), index=True)
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Computing device specifications
    processor = db.Column(db.String(100))
    ram_gb = db.Column(db.Integer)
    storage_gb = db.Column(db.Integer)
    storage_type = db.Column(db.String(20))  # SSD, HDD
    
    # Network device specifications
    port_count = db.Column(db.Integer)
    network_type = db.Column(db.String(50))  # Ethernet, WiFi, Fiber
    
    # Display specifications
    screen_size = db.Column(db.String(20))
    resolution = db.Column(db.String(20))  # 1920x1080, 4K, etc.
    
    # Audio/Video specifications
    audio_type = db.Column(db.String(50))  # Microphone, Speaker, Headset
    connector_type = db.Column(db.String(50))  # HDMI, USB-C, Lightning
    
    # Assignment and location tracking
    assigned_to = db.Column(db.String(100), index=True)
    assign_date = db.Column(db.Date)
    remove_date = db.Column(db.Date)
    location = db.Column(db.String(100), index=True)
    
    # Status and condition
    status = db.Column(db.String(20), default='unassigned', nullable=False, index=True)
    condition = db.Column(db.String(20), default='good', nullable=False, index=True)
    
    # Additional information
    remarks = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """String representation of Asset object."""
        return f'<Asset {self.asset_tag}: {self.asset_type}>'
    
    @property
    def is_assigned(self) -> bool:
        """Check if asset is currently assigned."""
        return self.status == 'assigned' and self.assigned_to is not None
    
    @property
    def is_rental(self) -> bool:
        """Check if asset is rented."""
        return self.ownership_type in ['rented', 'leased']
    
    @property
    def is_warranty_expired(self) -> bool:
        """Check if warranty has expired."""
        if not self.warranty_expiry:
            return False
        return date.today() > self.warranty_expiry
    
    @property
    def rental_days_remaining(self) -> Optional[int]:
        """Calculate remaining rental days."""
        if not self.is_rental or not self.rental_end_date:
            return None
        
        remaining = (self.rental_end_date - date.today()).days
        return max(0, remaining)
    
    def assign_to_user(self, username: str, location: Optional[str] = None) -> None:
        """
        Assign asset to a user.
        
        Args:
            username: Username to assign asset to
            location: Optional location information
        """
        self.assigned_to = username
        self.assign_date = date.today()
        self.remove_date = None
        self.status = 'assigned'
        if location:
            self.location = location
        self.updated_at = datetime.utcnow()
    
    def unassign(self) -> None:
        """Unassign asset from current user."""
        self.remove_date = date.today()
        self.status = 'unassigned'
        self.updated_at = datetime.utcnow()
        # Keep assigned_to for history, but could be cleared if needed
    
    def set_maintenance_mode(self, remarks: Optional[str] = None) -> None:
        """
        Set asset to maintenance mode.
        
        Args:
            remarks: Optional maintenance notes
        """
        self.status = 'maintenance'
        if remarks:
            self.remarks = remarks
        self.updated_at = datetime.utcnow()
    
    def retire_asset(self, remarks: Optional[str] = None) -> None:
        """
        Retire asset from active use.
        
        Args:
            remarks: Optional retirement notes
        """
        self.status = 'retired'
        if self.assigned_to:
            self.unassign()
        if remarks:
            self.remarks = remarks
        self.updated_at = datetime.utcnow()
    
    @classmethod
    def find_by_tag(cls, asset_tag: str) -> Optional['Asset']:
        """
        Find asset by asset tag.
        
        Args:
            asset_tag: Asset tag to search for
            
        Returns:
            Asset object if found, None otherwise
        """
        return cls.query.filter_by(asset_tag=asset_tag).first()
    
    @classmethod
    def find_by_serial(cls, serial_number: str) -> Optional['Asset']:
        """
        Find asset by serial number.
        
        Args:
            serial_number: Serial number to search for
            
        Returns:
            Asset object if found, None otherwise
        """
        return cls.query.filter_by(serial_number=serial_number).first()
    
    @classmethod
    def find_assigned_to_user(cls, username: str) -> List['Asset']:
        """
        Find all assets assigned to a specific user.
        
        Args:
            username: Username to search for
            
        Returns:
            List of Asset objects assigned to the user
        """
        return cls.query.filter_by(assigned_to=username, status='assigned').all()
    
    @classmethod
    def find_by_type(cls, asset_type: str) -> List['Asset']:
        """
        Find all assets of a specific type.
        
        Args:
            asset_type: Asset type to search for
            
        Returns:
            List of Asset objects of the specified type
        """
        return cls.query.filter_by(asset_type=asset_type).all()
    
    @classmethod
    def find_expiring_warranties(cls, days: int = 30) -> List['Asset']:
        """
        Find assets with warranties expiring within specified days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of Asset objects with expiring warranties
        """
        cutoff_date = date.today() + timedelta(days=days)
        return cls.query.filter(
            and_(
                cls.warranty_expiry.isnot(None),
                cls.warranty_expiry <= cutoff_date,
                cls.warranty_expiry >= date.today()
            )
        ).all()
    
    @classmethod
    def search(cls, query: str) -> List['Asset']:
        """
        Search assets by multiple fields.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching Asset objects
        """
        search_term = f'%{query}%'
        return cls.query.filter(
            or_(
                cls.asset_tag.ilike(search_term),
                cls.asset_type.ilike(search_term),
                cls.brand.ilike(search_term),
                cls.model.ilike(search_term),
                cls.serial_number.ilike(search_term),
                cls.assigned_to.ilike(search_term),
                cls.location.ilike(search_term)
            )
        ).all()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert asset object to dictionary.
        
        Returns:
            Dictionary representation of asset
        """
        return {
            'id': self.id,
            'asset_tag': self.asset_tag,
            'asset_type': self.asset_type,
            'asset_category': self.asset_category,
            'ownership_type': self.ownership_type,
            'vendor_name': self.vendor_name,
            'rental_start_date': self.rental_start_date.isoformat() if self.rental_start_date else None,
            'rental_end_date': self.rental_end_date.isoformat() if self.rental_end_date else None,
            'rental_cost_monthly': self.rental_cost_monthly,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_cost': self.purchase_cost,
            'warranty_expiry': self.warranty_expiry.isoformat() if self.warranty_expiry else None,
            'brand': self.brand,
            'model': self.model,
            'serial_number': self.serial_number,
            'processor': self.processor,
            'ram_gb': self.ram_gb,
            'storage_gb': self.storage_gb,
            'storage_type': self.storage_type,
            'port_count': self.port_count,
            'network_type': self.network_type,
            'screen_size': self.screen_size,
            'resolution': self.resolution,
            'audio_type': self.audio_type,
            'connector_type': self.connector_type,
            'assigned_to': self.assigned_to,
            'assign_date': self.assign_date.isoformat() if self.assign_date else None,
            'remove_date': self.remove_date.isoformat() if self.remove_date else None,
            'location': self.location,
            'status': self.status,
            'condition': self.condition,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_assigned': self.is_assigned,
            'is_rental': self.is_rental,
            'is_warranty_expired': self.is_warranty_expired,
            'rental_days_remaining': self.rental_days_remaining
        }
