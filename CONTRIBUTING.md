# Contributing to IT Asset Manager

First off, thank you for considering contributing to IT Asset Manager! It's people like you that make IT Asset Manager such a great tool for IT professionals worldwide.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by the [IT Asset Manager Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [deepak.nemade@example.com](mailto:deepak.nemade@example.com).

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.7+**
- **Docker & Docker Compose** (recommended)
- **Git**
- **Node.js** (for frontend dependencies, if applicable)

### Quick Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/it-asset-manager.git
   cd it-asset-manager
   ```
3. **Add the original repository** as upstream:
   ```bash
   git remote add upstream https://github.com/DeepDN/it-asset-manager.git
   ```

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/DeepDN/it-asset-manager/issues) to avoid duplicates.

**When submitting a bug report, please include:**
- **Clear title** and description
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, Docker version)
- **Screenshots** if applicable
- **Error logs** or stack traces

### 💡 Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:
- **Clear title** and detailed description
- **Use case** and motivation
- **Proposed solution** or implementation ideas
- **Alternative solutions** considered

### 🔧 Code Contributions

#### Types of Contributions Welcome:

1. **Bug Fixes**
2. **New Features**
3. **Performance Improvements**
4. **Documentation Updates**
5. **Test Coverage Improvements**
6. **UI/UX Enhancements**
7. **Security Improvements**

## Development Setup

### Option 1: Docker Development (Recommended)

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/it-asset-manager.git
cd it-asset-manager

# Start development environment
./docker-start.sh dev

# Access application at http://localhost:5000
# Username: admin | Password: admin123
```

### Option 2: Local Python Development

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Initialize database
python app.py

# Access application at http://localhost:5000
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test categories
make test-unit
make test-integration
make test-security

# Run with coverage
make test-coverage
```

## Pull Request Process

### Before Submitting

1. **Create a feature branch** from `dev`:
   ```bash
   git checkout dev
   git pull upstream dev
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our style guidelines

3. **Test thoroughly**:
   ```bash
   make test
   make lint
   ```

4. **Update documentation** if needed

5. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add asset bulk import functionality
   
   - Add CSV upload endpoint
   - Implement data validation
   - Add progress tracking
   - Update UI components"
   ```

### Commit Message Format

We follow the [Conventional Commits](https://conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(assets): add bulk CSV import functionality
fix(auth): resolve login session timeout issue
docs(readme): update installation instructions
test(api): add unit tests for asset endpoints
```

### Pull Request Guidelines

1. **Target the correct branch**:
   - `dev` for new features and non-critical fixes
   - `main` for critical hotfixes only

2. **Fill out the PR template** completely

3. **Ensure all checks pass**:
   - ✅ All tests pass
   - ✅ Code coverage maintained
   - ✅ Linting passes
   - ✅ Security scans pass

4. **Request review** from maintainers

5. **Address feedback** promptly

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated for changes
- [ ] Documentation updated if needed
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages follow convention
- [ ] PR description is clear and complete

## Style Guidelines

### Python Code Style

We follow **PEP 8** with some project-specific conventions:

```python
# Good
def create_asset(asset_type, serial_number, assigned_to=None):
    """Create a new IT asset with proper validation.
    
    Args:
        asset_type (str): Type of asset (laptop, desktop, etc.)
        serial_number (str): Unique serial number
        assigned_to (str, optional): User assignment
        
    Returns:
        Asset: Created asset instance
        
    Raises:
        ValidationError: If asset data is invalid
    """
    if not asset_type or not serial_number:
        raise ValidationError("Asset type and serial number required")
    
    return Asset(
        type=asset_type,
        serial_number=serial_number,
        assigned_to=assigned_to,
        created_at=datetime.utcnow()
    )
```

### Frontend Guidelines

- **Bootstrap 5** for styling
- **Vanilla JavaScript** preferred over heavy frameworks
- **Responsive design** mandatory
- **Accessibility** compliance (WCAG 2.1 AA)

### Database Guidelines

- **SQLAlchemy ORM** for database operations
- **Migrations** for schema changes
- **Proper indexing** for performance
- **Data validation** at model level

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test data
└── conftest.py     # Pytest configuration
```

### Writing Tests

```python
def test_create_asset_success():
    """Test successful asset creation."""
    asset = create_asset("laptop", "LAP001", "john.doe")
    
    assert asset.type == "laptop"
    assert asset.serial_number == "LAP001"
    assert asset.assigned_to == "john.doe"
    assert asset.created_at is not None

def test_create_asset_validation_error():
    """Test asset creation with invalid data."""
    with pytest.raises(ValidationError):
        create_asset("", "LAP001")
```

## Documentation Guidelines

- **Clear and concise** language
- **Code examples** for complex features
- **Screenshots** for UI changes
- **API documentation** for endpoints
- **Deployment guides** kept updated

## Security Guidelines

### Security Best Practices

1. **Input Validation**: Validate all user inputs
2. **SQL Injection Prevention**: Use parameterized queries
3. **XSS Prevention**: Escape output properly
4. **Authentication**: Secure session management
5. **Authorization**: Proper access controls
6. **Secrets Management**: No hardcoded secrets

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead, email security concerns to: [security@example.com](mailto:security@example.com)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Branch Strategy

- **`main`**: Production-ready code
- **`dev`**: Development integration branch
- **`feature/*`**: Feature development branches
- **`hotfix/*`**: Critical production fixes

## Community

### Getting Help

- **GitHub Discussions**: For questions and community support
- **GitHub Issues**: For bug reports and feature requests
- **LinkedIn**: [Connect with Deepak Nemade](https://www.linkedin.com/in/deepak-nemade/)

### Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page

## Development Roadmap

### Current Priorities

1. **Enhanced Reporting**: Advanced analytics and dashboards
2. **API Development**: RESTful API for integrations
3. **Mobile Support**: Responsive mobile interface
4. **Audit Logging**: Comprehensive audit trails
5. **Multi-tenancy**: Support for multiple organizations

### Future Enhancements

- **LDAP/AD Integration**: Enterprise authentication
- **Barcode Scanning**: Mobile asset scanning
- **Automated Discovery**: Network asset discovery
- **Compliance Reporting**: SOX, HIPAA, etc.

## Questions?

Don't hesitate to ask questions! You can:

1. **Create a GitHub Discussion** for general questions
2. **Open an issue** for specific problems
3. **Contact maintainers** directly for sensitive matters

## Thank You!

Your contributions make IT Asset Manager better for IT professionals worldwide. Every contribution, no matter how small, is valued and appreciated.

---

**Happy Contributing! 🚀**

*Created with ❤️ by the IT Asset Manager community*
