"""
Authentication Routes - User Registration and Login API

Provides RESTful API endpoints for user authentication including
secure user registration with input validation and password hashing.

Reference: #auth_routes.py - REST API endpoints for authentication
Integration with: #models.py (User model), #validators.py (input validation)
"""

from flask import Blueprint, Flask, jsonify, request
from sqlalchemy.exc import IntegrityError

from src.api.models import DatabaseManager, User
from src.api.validators import validate_registration_data

# Create Blueprint for authentication routes
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Initialize database manager (will be configured by app)
db_manager = None


def init_auth_routes(app: Flask, database_url: str = "sqlite:///data/users.db"):
    """
    Initialize authentication routes with database connection.

    Args:
        app: Flask application instance
        database_url: Database connection URL

    Reference: #init_auth_routes - Blueprint initialization with database
    """
    global db_manager
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()
    app.register_blueprint(auth_bp)


@auth_bp.route("/register", methods=["POST"])
def register_user():
    """
    Register a new user with secure password hashing.

    Endpoint: POST /api/auth/register

    Request Body (JSON):
        {
            "username": "john_doe",           # Required, 3-50 chars
            "email": "john@example.com",      # Required, valid email
            "password": "SecurePass123!",     # Required, strong password
            "full_name": "John Doe"           # Optional
        }

    Response (Success - 201):
        {
            "success": true,
            "message": "User registered successfully",
            "user": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": true,
                "created_at": "2025-12-10T05:00:00"
            }
        }

    Response (Error - 400):
        {
            "success": false,
            "message": "Validation failed",
            "errors": ["Password must be at least 8 characters", ...]
        }

    Response (Error - 409):
        {
            "success": false,
            "message": "Username or email already exists"
        }

    Security Features:
        - Input validation (email format, password strength)
        - Bcrypt password hashing with salt (cost factor 12)
        - Duplicate user detection
        - Never returns password in response
        - SQL injection protection via SQLAlchemy ORM

    Integration:
        - Uses #User model from models.py for database operations
        - Uses #validate_registration_data from validators.py for input validation
        - Calls #set_password method which uses bcrypt hashing

    Reference: #registerUser endpoint - Secure user registration with validation
    """
    try:
        # Parse JSON request body
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "Request body is required"}), 400

        # Extract fields
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        full_name = data.get("full_name", "").strip() if data.get("full_name") else None

        # Validate input data (Integration with #validators.py)
        validation_result = validate_registration_data(username, email, password, full_name)

        if not validation_result["valid"]:
            return (
                jsonify({"success": False, "message": "Validation failed", "errors": validation_result["errors"]}),
                400,
            )

        # Create database session
        session = db_manager.get_session()

        try:
            # Check if username or email already exists
            existing_user = (
                session.query(User).filter((User.username == username) | (User.email == email)).first()
            )

            if existing_user:
                if existing_user.username == username:
                    return jsonify({"success": False, "message": "Username already exists"}), 409
                else:
                    return jsonify({"success": False, "message": "Email already exists"}), 409

            # Create new user (Integration with #User model)
            new_user = User(username=username, email=email, full_name=full_name)

            # Hash password using bcrypt (Integration with #set_password method)
            new_user.set_password(password)

            # Save to database
            session.add(new_user)
            session.commit()

            # Refresh to get auto-generated fields
            session.refresh(new_user)

            # Return success response (Integration with #to_dict method - excludes password)
            return (
                jsonify(
                    {"success": True, "message": "User registered successfully", "user": new_user.to_dict()}
                ),
                201,
            )

        except IntegrityError as e:
            session.rollback()
            return jsonify({"success": False, "message": "Username or email already exists"}), 409

        except Exception as e:
            session.rollback()
            return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

        finally:
            session.close()

    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login_user():
    """
    Authenticate user with username/email and password.

    Endpoint: POST /api/auth/login

    Request Body (JSON):
        {
            "username": "john_doe",      # Required (username or email)
            "password": "SecurePass123!"  # Required
        }

    Response (Success - 200):
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

    Response (Error - 401):
        {
            "success": false,
            "message": "Invalid credentials"
        }

    Security Features:
        - Bcrypt password verification
        - Constant-time password comparison
        - No information leakage about username existence
        - Account active status check

    Integration:
        - Uses #check_password method from User model (bcrypt verification)
        - Uses #to_dict method to safely serialize user data

    Reference: #loginUser endpoint - Secure login with bcrypt verification
    """
    try:
        # Parse JSON request body
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "Request body is required"}), 400

        # Extract credentials
        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return jsonify({"success": False, "message": "Username and password are required"}), 400

        # Create database session
        session = db_manager.get_session()

        try:
            # Find user by username or email
            user = session.query(User).filter((User.username == username) | (User.email == username)).first()

            # Check if user exists and password is correct (Integration with #check_password)
            if not user or not user.check_password(password):
                # Generic error message to prevent username enumeration
                return jsonify({"success": False, "message": "Invalid credentials"}), 401

            # Check if account is active
            if not user.is_active:
                return jsonify({"success": False, "message": "Account is disabled"}), 401

            # Return success response (Integration with #to_dict)
            return (
                jsonify({"success": True, "message": "Login successful", "user": user.to_dict()}),
                200,
            )

        finally:
            session.close()

    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@auth_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for API monitoring.

    Endpoint: GET /api/auth/health

    Response (Success - 200):
        {
            "status": "healthy",
            "service": "Authentication API"
        }

    Reference: #health endpoint - API health monitoring
    """
    return jsonify({"status": "healthy", "service": "Authentication API"}), 200
