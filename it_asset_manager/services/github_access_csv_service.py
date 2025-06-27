"""
CSV service for bulk GitHub access operations.

This module handles CSV import/export functionality for GitHub access,
including sample file generation and bulk data upload.
"""

import csv
import io
from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
from flask import current_app

from ..models.access import GitHubAccess
from ..core.database import db


class GitHubAccessCSVService:
    """Service for handling CSV operations for GitHub access."""
    
    # Define CSV headers and their corresponding model fields
    CSV_HEADERS = [
        'user_name',
        'organization_name',
        'repo_name',
        'access_type',
        'assign_date',
        'remove_date',
        'status',
        'remarks'
    ]
    
    # Sample data for GitHub access
    SAMPLE_DATA = [
        {
            'user_name': 'john.doe',
            'organization_name': 'company-org',
            'repo_name': 'main-application',
            'access_type': 'admin',
            'assign_date': '2024-01-15',
            'remove_date': '',
            'status': 'active',
            'remarks': 'Lead developer access'
        },
        {
            'user_name': 'jane.smith',
            'organization_name': 'company-org',
            'repo_name': 'frontend-app',
            'access_type': 'write',
            'assign_date': '2024-02-01',
            'remove_date': '',
            'status': 'active',
            'remarks': 'Frontend developer'
        },
        {
            'user_name': 'mike.wilson',
            'organization_name': 'company-org',
            'repo_name': 'test-automation',
            'access_type': 'read',
            'assign_date': '2024-01-20',
            'remove_date': '2024-06-30',
            'status': 'revoked',
            'remarks': 'QA team member - access revoked'
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
    def bulk_import_github_access(cls, validated_rows: List[Dict[str, Any]]) -> Tuple[int, int, List[str]]:
        """
        Import validated GitHub access data into database.
        
        Args:
            validated_rows: List of validated access dictionaries
            
        Returns:
            Tuple of (created_count, updated_count, error_messages)
        """
        created_count = 0
        updated_count = 0
        errors = []
        
        try:
            for row in validated_rows:
                try:
                    # Check if access already exists
                    existing_access = GitHubAccess.query.filter_by(
                        user_name=row['user_name'],
                        organization_name=row['organization_name'],
                        repo_name=row['repo_name']
                    ).first()
                    
                    if existing_access:
                        # Update existing access
                        cls._update_access_from_row(existing_access, row)
                        updated_count += 1
                    else:
                        # Create new access
                        new_access = cls._create_access_from_row(row)
                        db.session.add(new_access)
                        created_count += 1
                        
                except Exception as e:
                    errors.append(f"Error processing GitHub access for {row.get('user_name', 'Unknown')} - {row.get('repo_name', 'Unknown')}: {str(e)}")
            
            # Commit all changes
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            errors.append(f"Database error during import: {str(e)}")
        
        return created_count, updated_count, errors
    
    @classmethod
    def export_github_access_to_csv(cls, access_records: List[GitHubAccess]) -> io.StringIO:
        """
        Export GitHub access to CSV format.
        
        Args:
            access_records: List of GitHubAccess objects to export
            
        Returns:
            StringIO object containing CSV data
        """
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=cls.CSV_HEADERS)
        
        # Write headers
        writer.writeheader()
        
        # Write access data
        for access in access_records:
            row = cls._access_to_csv_row(access)
            writer.writerow(row)
        
        output.seek(0)
        return output
    
    @classmethod
    def _validate_headers(cls, headers: List[str]) -> bool:
        """Validate CSV headers match expected format."""
        if not headers:
            return False
        
        # Check if all required headers are present
        required_headers = {'user_name', 'organization_name', 'repo_name', 'access_type'}
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
        if not row.get('user_name', '').strip():
            raise ValueError("User name is required")
        
        if not row.get('organization_name', '').strip():
            raise ValueError("Organization name is required")
        
        if not row.get('repo_name', '').strip():
            raise ValueError("Repository name is required")
        
        if not row.get('access_type', '').strip():
            raise ValueError("Access type is required")
        
        # Clean and validate each field
        for field in cls.CSV_HEADERS:
            value = row.get(field, '').strip()
            
            if field in ['assign_date', 'remove_date']:
                cleaned_row[field] = cls._parse_date(value) if value else None
            else:
                cleaned_row[field] = value if value else None
        
        # Set default values
        if not cleaned_row.get('status'):
            cleaned_row['status'] = 'active'
        
        if not cleaned_row.get('assign_date'):
            cleaned_row['assign_date'] = date.today()
        
        return cleaned_row
    
    @classmethod
    def _create_access_from_row(cls, row: Dict[str, Any]) -> GitHubAccess:
        """Create new GitHubAccess object from validated row data."""
        access = GitHubAccess()
        cls._update_access_from_row(access, row)
        return access
    
    @classmethod
    def _update_access_from_row(cls, access: GitHubAccess, row: Dict[str, Any]) -> None:
        """Update GitHubAccess object with row data."""
        for field, value in row.items():
            if hasattr(access, field) and value is not None:
                setattr(access, field, value)
        
        # Set updated timestamp
        access.updated_at = datetime.utcnow()
    
    @classmethod
    def _access_to_csv_row(cls, access: GitHubAccess) -> Dict[str, str]:
        """Convert GitHubAccess object to CSV row format."""
        row = {}
        for field in cls.CSV_HEADERS:
            value = getattr(access, field, None)
            
            if isinstance(value, date):
                row[field] = value.isoformat()
            elif value is not None:
                row[field] = str(value)
            else:
                row[field] = ''
        
        return row
    
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
