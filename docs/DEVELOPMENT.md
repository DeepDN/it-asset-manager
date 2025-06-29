# Development Guide - IT Asset Manager

## Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Development Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/DeepDN/it-asset-manager.git
   cd it-asset-manager
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Set Environment Variables**
   ```bash
   export FLASK_ENV=development
   export FLASK_DEBUG=1
   ```

5. **Initialize Database**
   ```bash
   python run.py  # This will create the database and default admin user
   ```

6. **Run the Application**
   ```bash
   python run.py
   ```

## Project Structure

```
it-asset-manager/
├── it_asset_manager/           # Main application package
│   ├── __init__.py
│   ├── core/                   # Core application components
│   │   ├── __init__.py
│   │   ├── app.py             # Application factory
│   │   ├── database.py        # Database initialization
│   │   └── auth.py            # Authentication setup
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   ├── asset.py           # Asset model
│   │   └── access.py          # Access models
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── asset_service.py   # Asset business logic
│   │   ├── auth_service.py    # Authentication logic
│   │   └── access_service.py  # Access management logic
│   ├── routes/                 # Flask route blueprints
│   │   ├── __init__.py
│   │   ├── main.py            # Main routes
│   │   ├── auth.py            # Authentication routes
│   │   ├── assets.py          # Asset routes
│   │   └── access.py          # Access routes
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── validators.py      # Input validation
│   │   ├── formatters.py      # Data formatting
│   │   └── generators.py      # ID generation
│   ├── templates/              # Jinja2 templates
│   └── static/                 # Static files (CSS, JS, images)
├── config/                     # Configuration files
│   └── settings.py            # Application settings
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── docs/                       # Documentation
├── run.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── pytest.ini                 # Pytest configuration
├── setup.cfg                  # Package configuration
└── README.md                  # Project documentation
```

## Development Workflow

### 1. Feature Development

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Write Tests First (TDD)**
   ```bash
   # Create test file in appropriate test directory
   touch tests/unit/test_new_feature.py
   ```

3. **Implement Feature**
   - Add models if needed
   - Implement service layer logic
   - Create routes and templates
   - Add utility functions

4. **Run Tests**
   ```bash
   pytest tests/
   ```

5. **Code Quality Checks**
   ```bash
   black it_asset_manager/  # Format code
   flake8 it_asset_manager/ # Lint code
   mypy it_asset_manager/   # Type checking
   ```

### 2. Testing

#### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_models.py

# Run with coverage
pytest --cov=it_asset_manager

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

#### Writing Tests
```python
# Unit test example
def test_create_asset(app):
    with app.app_context():
        asset_data = {
            'asset_tag': 'LAP0001',
            'asset_type': 'laptop',
            'serial_number': 'SN123456789'
        }
        
        success, message, asset = AssetService.create_asset(asset_data)
        
        assert success is True
        assert asset is not None
        assert asset.asset_tag == 'LAP0001'
```

### 3. Database Migrations

#### Creating Migrations
```python
# Add new field to model
class Asset(db.Model):
    # ... existing fields
    new_field = db.Column(db.String(100))

# Create migration script
# migrations/add_new_field.py
from it_asset_manager.core.database import db

def upgrade():
    # Add column
    db.engine.execute('ALTER TABLE assets ADD COLUMN new_field VARCHAR(100)')

def downgrade():
    # Remove column
    db.engine.execute('ALTER TABLE assets DROP COLUMN new_field')
```

#### Running Migrations
```bash
python migrations/add_new_field.py
```

### 4. Code Style and Standards

#### Python Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Maximum line length: 88 characters
- Use type hints for function parameters and return values

#### Example Code Style
```python
from typing import List, Optional, Tuple

def create_asset(asset_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Asset]]:
    """
    Create a new asset with validation.
    
    Args:
        asset_data: Dictionary containing asset information
        
    Returns:
        Tuple of (success, message, asset_object)
    """
    try:
        # Implementation here
        return True, "Asset created successfully", asset
    except Exception as e:
        return False, f"Error creating asset: {str(e)}", None
```

#### Documentation Standards
- Use docstrings for all classes and functions
- Include type hints
- Document parameters and return values
- Provide usage examples for complex functions

### 5. Adding New Features

#### Adding a New Model
1. Create model file in `it_asset_manager/models/`
2. Define model class with proper relationships
3. Add model to `__init__.py` exports
4. Create migration if needed
5. Write unit tests for model

#### Adding a New Service
1. Create service file in `it_asset_manager/services/`
2. Implement business logic methods
3. Add service to `__init__.py` exports
4. Write comprehensive unit tests
5. Document all public methods

#### Adding New Routes
1. Create or update blueprint in `it_asset_manager/routes/`
2. Implement route handlers
3. Create templates if needed
4. Add route to blueprint registration
5. Write integration tests

### 6. Environment Configuration

#### Development Environment
```python
# config/settings.py
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_it_assets.db'
    WTF_CSRF_ENABLED = False
```

#### Testing Environment
```python
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
```

### 7. Debugging

#### Flask Debug Mode
```bash
export FLASK_DEBUG=1
python run.py
```

#### Using Python Debugger
```python
import pdb; pdb.set_trace()  # Add breakpoint
```

#### Logging
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Debug information")
logger.error("Error occurred", exc_info=True)
```

### 8. Performance Optimization

#### Database Queries
- Use eager loading for relationships
- Add database indexes for frequently queried fields
- Use pagination for large result sets

#### Caching
- Implement caching for expensive operations
- Use Flask-Caching for view caching
- Cache database query results

### 9. Security Considerations

#### Input Validation
```python
from it_asset_manager.utils.validators import validate_email

def update_user_email(user_id: int, email: str) -> Tuple[bool, str]:
    is_valid, error_message = validate_email(email)
    if not is_valid:
        return False, error_message
    
    # Update email
    return True, "Email updated successfully"
```

#### Authentication
- Always hash passwords
- Use secure session management
- Implement proper logout functionality

### 10. Deployment Preparation

#### Production Checklist
- [ ] Set secure SECRET_KEY
- [ ] Configure production database
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure error monitoring
- [ ] Set up backup procedures

#### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key
export DATABASE_URL=postgresql://user:pass@localhost/dbname
```

## Common Development Tasks

### Adding Sample Data
```bash
python add_sample_data.py
```

### Backing Up Database
```bash
./backup.sh
```

### Updating Dependencies
```bash
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
```

### Code Quality Checks
```bash
# Format code
black it_asset_manager/

# Check linting
flake8 it_asset_manager/

# Type checking
mypy it_asset_manager/

# Run all quality checks
make quality  # If Makefile is available
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database file permissions
   - Verify database URI configuration
   - Ensure database directory exists

2. **Import Errors**
   - Check PYTHONPATH
   - Verify package installation
   - Check for circular imports

3. **Template Not Found**
   - Verify template path
   - Check Flask template folder configuration
   - Ensure template file exists

### Getting Help

1. Check existing documentation
2. Review test cases for examples
3. Check GitHub issues
4. Contact the development team

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

For more detailed information, see the [Architecture Documentation](ARCHITECTURE.md) and [API Documentation](API.md).
