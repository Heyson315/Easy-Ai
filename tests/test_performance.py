"""
Performance Testing Framework for M365 Security Toolkit
Tests dashboard generation and audit processing performance with various dataset sizes
"""

import time
import psutil
import json
import sys
import statistics
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

# Import our test data generators
from performance_data_generators import PerformanceDataManager

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Note: Actual script imports would be used in production
# For testing, we simulate the workloads


@dataclass
class PerformanceMetrics:
    """Container for performance measurement results"""
    operation: str
    dataset_size: str
    execution_time: float
    memory_usage_mb: float
    peak_memory_mb: float
    cpu_percent: float
    file_size_mb: float
    records_processed: int
    records_per_second: float
    success: bool
    error_message: str = ""


class PerformanceMonitor:
    """Monitor system resources during test execution"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_memory = 0
        self.peak_memory = 0
        self.start_time = 0
        self.cpu_samples = []
    
    @contextmanager
    def monitor(self):
        """Context manager for monitoring performance"""
        # Initial measurements
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.start_memory
        self.cpu_samples = []
        
        try:
            yield self
        finally:
            pass
    
    def sample(self):
        """Take a performance sample"""
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = max(self.peak_memory, current_memory)
        
        try:
            cpu_percent = self.process.cpu_percent()
            self.cpu_samples.append(cpu_percent)
        except psutil.AccessDenied:
            # Fallback if we can't access CPU info
            self.cpu_samples.append(0)
    
    def get_metrics(self) -> Tuple[float, float, float, float]:
        """Get final metrics: execution_time, memory_usage, peak_memory, avg_cpu"""
        execution_time = time.time() - self.start_time
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = current_memory - self.start_memory
        avg_cpu = statistics.mean(self.cpu_samples) if self.cpu_samples else 0
        
        return execution_time, memory_usage, self.peak_memory, avg_cpu


class PerformanceTester:
    """Main performance testing class"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[PerformanceMetrics] = []
    
    def test_cis_report_generation(self, cis_file: Path, dataset_info: Dict) -> PerformanceMetrics:
        """Test CIS report generation performance"""
        monitor = PerformanceMonitor()
        
        with monitor.monitor():
            try:
                # Create output file path
                output_file = self.output_dir / f"cis_report_{dataset_info['dataset_size']}.xlsx"
                
                # Read and process the JSON file
                with open(cis_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                monitor.sample()
                
                # Simulate data processing (grouping, aggregation, etc.)
                processed_data = self._simulate_cis_processing(data)
                
                monitor.sample()
                
                # Simulate Excel generation
                self._simulate_excel_generation(output_file, processed_data)
                
                monitor.sample()
                
                execution_time, memory_usage, peak_memory, avg_cpu = monitor.get_metrics()
                
                # Calculate metrics
                file_size_mb = output_file.stat().st_size / 1024 / 1024 if output_file.exists() else 0
                records_processed = len(data)
                records_per_second = records_processed / execution_time if execution_time > 0 else 0
                
                return PerformanceMetrics(
                    operation="CIS Report Generation",
                    dataset_size=dataset_info['dataset_size'],
                    execution_time=execution_time,
                    memory_usage_mb=memory_usage,
                    peak_memory_mb=peak_memory,
                    cpu_percent=avg_cpu,
                    file_size_mb=file_size_mb,
                    records_processed=records_processed,
                    records_per_second=records_per_second,
                    success=True
                )
                
            except Exception as e:
                execution_time, memory_usage, peak_memory, avg_cpu = monitor.get_metrics()
                return PerformanceMetrics(
                    operation="CIS Report Generation",
                    dataset_size=dataset_info['dataset_size'],
                    execution_time=execution_time,
                    memory_usage_mb=memory_usage,
                    peak_memory_mb=peak_memory,
                    cpu_percent=avg_cpu,
                    file_size_mb=0,
                    records_processed=0,
                    records_per_second=0,
                    success=False,
                    error_message=str(e)
                )
    
    def test_dashboard_generation(self, cis_file: Path, dataset_info: Dict) -> PerformanceMetrics:
        """Test security dashboard generation performance"""
        monitor = PerformanceMonitor()
        
        with monitor.monitor():
            try:
                # Create output file path
                output_file = self.output_dir / f"dashboard_{dataset_info['dataset_size']}.html"
                
                monitor.sample()
                
                # Read and process the JSON file
                with open(cis_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                monitor.sample()
                
                # Simulate dashboard data processing
                dashboard_data = self._simulate_dashboard_processing(data)
                
                monitor.sample()
                
                # Simulate HTML generation
                self._simulate_html_generation(output_file, dashboard_data)
                
                monitor.sample()
                
                execution_time, memory_usage, peak_memory, avg_cpu = monitor.get_metrics()
                
                # Calculate metrics
                file_size_mb = output_file.stat().st_size / 1024 / 1024 if output_file.exists() else 0
                records_processed = len(data)
                records_per_second = records_processed / execution_time if execution_time > 0 else 0
                
                return PerformanceMetrics(
                    operation="Dashboard Generation",
                    dataset_size=dataset_info['dataset_size'],
                    execution_time=execution_time,
                    memory_usage_mb=memory_usage,
                    peak_memory_mb=peak_memory,
                    cpu_percent=avg_cpu,
                    file_size_mb=file_size_mb,
                    records_processed=records_processed,
                    records_per_second=records_per_second,
                    success=True
                )
                
            except Exception as e:
                execution_time, memory_usage, peak_memory, avg_cpu = monitor.get_metrics()
                return PerformanceMetrics(
                    operation="Dashboard Generation",
                    dataset_size=dataset_info['dataset_size'],
                    execution_time=execution_time,
                    memory_usage_mb=memory_usage,
                    peak_memory_mb=peak_memory,
                    cpu_percent=avg_cpu,
                    file_size_mb=0,
                    records_processed=0,
                    records_per_second=0,
                    success=False,
                    error_message=str(e)
                )
    
    def test_sharepoint_processing(self, sp_file: Path, dataset_info: Dict) -> PerformanceMetrics:
        """Test SharePoint permissions processing performance"""
        monitor = PerformanceMonitor()
        
        with monitor.monitor():
            try:
                # Create output file path
                output_file = self.output_dir / f"sharepoint_report_{dataset_info['dataset_size']}.xlsx"
                
                monitor.sample()
                
                # Simulate CSV reading and processing
                import pandas as pd
                df = pd.read_csv(sp_file)
                
                monitor.sample()
                
                # Simulate data processing (grouping, aggregation, etc.)
                processed_data = self._simulate_sharepoint_processing(df)
                
                monitor.sample()
                
                # Simulate Excel generation
                self._simulate_excel_generation(output_file, processed_data)
                
                monitor.sample()
                
                execution_time, memory_usage, peak_memory, avg_cpu = monitor.get_metrics()
                
                # Calculate metrics
                file_size_mb = output_file.stat().st_size / 1024 / 1024 if output_file.exists() else 0
                records_processed = len(df)
                records_per_second = records_processed / execution_time if execution_time > 0 else 0
                
                return PerformanceMetrics(
                    operation="SharePoint Processing",
                    dataset_size=dataset_info['dataset_size'],
                    execution_time=execution_time,
                    memory_usage_mb=memory_usage,
                    peak_memory_mb=peak_memory,
                    cpu_percent=avg_cpu,
                    file_size_mb=file_size_mb,
                    records_processed=records_processed,
                    records_per_second=records_per_second,
                    success=True
                )
                
            except Exception as e:
                execution_time, memory_usage, peak_memory, avg_cpu = monitor.get_metrics()
                return PerformanceMetrics(
                    operation="SharePoint Processing",
                    dataset_size=dataset_info['dataset_size'],
                    execution_time=execution_time,
                    memory_usage_mb=memory_usage,
                    peak_memory_mb=peak_memory,
                    cpu_percent=avg_cpu,
                    file_size_mb=0,
                    records_processed=0,
                    records_per_second=0,
                    success=False,
                    error_message=str(e)
                )
    
    def _simulate_cis_processing(self, data: List[Dict]) -> Dict:
        """Simulate CIS data processing workload"""
        # Simulate grouping by status
        status_groups = {}
        for record in data:
            status = record.get('Status', 'Unknown')
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(record)
        
        # Simulate some computation delay
        time.sleep(0.001 * len(data))  # 1ms per record
        
        return status_groups
    
    def _simulate_dashboard_processing(self, data: List[Dict]) -> Dict:
        """Simulate dashboard data processing workload"""
        # Simulate trend analysis
        timeline = {}
        for record in data:
            date = record.get('Timestamp', '')[:10]  # Extract date
            if date not in timeline:
                timeline[date] = {'pass': 0, 'fail': 0, 'manual': 0}
            
            status = record.get('Status', '').lower()
            if status in timeline[date]:
                timeline[date][status] += 1
        
        # Simulate computation delay
        time.sleep(0.002 * len(data))  # 2ms per record
        
        return timeline
    
    def _simulate_sharepoint_processing(self, df) -> Dict:
        """Simulate SharePoint data processing workload"""
        # Simulate grouping operations
        site_summary = df.groupby('Site Name').size().to_dict()
        permission_summary = df.groupby('Permission Level').size().to_dict()
        
        # Simulate computation delay
        time.sleep(0.001 * len(df))  # 1ms per record
        
        return {'sites': site_summary, 'permissions': permission_summary}
    
    def _simulate_excel_generation(self, output_file: Path, data: Dict):
        """Simulate Excel file generation"""
        # Create a simple file to represent the output
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Simulate Excel generation delay
        time.sleep(0.1)  # 100ms base delay
    
    def _simulate_html_generation(self, output_file: Path, data: Dict):
        """Simulate HTML file generation"""
        # Create a simple HTML file
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Performance Test Dashboard</title></head>
        <body>
            <h1>Security Dashboard</h1>
            <pre>{json.dumps(data, indent=2)}</pre>
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        # Simulate HTML generation delay
        time.sleep(0.05)  # 50ms base delay
    
    def run_comprehensive_test(self) -> List[PerformanceMetrics]:
        """Run comprehensive performance tests across all dataset sizes"""
        dataset_sizes = ["small", "medium", "large"]
        
        print("🚀 Starting Comprehensive Performance Testing...")
        print("=" * 60)
        
        with PerformanceDataManager(self.output_dir) as data_manager:
            for size in dataset_sizes:
                print(f"\n📊 Testing with {size.upper()} dataset...")
                
                # Create test datasets
                datasets = data_manager.create_test_datasets(size)
                
                print(f"  Generated {datasets['cis_records']} CIS records")
                print(f"  Generated {datasets['sharepoint_records']} SharePoint records")
                
                # Test CIS report generation
                print("  🔍 Testing CIS report generation...")
                cis_metrics = self.test_cis_report_generation(datasets['cis_file'], datasets)
                self.results.append(cis_metrics)
                
                # Test dashboard generation
                print("  📈 Testing dashboard generation...")
                dashboard_metrics = self.test_dashboard_generation(datasets['cis_file'], datasets)
                self.results.append(dashboard_metrics)
                
                # Test SharePoint processing
                print("  🔗 Testing SharePoint processing...")
                sp_metrics = self.test_sharepoint_processing(datasets['sharepoint_file'], datasets)
                self.results.append(sp_metrics)
                
                print(f"  ✅ {size.upper()} dataset tests completed")
        
        print("\n🎯 Performance testing completed!")
        return self.results
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report"""
        if not self.results:
            return {"error": "No performance data available"}
        
        # Organize results by operation and dataset size
        report = {
            "summary": {
                "total_tests": len(self.results),
                "successful_tests": sum(1 for r in self.results if r.success),
                "failed_tests": sum(1 for r in self.results if not r.success)
            },
            "operations": {},
            "recommendations": []
        }
        
        # Group results by operation
        for result in self.results:
            op = result.operation
            if op not in report["operations"]:
                report["operations"][op] = {}
            
            report["operations"][op][result.dataset_size] = {
                "execution_time": result.execution_time,
                "memory_usage_mb": result.memory_usage_mb,
                "peak_memory_mb": result.peak_memory_mb,
                "cpu_percent": result.cpu_percent,
                "file_size_mb": result.file_size_mb,
                "records_processed": result.records_processed,
                "records_per_second": result.records_per_second,
                "success": result.success,
                "error_message": result.error_message
            }
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations()
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Analyze execution times
        slow_operations = [r for r in self.results if r.execution_time > 10.0]
        if slow_operations:
            recommendations.append(
                f"⚠️ {len(slow_operations)} operations took >10 seconds. "
                "Consider optimizing data processing algorithms."
            )
        
        # Analyze memory usage
        high_memory = [r for r in self.results if r.peak_memory_mb > 500]
        if high_memory:
            recommendations.append(
                f"⚠️ {len(high_memory)} operations used >500MB memory. "
                "Consider streaming data processing for large datasets."
            )
        
        # Analyze failure rates
        failed_tests = [r for r in self.results if not r.success]
        if failed_tests:
            recommendations.append(
                f"❌ {len(failed_tests)} tests failed. "
                "Review error handling and resource limits."
            )
        
        if not recommendations:
            recommendations.append("✅ All performance metrics are within acceptable ranges.")
        
        return recommendations


def main():
    """Main performance testing entry point"""
    # Set up output directory
    output_dir = Path(__file__).parent.parent / "output" / "performance_testing"
    
    # Run performance tests
    tester = PerformanceTester(output_dir)
    results = tester.run_comprehensive_test()
    
    # Generate and save report
    report = tester.generate_performance_report()
    
    # Save detailed results
    report_file = output_dir / "performance_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 PERFORMANCE TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Total tests: {report['summary']['total_tests']}")
    print(f"✅ Successful: {report['summary']['successful_tests']}")
    print(f"❌ Failed: {report['summary']['failed_tests']}")
    
    print("\n🔍 RECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return results


if __name__ == "__main__":
    main()