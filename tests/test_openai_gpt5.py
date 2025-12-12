import os
from unittest.mock import MagicMock, patch

import pytest

from src.integrations.openai_gpt5 import GPT5Client, analyze_with_reasoning, quick_chat


@pytest.fixture
def mock_env():
    with patch.dict(
        os.environ, {"AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com", "AZURE_OPENAI_API_KEY": "test-key"}
    ):
        yield


@pytest.fixture
def mock_openai_client():
    with patch("src.integrations.openai_gpt5.OpenAI") as mock:
        yield mock


@pytest.fixture
def mock_azure_credential():
    with patch("src.integrations.openai_gpt5.DefaultAzureCredential") as mock_cred, patch(
        "src.integrations.openai_gpt5.get_bearer_token_provider"
    ) as mock_token:
        yield mock_cred, mock_token


class TestGPT5Client:

    def test_init_api_key(self, mock_env, mock_openai_client):
        client = GPT5Client()
        assert client.azure_endpoint == "https://test.openai.azure.com"
        assert client.api_key == "test-key"
        mock_openai_client.assert_called_once()

    def test_init_entra_id(self, mock_env, mock_openai_client, mock_azure_credential):
        client = GPT5Client(use_entra_id=True)
        assert client.use_entra_id is True
        mock_azure_credential[1].assert_called_once()  # get_bearer_token_provider called
        mock_openai_client.assert_called_once()

    def test_init_missing_endpoint(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Azure OpenAI endpoint is required"):
                GPT5Client()

    def test_init_missing_api_key(self):
        with patch.dict(os.environ, {"AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com"}, clear=True):
            with pytest.raises(ValueError, match="Azure OpenAI API key is required"):
                GPT5Client()

    def test_chat_completion(self, mock_env, mock_openai_client):
        client = GPT5Client()
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"total_tokens": 10},
        }
        client.client.chat.completions.create.return_value = mock_response

        result = client.chat_completion("Test prompt", system_message="System msg")

        assert result["choices"][0]["message"]["content"] == "Test response"
        client.client.chat.completions.create.assert_called_once()
        call_kwargs = client.client.chat.completions.create.call_args[1]
        assert call_kwargs["messages"][0]["role"] == "developer"
        assert call_kwargs["messages"][1]["role"] == "user"

    def test_reasoning_response(self, mock_env, mock_openai_client):
        client = GPT5Client()
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "output_text": "Reasoned response",
            "reasoning_summary": "Detailed reasoning",
            "usage": {"total_tokens": 20},
        }
        client.client.responses.create.return_value = mock_response

        result = client.reasoning_response("Reasoning prompt", reasoning_effort="high")

        assert result["output_text"] == "Reasoned response"
        client.client.responses.create.assert_called_once()
        call_kwargs = client.client.responses.create.call_args[1]
        assert call_kwargs["reasoning"]["effort"] == "high"

    def test_analyze_financial_document(self, mock_env, mock_openai_client):
        client = GPT5Client()
        # Mock reasoning_response since analyze_financial_document calls it
        with patch.object(client, "reasoning_response") as mock_reasoning:
            mock_reasoning.return_value = {"output_text": "Analysis result"}

            result = client.analyze_financial_document("Doc text", analysis_type="audit")

            assert result["output_text"] == "Analysis result"
            mock_reasoning.assert_called_once()
            call_kwargs = mock_reasoning.call_args[1]
            assert "senior auditor" in call_kwargs["prompt"]

    def test_generate_client_report_summary(self, mock_env, mock_openai_client):
        client = GPT5Client()
        with patch.object(client, "chat_completion") as mock_chat:
            mock_chat.return_value = {"choices": [{"message": {"content": "Summary"}}]}

            result = client.generate_client_report_summary("Client data")

            assert result["choices"][0]["message"]["content"] == "Summary"
            mock_chat.assert_called_once()

    def test_draft_engagement_letter(self, mock_env, mock_openai_client):
        client = GPT5Client()
        with patch.object(client, "chat_completion") as mock_chat:
            mock_chat.return_value = {"choices": [{"message": {"content": "Letter"}}]}

            result = client.draft_engagement_letter("Client A", "Audit", "Scope", "Fees")

            assert result["choices"][0]["message"]["content"] == "Letter"
            mock_chat.assert_called_once()
            call_kwargs = mock_chat.call_args[1]
            assert "Fee Structure: Fees" in call_kwargs["prompt"]


def test_quick_chat(mock_env, mock_openai_client):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {"choices": [{"message": {"content": "Quick response"}}]}
    # We need to mock the client instance created inside quick_chat
    with patch("src.integrations.openai_gpt5.GPT5Client") as MockClient:
        instance = MockClient.return_value
        instance.chat_completion.return_value = {"choices": [{"message": {"content": "Quick response"}}]}

        result = quick_chat("Prompt")
        assert result == "Quick response"


def test_analyze_with_reasoning(mock_env, mock_openai_client):
    with patch("src.integrations.openai_gpt5.GPT5Client") as MockClient:
        instance = MockClient.return_value
        instance.reasoning_response.return_value = {
            "output_text": "Analysis",
            "reasoning_summary": "Reasoning",
            "usage": {},
        }

        result = analyze_with_reasoning("Prompt")
        assert result["output"] == "Analysis"
        assert result["reasoning"] == "Reasoning"
