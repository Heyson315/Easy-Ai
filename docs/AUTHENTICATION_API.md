# Authentication API Documentation

## Overview

This document describes the authentication system implementation for the Easy-AI Toolkit. The system provides secure user registration and login capabilities using industry best practices.

## Architecture Summary

### File References

| Component | File | Description |
|-----------|------|-------------|
| **User Model** | `#models.py` | User database model with bcrypt password hashing |
| **Validation** | `#validators.py` | Input validation for email, username, password |
| **API Routes** | `#auth_routes.py` | REST API endpoints for registration and login |
| **Flask App** | `#app.py` | Flask application initialization and configuration |
| **Tests** | `test_auth_api.py`, `test_validators.py` | Comprehensive test suite |

## How Authentication Works

### 1. User Registration Flow

**Endpoint:** `POST /api/auth/register`

```
Client Request
     ↓
Input Validation (#validators.py)
     ↓
Duplicate Check (database query)
     ↓
Password Hashing (#User.set_password - bcrypt)
     ↓
Database Insert (#models.py)
     ↓
Return User Data (safe, no password)
```

**Code References:**
- **Registration endpoint**: `#registerUser` in `auth_routes.py` line 45-144
- **Password hashing**: `#User.set_password` in `models.py` line 53-67
- **Input validation**: `#validate_registration_data` in `validators.py` line 114-145
- **User serialization**: `#User.to_dict` in `models.py` line 85-107

### 2. User Login Flow

**Endpoint:** `POST /api/auth/login`

```
Client Request (username/email + password)
     ↓
Find User in Database
     ↓
Password Verification (#User.check_password - bcrypt)
     ↓
Account Status Check (is_active)
     ↓
Return User Data (safe, no password)
```

**Code References:**
- **Login endpoint**: `#loginUser` in `auth_routes.py` line 147-232
- **Password verification**: `#User.check_password` in `models.py` line 69-83

## API Endpoints

### 1. Register User

**POST** `/api/auth/register`

Creates a new user account with secure password hashing.

**Request Body:**
```json
{
    "username": "john_doe",           // Required, 3-50 chars
    "email": "john@example.com",      // Required, valid email
    "password": "SecurePass123!",     // Required, strong password
    "full_name": "John Doe"           // Optional
}
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "is_active": true,
        "created_at": "2025-12-10T05:00:00",
        "updated_at": "2025-12-10T05:00:00"
    }
}
```

**Error Responses:**

**400 - Validation Error:**
```json
{
    "success": false,
    "message": "Validation failed",
    "errors": [
        "Password must be at least 8 characters",
        "Password must contain at least one uppercase letter"
    ]
}
```

**409 - Conflict (duplicate):**
```json
{
    "success": false,
    "message": "Username already exists"
}
```

**Implementation References:**
- Endpoint implementation: `#registerUser` function
- Uses `#validate_registration_data` from validators.py
- Uses `#User.set_password` for bcrypt hashing
- Uses `#User.to_dict` for safe response serialization

### 2. Login User

**POST** `/api/auth/login`

Authenticates user with username/email and password.

**Request Body:**
```json
{
    "username": "john_doe",           // Or email address
    "password": "SecurePass123!"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "is_active": true
    }
}
```

**Error Response (401):**
```json
{
    "success": false,
    "message": "Invalid credentials"
}
```

**Implementation References:**
- Endpoint implementation: `#loginUser` function
- Uses `#User.check_password` for bcrypt verification
- Generic error message prevents username enumeration

### 3. Health Check

**GET** `/api/auth/health`

Check API health status.

**Response (200):**
```json
{
    "status": "healthy",
    "service": "Authentication API"
}
```

**Implementation References:**
- Endpoint implementation: `#health_check` function

## Security Features

### Password Security

**Bcrypt Hashing:**
- Cost factor: 12 (balanced security/performance)
- Automatic salt generation
- Never stores plain text passwords
- Implementation: `#User.set_password` in models.py

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character
- Validation: `#validate_password` in validators.py

### Input Validation

**Email Validation:**
- RFC 5322 compliant format
- Maximum 120 characters
- Implementation: `#validate_email` in validators.py

**Username Validation:**
- 3-50 characters
- Alphanumeric, underscore, hyphen only
- Must start with letter or number
- Implementation: `#validate_username` in validators.py

### Security Best Practices

1. **Password Hash Never Exposed**: The `#User.to_dict` method explicitly excludes password_hash
2. **SQL Injection Protection**: Uses SQLAlchemy ORM with parameterized queries
3. **Username Enumeration Prevention**: Generic "Invalid credentials" message for login failures
4. **Account Status Check**: Verifies `is_active` flag before allowing login
5. **Input Sanitization**: All inputs trimmed and validated before processing

## Database Schema

### User Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX ix_users_username ON users(username);
CREATE INDEX ix_users_email ON users(email);
```

**Implementation References:**
- Model definition: `#User` class in models.py
- Database manager: `#DatabaseManager` class in models.py

## Running the API

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Start the Server

```bash
# Development server
python -m src.api.app

# With custom configuration
export DATABASE_URL="sqlite:///data/users.db"
export SECRET_KEY="your-secret-key"
export FLASK_DEBUG="false"
python -m src.api.app
```

The API will start on `http://127.0.0.1:5000`

### Configuration

Environment variables:
- `DATABASE_URL`: Database connection string (default: sqlite:///data/users.db)
- `SECRET_KEY`: Flask secret key (change in production!)
- `FLASK_DEBUG`: Debug mode (default: false)
- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 5000)

## Testing

### Run All Tests

```bash
# Run authentication API tests
python -m pytest tests/test_auth_api.py -v

# Run validator tests
python -m pytest tests/test_validators.py -v

# Run all tests
python -m pytest tests/ -v
```

### Test Coverage

The test suite includes:

**Authentication Tests** (`test_auth_api.py`):
- ✅ Successful user registration
- ✅ Duplicate username detection
- ✅ Duplicate email detection
- ✅ Email format validation
- ✅ Password strength validation
- ✅ Username length validation
- ✅ Successful login
- ✅ Login with email
- ✅ Invalid password handling
- ✅ Non-existent user handling
- ✅ Bcrypt password hashing verification

**Validator Tests** (`test_validators.py`):
- ✅ Email format validation (valid/invalid)
- ✅ Email length validation
- ✅ Username format validation
- ✅ Username length validation
- ✅ Password strength validation
- ✅ Complete registration data validation

## Example Usage

### Python Example

```python
import requests

# Register new user
response = requests.post(
    "http://127.0.0.1:5000/api/auth/register",
    json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }
)

if response.status_code == 201:
    user = response.json()["user"]
    print(f"✅ User registered: {user['username']}")

# Login
response = requests.post(
    "http://127.0.0.1:5000/api/auth/login",
    json={
        "username": "testuser",
        "password": "SecurePass123!"
    }
)

if response.status_code == 200:
    user = response.json()["user"]
    print(f"✅ Login successful: {user['username']}")
```

### cURL Examples

```bash
# Register user
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'

# Health check
curl http://127.0.0.1:5000/api/auth/health
```

## Integration with Existing Code

The authentication system is **completely standalone** and does not interfere with existing M365 authentication:

| System | Purpose | Location |
|--------|---------|----------|
| **New User Auth** | Web API user authentication | `src/api/` |
| **M365 Auth** | Microsoft 365 service authentication | `scripts/powershell/modules/M365CIS.psm1` |

**M365 Authentication** (`#Connect-M365CIS` in M365CIS.psm1):
- Connects to Exchange Online, Microsoft Graph, SharePoint Online
- Uses OAuth/service principals
- For M365 security auditing

**User Authentication** (this new system):
- Web API user authentication
- Uses bcrypt password hashing
- For application access control

These systems are independent and serve different purposes.

## Code References Summary

| Function/Class | File | Line | Description |
|----------------|------|------|-------------|
| `#User` | models.py | 18-108 | User model with bcrypt hashing |
| `#User.set_password` | models.py | 53-67 | Bcrypt password hashing |
| `#User.check_password` | models.py | 69-83 | Password verification |
| `#User.to_dict` | models.py | 85-107 | Safe user serialization |
| `#DatabaseManager` | models.py | 111-168 | Database operations |
| `#validate_email` | validators.py | 11-29 | Email validation |
| `#validate_username` | validators.py | 32-59 | Username validation |
| `#validate_password` | validators.py | 62-99 | Password strength validation |
| `#validate_registration_data` | validators.py | 102-145 | Complete validation |
| `#registerUser` | auth_routes.py | 45-144 | Registration endpoint |
| `#loginUser` | auth_routes.py | 147-232 | Login endpoint |
| `#create_app` | app.py | 12-76 | Flask app factory |

## Security Considerations

### Production Deployment

⚠️ **Important:** Before deploying to production:

1. **Change SECRET_KEY**: Never use the default secret key
2. **Use HTTPS**: All authentication must be over HTTPS
3. **Database Security**: Use PostgreSQL or MySQL with encrypted connections
4. **Rate Limiting**: Implement rate limiting to prevent brute force attacks
5. **Session Management**: Add JWT tokens or session management for authenticated requests
6. **Environment Variables**: Store all secrets in environment variables, never in code

### Recommended Enhancements

For production use, consider adding:
- JWT token authentication
- Password reset functionality
- Email verification
- Two-factor authentication (2FA)
- Account lockout after failed login attempts
- Audit logging
- CORS configuration
- Rate limiting middleware

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure you're in the project root
cd /path/to/Easy-Ai

# Install dependencies
pip install -r requirements.txt
```

**Database Errors:**
```bash
# Ensure data directory exists
mkdir -p data

# Check database file permissions
ls -la data/users.db
```

**Test Failures:**
```bash
# Run with verbose output
python -m pytest tests/test_auth_api.py -v -s

# Run single test
python -m pytest tests/test_auth_api.py::TestAuthenticationAPI::test_register_user_success -v
```

## Support

For questions or issues:
1. Check this documentation first
2. Review code references (`#function_name` markers)
3. Run tests to verify functionality
4. Check error logs in Flask output
