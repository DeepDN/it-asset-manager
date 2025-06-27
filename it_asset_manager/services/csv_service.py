"""
CSV service for bulk asset operations.

This module handles CSV import/export functionality for assets,
including sample file generation and bulk data upload.
"""

import csv
import io
from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
from flask import current_app

from ..models.asset import Asset
from ..core.database import db


class CSVService:
    """Service for handling CSV operations for assets."""
    
    # Define CSV headers and their corresponding model fields
    CSV_HEADERS = [
        'asset_tag',
        'asset_type', 
        'asset_category',
        'ownership_type',
        'vendor_name',
        'rental_start_date',
        'rental_end_date',
        'rental_cost_monthly',
        'purchase_date',
        'purchase_cost',
        'warranty_expiry',
        'brand',
        'model',
        'serial_number',
        'processor',
        'ram_gb',
        'storage_gb',
        'storage_type',
        'port_count',
        'network_type',
        'screen_size',
        'resolution',
        'audio_type',
        'connector_type',
        'assigned_to',
        'assign_date',
        'location',
        'status',
        'condition',
        'remarks'
    ]
    
    # Sample data for different asset types
    SAMPLE_DATA = [
        {
            'asset_tag': 'LAP0001',
            'asset_type': 'laptop',
            'asset_category': 'Computing',
            'ownership_type': 'purchased',
            'vendor_name': '',
            'rental_start_date': '',
            'rental_end_date': '',
            'rental_cost_monthly': '',
            'purchase_date': '2024-01-15',
            'purchase_cost': '1200.00',
            'warranty_expiry': '2027-01-15',
            'brand': 'Dell',
            'model': 'Latitude 5520',
            'serial_number': 'DL123456789',
            'processor': 'Intel Core i7-1165G7',
            'ram_gb': '16',
            'storage_gb': '512',
            'storage_type': 'SSD',
            'port_count': '',
            'network_type': '',
            'screen_size': '15.6"',
            'resolution': '1920x1080',
            'audio_type': '',
            'connector_type': '',
            'assigned_to': 'john.doe',
            'assign_date': '2024-01-20',
            'location': 'Office Floor 2, Desk 15',
            'status': 'assigned',
            'condition': 'excellent',
            'remarks': 'Primary work laptop'
        },
        {
            'asset_tag': 'RTR0001',
            'asset_type': 'router',
            'asset_category': 'Network',
            'ownership_type': 'rented',
            'vendor_name': 'TechRent Solutions',
            'rental_start_date': '2024-01-01',
            'rental_end_date': '2024-12-31',
            'rental_cost_monthly': '150.00',
            'purchase_date': '',
            'purchase_cost': '',
            'warranty_expiry': '2025-01-01',
            'brand': 'Cisco',
            'model': 'ISR 4331',
            'serial_number': 'CS987654321',
            'processor': '',
            'ram_gb': '',
            'storage_gb': '',
            'storage_type': '',
            'port_count': '4',
            'network_type': 'Ethernet',
            'screen_size': '',
            'resolution': '',
            'audio_type': '',
            'connector_type': '',
            'assigned_to': '',
            'assign_date': '',
            'location': 'Server Room A, Rack 1',
            'status': 'unassigned',
            'condition': 'good',
            'remarks': 'Main office router'
        },
        {
            'asset_tag': 'MON0001',
            'asset_type': 'monitor',
            'asset_category': 'Display',
            'ownership_type': 'purchased',
            'vendor_name': '',
            'rental_start_date': '',
            'rental_end_date': '',
            'rental_cost_monthly': '',
            'purchase_date': '2024-02-01',
            'purchase_cost': '350.00',
            'warranty_expiry': '2027-02-01',
            'brand': 'Samsung',
            'model': 'Odyssey G5',
            'serial_number': 'SM456789123',
            'processor': '',
            'ram_gb': '',
            'storage_gb': '',
            'storage_type': '',
            'port_count': '',
            'network_type': '',
            'screen_size': '27"',
            'resolution': '2560x1440',
            'audio_type': '',
            'connector_type': 'HDMI',
            'assigned_to': 'jane.smith',
            'assign_date': '2024-02-05',
            'location': 'Office Floor 1, Desk 8',
            'status': 'assigned',
            'condition': 'excellent',
            'remarks': 'Secondary monitor for development'
        }
    ]
    
    @classmethod
    def generate_sample_csv(cls) -> io.StringIO:
        """
        Generate a sample CSV file with headers and example data.
        
        Returns:
            StringIO object containing CSV data
        """
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=cls.CSV_HEADERS)
        
        # Write headers
        writer.writeheader()
        
        # Write sample data
        for row in cls.SAMPLE_DATA:
            writer.writerow(row)
        
        output.seek(0)
        return output
    
    @classmethod
    def parse_csv_file(cls, file_content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parse CSV file content and validate data.
        
        Args:
            file_content: CSV file content as string
            
        Returns:
            Tuple of (valid_rows, error_messages)
        """
        valid_rows = []
        errors = []
        
        try:
            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(file_content))
            
            # Validate headers
            if not cls._validate_headers(csv_reader.fieldnames):
                errors.append("Invalid CSV headers. Please use the sample CSV template.")
                return valid_rows, errors
            
            # Process each row
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (after header)
                try:
                    validated_row = cls._validate_and_clean_row(row, row_num)
                    if validated_row:
                        valid_rows.append(validated_row)
                except ValueError as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    
        except Exception as e:
            errors.append(f"Error parsing CSV file: {str(e)}")
        
        return valid_rows, errors
    
    @classmethod
    def bulk_import_assets(cls, validated_rows: List[Dict[str, Any]]) -> Tuple[int, int, List[str]]:
        """
        Import validated asset data into database.
        
        Args:
            validated_rows: List of validated asset dictionaries
            
        Returns:
            Tuple of (created_count, updated_count, error_messages)
        """
        created_count = 0
        updated_count = 0
        errors = []
        
        try:
            for row in validated_rows:
                try:
                    # Check if asset already exists
                    existing_asset = Asset.find_by_tag(row['asset_tag'])
                    
                    # Check for duplicate serial number
                    existing_serial = Asset.find_by_serial(row['serial_number'])
                    if existing_serial and (not existing_asset or existing_serial.asset_tag != row['asset_tag']):
                        errors.append(f"Serial number {row['serial_number']} already exists for asset {existing_serial.asset_tag}")
                        continue
                    
                    if existing_asset:
                        # Update existing asset
                        cls._update_asset_from_row(existing_asset, row)
                        updated_count += 1
                    else:
                        # Create new asset
                        new_asset = cls._create_asset_from_row(row)
                        db.session.add(new_asset)
                        created_count += 1
                        
                except Exception as e:
                    errors.append(f"Error processing asset {row.get('asset_tag', 'Unknown')}: {str(e)}")
            
            # Commit all changes
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            errors.append(f"Database error during import: {str(e)}")
        
        return created_count, updated_count, errors
    
    @classmethod
    def export_assets_to_csv(cls, assets: List[Asset]) -> io.StringIO:
        """
        Export assets to CSV format.
        
        Args:
            assets: List of Asset objects to export
            
        Returns:
            StringIO object containing CSV data
        """
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=cls.CSV_HEADERS)
        
        # Write headers
        writer.writeheader()
        
        # Write asset data
        for asset in assets:
            row = cls._asset_to_csv_row(asset)
            writer.writerow(row)
        
        output.seek(0)
        return output
    
    @classmethod
    def _validate_headers(cls, headers: List[str]) -> bool:
        """Validate CSV headers match expected format."""
        if not headers:
            return False
        
        # Check if all required headers are present
        required_headers = {'asset_tag', 'asset_type', 'serial_number'}
        provided_headers = set(headers)
        
        return required_headers.issubset(provided_headers)
    
    @classmethod
    def _validate_and_clean_row(cls, row: Dict[str, str], row_num: int) -> Dict[str, Any]:
        """
        Validate and clean a single CSV row.
        
        Args:
            row: Raw CSV row data
            row_num: Row number for error reporting
            
        Returns:
            Cleaned and validated row data
            
        Raises:
            ValueError: If validation fails
        """
        cleaned_row = {}
        
        # Required fields validation
        if not row.get('asset_tag', '').strip():
            raise ValueError("Asset tag is required")
        
        if not row.get('asset_type', '').strip():
            raise ValueError("Asset type is required")
        
        if not row.get('serial_number', '').strip():
            raise ValueError("Serial number is required")
        
        # Note: Database checks will be done during import, not during parsing
        # to avoid Flask application context issues during testing
        
        # Clean and validate each field
        for field in cls.CSV_HEADERS:
            value = row.get(field, '').strip()
            
            if field in ['ram_gb', 'storage_gb', 'port_count']:
                cleaned_row[field] = int(value) if value and value.isdigit() else None
            elif field in ['rental_cost_monthly', 'purchase_cost']:
                cleaned_row[field] = float(value) if value and cls._is_valid_float(value) else None
            elif field in ['rental_start_date', 'rental_end_date', 'purchase_date', 'warranty_expiry', 'assign_date']:
                cleaned_row[field] = cls._parse_date(value) if value else None
            else:
                cleaned_row[field] = value if value else None
        
        # Set default values
        if not cleaned_row.get('asset_category'):
            cleaned_row['asset_category'] = cls._get_category_from_type(cleaned_row['asset_type'])
        
        if not cleaned_row.get('ownership_type'):
            cleaned_row['ownership_type'] = 'purchased'
        
        if not cleaned_row.get('status'):
            cleaned_row['status'] = 'assigned' if cleaned_row.get('assigned_to') else 'unassigned'
        
        if not cleaned_row.get('condition'):
            cleaned_row['condition'] = 'good'
        
        return cleaned_row
    
    @classmethod
    def _create_asset_from_row(cls, row: Dict[str, Any]) -> Asset:
        """Create new Asset object from validated row data."""
        asset = Asset()
        cls._update_asset_from_row(asset, row)
        return asset
    
    @classmethod
    def _update_asset_from_row(cls, asset: Asset, row: Dict[str, Any]) -> None:
        """Update Asset object with row data."""
        for field, value in row.items():
            if hasattr(asset, field) and value is not None:
                setattr(asset, field, value)
        
        # Set updated timestamp
        asset.updated_at = datetime.utcnow()
    
    @classmethod
    def _asset_to_csv_row(cls, asset: Asset) -> Dict[str, str]:
        """Convert Asset object to CSV row format."""
        row = {}
        for field in cls.CSV_HEADERS:
            value = getattr(asset, field, None)
            
            if isinstance(value, date):
                row[field] = value.isoformat()
            elif value is not None:
                row[field] = str(value)
            else:
                row[field] = ''
        
        return row
    
    @classmethod
    def _is_valid_float(cls, value: str) -> bool:
        """Check if string can be converted to float."""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    @classmethod
    def _parse_date(cls, date_str: str) -> Optional[date]:
        """Parse date string in various formats."""
        if not date_str:
            return None
        
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")
    
    @classmethod
    def _get_category_from_type(cls, asset_type: str) -> str:
        """Get asset category based on asset type."""
        type_to_category = {
            'laptop': 'Computing',
            'desktop': 'Computing', 
            'cpu': 'Computing',
            'mobile': 'Mobile',
            'tablet': 'Mobile',
            'ipad': 'Mobile',
            'iphone': 'Mobile',
            'router': 'Network',
            'switch': 'Network',
            'firewall': 'Network',
            'load_balancer': 'Network',
            'monitor': 'Display',
            'television': 'Display',
            'projector': 'Display',
            'speaker': 'Audio/Video',
            'microphone': 'Audio/Video',
            'usb_drive': 'Storage',
            'external_hdd': 'Storage',
            'external_ssd': 'Storage',
            'keyboard': 'Peripherals',
            'mouse': 'Peripherals',
            'hdmi_cable': 'Connectors',
            'usb_c_cable': 'Connectors',
            'lightning_cable': 'Connectors',
            'ethernet_cable': 'Connectors'
        }
        
        return type_to_category.get(asset_type.lower(), 'Other')
