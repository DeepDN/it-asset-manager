"""
Formatting utilities for data presentation.

This module contains formatting functions for displaying data
in user-friendly formats throughout the application.
"""

from datetime import datetime, date
from typing import Optional, Union


def format_date(date_obj: Optional[Union[datetime, date]], format_string: str = '%Y-%m-%d') -> str:
    """
    Format date object to string.
    
    Args:
        date_obj: Date or datetime object to format
        format_string: Format string for date formatting
        
    Returns:
        Formatted date string or empty string if None
    """
    if date_obj is None:
        return ''
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_string)
    elif isinstance(date_obj, date):
        return date_obj.strftime(format_string)
    else:
        return str(date_obj)


def format_datetime(datetime_obj: Optional[datetime], format_string: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format datetime object to string.
    
    Args:
        datetime_obj: Datetime object to format
        format_string: Format string for datetime formatting
        
    Returns:
        Formatted datetime string or empty string if None
    """
    if datetime_obj is None:
        return ''
    
    return datetime_obj.strftime(format_string)


def format_currency(amount: Optional[float], currency_symbol: str = '$') -> str:
    """
    Format currency amount.
    
    Args:
        amount: Amount to format
        currency_symbol: Currency symbol to use
        
    Returns:
        Formatted currency string
    """
    if amount is None:
        return ''
    
    return f"{currency_symbol}{amount:,.2f}"


def format_file_size(size_bytes: Optional[int]) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes is None or size_bytes == 0:
        return '0 B'
    
    size_names = ['B', 'KB', 'MB', 'GB', 'TB']
    size_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and size_index < len(size_names) - 1:
        size /= 1024.0
        size_index += 1
    
    if size_index == 0:
        return f"{int(size)} {size_names[size_index]}"
    else:
        return f"{size:.1f} {size_names[size_index]}"


def format_storage_size(size_gb: Optional[int]) -> str:
    """
    Format storage size from GB to human-readable format.
    
    Args:
        size_gb: Size in GB
        
    Returns:
        Formatted storage size string
    """
    if size_gb is None:
        return ''
    
    if size_gb < 1024:
        return f"{size_gb} GB"
    else:
        size_tb = size_gb / 1024
        return f"{size_tb:.1f} TB"


def format_percentage(value: Optional[float], decimal_places: int = 1) -> str:
    """
    Format percentage value.
    
    Args:
        value: Percentage value (0-100)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return ''
    
    return f"{value:.{decimal_places}f}%"


def format_boolean(value: Optional[bool], true_text: str = 'Yes', false_text: str = 'No') -> str:
    """
    Format boolean value to text.
    
    Args:
        value: Boolean value
        true_text: Text to display for True
        false_text: Text to display for False
        
    Returns:
        Formatted boolean string
    """
    if value is None:
        return ''
    
    return true_text if value else false_text


def format_list(items: list, separator: str = ', ', max_items: Optional[int] = None) -> str:
    """
    Format list of items to string.
    
    Args:
        items: List of items to format
        separator: Separator between items
        max_items: Maximum number of items to display
        
    Returns:
        Formatted list string
    """
    if not items:
        return ''
    
    if max_items and len(items) > max_items:
        displayed_items = items[:max_items]
        remaining_count = len(items) - max_items
        formatted_items = separator.join(str(item) for item in displayed_items)
        return f"{formatted_items} and {remaining_count} more"
    else:
        return separator.join(str(item) for item in items)


def format_duration(start_date: Optional[date], end_date: Optional[date] = None) -> str:
    """
    Format duration between two dates.
    
    Args:
        start_date: Start date
        end_date: End date (defaults to today)
        
    Returns:
        Formatted duration string
    """
    if start_date is None:
        return ''
    
    if end_date is None:
        end_date = date.today()
    
    duration = end_date - start_date
    days = duration.days
    
    if days == 0:
        return 'Today'
    elif days == 1:
        return '1 day'
    elif days < 30:
        return f"{days} days"
    elif days < 365:
        months = days // 30
        return f"{months} month{'s' if months != 1 else ''}"
    else:
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''}"


def format_status_badge(status: str) -> str:
    """
    Format status with appropriate CSS class for badges.
    
    Args:
        status: Status string
        
    Returns:
        HTML string with badge formatting
    """
    status_classes = {
        'active': 'badge-success',
        'assigned': 'badge-success',
        'unassigned': 'badge-secondary',
        'maintenance': 'badge-warning',
        'retired': 'badge-danger',
        'revoked': 'badge-danger',
        'excellent': 'badge-success',
        'good': 'badge-info',
        'fair': 'badge-warning',
        'poor': 'badge-warning',
        'damaged': 'badge-danger'
    }
    
    css_class = status_classes.get(status.lower(), 'badge-secondary')
    return f'<span class="badge {css_class}">{status.title()}</span>'


def truncate_text(text: Optional[str], max_length: int = 50, suffix: str = '...') -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text string
    """
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
