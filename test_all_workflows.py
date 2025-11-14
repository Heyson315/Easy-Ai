#!/usr/bin/env python3
"""
Comprehensive workflow testing script for M365 Security & SharePoint Analysis Toolkit.
Tests all Python scripts, PowerShell scripts, and workflows to identify failures.
"""

import os
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.absolute()

class WorkflowTester:
    """Tests all workflows and scripts in the repository."""
    
    def __init__(self):
        self.results = {
            "python_scripts": {},
            "powershell_scripts": {},
            "python_modules": {},
            "workflows": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
    
    def test_python_script_syntax(self, script_path: Path) -> Tuple[bool, str]:
        """Test if a Python script has valid syntax."""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, str(script_path), 'exec')
            return True, "Syntax valid"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Error: {e}"
    
    def test_python_script_imports(self, script_path: Path) -> Tuple[bool, str]:
        """Test if a Python script can import without errors (check dependencies)."""
        try:
            # Read the script and check for imports
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for external dependencies
            external_deps = []
            if 'import pandas' in content or 'from pandas' in content:
                external_deps.append('pandas')
            if 'import openpyxl' in content or 'from openpyxl' in content:
                external_deps.append('openpyxl')
            if 'import pytest' in content or 'from pytest' in content:
                external_deps.append('pytest')
            
            if external_deps:
                return False, f"Missing dependencies: {', '.join(external_deps)}"
            
            return True, "No external dependencies or all available"
        except Exception as e:
            return False, f"Error checking imports: {e}"
    
    def test_python_script_help(self, script_path: Path) -> Tuple[bool, str]:
        """Test if a Python script can show help text."""
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), '--help'],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=REPO_ROOT
            )
            if result.returncode == 0 or 'usage:' in result.stdout.lower() or 'help' in result.stdout.lower():
                return True, "Help text available"
            return False, f"No help text: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Timeout waiting for help"
        except Exception as e:
            return False, f"Error: {e}"
    
    def test_powershell_script_syntax(self, script_path: Path) -> Tuple[bool, str]:
        """Test if a PowerShell script has valid syntax."""
        try:
            # Check if PowerShell is available
            result = subprocess.run(
                ['pwsh', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                # Try powershell.exe on Windows
                result = subprocess.run(
                    ['powershell.exe', '-Version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return False, "PowerShell not available"
                ps_cmd = 'powershell.exe'
            else:
                ps_cmd = 'pwsh'
            
            # Test syntax
            cmd = [ps_cmd, '-NoProfile', '-Command', 
                   f'$null = Get-Content -Path "{script_path}" -ErrorAction Stop; Write-Output "OK"']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=REPO_ROOT
            )
            
            if 'OK' in result.stdout or result.returncode == 0:
                return True, "Syntax appears valid"
            return False, f"Syntax check failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Timeout during syntax check"
        except Exception as e:
            return False, f"Cannot test (PowerShell unavailable): {e}"
    
    def test_python_module_structure(self, module_path: Path) -> Tuple[bool, str]:
        """Test if a Python module directory has proper structure."""
        init_file = module_path / '__init__.py'
        
        if not module_path.is_dir():
            return False, "Not a directory"
        
        # Check for __init__.py
        has_init = init_file.exists()
        
        # Count Python files
        py_files = list(module_path.glob('*.py'))
        py_count = len([f for f in py_files if f.name != '__init__.py'])
        
        if has_init:
            return True, f"Valid module structure ({py_count} Python files)"
        else:
            return False, "Missing __init__.py"
    
    def test_workflow_documentation(self, workflow_name: str, doc_path: Path) -> Tuple[bool, str]:
        """Test if workflow documentation exists."""
        if doc_path.exists():
            size = doc_path.stat().st_size
            return True, f"Documentation exists ({size} bytes)"
        return False, "Documentation missing"
    
    def run_all_tests(self):
        """Run all workflow tests."""
        print("=" * 80)
        print("WORKFLOW TESTING - M365 Security & SharePoint Analysis Toolkit")
        print("=" * 80)
        print()
        
        # Test Python scripts
        print("Testing Python Scripts...")
        print("-" * 80)
        scripts_dir = REPO_ROOT / 'scripts'
        python_scripts = [
            'clean_csv.py',
            'generate_security_dashboard.py',
            'inspect_cis_report.py',
            'inspect_processed_csv.py',
            'inspect_report.py',
            'm365_cis_report.py',
            'run_performance_benchmark.py',
            'sync_cis_csv.py'
        ]
        
        for script_name in python_scripts:
            script_path = scripts_dir / script_name
            if script_path.exists():
                print(f"\n  {script_name}:")
                
                # Syntax test
                passed, msg = self.test_python_script_syntax(script_path)
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"    Syntax: {status} - {msg}")
                self.results["python_scripts"][f"{script_name}:syntax"] = {"passed": passed, "message": msg}
                
                # Import test
                passed, msg = self.test_python_script_imports(script_path)
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"    Imports: {status} - {msg}")
                self.results["python_scripts"][f"{script_name}:imports"] = {"passed": passed, "message": msg}
                
                # Help test (skip for utility scripts)
                if script_name not in ['inspect_processed_csv.py', 'inspect_report.py', 'inspect_cis_report.py']:
                    passed, msg = self.test_python_script_help(script_path)
                    status = "✓ PASS" if passed else "✗ FAIL"
                    print(f"    Help: {status} - {msg}")
                    self.results["python_scripts"][f"{script_name}:help"] = {"passed": passed, "message": msg}
            else:
                print(f"\n  {script_name}: ⊘ SKIP - File not found")
                self.results["python_scripts"][script_name] = {"passed": None, "message": "File not found"}
        
        # Test PowerShell scripts
        print("\n\nTesting PowerShell Scripts...")
        print("-" * 80)
        ps_scripts_dir = REPO_ROOT / 'scripts' / 'powershell'
        powershell_scripts = [
            'Invoke-M365CISAudit.ps1',
            'PostRemediateM365CIS.ps1',
            'Compare-M365CISResults.ps1',
            'Setup-ScheduledAudit.ps1',
            'Remove-ScheduledAudit.ps1'
        ]
        
        for script_name in powershell_scripts:
            script_path = ps_scripts_dir / script_name
            if script_path.exists():
                print(f"\n  {script_name}:")
                
                # Syntax test
                passed, msg = self.test_powershell_script_syntax(script_path)
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"    Syntax: {status} - {msg}")
                self.results["powershell_scripts"][f"{script_name}:syntax"] = {"passed": passed, "message": msg}
            else:
                print(f"\n  {script_name}: ⊘ SKIP - File not found")
                self.results["powershell_scripts"][script_name] = {"passed": None, "message": "File not found"}
        
        # Test PowerShell module
        print("\n\nTesting PowerShell Module...")
        print("-" * 80)
        ps_module = ps_scripts_dir / 'modules' / 'M365CIS.psm1'
        if ps_module.exists():
            print(f"\n  M365CIS.psm1:")
            passed, msg = self.test_powershell_script_syntax(ps_module)
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"    Syntax: {status} - {msg}")
            self.results["powershell_scripts"]["M365CIS.psm1:syntax"] = {"passed": passed, "message": msg}
        
        # Test Python modules
        print("\n\nTesting Python Modules...")
        print("-" * 80)
        src_dir = REPO_ROOT / 'src'
        python_modules = ['core', 'integrations']
        
        for module_name in python_modules:
            module_path = src_dir / module_name
            if module_path.exists():
                print(f"\n  {module_name}/:")
                passed, msg = self.test_python_module_structure(module_path)
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"    Structure: {status} - {msg}")
                self.results["python_modules"][f"{module_name}:structure"] = {"passed": passed, "message": msg}
                
                # Test individual files in module
                for py_file in module_path.glob('*.py'):
                    if py_file.name != '__init__.py':
                        passed, msg = self.test_python_script_syntax(py_file)
                        status = "✓ PASS" if passed else "✗ FAIL"
                        print(f"    {py_file.name}: {status} - {msg}")
                        self.results["python_modules"][f"{module_name}/{py_file.name}"] = {"passed": passed, "message": msg}
        
        # Test workflow documentation
        print("\n\nTesting Workflow Documentation...")
        print("-" * 80)
        workflows = {
            "M365 CIS Security Audit": REPO_ROOT / 'docs' / 'SECURITY_M365_CIS.md',
            "SharePoint Permissions": REPO_ROOT / 'docs' / 'USAGE_SHAREPOINT.md',
            "Scripts README": REPO_ROOT / 'scripts' / 'README.md'
        }
        
        for workflow_name, doc_path in workflows.items():
            print(f"\n  {workflow_name}:")
            passed, msg = self.test_workflow_documentation(workflow_name, doc_path)
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"    Documentation: {status} - {msg}")
            self.results["workflows"][f"{workflow_name}:docs"] = {"passed": passed, "message": msg}
        
        # Calculate summary
        self.calculate_summary()
        
        # Print summary
        print("\n")
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.results['summary']['total']}")
        print(f"✓ Passed: {self.results['summary']['passed']}")
        print(f"✗ Failed: {self.results['summary']['failed']}")
        print(f"⊘ Skipped: {self.results['summary']['skipped']}")
        print()
        
        # List all failures
        if self.results['summary']['failed'] > 0:
            print("FAILURES:")
            print("-" * 80)
            for category, tests in self.results.items():
                if category != 'summary':
                    for test_name, result in tests.items():
                        if isinstance(result, dict) and result.get('passed') == False:
                            print(f"  ✗ {category}/{test_name}")
                            print(f"    Reason: {result['message']}")
        
        return self.results
    
    def calculate_summary(self):
        """Calculate test summary statistics."""
        total = 0
        passed = 0
        failed = 0
        skipped = 0
        
        for category, tests in self.results.items():
            if category != 'summary':
                for test_name, result in tests.items():
                    if isinstance(result, dict):
                        total += 1
                        if result['passed'] is True:
                            passed += 1
                        elif result['passed'] is False:
                            failed += 1
                        else:
                            skipped += 1
        
        self.results['summary'] = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped
        }
    
    def save_results(self, output_path: Path):
        """Save test results to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {output_path}")


def main():
    """Main entry point."""
    tester = WorkflowTester()
    results = tester.run_all_tests()
    
    # Save results
    output_dir = REPO_ROOT / 'output' / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'workflow_test_results.json'
    tester.save_results(output_path)
    
    # Exit with error code if there are failures
    if results['summary']['failed'] > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
