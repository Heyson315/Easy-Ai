"""
Simple Performance Benchmark Script
Tests key functionality with timing and memory monitoring
"""

import time
import json
import csv
import sys
import psutil
from pathlib import Path
from datetime import datetime
import tempfile

# Add src to path
sys.path.append(str(Path(__file__).parent))


def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def benchmark_json_processing(num_records=1000):
    """Benchmark JSON data processing"""
    print(f"🔍 Benchmarking JSON processing with {num_records:,} records...")
    
    # Generate test data
    start_memory = get_memory_usage()
    start_time = time.time()
    
    # Create synthetic CIS audit data
    test_data = []
    for i in range(num_records):
        record = {
            "ControlId": f"1.{i % 10}.{i % 5}",
            "Title": f"Test Control {i}",
            "Status": ["Pass", "Fail", "Manual"][i % 3],
            "Severity": ["Critical", "High", "Medium", "Low"][i % 4],
            "Timestamp": datetime.now().isoformat(),
            "Evidence": f"Test evidence for control {i}" * 5  # Make it realistic size
        }
        test_data.append(record)
    
    generation_time = time.time() - start_time
    generation_memory = get_memory_usage() - start_memory
    
    # Test JSON serialization
    json_start = time.time()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, indent=2)
        json_file = f.name
    
    json_time = time.time() - json_start
    
    # Test JSON deserialization
    parse_start = time.time()
    with open(json_file, 'r') as f:
        json.load(f)  # Load and validate JSON structure
    parse_time = time.time() - parse_start
    
    # Cleanup
    Path(json_file).unlink()
    
    total_time = time.time() - start_time
    peak_memory = get_memory_usage()
    
    return {
        "records": num_records,
        "generation_time": generation_time,
        "json_write_time": json_time,
        "json_read_time": parse_time,
        "total_time": total_time,
        "memory_used_mb": generation_memory,
        "peak_memory_mb": peak_memory - start_memory,
        "records_per_second": num_records / total_time if total_time > 0 else 0
    }


def benchmark_csv_processing(num_records=1000):
    """Benchmark CSV data processing"""
    print(f"📊 Benchmarking CSV processing with {num_records:,} records...")
    
    start_memory = get_memory_usage()
    start_time = time.time()
    
    # Create synthetic SharePoint permissions data
    headers = ["Site Name", "Site URL", "Principal Name", "Permission Level", "Granted Through"]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i in range(num_records):
            row = [
                f"Site-{i:04d}",
                f"https://contoso.sharepoint.com/sites/site{i}",
                f"user{i}@contoso.com",
                ["Full Control", "Edit", "Read"][i % 3],
                ["Direct", "Group", "Inheritance"][i % 3]
            ]
            writer.writerow(row)
        
        csv_file = f.name
    
    write_time = time.time() - start_time
    
    # Test CSV reading
    read_start = time.time()
    rows_read = 0
    with open(csv_file, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            rows_read += 1
    
    read_time = time.time() - read_start
    
    # Cleanup
    Path(csv_file).unlink()
    
    total_time = time.time() - start_time
    peak_memory = get_memory_usage() - start_memory
    
    return {
        "records": num_records,
        "csv_write_time": write_time,
        "csv_read_time": read_time,
        "total_time": total_time,
        "peak_memory_mb": peak_memory,
        "records_per_second": num_records / total_time if total_time > 0 else 0
    }


def benchmark_excel_simulation(num_records=1000):
    """Simulate Excel generation workload"""
    print(f"📈 Benchmarking Excel simulation with {num_records:,} records...")
    
    start_memory = get_memory_usage()
    start_time = time.time()
    
    # Simulate data processing for Excel
    data_groups = {}
    for i in range(num_records):
        category = f"Category-{i % 10}"
        if category not in data_groups:
            data_groups[category] = []
        
        data_groups[category].append({
            "id": i,
            "value": i * 1.5,
            "status": ["Active", "Inactive", "Pending"][i % 3]
        })
    
    processing_time = time.time() - start_time
    
    # Simulate Excel workbook creation (using JSON as placeholder)
    excel_start = time.time()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Simulate multiple worksheets
        workbook_data = {
            "Summary": {"total_records": num_records, "categories": len(data_groups)},
            "Details": data_groups,
            "Charts": {"chart_data": list(range(0, num_records, max(1, num_records // 100)))}
        }
        json.dump(workbook_data, f, indent=2)
        excel_file = f.name
    
    excel_time = time.time() - excel_start
    
    # Cleanup
    Path(excel_file).unlink()
    
    total_time = time.time() - start_time
    peak_memory = get_memory_usage() - start_memory
    
    return {
        "records": num_records,
        "data_processing_time": processing_time,
        "excel_generation_time": excel_time,
        "total_time": total_time,
        "peak_memory_mb": peak_memory,
        "categories_created": len(data_groups),
        "records_per_second": num_records / total_time if total_time > 0 else 0
    }


def run_performance_benchmarks():
    """Run all performance benchmarks"""
    print("🚀 M365 Security Toolkit - Performance Benchmarks")
    print("=" * 55)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💻 System: Python {sys.version.split()[0]}, {psutil.cpu_count()} CPUs")
    print()
    
    # Test different dataset sizes
    test_sizes = [100, 1000, 5000]
    results = {}
    
    for size in test_sizes:
        print(f"📊 Testing with {size:,} records...")
        print("-" * 30)
        
        try:
            # JSON processing benchmark
            json_result = benchmark_json_processing(size)
            print(f"  ✅ JSON: {json_result['total_time']:.2f}s, "
                  f"{json_result['peak_memory_mb']:.1f}MB, "
                  f"{json_result['records_per_second']:.0f} rec/sec")
            
            # CSV processing benchmark
            csv_result = benchmark_csv_processing(size)
            print(f"  ✅ CSV: {csv_result['total_time']:.2f}s, "
                  f"{csv_result['peak_memory_mb']:.1f}MB, "
                  f"{csv_result['records_per_second']:.0f} rec/sec")
            
            # Excel simulation benchmark
            excel_result = benchmark_excel_simulation(size)
            print(f"  ✅ Excel: {excel_result['total_time']:.2f}s, "
                  f"{excel_result['peak_memory_mb']:.1f}MB, "
                  f"{excel_result['records_per_second']:.0f} rec/sec")
            
            results[size] = {
                "json": json_result,
                "csv": csv_result,
                "excel": excel_result
            }
            
        except Exception as e:
            print(f"  ❌ Error testing {size} records: {str(e)}")
        
        print()
    
    # Generate summary
    print("📋 PERFORMANCE SUMMARY")
    print("=" * 25)
    
    # Find best and worst performers
    all_results = []
    for size, tests in results.items():
        for test_type, result in tests.items():
            all_results.append({
                "size": size,
                "type": test_type,
                "time": result["total_time"],
                "memory": result["peak_memory_mb"],
                "rate": result["records_per_second"]
            })
    
    if all_results:
        fastest = min(all_results, key=lambda x: x["time"])
        slowest = max(all_results, key=lambda x: x["time"])
        most_efficient = max(all_results, key=lambda x: x["rate"])
        
        print(f"⚡ Fastest: {fastest['type'].upper()} with {fastest['size']:,} records - {fastest['time']:.2f}s")
        print(f"🐌 Slowest: {slowest['type'].upper()} with {slowest['size']:,} records - {slowest['time']:.2f}s")
        print(f"🏆 Most efficient: {most_efficient['type'].upper()} - {most_efficient['rate']:.0f} rec/sec")
        
        # Memory analysis
        high_memory = [r for r in all_results if r["memory"] > 50]
        if high_memory:
            print(f"⚠️ High memory usage detected in {len(high_memory)} tests (>50MB)")
        else:
            print("✅ All tests completed within reasonable memory limits")
    
    # Save results
    output_dir = Path(__file__).parent / "output" / "performance_testing"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"benchmark_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "total_memory_gb": psutil.virtual_memory().total / (1024**3)
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    print("\n🎯 Benchmark completed successfully!")
    
    return results


if __name__ == "__main__":
    try:
        run_performance_benchmarks()
    except KeyboardInterrupt:
        print("\n\n⚠️ Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {str(e)}")
        sys.exit(1)