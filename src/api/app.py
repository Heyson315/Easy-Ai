"""
Flask Application for Easy-AI Authentication API

Main application entry point that initializes the Flask app with
authentication routes and database configuration.

Usage:
    python -m src.api.app

Reference: #app.py - Flask application initialization and configuration
"""

import os
from pathlib import Path

from flask import Flask, jsonify

from src.api.auth_routes import init_auth_routes


def create_app(config: dict = None) -> Flask:
    """
    Create and configure Flask application.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured Flask application instance

    Configuration:
        DATABASE_URL: Database connection string (default: sqlite:///data/users.db)
        SECRET_KEY: Flask secret key for session management
        DEBUG: Debug mode (default: False)

    Reference: #create_app - Flask application factory pattern
    """
    app = Flask(__name__)

    # Default configuration
    default_config = {
        "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///data/users.db"),
        "SECRET_KEY": os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
        "DEBUG": os.getenv("FLASK_DEBUG", "False").lower() == "true",
    }

    # Merge with provided config
    if config:
        default_config.update(config)

    app.config.update(default_config)

    # Ensure data directory exists for SQLite
    if app.config["DATABASE_URL"].startswith("sqlite:///"):
        db_path = app.config["DATABASE_URL"].replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    # Initialize authentication routes with database
    init_auth_routes(app, app.config["DATABASE_URL"])

    # Root endpoint
    @app.route("/")
    def index():
        """API root endpoint with available routes."""
        return jsonify(
            {
                "name": "Easy-AI Authentication API",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/api/auth/health",
                    "register": "POST /api/auth/register",
                    "login": "POST /api/auth/login",
                },
            }
        )

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({"success": False, "message": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({"success": False, "message": "Internal server error"}), 500

    return app


def main():
    """
    Run Flask development server.

    Reference: #main - Development server entry point
    """
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")

    print(f"🚀 Starting Easy-AI Authentication API")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📖 API Docs: http://{host}:{port}/")
    print(f"🔐 Register: POST http://{host}:{port}/api/auth/register")
    print(f"🔑 Login: POST http://{host}:{port}/api/auth/login")
    print(f"❤️  Health: GET http://{host}:{port}/api/auth/health")

    app.run(host=host, port=port, debug=app.config["DEBUG"])


if __name__ == "__main__":
    main()
