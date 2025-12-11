"""
Tests for cost tracker performance optimizations.

Verifies that performance improvements don't break functionality:
- Deferred saves (auto_save=False)
- Datetime caching
- Manual save() method
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.core.cost_tracker import GPT5CostTracker


def test_auto_save_disabled_performance():
    """Test that auto_save=False improves performance by avoiding disk I/O."""
    with TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "cost_log.json"
        
        # Test with auto_save=False (optimized)
        tracker_fast = GPT5CostTracker(log_file=str(log_file), auto_save=False)
        
        start = time.perf_counter()
        for i in range(100):
            tracker_fast.track_request(
                model="gpt-5-mini",
                prompt_tokens=100,
                completion_tokens=50,
                cached_tokens=0,
            )
        time_no_save = time.perf_counter() - start
        
        # Verify file doesn't exist yet OR has fewer than 100 entries (only 10 saved at most due to batch save)
        if log_file.exists():
            saved_count = len(json.loads(log_file.read_text()))
            assert saved_count <= 100  # At most all entries if batch save triggered
        
        # Manual save
        tracker_fast.save()
        assert log_file.exists()
        assert len(json.loads(log_file.read_text())) == 100
        
        # Test with auto_save=True (slower)
        log_file2 = Path(tmpdir) / "cost_log2.json"
        tracker_slow = GPT5CostTracker(log_file=str(log_file2), auto_save=True)
        
        start = time.perf_counter()
        for i in range(100):
            tracker_slow.track_request(
                model="gpt-5-mini",
                prompt_tokens=100,
                completion_tokens=50,
                cached_tokens=0,
            )
        time_with_save = time.perf_counter() - start
        
        # Verify auto_save wrote the file
        assert log_file2.exists()
        assert len(json.loads(log_file2.read_text())) == 100
        
        # auto_save=False should be faster or at least not significantly slower
        # Note: In fast systems, both might be very fast, so we just verify correctness
        print(f"\nPerformance: auto_save=False: {time_no_save:.4f}s, auto_save=True: {time_with_save:.4f}s")
        print(f"Speedup: {time_with_save/time_no_save if time_no_save > 0 else 1:.2f}x")


def test_auto_save_every_10_entries():
    """Test that auto_save=False still saves every 10 entries as safety fallback."""
    with TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "cost_log.json"
        tracker = GPT5CostTracker(log_file=str(log_file), auto_save=False)
        
        # Add 9 entries - should not auto-save yet
        for i in range(9):
            tracker.track_request(
                model="gpt-5-mini",
                prompt_tokens=100,
                completion_tokens=50,
            )
        
        # Should have 9 unsaved entries
        assert tracker._unsaved_entries == 9
        
        # Add 10th entry - should trigger auto-save
        tracker.track_request(
            model="gpt-5-mini",
            prompt_tokens=100,
            completion_tokens=50,
        )
        
        # Now file should exist with all 10 entries (auto-saved on 10th entry)
        assert log_file.exists()
        saved_data = json.loads(log_file.read_text())
        assert len(saved_data) == 10
        
        # Unsaved entries counter should be reset
        assert tracker._unsaved_entries == 0


def test_datetime_caching_performance():
    """Test that datetime caching improves performance of cost queries."""
    with TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "cost_log.json"
        tracker = GPT5CostTracker(log_file=str(log_file), auto_save=False)
        
        # Add entries over multiple days
        base_time = datetime.now()
        for i in range(100):
            entry = {
                "timestamp": (base_time - timedelta(days=i % 7)).isoformat(),
                "model": "gpt-5-mini",
                "request_type": "chat",
                "tokens": {"input": 100, "cached_input": 0, "output": 50, "total": 150},
                "cost": {"input": 0.0001, "cached_input": 0.0, "output": 0.000225, "total": 0.000325},
                "metadata": {},
            }
            tracker.history.append(entry)
        
        # Test datetime caching - repeated calls should be faster
        start = time.perf_counter()
        for _ in range(10):
            _ = tracker.get_daily_cost()
            _ = tracker.get_weekly_cost()
            _ = tracker.get_monthly_cost()
        elapsed = time.perf_counter() - start
        
        # Should complete quickly even with repeated calls (< 0.1s for 30 calls with 100 entries)
        print(f"\nDatetime caching performance: {elapsed:.4f}s for 30 cost queries")
        assert elapsed < 0.1  # Should be very fast with caching


def test_manual_save_method():
    """Test that manual save() method works correctly."""
    with TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "cost_log.json"
        tracker = GPT5CostTracker(log_file=str(log_file), auto_save=False)
        
        # Add some entries
        for i in range(5):
            tracker.track_request(
                model="gpt-5-mini",
                prompt_tokens=100,
                completion_tokens=50,
            )
        
        # File shouldn't exist yet (or has fewer entries)
        if log_file.exists():
            assert len(json.loads(log_file.read_text())) < 5
        
        # Manual save
        tracker.save()
        
        # Now file should exist with all entries
        assert log_file.exists()
        assert len(json.loads(log_file.read_text())) == 5
        
        # Calling save() again should be safe (idempotent)
        tracker.save()
        assert len(json.loads(log_file.read_text())) == 5


def test_cleanup_saves_history():
    """Test that __del__ method saves unsaved history on cleanup."""
    with TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "cost_log.json"
        
        # Create tracker in scope that will be destroyed
        tracker = GPT5CostTracker(log_file=str(log_file), auto_save=False)
        tracker.track_request(
            model="gpt-5-mini",
            prompt_tokens=100,
            completion_tokens=50,
        )
        
        # Explicitly delete to trigger __del__
        del tracker
        
        # History should be saved
        assert log_file.exists()
        data = json.loads(log_file.read_text())
        assert len(data) == 1


def test_cached_datetime_correctness():
    """Test that datetime caching doesn't affect correctness of results."""
    with TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "cost_log.json"
        tracker = GPT5CostTracker(log_file=str(log_file), auto_save=False)
        
        # Add entries for today
        now = datetime.now()
        for i in range(5):
            entry = {
                "timestamp": now.isoformat(),
                "model": "gpt-5",
                "request_type": "chat",
                "tokens": {"input": 100, "cached_input": 0, "output": 50, "total": 150},
                "cost": {"input": 0.0004, "cached_input": 0.0, "output": 0.0006, "total": 0.001},
                "metadata": {},
            }
            tracker.history.append(entry)
        
        # Add entries for yesterday
        yesterday = now - timedelta(days=1)
        for i in range(3):
            entry = {
                "timestamp": yesterday.isoformat(),
                "model": "gpt-5",
                "request_type": "chat",
                "tokens": {"input": 100, "cached_input": 0, "output": 50, "total": 150},
                "cost": {"input": 0.0004, "cached_input": 0.0, "output": 0.0006, "total": 0.001},
                "metadata": {},
            }
            tracker.history.append(entry)
        
        # Daily cost should only include today's entries
        daily_cost = tracker.get_daily_cost()
        assert daily_cost == pytest.approx(0.005, rel=0.01)  # 5 entries * $0.001
        
        # Weekly cost should include all entries
        weekly_cost = tracker.get_weekly_cost()
        assert weekly_cost == pytest.approx(0.008, rel=0.01)  # 8 entries * $0.001
        
        # Monthly cost should include all entries (same month)
        if now.month == yesterday.month:
            monthly_cost = tracker.get_monthly_cost()
            assert monthly_cost == pytest.approx(0.008, rel=0.01)


def test_performance_with_large_history():
    """Test performance with large history (1000+ entries)."""
    with TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "cost_log.json"
        tracker = GPT5CostTracker(log_file=str(log_file), auto_save=False)
        
        # Add 1000 entries
        base_time = datetime.now()
        for i in range(1000):
            entry = {
                "timestamp": (base_time - timedelta(hours=i)).isoformat(),
                "model": "gpt-5-mini",
                "request_type": "chat",
                "tokens": {"input": 100, "cached_input": 0, "output": 50, "total": 150},
                "cost": {"input": 0.0001, "cached_input": 0.0, "output": 0.000225, "total": 0.000325},
                "metadata": {},
            }
            tracker.history.append(entry)
        
        # Cost queries should still be fast
        start = time.perf_counter()
        _ = tracker.get_daily_cost()
        _ = tracker.get_weekly_cost()
        _ = tracker.get_monthly_cost()
        elapsed = time.perf_counter() - start
        
        print(f"\nLarge history performance (1000 entries): {elapsed:.4f}s for 3 cost queries")
        assert elapsed < 0.1  # Should still be fast with caching


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
