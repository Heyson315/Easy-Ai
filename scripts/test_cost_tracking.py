"""
GPT-5 Cost Tracker Demo and Testing
====================================

Demonstrates cost tracking and budget management for development/testing.

Usage:
    python scripts/test_cost_tracking.py
"""

import sys
from pathlib import Path

# Add project root to path (must be before src imports)
sys.path.insert(0, str(Path(__file__).parent.parent))

# pylint: disable=wrong-import-position
from src.core.console_utils import print_header  # noqa: E402
from src.core.cost_tracker import GPT5CostTracker  # noqa: E402


def demo_cost_tracking():
    """Demonstrate cost tracking features."""
    print_header("GPT-5 Cost Tracking Demo - Development/Testing Mode")

    # Create tracker with $5 daily budget (good for development)
    print("\n🎯 Creating tracker with $5.00 daily budget limit...")
    tracker = GPT5CostTracker(budget_limit=5.00)

    print("\n📝 Simulating various GPT-5 requests...\n")

    # Scenario 1: Simple Q&A with gpt-5-mini (cheapest)
    print("1️⃣  Simple Q&A (gpt-5-mini):")
    result1 = tracker.track_request(
        model="gpt-5-mini",
        prompt_tokens=200,
        completion_tokens=300,
        request_type="chat",
        metadata={"task": "simple_question", "user": "developer"},
    )
    print(f"   Cost: ${result1['request']['cost']['total']:.6f}")

    # Scenario 2: Financial document analysis (gpt-5)
    print("\n2️⃣  Financial Document Analysis (gpt-5):")
    result2 = tracker.track_request(
        model="gpt-5",
        prompt_tokens=1500,
        completion_tokens=2000,
        cached_tokens=500,  # Some prompt caching
        request_type="reasoning",
        metadata={"task": "document_analysis", "document": "tax_return_2025.pdf"},
    )
    print(f"   Cost: ${result2['request']['cost']['total']:.6f}")
    print(f"   Cache savings: ${(500 / 1_000_000) * 2:.6f}")

    # Scenario 3: Client email draft (gpt-5-mini)
    print("\n3️⃣  Client Email Draft (gpt-5-mini):")
    result3 = tracker.track_request(
        model="gpt-5-mini",
        prompt_tokens=300,
        completion_tokens=500,
        request_type="chat",
        metadata={"task": "email_draft", "client": "ABC Corp"},
    )
    print(f"   Cost: ${result3['request']['cost']['total']:.6f}")

    # Scenario 4: Complex tax planning (gpt-5 with high reasoning)
    print("\n4️⃣  Complex Tax Planning (gpt-5 + high reasoning):")
    result4 = tracker.track_request(
        model="gpt-5",
        prompt_tokens=2500,
        completion_tokens=3500,
        cached_tokens=1000,
        request_type="reasoning",
        metadata={"task": "tax_planning", "reasoning_effort": "high"},
    )
    print(f"   Cost: ${result4['request']['cost']['total']:.6f}")

    # Scenario 5: Batch processing with gpt-5-nano (cheapest)
    print("\n5️⃣  Batch Processing (gpt-5-nano x 10):")
    batch_cost = 0
    for i in range(10):
        result = tracker.track_request(
            model="gpt-5-nano",
            prompt_tokens=100,
            completion_tokens=150,
            request_type="chat",
            metadata={"task": "batch_processing", "item": i + 1},
        )
        batch_cost += result["request"]["cost"]["total"]
    print(f"   Total batch cost: ${batch_cost:.6f}")

    # Print session summary
    tracker.print_session_summary()

    # Print detailed report
    tracker.print_detailed_report(days=1)

    # Export to CSV
    print("\n📁 Exporting cost data to CSV...")
    tracker.export_to_csv("output/reports/gpt5_dev_costs.csv")


def demo_budget_alerts():
    """Demonstrate budget alert system."""
    print("\n" + "=" * 80)
    print("  Budget Alert Demo")
    print("=" * 80)

    # Create tracker with very low budget ($0.10) to trigger alert
    print("\n⚠️  Creating tracker with $0.10 budget limit (will trigger alert)...\n")
    tracker = GPT5CostTracker(budget_limit=0.10)

    # Make a request that exceeds budget
    print("Making expensive request with gpt-5...")
    tracker.track_request(
        model="gpt-5",
        prompt_tokens=5000,
        completion_tokens=10000,
        request_type="reasoning",
        metadata={"task": "expensive_request"},
    )

    # The alert will be printed automatically
    print("\n✅ Budget alert system is working!")


def demo_cost_optimization():
    """Demonstrate cost optimization recommendations."""
    print("\n" + "=" * 80)
    print("  Cost Optimization Recommendations Demo")
    print("=" * 80)

    tracker = GPT5CostTracker()

    # Simulate suboptimal usage patterns
    print("\n📊 Simulating various usage patterns...\n")

    # Pattern 1: Too much gpt-5 usage (expensive)
    print("Pattern 1: Heavy gpt-5 usage (expensive)")
    for i in range(15):
        tracker.track_request(
            model="gpt-5",
            prompt_tokens=1000,
            completion_tokens=1500,
            request_type="chat",
            metadata={"pattern": "expensive_model_overuse"},
        )

    # Pattern 2: Low cache usage (inefficient)
    print("Pattern 2: Low cache usage (inefficient)")
    for i in range(10):
        tracker.track_request(
            model="gpt-5",
            prompt_tokens=2000,
            completion_tokens=1000,
            cached_tokens=0,  # Not using caching!
            request_type="chat",
            metadata={"pattern": "no_caching"},
        )

    # Pattern 3: High output tokens (wasteful)
    print("Pattern 3: High output tokens (wasteful)")
    for i in range(8):
        tracker.track_request(
            model="gpt-5",
            prompt_tokens=500,
            completion_tokens=5000,  # Very high output!
            request_type="chat",
            metadata={"pattern": "high_output"},
        )

    # Pattern 4: Overusing reasoning API
    print("Pattern 4: Overusing Reasoning API")
    for i in range(12):
        tracker.track_request(
            model="gpt-5",
            prompt_tokens=1000,
            completion_tokens=1500,
            request_type="reasoning",  # Using reasoning for simple tasks
            metadata={"pattern": "reasoning_overuse"},
        )

    # Get recommendations
    print("\n" + "=" * 80)
    tracker.print_detailed_report(days=1)


def demo_model_comparison():
    """Compare costs across different GPT-5 models."""
    print("\n" + "=" * 80)
    print("  Model Cost Comparison")
    print("=" * 80)

    tracker = GPT5CostTracker()

    # Same request across all models
    prompt_tokens = 1000
    completion_tokens = 1500

    print(f"\n📊 Request: {prompt_tokens:,} input + {completion_tokens:,} output tokens\n")

    models = ["gpt-5", "gpt-5-mini", "gpt-5-nano"]
    results = {}

    for model in models:
        result = tracker.track_request(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            request_type="chat",
            metadata={"comparison_test": True},
        )
        cost = result["request"]["cost"]["total"]
        results[model] = cost
        print(f"   {model:15s}: ${cost:.6f}")

    # Calculate savings
    baseline = results["gpt-5"]
    print("\n💰 Savings vs gpt-5:")
    savings_mini = baseline - results["gpt-5-mini"]
    savings_nano = baseline - results["gpt-5-nano"]
    print(f"   gpt-5-mini: ${savings_mini:.6f} " f"({(savings_mini / baseline * 100):.1f}% cheaper)")
    print(f"   gpt-5-nano: ${savings_nano:.6f} " f"({(savings_nano / baseline * 100):.1f}% cheaper)")

    print("\n💡 Recommendation:")
    print("   Use gpt-5-mini for most CPA tasks (2-3x cheaper)")
    print("   Use gpt-5-nano for simple queries (4-5x cheaper)")
    print("   Reserve gpt-5 for complex reasoning and critical analysis")
    print("=" * 80 + "\n")


def print_development_tips():
    """Print cost-saving tips for development."""
    print("\n" + "=" * 80)
    print("  💡 Cost-Saving Tips for Development & Testing")
    print("=" * 80)

    tips = [
        ("Set Daily Budgets", "$3-10/day is reasonable for active development"),
        ("Start with Smaller Models", "Use gpt-5-mini or gpt-5-nano first, upgrade only if needed"),
        ("Limit max_tokens", "Set max_completion_tokens=500-1000 for testing"),
        ("Use Prompt Caching", "Reuse common prompt prefixes to save 50% on input"),
        ("Batch Processing", "Use Batch API for 50% discount (24hr turnaround)"),
        ("Monitor Daily", "Check costs every day during development"),
        ("Test with Free Tier First", "Use Azure's free tier credits before paid usage"),
        ("Use Development Environments", "Set up separate dev/test/prod with different budgets"),
        ("Log Everything", "Track all requests to identify expensive operations"),
        ("Review Weekly Reports", "Analyze patterns and optimize high-cost areas"),
    ]

    for i, (title, description) in enumerate(tips, 1):
        print(f"\n{i:2d}. {title}")
        print(f"    {description}")

    print("\n" + "=" * 80)
    print("\n📌 Quick Budget Reference for CPA Firms:")
    print("   Development/Testing: $5-10/day")
    print("   Light Production: $20-50/day")
    print("   Medium Production: $50-200/day")
    print("   Heavy Production: $200-1000/day")
    print("\n" + "=" * 80 + "\n")


def main():
    """Run all demos."""
    print("\n" + "🚀" * 40)
    print("  GPT-5 Cost Tracking & Budget Management Demo")
    print("  Perfect for Development & Testing Environments")
    print("🚀" * 40)

    try:
        # Run demos
        demo_cost_tracking()
        demo_model_comparison()
        demo_budget_alerts()
        demo_cost_optimization()
        print_development_tips()

        print("\n✅ All demos completed successfully!")
        print("\n📚 Next Steps:")
        print("   1. Review the cost log: output/reports/gpt5_cost_log.json")
        print("   2. Check CSV export: output/reports/gpt5_dev_costs.csv")
        print("   3. Import the tracker in your scripts:")
        print("      from src.core.cost_tracker import get_tracker")
        print("   4. Set your daily budget:")
        print("      tracker = get_tracker(budget_limit=5.00)")
        print("\n" + "=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
