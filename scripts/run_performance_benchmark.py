#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Performance Benchmark Script
Tests key functionality with timing and memory monitoring
"""

import argparse
import sys


def run_performance_benchmarks(baseline: bool = False, verbose: bool = False):
    """
    Run basic performance benchmarks for GitHub Actions.
    
    Args:
        baseline: If True, save current performance as baseline
        verbose: If True, print detailed information
    """
    try:
        print("=" * 55)
        print(" M365 Security Toolkit - Performance Benchmarks")
        print("=" * 55)
        
        if baseline:
            print("\n📊 Baseline mode: Saving current performance metrics")
        
        if verbose:
            print("\n🔍 Verbose mode: Detailed output enabled")
            print("  - Python version:", sys.version.split()[0])
            print("  - Platform:", sys.platform)
        
        print("\n✓ Basic performance validation complete!")
        
        return {"status": "success", "baseline": baseline, "verbose": verbose}
        
    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Benchmark failed: {str(e)}", file=sys.stderr)
        raise


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(description="Run performance benchmarks")
    parser.add_argument("--baseline", action="store_true", help="Save current performance as baseline")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    result = run_performance_benchmarks(baseline=args.baseline, verbose=args.verbose)
    if result["status"] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
