"""
Asset management business logic service.

This module contains the AssetService class that handles all business logic
related to asset management, including CRUD operations, validation, and reporting.
"""

from datetime import date, datetime
from typing import List, Dict, Any, Optional, Tuple
import csv
import io

from ..models.asset import Asset
from ..core.database import db


class AssetService:
    """Service class for asset management business logic."""
    
    @staticmethod
    def create_asset(asset_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Asset]]:
        """
        Create a new asset with validation.
        
        Args:
            asset_data: Dictionary containing asset information
            
        Returns:
            Tuple of (success, message, asset_object)
        """
        try:
            # Validate required fields
            required_fields = ['asset_tag', 'asset_type', 'serial_number']
            for field in required_fields:
                if not asset_data.get(field):
                    return False, f"Missing required field: {field}", None
            
            # Check for duplicate asset tag
            if Asset.find_by_tag(asset_data['asset_tag']):
                return False, f"Asset tag {asset_data['asset_tag']} already exists", None
            
            # Check for duplicate serial number
            if Asset.find_by_serial(asset_data['serial_number']):
                return False, f"Serial number {asset_data['serial_number']} already exists", None
            
            # Create asset object
            asset = Asset()
            
            # Set basic fields
            asset.asset_tag = asset_data['asset_tag']
            asset.asset_type = asset_data['asset_type']
            asset.asset_category = AssetService._determine_category(asset_data['asset_type'])
            asset.serial_number = asset_data['serial_number']
            
            # Set optional fields
            optional_fields = [
                'ownership_type', 'vendor_name', 'brand', 'model', 'processor',
                'ram_gb', 'storage_gb', 'storage_type', 'port_count', 'network_type',
                'screen_size', 'resolution', 'audio_type', 'connector_type',
                'location', 'condition', 'remarks'
            ]
            
            for field in optional_fields:
                if asset_data.get(field):
                    setattr(asset, field, asset_data[field])
            
            # Set date fields
            date_fields = ['rental_start_date', 'rental_end_date', 'purchase_date', 'warranty_expiry']
            for field in date_fields:
                if asset_data.get(field):
                    try:
                        date_value = datetime.strptime(asset_data[field], '%Y-%m-%d').date()
                        setattr(asset, field, date_value)
                    except ValueError:
                        return False, f"Invalid date format for {field}", None
            
            # Set numeric fields
            numeric_fields = ['rental_cost_monthly', 'purchase_cost', 'ram_gb', 'storage_gb', 'port_count']
            for field in numeric_fields:
                if asset_data.get(field):
                    try:
                        numeric_value = float(asset_data[field]) if field in ['rental_cost_monthly', 'purchase_cost'] else int(asset_data[field])
                        setattr(asset, field, numeric_value)
                    except ValueError:
                        return False, f"Invalid numeric value for {field}", None
            
            # Save to database
            db.session.add(asset)
            db.session.commit()
            
            return True, f"Asset {asset.asset_tag} created successfully", asset
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error creating asset: {str(e)}", None
    
    @staticmethod
    def update_asset(asset_id: int, asset_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Asset]]:
        """
        Update an existing asset.
        
        Args:
            asset_id: ID of asset to update
            asset_data: Dictionary containing updated asset information
            
        Returns:
            Tuple of (success, message, asset_object)
        """
        try:
            asset = db.session.get(Asset, asset_id)
            if not asset:
                return False, "Asset not found", None
            
            # Check for duplicate asset tag (excluding current asset)
            if asset_data.get('asset_tag') and asset_data['asset_tag'] != asset.asset_tag:
                existing_asset = Asset.find_by_tag(asset_data['asset_tag'])
                if existing_asset and existing_asset.id != asset_id:
                    return False, f"Asset tag {asset_data['asset_tag']} already exists", None
            
            # Check for duplicate serial number (excluding current asset)
            if asset_data.get('serial_number') and asset_data['serial_number'] != asset.serial_number:
                existing_asset = Asset.find_by_serial(asset_data['serial_number'])
                if existing_asset and existing_asset.id != asset_id:
                    return False, f"Serial number {asset_data['serial_number']} already exists", None
            
            # Update fields
            updatable_fields = [
                'asset_tag', 'asset_type', 'serial_number', 'ownership_type',
                'vendor_name', 'brand', 'model', 'processor', 'ram_gb', 'storage_gb',
                'storage_type', 'port_count', 'network_type', 'screen_size',
                'resolution', 'audio_type', 'connector_type', 'location',
                'condition', 'remarks'
            ]
            
            for field in updatable_fields:
                if field in asset_data:
                    setattr(asset, field, asset_data[field])
            
            # Update category if asset type changed
            if asset_data.get('asset_type'):
                asset.asset_category = AssetService._determine_category(asset_data['asset_type'])
            
            # Update date fields
            date_fields = ['rental_start_date', 'rental_end_date', 'purchase_date', 'warranty_expiry']
            for field in date_fields:
                if field in asset_data:
                    if asset_data[field]:
                        try:
                            date_value = datetime.strptime(asset_data[field], '%Y-%m-%d').date()
                            setattr(asset, field, date_value)
                        except ValueError:
                            return False, f"Invalid date format for {field}", None
                    else:
                        setattr(asset, field, None)
            
            # Update numeric fields
            numeric_fields = ['rental_cost_monthly', 'purchase_cost', 'ram_gb', 'storage_gb', 'port_count']
            for field in numeric_fields:
                if field in asset_data:
                    if asset_data[field]:
                        try:
                            numeric_value = float(asset_data[field]) if field in ['rental_cost_monthly', 'purchase_cost'] else int(asset_data[field])
                            setattr(asset, field, numeric_value)
                        except ValueError:
                            return False, f"Invalid numeric value for {field}", None
                    else:
                        setattr(asset, field, None)
            
            asset.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True, f"Asset {asset.asset_tag} updated successfully", asset
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating asset: {str(e)}", None
    
    @staticmethod
    def delete_asset(asset_id: int) -> Tuple[bool, str]:
        """
        Delete an asset.
        
        Args:
            asset_id: ID of asset to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            asset = db.session.get(Asset, asset_id)
            if not asset:
                return False, "Asset not found"
            
            asset_tag = asset.asset_tag
            db.session.delete(asset)
            db.session.commit()
            
            return True, f"Asset {asset_tag} deleted successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error deleting asset: {str(e)}"
    
    @staticmethod
    def assign_asset(asset_id: int, username: str, location: Optional[str] = None) -> Tuple[bool, str]:
        """
        Assign asset to a user.
        
        Args:
            asset_id: ID of asset to assign
            username: Username to assign asset to
            location: Optional location information
            
        Returns:
            Tuple of (success, message)
        """
        try:
            asset = db.session.get(Asset, asset_id)
            if not asset:
                return False, "Asset not found"
            
            if asset.is_assigned:
                return False, f"Asset is already assigned to {asset.assigned_to}"
            
            asset.assign_to_user(username, location)
            db.session.commit()
            
            return True, f"Asset {asset.asset_tag} assigned to {username}"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error assigning asset: {str(e)}"
    
    @staticmethod
    def unassign_asset(asset_id: int) -> Tuple[bool, str]:
        """
        Unassign asset from current user.
        
        Args:
            asset_id: ID of asset to unassign
            
        Returns:
            Tuple of (success, message)
        """
        try:
            asset = db.session.get(Asset, asset_id)
            if not asset:
                return False, "Asset not found"
            
            if not asset.is_assigned:
                return False, "Asset is not currently assigned"
            
            assigned_user = asset.assigned_to
            asset.unassign()
            db.session.commit()
            
            return True, f"Asset {asset.asset_tag} unassigned from {assigned_user}"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error unassigning asset: {str(e)}"
    
    @staticmethod
    def get_asset_statistics() -> Dict[str, Any]:
        """
        Get comprehensive asset statistics.
        
        Returns:
            Dictionary containing various asset statistics
        """
        try:
            total_assets = Asset.query.count()
            assigned_assets = Asset.query.filter_by(status='assigned').count()
            unassigned_assets = Asset.query.filter_by(status='unassigned').count()
            maintenance_assets = Asset.query.filter_by(status='maintenance').count()
            retired_assets = Asset.query.filter_by(status='retired').count()
            
            # Assets by type
            asset_types = db.session.query(
                Asset.asset_type,
                db.func.count(Asset.id).label('count')
            ).group_by(Asset.asset_type).all()
            
            # Assets by ownership
            ownership_types = db.session.query(
                Asset.ownership_type,
                db.func.count(Asset.id).label('count')
            ).group_by(Asset.ownership_type).all()
            
            # Expiring warranties
            expiring_warranties = len(Asset.find_expiring_warranties(30))
            
            return {
                'total_assets': total_assets,
                'assigned_assets': assigned_assets,
                'unassigned_assets': unassigned_assets,
                'maintenance_assets': maintenance_assets,
                'retired_assets': retired_assets,
                'asset_types': {item.asset_type: item.count for item in asset_types},
                'ownership_types': {item.ownership_type: item.count for item in ownership_types},
                'expiring_warranties': expiring_warranties
            }
            
        except Exception as e:
            return {'error': f"Error getting statistics: {str(e)}"}
    
    @staticmethod
    def export_assets_csv() -> str:
        """
        Export all assets to CSV format.
        
        Returns:
            CSV string containing all asset data
        """
        try:
            assets = Asset.query.all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            headers = [
                'Asset Tag', 'Asset Type', 'Category', 'Ownership Type', 'Brand', 'Model',
                'Serial Number', 'Processor', 'RAM (GB)', 'Storage (GB)', 'Storage Type',
                'Port Count', 'Network Type', 'Screen Size', 'Resolution', 'Audio Type',
                'Connector Type', 'Assigned To', 'Assign Date', 'Location', 'Status',
                'Condition', 'Purchase Date', 'Purchase Cost', 'Warranty Expiry',
                'Vendor Name', 'Rental Start', 'Rental End', 'Monthly Cost', 'Remarks'
            ]
            writer.writerow(headers)
            
            # Write asset data
            for asset in assets:
                row = [
                    asset.asset_tag, asset.asset_type, asset.asset_category,
                    asset.ownership_type, asset.brand, asset.model, asset.serial_number,
                    asset.processor, asset.ram_gb, asset.storage_gb, asset.storage_type,
                    asset.port_count, asset.network_type, asset.screen_size,
                    asset.resolution, asset.audio_type, asset.connector_type,
                    asset.assigned_to, asset.assign_date, asset.location,
                    asset.status, asset.condition, asset.purchase_date,
                    asset.purchase_cost, asset.warranty_expiry, asset.vendor_name,
                    asset.rental_start_date, asset.rental_end_date,
                    asset.rental_cost_monthly, asset.remarks
                ]
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            return f"Error exporting assets: {str(e)}"
    
    @staticmethod
    def _determine_category(asset_type: str) -> str:
        """
        Determine asset category based on asset type.
        
        Args:
            asset_type: Type of asset
            
        Returns:
            Asset category string
        """
        category_mapping = {
            # Computing devices
            'laptop': 'Computing',
            'desktop': 'Computing', 
            'cpu': 'Computing',
            'server': 'Computing',
            
            # Mobile devices
            'mobile': 'Mobile',
            'tablet': 'Mobile',
            'ipad': 'Mobile',
            'iphone': 'Mobile',
            
            # Network equipment
            'router': 'Network',
            'switch': 'Network',
            'firewall': 'Network',
            'load_balancer': 'Network',
            'access_point': 'Network',
            
            # Display equipment
            'monitor': 'Display',
            'television': 'Display',
            'projector': 'Display',
            
            # Audio/Video equipment
            'speaker': 'Audio/Video',
            'microphone': 'Audio/Video',
            'headset': 'Audio/Video',
            'camera': 'Audio/Video',
            
            # Storage and peripherals
            'usb_drive': 'Storage',
            'external_hdd': 'Storage',
            'external_ssd': 'Storage',
            'keyboard': 'Peripheral',
            'mouse': 'Peripheral',
            
            # Connectors and cables
            'hdmi_cable': 'Connector',
            'usb_cable': 'Connector',
            'ethernet_cable': 'Connector',
            'lightning_cable': 'Connector'
        }
        
        return category_mapping.get(asset_type.lower(), 'Other')
