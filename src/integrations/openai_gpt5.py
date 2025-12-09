"""
OpenAI GPT-5 Integration for Rahman Finance and Accounting P.L.LC
==================================================================

This module provides integration with OpenAI GPT-5 models via Azure OpenAI Service.
Supports both Chat Completions API and the new Responses API with reasoning capabilities.

Features:
- GPT-5 and GPT-5 Mini models
- Reasoning API with configurable effort levels (low, medium, high)
- Azure Entra ID authentication (keyless) or API key authentication
- Specialized prompts for CPA firm tasks (tax, audit, financial analysis)

Microsoft Documentation:
- https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/reasoning
- https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages

Author: Rahman Finance and Accounting P.L.LC
Created: November 2025
"""

import os
from typing import Dict, List, Literal, Optional

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

# Import cost tracking
try:
    from src.core.cost_tracker import track_gpt5_request

    COST_TRACKING_ENABLED = True
except ImportError:
    COST_TRACKING_ENABLED = False

# Import secrets manager for SOX-compliant secret retrieval
try:
    from src.core.secrets_manager import SecretsManager

    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False


class GPT5Client:
    """
    Client for OpenAI GPT-5 models with Azure OpenAI Service integration.

    Supports:
    - Chat Completions API (gpt-5, gpt-5-mini)
    - Responses API with reasoning capabilities
    - Both API key and Entra ID authentication
    """

    def __init__(
        self,
        azure_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        use_entra_id: bool = False,
        model: str = "gpt-5",
    ):
        """
        Initialize GPT-5 client.

        Args:
            azure_endpoint: Azure OpenAI endpoint (e.g., https://your-resource.openai.azure.com)
            api_key: Azure OpenAI API key (if not using Entra ID)
            use_entra_id: Use Azure Entra ID authentication (keyless)
            model: Model deployment name (default: gpt-5)

        Environment Variables:
            AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint URL
            AZURE_OPENAI_API_KEY: Azure OpenAI API key (fallback if Key Vault unavailable)
            AZURE_KEY_VAULT_URL: Azure Key Vault URL for SOX-compliant secret storage
        """
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")

        # Get API key from Key Vault (SOX-compliant) or fall back to environment variable
        if api_key:
            self.api_key = api_key
        elif SECRETS_MANAGER_AVAILABLE:
            try:
                secrets = SecretsManager(enable_fallback=True)
                self.api_key = secrets.get_secret("AZURE-OPENAI-API-KEY")
            except Exception:  # noqa: S110
                # Fall back to environment variable if Key Vault fails
                self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        else:
            self.api_key = os.getenv("AZURE_OPENAI_API_KEY")

        self.model = model
        self.use_entra_id = use_entra_id

        if not self.azure_endpoint:
            raise ValueError(
                "Azure OpenAI endpoint is required. Set AZURE_OPENAI_ENDPOINT environment variable "
                "or pass azure_endpoint parameter."
            )

        # Initialize OpenAI client
        if self.use_entra_id:
            # Use Azure Entra ID authentication (keyless)
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            )
            self.client = OpenAI(
                base_url=f"{self.azure_endpoint}/openai/v1/",
                api_key=token_provider,
            )
        else:
            # Use API key authentication
            if not self.api_key:
                raise ValueError(
                    "Azure OpenAI API key is required when not using Entra ID. "
                    "Set AZURE_OPENAI_API_KEY environment variable or pass api_key parameter."
                )
            self.client = OpenAI(base_url=f"{self.azure_endpoint}/openai/v1/", api_key=self.api_key)

    def chat_completion(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 5000,
        temperature: Optional[float] = None,
    ) -> Dict:
        """
        Send a chat completion request to GPT-5.

        Args:
            prompt: User prompt/question
            system_message: Optional system message for context
            max_tokens: Maximum completion tokens
            temperature: Optional temperature (0.0-2.0, default: model default)

        Returns:
            Dict with response data including choices, usage, model info
        """
        messages = []
        if system_message:
            messages.append({"role": "developer", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_completion_tokens": max_tokens,
        }
        if temperature is not None:
            kwargs["temperature"] = temperature

        response = self.client.chat.completions.create(**kwargs)
        result = response.model_dump()

        # Track costs if enabled
        if COST_TRACKING_ENABLED and "usage" in result:
            track_gpt5_request(
                model=self.model,
                usage=result["usage"],
                request_type="chat",
                metadata={"prompt_preview": prompt[:100]},
            )

        return result

    def reasoning_response(
        self,
        prompt: str,
        reasoning_effort: Literal["low", "medium", "high"] = "medium",
        reasoning_summary: Literal["auto", "detailed"] = "auto",
        text_verbosity: Literal["low", "medium", "high"] = "medium",
        tools: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Send a request to GPT-5 using the Responses API with reasoning capabilities.

        GPT-5 Reasoning Features:
        - reasoning_effort: Controls how much time the model spends reasoning
        - reasoning_summary: Controls detail level of reasoning explanation
        - text_verbosity: Controls length of generated text (GPT-5 specific)

        Args:
            prompt: Input prompt/question
            reasoning_effort: Reasoning effort level (low, medium, high)
            reasoning_summary: Reasoning summary detail (auto, detailed)
                Note: GPT-5 does not support "concise" summary
            text_verbosity: Text generation verbosity (low, medium, high)
            tools: Optional list of tools (e.g., MCP servers)

        Returns:
            Dict with response data including output, reasoning, usage
        """
        request_params = {
            "input": prompt,
            "model": self.model,
            "reasoning": {
                "effort": reasoning_effort,
                "summary": reasoning_summary,
            },
            "text": {
                "verbosity": text_verbosity,
            },
        }

        if tools:
            request_params["tools"] = tools

        response = self.client.responses.create(**request_params)
        result = response.model_dump()

        # Track costs if enabled
        if COST_TRACKING_ENABLED and "usage" in result:
            track_gpt5_request(
                model=self.model,
                usage=result["usage"],
                request_type="reasoning",
                metadata={
                    "reasoning_effort": reasoning_effort,
                    "prompt_preview": prompt[:100],
                },
            )

        return result

    def analyze_financial_document(
        self, document_text: str, analysis_type: Literal["tax", "audit", "general"] = "general"
    ) -> Dict:
        """
        Analyze financial document using GPT-5 reasoning capabilities.

        Specialized for CPA firm tasks:
        - Tax: Identify tax implications, deductions, compliance issues
        - Audit: Find discrepancies, risk areas, audit trail issues
        - General: General financial analysis and insights

        Args:
            document_text: Text content of financial document
            analysis_type: Type of analysis (tax, audit, general)

        Returns:
            Dict with analysis results, findings, and recommendations
        """
        system_prompts = {
            "tax": (
                "You are a senior tax accountant at Rahman Finance and Accounting P.L.LLC. "
                "Analyze the following document for tax implications, potential deductions, "
                "compliance issues, and filing requirements. Provide detailed reasoning for "
                "your findings."
            ),
            "audit": (
                "You are a senior auditor at Rahman Finance and Accounting P.L.LLC. "
                "Review the following document for discrepancies, unusual transactions, "
                "internal control weaknesses, and areas requiring additional evidence. "
                "Explain your reasoning for each finding."
            ),
            "general": (
                "You are a senior accountant at Rahman Finance and Accounting P.L.LLC. "
                "Analyze the following financial document and provide insights on financial "
                "health, trends, risks, and recommendations."
            ),
        }

        prompt = f"{system_prompts[analysis_type]}\n\n{document_text}"

        return self.reasoning_response(
            prompt=prompt,
            reasoning_effort="high",
            reasoning_summary="detailed",
            text_verbosity="medium",
        )

    def generate_client_report_summary(self, client_data: str, report_type: str = "quarterly") -> Dict:
        """
        Generate executive summary for client reports using GPT-5.

        Args:
            client_data: Client financial data and metrics
            report_type: Type of report (quarterly, annual, tax, etc.)

        Returns:
            Dict with generated summary and key insights
        """
        prompt = (
            f"Generate a professional executive summary for a {report_type} client report "
            f"for Rahman Finance and Accounting P.L.LLC.\n\n"
            f"Client Data:\n{client_data}\n\n"
            f"Include: Key financial highlights, significant changes, recommendations, "
            f"and next steps. Use professional CPA language."
        )

        return self.chat_completion(
            prompt=prompt,
            system_message=(
                "You are a senior partner at Rahman Finance and Accounting P.L.LLC. "
                "Write clear, professional client reports that comply with accounting "
                "standards and professional ethics."
            ),
            max_tokens=2000,
        )

    def draft_engagement_letter(
        self,
        client_name: str,
        service_type: str,
        scope_details: str,
        fee_structure: Optional[str] = None,
    ) -> Dict:
        """
        Draft professional engagement letter using GPT-5.

        Args:
            client_name: Client name
            service_type: Type of service (audit, tax, consulting, etc.)
            scope_details: Detailed scope of work
            fee_structure: Optional fee structure details

        Returns:
            Dict with drafted engagement letter
        """
        prompt = (
            f"Draft a professional engagement letter for:\n\n"
            f"Client: {client_name}\n"
            f"Service: {service_type}\n"
            f"Scope: {scope_details}\n"
        )

        if fee_structure:
            prompt += f"Fee Structure: {fee_structure}\n"

        prompt += (
            "\n\nThe letter should include: introduction, scope of services, "
            "responsibilities (firm and client), limitations, fee arrangement, "
            "terms and conditions, and signature blocks. Follow AICPA standards."
        )

        return self.chat_completion(
            prompt=prompt,
            system_message=(
                "You are a managing partner at Rahman Finance and Accounting P.L.LLC. "
                "Draft engagement letters that comply with AICPA professional standards, "
                "clearly define scope, protect the firm legally, and maintain professional tone."
            ),
            max_tokens=3000,
        )


# Convenience functions for common use cases


def quick_chat(prompt: str, model: str = "gpt-5") -> str:
    """
    Quick GPT-5 chat completion (uses environment variables for auth).

    Args:
        prompt: User prompt
        model: Model deployment name (default: gpt-5)

    Returns:
        String response from GPT-5
    """
    client = GPT5Client(model=model)
    response = client.chat_completion(prompt=prompt)
    return response["choices"][0]["message"]["content"]


def analyze_with_reasoning(prompt: str, model: str = "gpt-5") -> Dict:
    """
    Analyze prompt using GPT-5 reasoning capabilities.

    Args:
        prompt: Input prompt
        model: Model deployment name (default: gpt-5)

    Returns:
        Dict with output_text and reasoning_summary
    """
    client = GPT5Client(model=model)
    response = client.reasoning_response(prompt=prompt, reasoning_effort="high", reasoning_summary="detailed")
    return {
        "output": response.get("output_text", ""),
        "reasoning": response.get("reasoning_summary", ""),
        "usage": response.get("usage", {}),
    }


# Example usage
if __name__ == "__main__":
    # Example 1: Simple chat completion
    print("=" * 80)
    print("Example 1: GPT-5 Chat Completion")
    print("=" * 80)

    try:
        client = GPT5Client(model="gpt-5")
        response = client.chat_completion(
            prompt="What are the key considerations for tax planning in a CPA firm?",
            system_message="You are a senior tax advisor at Rahman Finance and Accounting P.L.LLC.",
            max_tokens=500,
        )
        print(f"Response: {response['choices'][0]['message']['content']}\n")
        print(f"Tokens used: {response['usage']}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Example 2: Reasoning API with high reasoning effort
    print("=" * 80)
    print("Example 2: GPT-5 Reasoning API")
    print("=" * 80)

    try:
        client = GPT5Client(model="gpt-5")
        response = client.reasoning_response(
            prompt=(
                "A client has $50,000 in capital gains and $30,000 in capital losses. "
                "They're considering selling an investment property with a $40,000 gain. "
                "What are the tax implications for this tax year?"
            ),
            reasoning_effort="high",
            reasoning_summary="detailed",
            text_verbosity="medium",
        )
        print(f"Output: {response.get('output_text', 'N/A')}\n")
        print(f"Reasoning: {response.get('reasoning_summary', 'N/A')}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Example 3: Financial document analysis
    print("=" * 80)
    print("Example 3: Financial Document Analysis")
    print("=" * 80)

    try:
        sample_document = """
        Revenue: $500,000 (increased 15% from prior year)
        COGS: $300,000 (increased 20% from prior year)
        Operating Expenses: $150,000 (decreased 5% from prior year)
        Net Income: $50,000 (decreased 10% from prior year)

        Notable items:
        - New equipment purchase: $75,000 (Section 179 eligible)
        - Customer concentration: Top 3 customers represent 60% of revenue
        - Inventory increased 30% year-over-year
        """

        client = GPT5Client(model="gpt-5")
        response = client.analyze_financial_document(document_text=sample_document, analysis_type="audit")
        print(f"Analysis: {response.get('output_text', 'N/A')[:500]}...\n")
    except Exception as e:
        print(f"Error: {e}\n")

    print("=" * 80)
    print("Setup Instructions:")
    print("=" * 80)
    print("1. Set environment variables:")
    print("   - AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com")
    print("   - AZURE_OPENAI_API_KEY=your-api-key")
    print("2. Or use Azure Entra ID: GPT5Client(use_entra_id=True)")
    print("3. Ensure GPT-5 model is deployed in your Azure OpenAI resource")
    print("=" * 80)
