"""
Azure Key Vault Secrets Manager for SOX Compliance
====================================================

Production-ready Azure Key Vault client with:
- Managed Identity support (DefaultAzureCredential)
- Structured audit logging (JSON format, no sensitive data leakage)
- Retry logic with exponential backoff
- Backward compatibility with environment variables

Author: Rahman Finance and Accounting P.L.LC
Created: December 2025
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Optional
from uuid import uuid4

from azure.core.exceptions import AzureError, ResourceNotFoundError, ServiceRequestError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Configure structured logging
logger = logging.getLogger(__name__)


class SecretsManagerError(Exception):
    """Base exception for secrets manager errors."""

    pass


class SecretNotFoundError(SecretsManagerError):
    """Raised when a secret is not found in Key Vault or environment."""

    pass


class VaultConfigurationError(SecretsManagerError):
    """Raised when Key Vault configuration is invalid."""

    pass


class SecretsManager:
    """
    Production-ready Azure Key Vault client for SOX-compliant secret management.

    Features:
    - Azure Key Vault integration with Managed Identity (DefaultAzureCredential)
    - Structured audit logging (JSON format)
    - Automatic retry with exponential backoff
    - Input validation for secret names
    - Fallback to environment variables for backward compatibility

    Example:
        >>> from src.core.secrets_manager import SecretsManager
        >>> secrets = SecretsManager()
        >>> api_key = secrets.get_secret("AZURE-OPENAI-API-KEY")
    """

    # Secret name validation pattern (alphanumeric and hyphens only)
    SECRET_NAME_PATTERN = re.compile(r"^[A-Za-z0-9-]+$")

    # Retry configuration
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 1.0  # seconds
    RETRY_BACKOFF_MULTIPLIER = 2.0

    def __init__(self, vault_url: Optional[str] = None, enable_fallback: bool = True):
        """
        Initialize Azure Key Vault Secrets Manager.

        Args:
            vault_url: Azure Key Vault URL (e.g., https://your-vault.vault.azure.net/)
                      If not provided, reads from AZURE_KEY_VAULT_URL environment variable
            enable_fallback: Enable fallback to environment variables if Key Vault fails

        Raises:
            VaultConfigurationError: If vault_url is not provided and not in environment

        Environment Variables:
            AZURE_KEY_VAULT_URL: Azure Key Vault URL (required if vault_url not provided)
        """
        self.vault_url = vault_url or os.getenv("AZURE_KEY_VAULT_URL")
        self.enable_fallback = enable_fallback
        self.client: Optional[SecretClient] = None
        self._credential: Optional[DefaultAzureCredential] = None

        # Validate vault URL configuration
        if not self.vault_url:
            error_msg = (
                "Azure Key Vault URL is required. Set AZURE_KEY_VAULT_URL environment variable "
                "or pass vault_url parameter."
            )
            self._log_audit_event("initialization", None, "failed", error_msg)
            if not self.enable_fallback:
                raise VaultConfigurationError(error_msg)
            logger.warning(f"{error_msg} Fallback to environment variables is enabled.")
        else:
            # Initialize Azure Key Vault client
            try:
                self._credential = DefaultAzureCredential()
                self.client = SecretClient(vault_url=self.vault_url, credential=self._credential)
                self._log_audit_event("initialization", None, "success", f"Connected to {self.vault_url}")
                logger.info(f"Azure Key Vault client initialized: {self.vault_url}")
            except Exception as e:
                error_msg = f"Failed to initialize Key Vault client: {str(e)}"
                self._log_audit_event("initialization", None, "failed", error_msg)
                if not self.enable_fallback:
                    raise VaultConfigurationError(error_msg) from e
                logger.warning(f"{error_msg}. Fallback to environment variables is enabled.")

    def get_secret(self, secret_name: str) -> str:
        """
        Retrieve a secret from Azure Key Vault with automatic retry and fallback.

        Args:
            secret_name: Name of the secret (alphanumeric and hyphens only)

        Returns:
            Secret value as string

        Raises:
            SecretNotFoundError: If secret not found in Key Vault or environment
            SecretsManagerError: If retrieval fails after retries

        Example:
            >>> secrets = SecretsManager()
            >>> api_key = secrets.get_secret("AZURE-OPENAI-API-KEY")
        """
        correlation_id = str(uuid4())

        # Validate secret name
        if not self._validate_secret_name(secret_name):
            error_msg = f"Invalid secret name: {secret_name}. Must match pattern: {self.SECRET_NAME_PATTERN.pattern}"
            self._log_audit_event("get_secret", secret_name, "failed", error_msg, correlation_id)
            raise ValueError(error_msg)

        # Try Key Vault first if available
        if self.client:
            try:
                secret_value = self._fetch_from_vault(secret_name, correlation_id)
                return secret_value
            except SecretNotFoundError:
                # Secret not found in vault - try fallback if enabled
                if not self.enable_fallback:
                    raise  # Re-raise if fallback disabled

                error_msg = f"Secret '{secret_name}' not found in Key Vault"
                self._log_audit_event("get_secret", secret_name, "vault_not_found", error_msg, correlation_id)
                logger.warning(f"{error_msg}. Attempting fallback to environment variable.")
            except Exception as e:
                error_msg = f"Key Vault unavailable: {str(e)}"
                self._log_audit_event("get_secret", secret_name, "vault_failed", error_msg, correlation_id)

                if not self.enable_fallback:
                    raise SecretsManagerError(error_msg) from e

                logger.warning(f"{error_msg}. Attempting fallback to environment variable.")

        # Fallback to environment variable
        if self.enable_fallback:
            try:
                secret_value = self._fetch_from_env(secret_name, correlation_id)
                return secret_value
            except SecretNotFoundError:
                # Re-raise if not found in environment either
                raise

        # Should not reach here, but handle edge case
        error_msg = f"Secret '{secret_name}' not found in Key Vault or environment"
        self._log_audit_event("get_secret", secret_name, "failed", error_msg, correlation_id)
        raise SecretNotFoundError(error_msg)

    def _fetch_from_vault(self, secret_name: str, correlation_id: str) -> str:
        """
        Fetch secret from Azure Key Vault with exponential backoff retry.

        Args:
            secret_name: Name of the secret
            correlation_id: Correlation ID for audit logging

        Returns:
            Secret value as string

        Raises:
            SecretNotFoundError: If secret not found in vault
            SecretsManagerError: If retrieval fails after retries
        """
        retry_delay = self.INITIAL_RETRY_DELAY

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                self._log_audit_event(
                    "fetch_from_vault",
                    secret_name,
                    "attempting",
                    f"Attempt {attempt}/{self.MAX_RETRIES}",
                    correlation_id,
                )

                secret = self.client.get_secret(secret_name)

                self._log_audit_event(
                    "fetch_from_vault",
                    secret_name,
                    "success",
                    f"Retrieved from Key Vault (attempt {attempt})",
                    correlation_id,
                )

                return secret.value

            except ResourceNotFoundError as e:
                # Secret doesn't exist - don't retry
                error_msg = f"Secret '{secret_name}' not found in Key Vault"
                self._log_audit_event("fetch_from_vault", secret_name, "not_found", error_msg, correlation_id)
                raise SecretNotFoundError(error_msg) from e

            except ServiceRequestError as e:
                # Network/transient error - retry with backoff
                if attempt < self.MAX_RETRIES:
                    self._log_audit_event(
                        "fetch_from_vault",
                        secret_name,
                        "retrying",
                        f"Network error, retrying in {retry_delay}s: {str(e)}",
                        correlation_id,
                    )
                    time.sleep(retry_delay)
                    retry_delay *= self.RETRY_BACKOFF_MULTIPLIER
                else:
                    error_msg = f"Failed to retrieve secret after {self.MAX_RETRIES} attempts: {str(e)}"
                    self._log_audit_event("fetch_from_vault", secret_name, "failed", error_msg, correlation_id)
                    raise SecretsManagerError(error_msg) from e

            except AzureError as e:
                # Other Azure errors - retry
                if attempt < self.MAX_RETRIES:
                    self._log_audit_event(
                        "fetch_from_vault",
                        secret_name,
                        "retrying",
                        f"Azure error, retrying in {retry_delay}s: {str(e)}",
                        correlation_id,
                    )
                    time.sleep(retry_delay)
                    retry_delay *= self.RETRY_BACKOFF_MULTIPLIER
                else:
                    error_msg = f"Azure error after {self.MAX_RETRIES} attempts: {str(e)}"
                    self._log_audit_event("fetch_from_vault", secret_name, "failed", error_msg, correlation_id)
                    raise SecretsManagerError(error_msg) from e

            except Exception as e:
                # Unexpected error - don't retry
                error_msg = f"Unexpected error retrieving secret: {str(e)}"
                self._log_audit_event("fetch_from_vault", secret_name, "failed", error_msg, correlation_id)
                raise SecretsManagerError(error_msg) from e

        # Should not reach here, but handle edge case
        error_msg = f"Failed to retrieve secret '{secret_name}' after {self.MAX_RETRIES} attempts"
        self._log_audit_event("fetch_from_vault", secret_name, "failed", error_msg, correlation_id)
        raise SecretsManagerError(error_msg)

    def _fetch_from_env(self, secret_name: str, correlation_id: str) -> str:
        """
        Fetch secret from environment variable as fallback.

        Args:
            secret_name: Name of the secret (converted from KEY-NAME to KEY_NAME format)
            correlation_id: Correlation ID for audit logging

        Returns:
            Secret value as string

        Raises:
            SecretNotFoundError: If secret not found in environment
        """
        # Convert Key Vault naming convention to environment variable naming
        # Example: AZURE-OPENAI-API-KEY -> AZURE_OPENAI_API_KEY
        env_name = secret_name.replace("-", "_")

        self._log_audit_event(
            "fetch_from_env", secret_name, "attempting", f"Trying env var: {env_name}", correlation_id
        )

        secret_value = os.getenv(env_name)

        if secret_value:
            self._log_audit_event(
                "fetch_from_env",
                secret_name,
                "success",
                f"Retrieved from environment variable: {env_name}",
                correlation_id,
            )
            logger.warning(
                f"Using environment variable '{env_name}' for secret '{secret_name}'. "
                "Consider migrating to Key Vault for SOX compliance."
            )
            return secret_value
        else:
            error_msg = f"Secret '{secret_name}' not found in environment variable '{env_name}'"
            self._log_audit_event("fetch_from_env", secret_name, "not_found", error_msg, correlation_id)
            raise SecretNotFoundError(error_msg)

    def _validate_secret_name(self, secret_name: str) -> bool:
        """
        Validate secret name format.

        Args:
            secret_name: Name to validate

        Returns:
            True if valid, False otherwise
        """
        if not secret_name:
            return False
        return bool(self.SECRET_NAME_PATTERN.match(secret_name))

    def _log_audit_event(
        self,
        action: str,
        resource: Optional[str],
        status: str,
        details: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Log audit event in structured JSON format.

        Args:
            action: Action being performed (e.g., 'get_secret', 'initialization')
            resource: Resource name (e.g., secret name) - DO NOT include secret value
            status: Status of the action (e.g., 'success', 'failed', 'retrying')
            details: Additional details about the action - DO NOT include secret value
            correlation_id: Optional correlation ID for tracking related events
        """
        audit_event = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "action": action,
            "resource": resource,
            "status": status,
            "details": details,
            "correlation_id": correlation_id,
            "vault_url": self.vault_url if self.vault_url else "not_configured",
        }

        # Log as structured JSON (safe for log aggregation tools)
        logger.info(json.dumps(audit_event))

    def close(self) -> None:
        """
        Close the credential and release resources.

        Note: DefaultAzureCredential resources are automatically managed,
        but this method is provided for explicit cleanup if needed.
        """
        if self._credential:
            try:
                # Note: DefaultAzureCredential doesn't have an explicit close method
                # but we can set it to None to allow garbage collection
                self._credential = None
                self.client = None
                self._log_audit_event("close", None, "success", "Secrets manager closed")
            except Exception as e:
                self._log_audit_event("close", None, "failed", f"Error closing: {str(e)}")
                logger.warning(f"Error closing secrets manager: {str(e)}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
