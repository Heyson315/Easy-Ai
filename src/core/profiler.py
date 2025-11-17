"""
Performance profiling utilities for M365 Security Toolkit.

Usage:
    from src.core.profiler import profile_function, profile_script

    @profile_function
    def my_function():
        ...

    # Or profile entire script
    if __name__ == "__main__":
        profile_script(main)
"""

import cProfile
import functools
import io
import pstats
import time
from pathlib import Path
from typing import Any, Callable


def profile_function(func: Callable) -> Callable:
    """
    Decorator to profile function execution time.

    Example:
        @profile_function
        def slow_operation():
            time.sleep(1)
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time

        print(f"⏱️  {func.__name__} took {duration:.4f}s")
        return result

    return wrapper


def profile_script(func: Callable, output_file: str = None) -> None:
    """
    Profile entire script execution with detailed statistics.

    Args:
        func: Function to profile
        output_file: Optional path to save profile stats

    Example:
        if __name__ == "__main__":
            profile_script(main, "output/profiling/script_profile.txt")
    """
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        func()
    finally:
        profiler.disable()

        # Print to console
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats("cumulative")
        stats.print_stats(20)  # Top 20 functions
        print(stream.getvalue())

        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                stats = pstats.Stats(profiler, stream=f)
                stats.sort_stats("cumulative")
                stats.print_stats()
            print(f"📊 Profile saved to {output_path}")


def memory_profile(func: Callable) -> Callable:
    """
    Decorator to track memory usage (requires memory_profiler).

    Install: pip install memory-profiler

    Example:
        @memory_profile
        def memory_intensive():
            large_list = [i for i in range(1000000)]
    """
    try:
        from memory_profiler import profile as mem_profile

        return mem_profile(func)
    except ImportError:
        print("⚠️  memory-profiler not installed. Install with: pip install memory-profiler")
        return func


if __name__ == "__main__":
    # Example usage
    @profile_function
    def example_slow_function():
        """Example function to demonstrate profiling."""
        total = 0
        for i in range(1000000):
            total += i
        return total

    print("🧪 Testing profiler...")
    result = example_slow_function()
    print(f"Result: {result}")
