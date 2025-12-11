"""
Cost Monitoring and Token Usage Tracker for GPT-5
==================================================

This module provides comprehensive cost tracking and budget management for
GPT-5 API usage during development and testing.

Features:
- Real-time token usage tracking
- Cost estimation and reporting
- Budget alerts and limits
- Usage statistics and analytics
- Cost-saving recommendations

Author: Rahman Finance and Accounting P.L.LLC
Created: November 2025
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class GPT5CostTracker:
    """
    Track and manage GPT-5 API costs for development and testing.

    Pricing (estimated, subject to change):
    - GPT-5: $4/1M input, $12/1M output
    - GPT-5-mini: $1.50/1M input, $4.50/1M output
    - GPT-5-nano: $0.75/1M input, $2.25/1M output
    - Cached input: 50% discount
    """

    # Estimated pricing (per 1M tokens) - update when official pricing released
    PRICING = {
        "gpt-5": {"input": 4.00, "cached_input": 2.00, "output": 12.00},
        "gpt-5-mini": {"input": 1.50, "cached_input": 0.75, "output": 4.50},
        "gpt-5-nano": {"input": 0.75, "cached_input": 0.375, "output": 2.25},
    }

    def __init__(self, budget_limit: Optional[float] = None, log_file: Optional[str] = None, auto_save: bool = False):
        """
        Initialize cost tracker.

        Args:
            budget_limit: Optional daily budget limit in USD (triggers warnings)
            log_file: Path to JSON log file for tracking usage history
            auto_save: If True, saves after every request. If False (default), call save() manually.
                      Performance optimization: Set to False for high-frequency usage.
        """
        self.budget_limit = budget_limit
        self.log_file = log_file or "output/reports/gpt5_cost_log.json"
        self.auto_save = auto_save
        self.session_costs = []
        self.total_tokens = {"input": 0, "cached_input": 0, "output": 0}
        self.total_cost = 0.0
        self._unsaved_entries = 0  # Track unsaved entries

        # Load existing log
        self.log_path = Path(self.log_file)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.history = self._load_history()
        
        # Cache for parsed dates to avoid repeated parsing
        self._date_cache: Dict[str, datetime] = {}

    def _load_history(self) -> List[Dict]:
        """Load cost history from log file."""
        if self.log_path.exists():
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def _save_history(self):
        """Save cost history to log file."""
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)
        self._unsaved_entries = 0  # Reset counter after save
    
    def save(self):
        """
        Explicitly save history to disk.
        
        Performance tip: Call this at the end of your session rather than
        relying on auto_save=True for better performance.
        """
        if self._unsaved_entries > 0:
            self._save_history()
    
    def _get_parsed_date(self, timestamp_str: str) -> datetime:
        """
        Get parsed datetime with caching to avoid repeated parsing.
        
        Performance optimization: Caches parsed dates to avoid O(n) datetime parsing
        in loops when filtering by date.
        """
        if timestamp_str not in self._date_cache:
            self._date_cache[timestamp_str] = datetime.fromisoformat(timestamp_str)
        return self._date_cache[timestamp_str]

    def track_request(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cached_tokens: int = 0,
        request_type: str = "chat",
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Track a single GPT-5 API request and calculate cost.

        Args:
            model: Model name (gpt-5, gpt-5-mini, gpt-5-nano)
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            cached_tokens: Number of cached input tokens (50% discount)
            request_type: Type of request (chat, reasoning, analysis)
            metadata: Optional metadata (user, task, etc.)

        Returns:
            Dict with cost breakdown and cumulative totals
        """
        # Normalize model name
        model_key = model.lower()
        if model_key not in self.PRICING:
            # Default to gpt-5 pricing if unknown
            model_key = "gpt-5"

        pricing = self.PRICING[model_key]

        # Calculate cost
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        cached_cost = (cached_tokens / 1_000_000) * pricing["cached_input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + cached_cost + output_cost

        # Update session totals
        self.total_tokens["input"] += prompt_tokens
        self.total_tokens["cached_input"] += cached_tokens
        self.total_tokens["output"] += completion_tokens
        self.total_cost += total_cost

        # Create log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "request_type": request_type,
            "tokens": {
                "input": prompt_tokens,
                "cached_input": cached_tokens,
                "output": completion_tokens,
                "total": prompt_tokens + cached_tokens + completion_tokens,
            },
            "cost": {
                "input": round(input_cost, 6),
                "cached_input": round(cached_cost, 6),
                "output": round(output_cost, 6),
                "total": round(total_cost, 6),
            },
            "metadata": metadata or {},
        }

        self.session_costs.append(entry)
        self.history.append(entry)
        self._unsaved_entries += 1
        
        # Only auto-save if enabled (performance optimization)
        if self.auto_save:
            self._save_history()
        elif self._unsaved_entries >= 10:  # Auto-save every 10 entries as safety fallback
            self._save_history()

        # Check budget
        if self.budget_limit:
            daily_cost = self.get_daily_cost()
            if daily_cost >= self.budget_limit:
                print(f"⚠️  BUDGET ALERT: Daily cost ${daily_cost:.2f} exceeds limit ${self.budget_limit:.2f}")

        return {
            "request": entry,
            "session_total": {
                "tokens": self.total_tokens.copy(),
                "cost": round(self.total_cost, 4),
            },
        }

    def get_daily_cost(self) -> float:
        """
        Get total cost for today.
        
        Performance optimization: Uses cached datetime parsing.
        """
        today = datetime.now().date()
        daily_cost = sum(
            entry["cost"]["total"]
            for entry in self.history
            if self._get_parsed_date(entry["timestamp"]).date() == today
        )
        return daily_cost

    def get_weekly_cost(self) -> float:
        """
        Get total cost for the past 7 days.
        
        Performance optimization: Uses cached datetime parsing.
        """
        week_ago = datetime.now() - timedelta(days=7)
        weekly_cost = sum(
            entry["cost"]["total"] for entry in self.history 
            if self._get_parsed_date(entry["timestamp"]) >= week_ago
        )
        return weekly_cost

    def get_monthly_cost(self) -> float:
        """
        Get total cost for the current month.
        
        Performance optimization: Uses cached datetime parsing and single comparison.
        """
        today = datetime.now()
        monthly_cost = sum(
            entry["cost"]["total"]
            for entry in self.history
            if (parsed := self._get_parsed_date(entry["timestamp"])) and
               parsed.month == today.month and parsed.year == today.year
        )
        return monthly_cost

    def get_cost_by_model(self) -> Dict[str, float]:
        """Get cost breakdown by model."""
        costs = defaultdict(float)
        for entry in self.history:
            costs[entry["model"]] += entry["cost"]["total"]
        return dict(costs)

    def get_cost_by_type(self) -> Dict[str, float]:
        """Get cost breakdown by request type."""
        costs = defaultdict(float)
        for entry in self.history:
            costs[entry["request_type"]] += entry["cost"]["total"]
        return dict(costs)

    def print_session_summary(self):
        """Print summary of current session costs."""
        print("\n" + "=" * 80)
        print("  GPT-5 Cost Tracker - Session Summary")
        print("=" * 80)
        print("\n📊 Session Statistics:")
        print(f"   Requests: {len(self.session_costs)}")
        print(f"   Input tokens: {self.total_tokens['input']:,}")
        print(f"   Cached tokens: {self.total_tokens['cached_input']:,}")
        print(f"   Output tokens: {self.total_tokens['output']:,}")
        print(f"   Total tokens: {sum(self.total_tokens.values()):,}")
        print(f"\n💰 Session Cost: ${self.total_cost:.4f}")
        print("\n📅 Period Costs:")
        print(f"   Today: ${self.get_daily_cost():.4f}")
        print(f"   This week: ${self.get_weekly_cost():.4f}")
        print(f"   This month: ${self.get_monthly_cost():.4f}")

        if self.budget_limit:
            remaining = self.budget_limit - self.get_daily_cost()
            print("\n🎯 Budget Status:")
            print(f"   Daily limit: ${self.budget_limit:.2f}")
            print(f"   Remaining: ${max(0, remaining):.2f}")

        print("=" * 80 + "\n")

    def print_detailed_report(self, days: int = 30):
        """
        Print detailed cost report.
        
        Performance optimization: Uses cached datetime parsing for filtering.
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent = [e for e in self.history if self._get_parsed_date(e["timestamp"]) >= cutoff]

        print("\n" + "=" * 80)
        print(f"  GPT-5 Cost Report - Last {days} Days")
        print("=" * 80)

        if not recent:
            print("\nNo usage data available.")
            return

        # Cost by model
        print("\n💵 Cost by Model:")
        model_costs = defaultdict(float)
        for entry in recent:
            model_costs[entry["model"]] += entry["cost"]["total"]
        for model, cost in sorted(model_costs.items(), key=lambda x: x[1], reverse=True):
            print(f"   {model}: ${cost:.4f}")

        # Cost by request type
        print("\n📝 Cost by Request Type:")
        type_costs = defaultdict(float)
        for entry in recent:
            type_costs[entry["request_type"]] += entry["cost"]["total"]
        for req_type, cost in sorted(type_costs.items(), key=lambda x: x[1], reverse=True):
            print(f"   {req_type}: ${cost:.4f}")

        # Token usage
        total_input = sum(e["tokens"]["input"] for e in recent)
        total_cached = sum(e["tokens"]["cached_input"] for e in recent)
        total_output = sum(e["tokens"]["output"] for e in recent)

        print("\n📊 Token Usage:")
        print(f"   Input tokens: {total_input:,}")
        print(f"   Cached tokens: {total_cached:,} (saves ${self._calculate_cache_savings(recent):.2f})")
        print(f"   Output tokens: {total_output:,}")
        print(f"   Total: {total_input + total_cached + total_output:,}")

        # Cost-saving recommendations
        print("\n💡 Cost-Saving Recommendations:")
        self._print_recommendations(recent)

        total_cost = sum(e["cost"]["total"] for e in recent)
        print(f"\n💰 Total Cost ({days} days): ${total_cost:.4f}")
        print("=" * 80 + "\n")

    def _calculate_cache_savings(self, entries: List[Dict]) -> float:
        """Calculate savings from cached tokens."""
        savings = 0.0
        for entry in entries:
            model_key = entry["model"].lower()
            if model_key in self.PRICING:
                pricing = self.PRICING[model_key]
                cached_tokens = entry["tokens"]["cached_input"]
                # Savings = (full price - discounted price) * tokens
                savings += (cached_tokens / 1_000_000) * (pricing["input"] - pricing["cached_input"])
        return savings

    def _print_recommendations(self, entries: List[Dict]):
        """Print cost optimization recommendations."""
        recommendations = []

        # Check if using expensive models when cheaper would work
        total_requests = len(entries)
        gpt5_requests = sum(1 for e in entries if e["model"] == "gpt-5")
        if gpt5_requests / total_requests > 0.5:
            recommendations.append("   • Consider using gpt-5-mini for simpler tasks (2-3x cheaper)")

        # Check cache usage
        total_input = sum(e["tokens"]["input"] for e in entries)
        total_cached = sum(e["tokens"]["cached_input"] for e in entries)
        if total_cached < total_input * 0.1:
            recommendations.append("   • Low cache usage detected - implement prompt caching for repeated content")

        # Check output token usage
        avg_output = sum(e["tokens"]["output"] for e in entries) / len(entries) if entries else 0
        if avg_output > 2000:
            recommendations.append("   • High output tokens - consider reducing max_completion_tokens parameter")

        # Check reasoning effort
        reasoning_requests = [e for e in entries if e["request_type"] == "reasoning"]
        if len(reasoning_requests) > total_requests * 0.3:
            recommendations.append("   • Heavy reasoning API usage - use Chat Completions for simple queries")

        if recommendations:
            for rec in recommendations:
                print(rec)
        else:
            print("   ✅ No major optimization opportunities detected")
    
    def __del__(self):
        """Ensure history is saved when tracker is destroyed."""
        try:
            self.save()
        except Exception:
            # Ignore errors during cleanup
            pass

    def export_to_csv(self, output_path: str = "output/reports/gpt5_costs.csv"):
        """Export cost history to CSV for analysis."""
        import csv

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            if not self.history:
                print("No data to export.")
                return

            fieldnames = [
                "timestamp",
                "model",
                "request_type",
                "input_tokens",
                "cached_tokens",
                "output_tokens",
                "total_tokens",
                "input_cost",
                "cached_cost",
                "output_cost",
                "total_cost",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for entry in self.history:
                writer.writerow(
                    {
                        "timestamp": entry["timestamp"],
                        "model": entry["model"],
                        "request_type": entry["request_type"],
                        "input_tokens": entry["tokens"]["input"],
                        "cached_tokens": entry["tokens"]["cached_input"],
                        "output_tokens": entry["tokens"]["output"],
                        "total_tokens": entry["tokens"]["total"],
                        "input_cost": entry["cost"]["input"],
                        "cached_cost": entry["cost"]["cached_input"],
                        "output_cost": entry["cost"]["output"],
                        "total_cost": entry["cost"]["total"],
                    }
                )

        print(f"✅ Cost data exported to {output_file}")


# Global cost tracker instance
_global_tracker: Optional[GPT5CostTracker] = None


def get_tracker(budget_limit: Optional[float] = None) -> GPT5CostTracker:
    """Get or create global cost tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = GPT5CostTracker(budget_limit=budget_limit)
    return _global_tracker


def track_gpt5_request(
    model: str,
    usage: Dict,
    request_type: str = "chat",
    metadata: Optional[Dict] = None,
) -> Dict:
    """
    Convenient function to track GPT-5 usage from response.

    Args:
        model: Model name
        usage: Usage dict from API response (contains prompt_tokens, completion_tokens)
        request_type: Type of request
        metadata: Optional metadata

    Returns:
        Cost tracking result
    """
    tracker = get_tracker()
    return tracker.track_request(
        model=model,
        prompt_tokens=usage.get("prompt_tokens", 0),
        completion_tokens=usage.get("completion_tokens", 0),
        cached_tokens=usage.get("cached_tokens", 0),
        request_type=request_type,
        metadata=metadata,
    )


# Example usage
if __name__ == "__main__":
    # Create tracker with $5 daily budget limit
    tracker = GPT5CostTracker(budget_limit=5.00)

    # Simulate some requests for demonstration
    print("Simulating GPT-5 API usage...\n")

    # Example 1: Chat completion with gpt-5
    tracker.track_request(
        model="gpt-5",
        prompt_tokens=1500,
        completion_tokens=2000,
        cached_tokens=0,
        request_type="chat",
        metadata={"task": "tax_advice"},
    )

    # Example 2: Reasoning API with gpt-5
    tracker.track_request(
        model="gpt-5",
        prompt_tokens=2500,
        completion_tokens=3500,
        cached_tokens=500,  # Some cached tokens
        request_type="reasoning",
        metadata={"task": "financial_analysis"},
    )

    # Example 3: Using gpt-5-mini (cheaper)
    tracker.track_request(
        model="gpt-5-mini",
        prompt_tokens=1000,
        completion_tokens=1500,
        cached_tokens=0,
        request_type="chat",
        metadata={"task": "client_email"},
    )

    # Print session summary
    tracker.print_session_summary()

    # Print detailed report
    tracker.print_detailed_report(days=30)

    # Export to CSV
    tracker.export_to_csv()

    print("\n📌 Usage Tips:")
    print("=" * 80)
    print("1. Always use the tracker in your GPT-5 scripts:")
    print("   from src.core.cost_tracker import track_gpt5_request")
    print("   track_gpt5_request(model='gpt-5', usage=response['usage'])")
    print()
    print("2. Set daily budget limits:")
    print("   tracker = GPT5CostTracker(budget_limit=10.00)  # $10/day")
    print()
    print("3. Use cheaper models for simple tasks:")
    print("   gpt-5-mini: 2-3x cheaper, excellent quality")
    print("   gpt-5-nano: 4-5x cheaper, good for basic tasks")
    print()
    print("4. Leverage prompt caching:")
    print("   Reuse common prompt prefixes to save 50% on input costs")
    print()
    print("5. Review reports regularly:")
    print("   tracker.print_detailed_report(days=7)")
    print("=" * 80 + "\n")
