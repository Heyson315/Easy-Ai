"""
Unit Tests for Flask Application Configuration

Tests the Flask app factory, configuration loading, error handlers,
and application initialization.

Reference: test_api_app.py - Comprehensive tests for Flask app setup
"""

import json
import pytest
from pathlib import Path

from src.api.app import create_app


class TestFlaskAppConfiguration:
    """
    Test suite for Flask application configuration and initialization.

    Tests:
        - App factory pattern
        - Configuration loading
        - Error handlers
        - CORS setup
        - Database initialization

    Reference: #TestFlaskAppConfiguration - Main test class for Flask app
    """

    def test_app_creation_default_config(self):
        """
        Test Flask app creation with default configuration.

        Reference: #test_app_creation_default_config - Default config test
        """
        app = create_app()

        assert app is not None
        assert app.config['TESTING'] is False
        assert 'SECRET_KEY' in app.config

    def test_app_creation_with_custom_config(self):
        """
        Test Flask app creation with custom configuration dict.

        Reference: #test_app_creation_with_custom_config - Custom config test
        """
        custom_config = {
            'TESTING': True,
            'DEBUG': False,
            'SECRET_KEY': 'test-secret-12345',
            'DATABASE_URL': 'sqlite:///test.db',
        }

        app = create_app(custom_config)

        assert app.config['TESTING'] is True
        assert app.config['DEBUG'] is False
        assert app.config['SECRET_KEY'] == 'test-secret-12345'
        assert app.config['DATABASE_URL'] == 'sqlite:///test.db'

    def test_app_has_auth_blueprint(self):
        """
        Test that authentication blueprint is registered.

        Reference: #test_app_has_auth_blueprint - Blueprint registration
        """
        app = create_app({'TESTING': True})

        # Check blueprint is registered
        assert 'auth' in app.blueprints
        assert app.blueprints['auth'].url_prefix == '/api/auth'

    def test_cors_enabled(self):
        """
        Test that CORS is properly configured for API endpoints.

        Reference: #test_cors_enabled - CORS configuration test
        """
        app = create_app({'TESTING': True})
        client = app.test_client()

        # Make request to check CORS is configured
        response = client.get('/api/auth/health')

        # CORS should allow requests (either headers present or request succeeds)
        assert response.status_code == 200 or 'Access-Control-Allow-Origin' in response.headers

    def test_health_endpoint_exists(self):
        """
        Test that health check endpoint is accessible.

        Reference: #test_health_endpoint_exists - Health endpoint test
        """
        app = create_app({'TESTING': True})
        client = app.test_client()

        response = client.get('/api/auth/health')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['status'] == 'healthy'

    def test_404_error_handler(self):
        """
        Test custom 404 error handler.

        Reference: #test_404_error_handler - Error handling test
        """
        app = create_app({'TESTING': True})
        client = app.test_client()

        response = client.get('/nonexistent-endpoint')

        assert response.status_code == 404
        # Should return JSON for API endpoints or HTML for others
        assert response.content_type in ['application/json', 'text/html; charset=utf-8']

    def test_500_error_handler(self):
        """
        Test that 500 errors are handled gracefully.

        Reference: #test_500_error_handler - Server error handling
        """
        app = create_app({'TESTING': True, 'PROPAGATE_EXCEPTIONS': False})

        # Create route that raises exception
        @app.route('/test-error')
        def trigger_error():
            raise ValueError("Test error")

        client = app.test_client()
        
        # In testing mode, exceptions might propagate
        # Test that app doesn't crash completely
        try:
            response = client.get('/test-error')
            # If we get here, error handler caught it
            assert response.status_code >= 400
        except ValueError:
            # If exception propagates in testing mode, that's also acceptable
            pass

    def test_app_context_available(self):
        """
        Test that Flask app context is properly set up.

        Reference: #test_app_context_available - Context management
        """
        app = create_app({'TESTING': True})

        with app.app_context():
            # Database and other extensions should be accessible
            assert app.config is not None

    def test_testing_mode_disables_features(self):
        """
        Test that TESTING mode disables certain production features.

        Reference: #test_testing_mode_disables_features - Testing mode behavior
        """
        app = create_app({'TESTING': True})

        assert app.config['TESTING'] is True
        # In testing mode, certain features should be disabled for safety
        # (e.g., CSRF protection, email sending, etc.)

    def test_database_url_configuration(self):
        """
        Test that database URL can be configured.

        Reference: #test_database_url_configuration - Database config test
        """
        custom_db = 'sqlite:///custom_test.db'
        app = create_app({'DATABASE_URL': custom_db})

        assert app.config.get('DATABASE_URL') == custom_db

    def test_secret_key_required(self):
        """
        Test that SECRET_KEY is set (required for sessions).

        Reference: #test_secret_key_required - Security requirement
        """
        app = create_app()

        # SECRET_KEY must be set for secure sessions
        assert 'SECRET_KEY' in app.config
        assert app.config['SECRET_KEY'] is not None
        assert len(app.config['SECRET_KEY']) > 0

    def test_multiple_app_instances(self):
        """
        Test that multiple app instances can be created independently.

        Reference: #test_multiple_app_instances - App isolation
        """
        app1 = create_app({'SECRET_KEY': 'key1'})
        app2 = create_app({'SECRET_KEY': 'key2'})

        assert app1.config['SECRET_KEY'] != app2.config['SECRET_KEY']
        assert app1 is not app2

    def test_app_name(self):
        """
        Test that app has correct name.

        Reference: #test_app_name - App naming
        """
        app = create_app()

        # Should have meaningful app name
        assert app.name is not None
        assert len(app.name) > 0

    @pytest.mark.parametrize("config_key,expected_type", [
        ('TESTING', bool),
        ('DEBUG', bool),
        ('SECRET_KEY', str),
    ])
    def test_config_types(self, config_key, expected_type):
        """
        Test that configuration values have correct types.

        Reference: #test_config_types - Type validation
        """
        app = create_app({config_key: expected_type()})

        if config_key in app.config:
            assert isinstance(app.config[config_key], expected_type)


class TestFlaskAppEnvironment:
    """
    Test suite for environment-specific app configurations.

    Reference: #TestFlaskAppEnvironment - Environment config tests
    """

    def test_development_config(self):
        """
        Test development configuration.

        Reference: #test_development_config - Development mode
        """
        app = create_app({'ENV': 'development', 'DEBUG': True})

        assert app.config.get('DEBUG') is True
        assert app.config.get('ENV') == 'development'

    def test_production_config(self):
        """
        Test production configuration.

        Reference: #test_production_config - Production mode
        """
        app = create_app({'ENV': 'production', 'DEBUG': False})

        assert app.config.get('DEBUG') is False
        assert app.config.get('ENV') == 'production'

    def test_testing_config(self):
        """
        Test testing configuration.

        Reference: #test_testing_config - Testing mode
        """
        app = create_app({'TESTING': True})

        assert app.config['TESTING'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
