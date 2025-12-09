"""
Tests for Azure Key Vault Secrets Manager.

Comprehensive test suite covering:
- Unit tests with mocked Azure SDK
- Error handling (missing vault, non-existent secrets, network failures)
- Audit log validation (no sensitive data leakage)
- Fallback to environment variables
- Retry logic with exponential backoff
"""

import json
import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from azure.core.exceptions import ResourceNotFoundError, ServiceRequestError
from azure.keyvault.secrets import KeyVaultSecret

from src.core.secrets_manager import (
    SecretNotFoundError,
    SecretsManager,
    SecretsManagerError,
    VaultConfigurationError,
)


@pytest.fixture
def mock_vault_url():
    """Fixture providing a mock vault URL."""
    return "https://test-vault.vault.azure.net/"


@pytest.fixture
def mock_env_with_vault(mock_vault_url):
    """Fixture that sets up environment with vault URL."""
    with patch.dict(os.environ, {"AZURE_KEY_VAULT_URL": mock_vault_url}, clear=True):
        yield


@pytest.fixture
def mock_env_without_vault():
    """Fixture that clears vault URL from environment."""
    with patch.dict(os.environ, {}, clear=True):
        yield


@pytest.fixture
def mock_azure_credential():
    """Fixture that mocks DefaultAzureCredential."""
    with patch("src.core.secrets_manager.DefaultAzureCredential") as mock_cred:
        mock_instance = Mock()
        mock_cred.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_secret_client():
    """Fixture that mocks SecretClient."""
    with patch("src.core.secrets_manager.SecretClient") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_logger():
    """Fixture that captures logger output."""
    with patch("src.core.secrets_manager.logger") as mock_log:
        yield mock_log


class TestSecretsManagerInitialization:
    """Test suite for SecretsManager initialization."""

    def test_init_with_vault_url_parameter(self, mock_azure_credential, mock_secret_client):
        """Test initialization with vault URL provided as parameter."""
        vault_url = "https://my-vault.vault.azure.net/"
        manager = SecretsManager(vault_url=vault_url)

        assert manager.vault_url == vault_url
        assert manager.client is not None  # Client was successfully created

    def test_init_with_vault_url_from_env(
        self, mock_env_with_vault, mock_vault_url, mock_azure_credential, mock_secret_client
    ):
        """Test initialization with vault URL from environment variable."""
        manager = SecretsManager()

        assert manager.vault_url == mock_vault_url
        assert manager.client is not None  # Client was successfully created

    def test_init_missing_vault_url_with_fallback_enabled(self, mock_env_without_vault, mock_logger):
        """Test initialization without vault URL but with fallback enabled."""
        manager = SecretsManager(enable_fallback=True)

        assert manager.vault_url is None
        assert manager.client is None
        assert manager.enable_fallback is True
        # Should log warning about missing vault URL
        assert mock_logger.warning.called

    def test_init_missing_vault_url_with_fallback_disabled(self, mock_env_without_vault):
        """Test initialization without vault URL and fallback disabled raises error."""
        with pytest.raises(VaultConfigurationError, match="Azure Key Vault URL is required"):
            SecretsManager(enable_fallback=False)

    def test_init_azure_error_with_fallback_enabled(self, mock_env_with_vault, mock_azure_credential, mock_logger):
        """Test initialization handles Azure errors when fallback is enabled."""
        # Mock SecretClient to raise exception on initialization
        with patch("src.core.secrets_manager.SecretClient", side_effect=Exception("Azure connection failed")):
            manager = SecretsManager(enable_fallback=True)

            assert manager.client is None
            assert manager.enable_fallback is True
            # Should log warning about initialization failure
            assert mock_logger.warning.called

    def test_init_azure_error_with_fallback_disabled(self, mock_env_with_vault, mock_azure_credential):
        """Test initialization raises error on Azure failure when fallback disabled."""
        # Mock SecretClient to raise exception on initialization
        with patch("src.core.secrets_manager.SecretClient", side_effect=Exception("Azure connection failed")):
            with pytest.raises(VaultConfigurationError, match="Failed to initialize Key Vault client"):
                SecretsManager(enable_fallback=False)


class TestGetSecret:
    """Test suite for get_secret functionality."""

    def test_get_secret_from_vault_success(self, mock_env_with_vault, mock_azure_credential, mock_secret_client):
        """Test successful secret retrieval from Key Vault."""
        # Mock successful secret retrieval
        mock_secret = Mock(spec=KeyVaultSecret)
        mock_secret.value = "test-secret-value-123"
        mock_secret_client.get_secret.return_value = mock_secret

        manager = SecretsManager()
        result = manager.get_secret("TEST-SECRET")

        assert result == "test-secret-value-123"
        mock_secret_client.get_secret.assert_called_once_with("TEST-SECRET")

    def test_get_secret_invalid_name(self, mock_env_with_vault, mock_azure_credential, mock_secret_client):
        """Test get_secret with invalid secret name."""
        manager = SecretsManager()

        with pytest.raises(ValueError, match="Invalid secret name"):
            manager.get_secret("INVALID$NAME!")

        with pytest.raises(ValueError, match="Invalid secret name"):
            manager.get_secret("name with spaces")

        with pytest.raises(ValueError, match="Invalid secret name"):
            manager.get_secret("")

    def test_get_secret_not_found_in_vault(self, mock_env_with_vault, mock_azure_credential, mock_secret_client):
        """Test get_secret when secret not found in vault and fallback disabled."""
        mock_secret_client.get_secret.side_effect = ResourceNotFoundError("Secret not found")

        manager = SecretsManager(enable_fallback=False)

        with pytest.raises(SecretNotFoundError, match="not found in Key Vault"):
            manager.get_secret("NONEXISTENT-SECRET")

    def test_get_secret_fallback_to_env_success(
        self, mock_env_with_vault, mock_azure_credential, mock_secret_client, mock_logger
    ):
        """Test fallback to environment variable when vault fails."""
        # Mock vault failure
        mock_secret_client.get_secret.side_effect = ServiceRequestError("Network error")

        # Set environment variable
        with patch.dict(os.environ, {"TEST_SECRET": "env-secret-value"}, clear=False):
            manager = SecretsManager(enable_fallback=True)
            result = manager.get_secret("TEST-SECRET")

            assert result == "env-secret-value"
            # Should log warning about using env var
            assert mock_logger.warning.called

    def test_get_secret_not_found_in_vault_or_env(self, mock_env_with_vault, mock_azure_credential, mock_secret_client):
        """Test get_secret fails when not found in vault or environment."""
        mock_secret_client.get_secret.side_effect = ResourceNotFoundError("Secret not found")

        manager = SecretsManager(enable_fallback=True)

        with pytest.raises(SecretNotFoundError, match="not found in environment variable"):
            manager.get_secret("MISSING-SECRET")

    def test_get_secret_without_vault_uses_env(self, mock_env_without_vault):
        """Test get_secret uses environment variable when vault not configured."""
        with patch.dict(os.environ, {"API_KEY": "env-only-secret"}, clear=False):
            manager = SecretsManager(enable_fallback=True)
            result = manager.get_secret("API-KEY")

            assert result == "env-only-secret"


class TestRetryLogic:
    """Test suite for retry logic with exponential backoff."""

    def test_retry_on_service_request_error(self, mock_env_with_vault, mock_azure_credential, mock_secret_client):
        """Test retry logic on transient network errors."""
        mock_secret = Mock(spec=KeyVaultSecret)
        mock_secret.value = "retry-success"

        # Fail twice, then succeed
        mock_secret_client.get_secret.side_effect = [
            ServiceRequestError("Network timeout"),
            ServiceRequestError("Network timeout"),
            mock_secret,
        ]

        with patch("src.core.secrets_manager.time.sleep") as mock_sleep:
            manager = SecretsManager()
            result = manager.get_secret("RETRY-TEST")

            assert result == "retry-success"
            assert mock_secret_client.get_secret.call_count == 3
            # Verify exponential backoff (1s, 2s)
            assert mock_sleep.call_count == 2
            mock_sleep.assert_any_call(1.0)
            mock_sleep.assert_any_call(2.0)

    def test_retry_exhausted_raises_error(self, mock_env_with_vault, mock_azure_credential, mock_secret_client):
        """Test that error is raised after max retries exhausted."""
        mock_secret_client.get_secret.side_effect = ServiceRequestError("Persistent network error")

        with patch("src.core.secrets_manager.time.sleep"):
            manager = SecretsManager(enable_fallback=False)

            with pytest.raises(SecretsManagerError, match="Failed to retrieve secret after 3 attempts"):
                manager.get_secret("RETRY-FAIL")

            assert mock_secret_client.get_secret.call_count == 3

    def test_no_retry_on_resource_not_found(self, mock_env_with_vault, mock_azure_credential, mock_secret_client):
        """Test that ResourceNotFoundError does not trigger retries."""
        mock_secret_client.get_secret.side_effect = ResourceNotFoundError("Secret does not exist")

        manager = SecretsManager(enable_fallback=False)

        with pytest.raises(SecretNotFoundError, match="not found in Key Vault"):
            manager.get_secret("MISSING")

        # Should only try once (no retries for not found)
        assert mock_secret_client.get_secret.call_count == 1


class TestAuditLogging:
    """Test suite for audit logging functionality."""

    def test_audit_log_structure(self, mock_env_with_vault, mock_azure_credential, mock_secret_client, mock_logger):
        """Test that audit logs have correct JSON structure."""
        mock_secret = Mock(spec=KeyVaultSecret)
        mock_secret.value = "test-value"
        mock_secret_client.get_secret.return_value = mock_secret

        manager = SecretsManager()
        manager.get_secret("TEST-SECRET")

        # Verify logger.info was called with JSON strings
        assert mock_logger.info.called

        # Parse one of the log entries
        for call in mock_logger.info.call_args_list:
            log_entry = call[0][0]
            try:
                parsed = json.loads(log_entry)
                # Verify required fields
                assert "timestamp" in parsed
                assert "action" in parsed
                assert "resource" in parsed
                assert "status" in parsed
                assert "details" in parsed
                assert "correlation_id" in parsed
                assert "vault_url" in parsed
            except json.JSONDecodeError:
                # Some log entries might not be JSON (e.g., plain text logs)
                pass

    def test_audit_log_no_sensitive_data(
        self, mock_env_with_vault, mock_azure_credential, mock_secret_client, mock_logger
    ):
        """Test that audit logs do not contain secret values."""
        mock_secret = Mock(spec=KeyVaultSecret)
        mock_secret.value = "SUPER-SECRET-VALUE-12345"
        mock_secret_client.get_secret.return_value = mock_secret

        manager = SecretsManager()
        manager.get_secret("MY-SECRET")

        # Check all logger calls for sensitive data
        for call in mock_logger.info.call_args_list:
            log_message = str(call)
            # Secret value should NOT appear in logs
            assert "SUPER-SECRET-VALUE-12345" not in log_message

    def test_audit_log_correlation_id(
        self, mock_env_with_vault, mock_azure_credential, mock_secret_client, mock_logger
    ):
        """Test that audit logs include correlation ID for tracking."""
        mock_secret = Mock(spec=KeyVaultSecret)
        mock_secret.value = "test"
        mock_secret_client.get_secret.return_value = mock_secret

        manager = SecretsManager()
        manager.get_secret("TEST")

        # Find log entries with correlation_id
        correlation_ids = set()
        for call in mock_logger.info.call_args_list:
            try:
                parsed = json.loads(call[0][0])
                if parsed.get("correlation_id"):
                    correlation_ids.add(parsed["correlation_id"])
            except (json.JSONDecodeError, IndexError, KeyError):
                pass

        # Should have at least one correlation ID
        assert len(correlation_ids) > 0

    def test_audit_log_on_error(self, mock_env_with_vault, mock_azure_credential, mock_secret_client, mock_logger):
        """Test that errors are properly logged in audit trail."""
        mock_secret_client.get_secret.side_effect = ServiceRequestError("Network failure")

        manager = SecretsManager(enable_fallback=False)

        with pytest.raises(SecretsManagerError):
            manager.get_secret("ERROR-TEST")

        # Verify error was logged
        logged_messages = [str(call) for call in mock_logger.info.call_args_list]
        assert any("failed" in msg.lower() for msg in logged_messages)


class TestSecretNameValidation:
    """Test suite for secret name validation."""

    def test_valid_secret_names(self, mock_env_with_vault, mock_azure_credential, mock_secret_client):
        """Test that valid secret names are accepted."""
        mock_secret = Mock(spec=KeyVaultSecret)
        mock_secret.value = "value"
        mock_secret_client.get_secret.return_value = mock_secret

        manager = SecretsManager()

        # Valid names
        valid_names = [
            "AZURE-OPENAI-API-KEY",
            "M365-CLIENT-SECRET",
            "simple",
            "with-dashes",
            "MixedCase123",
            "123numeric",
        ]

        for name in valid_names:
            result = manager.get_secret(name)
            assert result == "value"

    def test_invalid_secret_names(self, mock_env_with_vault, mock_azure_credential, mock_secret_client):
        """Test that invalid secret names are rejected."""
        manager = SecretsManager()

        invalid_names = [
            "has spaces",
            "has$special",
            "has@symbols",
            "has.dots",
            "has_underscores",  # Azure Key Vault supports this but we restrict it
            "",
            "has/slashes",
        ]

        for name in invalid_names:
            with pytest.raises(ValueError, match="Invalid secret name"):
                manager.get_secret(name)


class TestContextManager:
    """Test suite for context manager functionality."""

    def test_context_manager_enter_exit(self, mock_env_with_vault, mock_azure_credential, mock_secret_client):
        """Test that SecretsManager works as context manager."""
        mock_secret = Mock(spec=KeyVaultSecret)
        mock_secret.value = "context-test"
        mock_secret_client.get_secret.return_value = mock_secret

        with SecretsManager() as manager:
            result = manager.get_secret("TEST")
            assert result == "context-test"

        # After exit, resources should be cleaned up
        assert manager.client is None
        assert manager._credential is None

    def test_close_method(self, mock_env_with_vault, mock_azure_credential, mock_secret_client):
        """Test explicit close method."""
        manager = SecretsManager()
        assert manager.client is not None

        manager.close()

        assert manager.client is None
        assert manager._credential is None


class TestBackwardCompatibility:
    """Test suite for backward compatibility with environment variables."""

    def test_env_var_name_conversion(self, mock_env_without_vault):
        """Test that Key Vault names are correctly converted to env var names."""
        test_cases = [
            ("AZURE-OPENAI-API-KEY", "AZURE_OPENAI_API_KEY"),
            ("M365-CLIENT-SECRET", "M365_CLIENT_SECRET"),
            ("SIMPLE-NAME", "SIMPLE_NAME"),
        ]

        for vault_name, env_name in test_cases:
            with patch.dict(os.environ, {env_name: "test-value"}, clear=True):
                manager = SecretsManager(enable_fallback=True)
                result = manager.get_secret(vault_name)
                assert result == "test-value"

    def test_fallback_warning_logged(self, mock_env_without_vault, mock_logger):
        """Test that using env var fallback logs appropriate warning."""
        with patch.dict(os.environ, {"TEST_VAR": "value"}, clear=True):
            manager = SecretsManager(enable_fallback=True)
            manager.get_secret("TEST-VAR")

            # Should log warning about using env var instead of Key Vault
            assert mock_logger.warning.called
            warning_messages = [str(call) for call in mock_logger.warning.call_args_list]
            assert any("environment variable" in msg.lower() for msg in warning_messages)


class TestIntegration:
    """Integration tests (optional - require real Key Vault)."""

    @pytest.mark.skip(reason="Requires real Azure Key Vault - run manually")
    def test_real_vault_integration(self):
        """
        Integration test with real Azure Key Vault.

        Prerequisites:
        - Azure Key Vault must be configured
        - AZURE_KEY_VAULT_URL environment variable must be set
        - Azure credentials must be available (DefaultAzureCredential)
        - Test secret 'TEST-INTEGRATION-SECRET' must exist in vault

        To run: pytest tests/test_secrets_manager.py::TestIntegration::test_real_vault_integration -v
        """
        manager = SecretsManager()
        secret = manager.get_secret("TEST-INTEGRATION-SECRET")
        assert secret is not None
        assert len(secret) > 0
