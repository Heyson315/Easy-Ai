#!/usr/bin/env python3
"""
Performance Test Runner Script
Orchestrates performance testing for the M365 Security Toolkit
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Add tests directory to path
sys.path.append(str(Path(__file__).parent / "tests"))

from test_performance import PerformanceTester, PerformanceDataManager


def run_performance_tests(test_sizes=None, output_dir=None, verbose=False):
    """Run performance tests with specified parameters"""
    
    # Set defaults
    if test_sizes is None:
        test_sizes = ["small", "medium", "large"]
    
    if output_dir is None:
        output_dir = Path(__file__).parent / "output" / "performance_testing"
    else:
        output_dir = Path(output_dir)
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 M365 Security Toolkit Performance Testing")
    print("=" * 50)
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Test sizes: {', '.join(test_sizes)}")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize performance tester
    tester = PerformanceTester(output_dir)
    
    # Run tests for each size
    with PerformanceDataManager(output_dir) as data_manager:
        for size in test_sizes:
            print(f"📈 Running {size.upper()} dataset tests...")
            
            try:
                # Create test datasets
                datasets = data_manager.create_test_datasets(size)
                
                if verbose:
                    print(f"  📋 Generated {datasets['cis_records']} CIS audit records")
                    print(f"  📋 Generated {datasets['sharepoint_records']} SharePoint permission records")
                    print(f"  📁 Test data in: {datasets['temp_dir']}")
                
                # Test CIS report generation
                print("  🔍 Testing CIS report generation...")
                cis_result = tester.test_cis_report_generation(datasets['cis_file'], datasets)
                tester.results.append(cis_result)
                
                if verbose:
                    status = "✅" if cis_result.success else "❌"
                    print(f"    {status} Time: {cis_result.execution_time:.2f}s, "
                          f"Memory: {cis_result.peak_memory_mb:.1f}MB, "
                          f"Rate: {cis_result.records_per_second:.0f} rec/sec")
                
                # Test dashboard generation
                print("  📊 Testing dashboard generation...")
                dashboard_result = tester.test_dashboard_generation(datasets['cis_file'], datasets)
                tester.results.append(dashboard_result)
                
                if verbose:
                    status = "✅" if dashboard_result.success else "❌"
                    print(f"    {status} Time: {dashboard_result.execution_time:.2f}s, "
                          f"Memory: {dashboard_result.peak_memory_mb:.1f}MB, "
                          f"Rate: {dashboard_result.records_per_second:.0f} rec/sec")
                
                # Test SharePoint processing
                print("  🔗 Testing SharePoint processing...")
                sp_result = tester.test_sharepoint_processing(datasets['sharepoint_file'], datasets)
                tester.results.append(sp_result)
                
                if verbose:
                    status = "✅" if sp_result.success else "❌"
                    print(f"    {status} Time: {sp_result.execution_time:.2f}s, "
                          f"Memory: {sp_result.peak_memory_mb:.1f}MB, "
                          f"Rate: {sp_result.records_per_second:.0f} rec/sec")
                
                print(f"  ✅ {size.upper()} tests completed successfully")
                
            except Exception as e:
                print(f"  ❌ {size.upper()} tests failed: {str(e)}")
                if verbose:
                    import traceback
                    traceback.print_exc()
    
    # Generate comprehensive report
    print("\n📊 Generating performance report...")
    report = tester.generate_performance_report()
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"performance_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Generate summary report
    summary_file = output_dir / f"performance_summary_{timestamp}.txt"
    generate_text_summary(report, summary_file, tester.results)
    
    # Print results summary
    print_summary(report, tester.results)
    
    print(f"\n📄 Detailed report: {report_file}")
    print(f"📄 Summary report: {summary_file}")
    
    return tester.results, report


def generate_text_summary(report, output_file, results):
    """Generate a human-readable text summary"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("M365 Security Toolkit - Performance Test Summary\n")
        f.write("=" * 55 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Overall summary
        f.write("OVERALL SUMMARY\n")
        f.write("-" * 15 + "\n")
        f.write(f"Total tests run: {report['summary']['total_tests']}\n")
        f.write(f"Successful tests: {report['summary']['successful_tests']}\n")
        f.write(f"Failed tests: {report['summary']['failed_tests']}\n")
        success_rate = (report['summary']['successful_tests'] / report['summary']['total_tests']) * 100
        f.write(f"Success rate: {success_rate:.1f}%\n\n")
        
        # Performance metrics by operation
        f.write("PERFORMANCE METRICS BY OPERATION\n")
        f.write("-" * 35 + "\n")
        
        for operation, sizes in report.get('operations', {}).items():
            f.write(f"\n{operation}:\n")
            for size, metrics in sizes.items():
                f.write(f"  {size.upper()} dataset:\n")
                f.write(f"    Execution time: {metrics['execution_time']:.2f} seconds\n")
                f.write(f"    Peak memory: {metrics['peak_memory_mb']:.1f} MB\n")
                f.write(f"    Processing rate: {metrics['records_per_second']:.0f} records/second\n")
                f.write(f"    Output size: {metrics['file_size_mb']:.2f} MB\n")
                f.write(f"    Success: {'Yes' if metrics['success'] else 'No'}\n")
                if not metrics['success'] and metrics['error_message']:
                    f.write(f"    Error: {metrics['error_message']}\n")
        
        # Recommendations
        f.write("\nRECOMMENDATIONS\n")
        f.write("-" * 15 + "\n")
        for i, rec in enumerate(report.get('recommendations', []), 1):
            f.write(f"{i}. {rec}\n")
        
        # Detailed results
        f.write("\nDETAILED TEST RESULTS\n")
        f.write("-" * 21 + "\n")
        
        for result in results:
            f.write(f"\nTest: {result.operation} - {result.dataset_size}\n")
            f.write(f"  Status: {'PASS' if result.success else 'FAIL'}\n")
            f.write(f"  Execution time: {result.execution_time:.3f}s\n")
            f.write(f"  Memory usage: {result.memory_usage_mb:.1f}MB\n")
            f.write(f"  Peak memory: {result.peak_memory_mb:.1f}MB\n")
            f.write(f"  CPU usage: {result.cpu_percent:.1f}%\n")
            f.write(f"  Records processed: {result.records_processed:,}\n")
            f.write(f"  Processing rate: {result.records_per_second:.0f} rec/sec\n")
            f.write(f"  Output file size: {result.file_size_mb:.2f}MB\n")
            if not result.success:
                f.write(f"  Error: {result.error_message}\n")


def print_summary(report, results):
    """Print a summary to console"""
    print("\n" + "=" * 55)
    print("📋 PERFORMANCE TEST SUMMARY")
    print("=" * 55)
    
    # Overall stats
    total_tests = report['summary']['total_tests']
    successful = report['summary']['successful_tests']
    failed = report['summary']['failed_tests']
    success_rate = (successful / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"✅ Tests completed: {successful}/{total_tests} ({success_rate:.1f}% success)")
    if failed > 0:
        print(f"❌ Failed tests: {failed}")
    
    # Performance highlights
    print("\n🏃 PERFORMANCE HIGHLIGHTS")
    print("-" * 25)
    
    # Find fastest and slowest operations
    successful_results = [r for r in results if r.success]
    if successful_results:
        fastest = min(successful_results, key=lambda x: x.execution_time)
        slowest = max(successful_results, key=lambda x: x.execution_time)
        
        print(f"⚡ Fastest: {fastest.operation} ({fastest.dataset_size}) - {fastest.execution_time:.2f}s")
        print(f"🐌 Slowest: {slowest.operation} ({slowest.dataset_size}) - {slowest.execution_time:.2f}s")
        
        # Memory usage
        lowest_memory = min(successful_results, key=lambda x: x.peak_memory_mb)
        highest_memory = max(successful_results, key=lambda x: x.peak_memory_mb)
        
        print(f"💾 Lowest memory: {lowest_memory.operation} ({lowest_memory.dataset_size}) - {lowest_memory.peak_memory_mb:.1f}MB")
        print(f"💾 Highest memory: {highest_memory.operation} ({highest_memory.dataset_size}) - {highest_memory.peak_memory_mb:.1f}MB")
    
    # Recommendations
    recommendations = report.get('recommendations', [])
    if recommendations:
        print("\n💡 RECOMMENDATIONS")
        print("-" * 17)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")


def main():
    """Main entry point for performance testing"""
    parser = argparse.ArgumentParser(
        description="Performance testing for M365 Security Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_performance_tests.py                    # Run all tests
  python run_performance_tests.py --sizes small     # Run only small dataset tests
  python run_performance_tests.py --verbose         # Show detailed output
  python run_performance_tests.py --output ./perf   # Custom output directory
        """
    )
    
    parser.add_argument(
        '--sizes',
        nargs='+',
        choices=['small', 'medium', 'large', 'xlarge'],
        default=['small', 'medium', 'large'],
        help='Dataset sizes to test (default: small medium large)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output directory for test results'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output during testing'
    )
    
    args = parser.parse_args()
    
    try:
        results, report = run_performance_tests(
            test_sizes=args.sizes,
            output_dir=args.output,
            verbose=args.verbose
        )
        
        # Exit with error code if any tests failed
        failed_tests = sum(1 for r in results if not r.success)
        sys.exit(1 if failed_tests > 0 else 0)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Performance testing failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()