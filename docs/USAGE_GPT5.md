# OpenAI GPT-5 Integration Guide
**Rahman Finance and Accounting P.L.LLC**

## Overview

This guide covers the integration of OpenAI GPT-5 models into the share-report toolkit for CPA firm workflows. GPT-5 is OpenAI's latest reasoning model family, designed for complex analytical tasks requiring multi-step reasoning.

## Key Features

### 1. **GPT-5 Model Family**
- **gpt-5**: Full reasoning capabilities, highest quality
- **gpt-5-mini**: Faster, cost-effective alternative
- **gpt-5-nano**: Lightweight version (preview)

### 2. **Reasoning API**
GPT-5 introduces a new Responses API with advanced reasoning features:

```python
response = client.responses.create(
    model="gpt-5",
    input="Complex tax scenario...",
    reasoning={
        "effort": "high",      # low, medium, high
        "summary": "detailed"  # auto, detailed (no "concise" for GPT-5)
    },
    text={
        "verbosity": "medium"  # low, medium, high (GPT-5 specific)
    }
)
```

**Reasoning Effort Levels:**
- **Low**: Quick responses, less thorough analysis
- **Medium**: Balanced speed and quality (default)
- **High**: Deep analysis, multi-step reasoning (best for complex CPA tasks)

### 3. **Chat Completions API**
Traditional chat interface, compatible with GPT-4 code:

```python
response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "developer", "content": "You are a senior tax advisor..."},
        {"role": "user", "content": "What are the tax implications of..."}
    ],
    max_completion_tokens=5000
)
```

## Installation

### 1. Install Dependencies

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install required packages
pip install openai>=1.65.0 azure-identity>=1.19.0

# Or use requirements.txt
pip install -r requirements.txt
```

### 2. Azure OpenAI Setup

1. **Create Azure OpenAI Resource:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Create new Azure OpenAI resource
   - Select region with GPT-5 availability (check [model availability](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models))

2. **Deploy GPT-5 Model:**
   - Navigate to Azure OpenAI Studio
   - Go to Deployments → Create new deployment
   - Select `gpt-5` or `gpt-5-mini` model
   - Name deployment (e.g., "gpt-5")
   - Set capacity (TPM quota)

3. **Get Credentials:**
   - Azure Portal → Your OpenAI Resource → Keys and Endpoint
   - Copy **Endpoint** (e.g., `https://your-resource.openai.azure.com`)
   - Copy **KEY 1** or **KEY 2**

### 3. Configure Environment Variables

**Windows PowerShell:**
```powershell
$env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
$env:AZURE_OPENAI_API_KEY="your-api-key-here"
```

**Linux/Mac:**
```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key-here"
```

**Persistent Configuration (.env file):**
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
```

## Quick Start

### Basic Usage

```python
from src.integrations.openai_gpt5 import GPT5Client

# Initialize client
client = GPT5Client(model="gpt-5")

# Simple chat
response = client.chat_completion(
    prompt="What are the tax implications of converting from C-Corp to S-Corp?"
)
print(response['choices'][0]['message']['content'])

# Reasoning API (for complex analysis)
response = client.reasoning_response(
    prompt="Analyze this financial scenario...",
    reasoning_effort="high",
    reasoning_summary="detailed"
)
print(response['output_text'])
```

### Convenience Functions

```python
from src.integrations.openai_gpt5 import quick_chat, analyze_with_reasoning

# Quick chat (uses env vars)
answer = quick_chat("Explain accrual accounting in simple terms")

# Analysis with reasoning
result = analyze_with_reasoning(
    "What are the risks in this investment structure?"
)
print(result['output'])      # Final answer
print(result['reasoning'])   # Reasoning process
```

## CPA Firm Use Cases

### 1. Financial Document Analysis

```python
client = GPT5Client(model="gpt-5")

# Analyze from tax perspective
response = client.analyze_financial_document(
    document_text=financial_statements,
    analysis_type="tax"  # or "audit", "general"
)

# Returns detailed analysis with reasoning
print(response['output_text'])
print(response['reasoning_summary'])
```

**Analysis Types:**
- **tax**: Identify tax implications, deductions, compliance issues
- **audit**: Find discrepancies, risk areas, control weaknesses
- **general**: Financial health, trends, recommendations

### 2. Client Report Generation

```python
# Generate executive summary
response = client.generate_client_report_summary(
    client_data="""
    Revenue: $2.5M (up 15%)
    Net Income: $400K (up 8%)
    Key metrics...
    """,
    report_type="quarterly"  # or "annual", "tax"
)

summary = response['choices'][0]['message']['content']
```

### 3. Engagement Letter Drafting

```python
# Draft professional engagement letter
response = client.draft_engagement_letter(
    client_name="ABC Corporation",
    service_type="Corporate Tax Preparation",
    scope_details="Form 1120, quarterly estimates, tax planning",
    fee_structure="$5,000 fixed fee + $250/hour consulting"
)

letter = response['choices'][0]['message']['content']
```

## Demo Script

Run comprehensive demos:

```powershell
# Run all demos
python scripts/demo_gpt5.py
```

**Demos Include:**
1. Simple chat completion
2. Reasoning API with high effort
3. Financial document analysis (audit perspective)
4. Client report generation
5. Engagement letter drafting
6. Convenience functions

## Authentication Options

### Option 1: API Key (Default)

```python
client = GPT5Client(
    azure_endpoint="https://your-resource.openai.azure.com",
    api_key="your-api-key"
)
```

### Option 2: Azure Entra ID (Keyless)

```python
# Uses DefaultAzureCredential (your Azure login)
client = GPT5Client(
    azure_endpoint="https://your-resource.openai.azure.com",
    use_entra_id=True  # No API key needed
)
```

**Entra ID Setup:**
1. Ensure you're logged into Azure CLI: `az login`
2. Grant yourself "Cognitive Services OpenAI User" role on the resource
3. Use `use_entra_id=True` in client initialization

## Best Practices

### 1. Token Management

- **max_completion_tokens**: Limit output length (default: 5000)
- **Monitor usage**: Check `response['usage']` for token counts
- **Reasoning effort**: Higher effort = more tokens but better quality

```python
response = client.chat_completion(
    prompt="...",
    max_tokens=1000  # Limit to reduce costs
)
print(f"Tokens used: {response['usage']['total_tokens']}")
```

### 2. System Messages (Developer Role)

GPT-5 uses "developer" role instead of "system":

```python
# Good: Clear role definition
response = client.chat_completion(
    prompt="Analyze this tax scenario...",
    system_message=(
        "You are a senior tax partner at Rahman Finance and Accounting P.L.LLC. "
        "Follow IRS regulations and AICPA professional standards. "
        "Provide conservative, compliant advice."
    )
)
```

### 3. Reasoning for Complex Tasks

Use Reasoning API for multi-step analysis:

```python
# For simple Q&A: Use Chat Completions
answer = client.chat_completion("What is Form 1120?")

# For complex analysis: Use Reasoning API
analysis = client.reasoning_response(
    prompt="Complex tax optimization scenario...",
    reasoning_effort="high",      # Deep analysis
    reasoning_summary="detailed"  # Show reasoning steps
)
```

### 4. Error Handling

```python
try:
    client = GPT5Client(model="gpt-5")
    response = client.chat_completion("...")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"API error: {e}")
    # Check: endpoint, API key, model deployment, quota
```

## Pricing & Cost Management

**GPT-5 Pricing (approximate, as of Nov 2025):**
- **Input tokens**: ~$0.03 per 1,000 tokens
- **Output tokens**: ~$0.10 per 1,000 tokens
- **Reasoning effort**: Higher effort increases token usage

**GPT-5 Mini Pricing:**
- **Input tokens**: ~$0.01 per 1,000 tokens
- **Output tokens**: ~$0.03 per 1,000 tokens
- ~3x cheaper than GPT-5, still high quality

**Cost Optimization Tips:**
1. Use `max_completion_tokens` to limit output
2. Start with `reasoning_effort="medium"` (default)
3. Use `gpt-5-mini` for less critical tasks
4. Cache common prompts/responses
5. Monitor usage in Azure Portal

**Example Cost Calculation:**
```
Prompt: 1,000 tokens × $0.03 = $0.03
Response: 2,000 tokens × $0.10 = $0.20
Total: $0.23 per request
```

## Integration Examples

### Example 1: M365 Security Report Enhancement

```python
# Enhance security report with GPT-5 insights
from src.integrations.openai_gpt5 import GPT5Client
import json

# Load audit results
with open("output/reports/security/m365_cis_audit.json") as f:
    audit_data = json.load(f)

# Analyze findings
client = GPT5Client(model="gpt-5")
response = client.reasoning_response(
    prompt=f"""
    Analyze this M365 security audit for a CPA firm:
    {json.dumps(audit_data, indent=2)}

    Prioritize findings based on:
    1. Client data confidentiality (CRITICAL for CPA)
    2. Regulatory compliance (SOC 2, AICPA)
    3. Business continuity

    Provide actionable recommendations.
    """,
    reasoning_effort="high",
    reasoning_summary="detailed"
)

print(response['output_text'])
```

### Example 2: Automated Client Email Drafting

```python
def draft_client_email(scenario: str, tone: str = "professional"):
    """Draft client-facing email using GPT-5."""
    client = GPT5Client(model="gpt-5")

    response = client.chat_completion(
        prompt=f"""
        Draft an email to a client about: {scenario}

        Tone: {tone}
        Include: Greeting, explanation, next steps, closing
        """,
        system_message=(
            "You are a partner at Rahman Finance and Accounting P.L.LLC. "
            "Write professional, clear emails that build client trust."
        ),
        max_tokens=800
    )

    return response['choices'][0]['message']['content']

# Usage
email = draft_client_email(
    "Their Q3 estimated tax payment is due next week",
    tone="friendly but professional"
)
```

### Example 3: Tax Research Assistant

```python
def tax_research(question: str):
    """Research tax question with citations."""
    client = GPT5Client(model="gpt-5")

    response = client.reasoning_response(
        prompt=f"""
        Tax Research Question: {question}

        Provide:
        1. Direct answer
        2. Relevant IRC sections
        3. Key regulations/rulings
        4. Practical implications
        5. Risks/considerations
        """,
        reasoning_effort="high",
        reasoning_summary="detailed",
        text_verbosity="high"
    )

    return {
        'answer': response['output_text'],
        'reasoning': response['reasoning_summary'],
        'tokens': response['usage']['total_tokens']
    }

# Usage
result = tax_research(
    "Can a C-Corp deduct meals and entertainment in 2025?"
)
```

## Troubleshooting

### Common Issues

**1. "Configuration error: Azure OpenAI endpoint is required"**
- Set `AZURE_OPENAI_ENDPOINT` environment variable
- Or pass `azure_endpoint` parameter to GPT5Client

**2. "API error: 401 Unauthorized"**
- Check `AZURE_OPENAI_API_KEY` is correct
- Verify key hasn't expired (regenerate in Azure Portal)
- For Entra ID: Ensure you're logged in (`az login`)

**3. "API error: 404 Not Found"**
- Model deployment doesn't exist
- Check deployment name matches `model` parameter
- Verify model is deployed in Azure OpenAI Studio

**4. "API error: 429 Too Many Requests"**
- Hit rate limit/quota
- Wait and retry (implement exponential backoff)
- Increase quota in Azure Portal

**5. "High token usage"**
- Reduce `max_completion_tokens`
- Use lower `reasoning_effort` (medium instead of high)
- Switch to `gpt-5-mini` for less critical tasks

### Debug Mode

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

client = GPT5Client(model="gpt-5")
response = client.chat_completion("Test prompt")

# Check response structure
print(response.keys())
print(response['usage'])
```

## Resources

### Microsoft Documentation
- [GPT-5 Reasoning Models](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/reasoning)
- [Azure OpenAI Quickstart](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/quickstart)
- [Supported Languages (Python)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages?pivots=programming-language-python)
- [Model Availability](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models)

### OpenAI Resources
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [API Reference](https://platform.openai.com/docs/api-reference)

### Project Files
- `src/integrations/openai_gpt5.py` - GPT-5 client implementation
- `scripts/demo_gpt5.py` - Comprehensive demos
- `requirements.txt` - Dependencies (openai, azure-identity)

## Support

For questions or issues:
1. Check troubleshooting section above
2. Review demo script: `python scripts/demo_gpt5.py`
3. Consult Microsoft Learn documentation
4. Check Azure Portal for service health

---

**Last Updated**: November 2025  
**Version**: 1.0.0  
**Compatible Models**: gpt-5, gpt-5-mini, gpt-5-nano (preview)
