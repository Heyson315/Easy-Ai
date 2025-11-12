"""
GPT-5 Demo Script - Rahman Finance and Accounting P.L.LLC
==========================================================

Interactive demonstration of OpenAI GPT-5 capabilities for CPA firm tasks.

Features demonstrated:
1. Chat Completions API (simple Q&A)
2. Reasoning API with high reasoning effort
3. Financial document analysis (tax, audit)
4. Client report generation
5. Engagement letter drafting

Usage:
    python scripts/demo_gpt5.py

Requirements:
    - Azure OpenAI GPT-5 deployment
    - Environment variables set (see setup instructions below)
"""

import os
import sys
from pathlib import Path

# Add src directory to path (must be before src imports)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# pylint: disable=wrong-import-position
from src.integrations.openai_gpt5 import GPT5Client, analyze_with_reasoning, quick_chat  # noqa: E402


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_1_simple_chat():
    """Demo 1: Simple chat completion."""
    print_header("Demo 1: Simple Chat Completion")

    try:
        client = GPT5Client(model="gpt-5")

        print("Question: What are the top 3 tax planning strategies for small businesses in 2025?\n")

        response = client.chat_completion(
            prompt="What are the top 3 tax planning strategies for small businesses in 2025?",
            system_message=(
                "You are a senior tax advisor at Rahman Finance and Accounting P.L.LLC. "
                "Provide practical, compliant tax advice."
            ),
            max_tokens=800,
        )

        answer = response["choices"][0]["message"]["content"]
        usage = response["usage"]

        print(f"Answer:\n{answer}\n")
        print(
            f"Token Usage: {usage['total_tokens']} tokens "
            f"(prompt: {usage['prompt_tokens']}, completion: {usage['completion_tokens']})"
        )

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Ensure AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY are set.\n")


def demo_2_reasoning_api():
    """Demo 2: Reasoning API with detailed reasoning."""
    print_header("Demo 2: GPT-5 Reasoning API (High Reasoning Effort)")

    try:
        client = GPT5Client(model="gpt-5")

        scenario = """
        Client Scenario:
        - Small manufacturing business (S-Corp)
        - Annual revenue: $2.5M
        - Owner salary: $80,000
        - Net profit (before owner salary): $400,000
        - Considering purchasing $200,000 in equipment
        - Has $50,000 in capital loss carryforward from prior years

        Question: What are the tax optimization strategies for this year?
        """

        print(f"Scenario:\n{scenario}\n")
        print("Analyzing with high reasoning effort (this may take 10-20 seconds)...\n")

        response = client.reasoning_response(
            prompt=scenario,
            reasoning_effort="high",
            reasoning_summary="detailed",
            text_verbosity="medium",
        )

        output = response.get("output_text", "No output")
        reasoning = response.get("reasoning_summary", "No reasoning provided")
        usage = response.get("usage", {})

        print(f"GPT-5 Analysis:\n{output}\n")
        print(f"\n--- Reasoning Process ---\n{reasoning}\n")
        print(f"Token Usage: {usage.get('total_tokens', 'N/A')} tokens")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Ensure AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY are set.\n")


def demo_3_financial_analysis():
    """Demo 3: Financial document analysis."""
    print_header("Demo 3: Financial Document Analysis (Audit Perspective)")

    sample_financials = """
    ABC Manufacturing Inc. - Q3 2025 Financial Data

    Income Statement:
    - Revenue: $650,000 (up 25% from Q2)
    - Cost of Goods Sold: $420,000 (up 35% from Q2)
    - Gross Profit: $230,000 (35.4% margin, down from 41.2% in Q2)
    - Operating Expenses: $180,000 (up 10% from Q2)
    - Net Income: $50,000 (down 15% from Q2)

    Balance Sheet Highlights:
    - Cash: $45,000 (down from $120,000 in Q2)
    - Accounts Receivable: $280,000 (DSO increased to 65 days from 45 days)
    - Inventory: $340,000 (up 40% from Q2)
    - Accounts Payable: $190,000 (DPO increased to 75 days from 50 days)
    - Short-term debt: $150,000 (new line of credit drawn)

    Notable Items:
    - Major customer (30% of revenue) payment delayed 60 days
    - New product line launched in Q3
    - Equipment lease renegotiated mid-quarter
    - Two key employees left during the quarter
    """

    try:
        client = GPT5Client(model="gpt-5")

        print("Sample Financials:\n")
        print(sample_financials)
        print("\nAnalyzing from audit perspective (high reasoning effort)...\n")

        response = client.analyze_financial_document(document_text=sample_financials, analysis_type="audit")

        output = response.get("output_text", "No analysis available")
        reasoning = response.get("reasoning_summary", "")

        print(f"Audit Analysis:\n{output}\n")

        if reasoning:
            print(f"\n--- Auditor's Reasoning ---\n{reasoning[:500]}...\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Ensure AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY are set.\n")


def demo_4_client_report():
    """Demo 4: Generate client report summary."""
    print_header("Demo 4: Client Report Generation")

    client_data = """
    Rahman Finance and Accounting P.L.LLC - Client Quarterly Report

    Client: Tech Innovations LLC
    Period: Q3 2025

    Financial Performance:
    - Revenue: $1.2M (up 18% YoY)
    - Gross Margin: 58% (improved from 54% last year)
    - Operating Expenses: $420,000 (controlled at 35% of revenue)
    - Net Profit: $276,000 (23% margin)
    - Cash Flow from Operations: $310,000 (strong conversion)

    Key Achievements:
    - Successfully launched new SaaS product (contributing 15% of revenue)
    - Reduced customer acquisition cost by 22%
    - Improved gross margin through better pricing strategy
    - Paid off $150,000 term loan ahead of schedule

    Recommendations:
    - Consider R&D tax credit for new product development ($50K potential)
    - Evaluate Section 179 deduction for planned equipment purchases
    - Review sales tax nexus given expansion to 3 new states
    - Implement more sophisticated revenue recognition tracking
    """

    try:
        client = GPT5Client(model="gpt-5")

        print("Client Data Summary:\n")
        print(client_data[:400] + "...\n")
        print("Generating executive summary...\n")

        response = client.generate_client_report_summary(client_data=client_data, report_type="quarterly")

        summary = response["choices"][0]["message"]["content"]
        print(f"Generated Executive Summary:\n\n{summary}\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Ensure AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY are set.\n")


def demo_5_engagement_letter():
    """Demo 5: Draft engagement letter."""
    print_header("Demo 5: Engagement Letter Drafting")

    try:
        client = GPT5Client(model="gpt-5")

        print("Drafting engagement letter for tax preparation services...\n")

        response = client.draft_engagement_letter(
            client_name="Sunrise Retail Corporation",
            service_type="Corporate Tax Preparation and Planning",
            scope_details=(
                "Preparation of Form 1120 corporate tax return for tax year 2025, "
                "including federal and state returns. Quarterly estimated tax calculations. "
                "Tax planning consultation for capital expenditures and R&D activities. "
                "Sales tax compliance review for multi-state operations."
            ),
            fee_structure=(
                "$5,000 fixed fee for tax return preparation, plus $250/hour for " "additional consulting services."
            ),
        )

        letter = response["choices"][0]["message"]["content"]
        print(f"Generated Engagement Letter (excerpt):\n\n{letter[:1200]}...\n")
        print("(Full letter would be longer - this is a preview)\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Ensure AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY are set.\n")


def demo_6_convenience_functions():
    """Demo 6: Convenience functions."""
    print_header("Demo 6: Convenience Functions")

    print("Using quick_chat() function:\n")
    try:
        response = quick_chat("Explain the difference between cash basis and accrual accounting in 2 sentences.")
        print(f"Response: {response}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

    print("\nUsing analyze_with_reasoning() function:\n")
    try:
        result = analyze_with_reasoning(
            "A client wants to convert from C-Corp to S-Corp. What are the key considerations?"
        )
        print(f"Output: {result['output'][:300]}...\n")
        print(f"Reasoning: {result['reasoning'][:300]}...\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")


def print_setup_instructions():
    """Print setup instructions."""
    print_header("Setup Instructions")

    print(
        """
1. Create Azure OpenAI Resource:
   - Go to portal.azure.com
   - Create Azure OpenAI resource
   - Deploy GPT-5 or GPT-5-mini model

2. Get Credentials:
   - Navigate to Keys and Endpoint
   - Copy endpoint URL and API key

3. Set Environment Variables:

   Windows PowerShell:
   $env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
   $env:AZURE_OPENAI_API_KEY="your-api-key-here"

   Windows Command Prompt:
   set AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
   set AZURE_OPENAI_API_KEY=your-api-key-here

   Linux/Mac:
   export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
   export AZURE_OPENAI_API_KEY="your-api-key-here"

4. Install Dependencies:
   python -m pip install -r requirements.txt

5. Run Demo:
   python scripts/demo_gpt5.py

6. Alternative - Azure Entra ID (Keyless):
   # No API key needed, uses your Azure credentials
   from src.integrations.openai_gpt5 import GPT5Client
   client = GPT5Client(use_entra_id=True)

For more information:
- https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/reasoning
- https://learn.microsoft.com/en-us/azure/cognitive-services/openai/quickstart
    """
    )


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("  GPT-5 Integration Demo - Rahman Finance and Accounting P.L.LLC")
    print("=" * 80)

    # Check if environment variables are set
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if not endpoint or not api_key:
        print("\n⚠️  Environment variables not set!")
        print_setup_instructions()
        print("\nSet the environment variables and run this script again.\n")
        return

    print(f"\n✅ Azure OpenAI Endpoint: {endpoint}")
    print("✅ API Key: [SET]" if api_key else "✅ API Key: [NOT SET]")
    print("\nRunning demos...\n")

    # Run demos
    demo_1_simple_chat()
    demo_2_reasoning_api()
    demo_3_financial_analysis()
    demo_4_client_report()
    demo_5_engagement_letter()
    demo_6_convenience_functions()

    print_header("Demo Complete")
    print("All demos completed successfully! ✅")
    print("\nNext Steps:")
    print("1. Review src/integrations/openai_gpt5.py for full API documentation")
    print("2. Customize prompts for your specific CPA firm workflows")
    print("3. Integrate GPT-5 into your existing scripts and reports")
    print("4. Monitor token usage and costs (see Azure Portal)")
    print("\nGPT-5 Pricing (as of Nov 2025):")
    print("- gpt-5: ~$0.03/1K input tokens, ~$0.10/1K output tokens")
    print("- gpt-5-mini: ~$0.01/1K input tokens, ~$0.03/1K output tokens")
    print("- Reasoning effort increases token usage but improves quality")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
