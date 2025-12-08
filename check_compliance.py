#!/usr/bin/env python3
"""
Check compliance status from M365 CIS audit results.
"""
import argparse
import json
import sys
from pathlib import Path


def check_compliance(json_path: Path) -> None:
    """Check and display compliance status from audit results."""
    if not json_path.exists():
        print(f"ERROR: File not found: {json_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(json_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"ERROR: Permission denied when reading {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"ERROR: Encoding error when reading {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: I/O error when reading {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(data, list):
        print(f"ERROR: Expected JSON array, got {type(data).__name__}", file=sys.stderr)
        sys.exit(1)
    
    if not data:
        print("WARNING: No audit results found", file=sys.stderr)
        return
    
    # Calculate statistics
    statuses = [c.get("Status", "Unknown") for c in data]
    passed = statuses.count("Pass")
    failed = statuses.count("Fail")
    manual = statuses.count("Manual")
    error = statuses.count("Error")
    total = len(statuses)
    
    if total == 0:
        print("WARNING: No controls to evaluate", file=sys.stderr)
        return
    
    print(f"Pass: {passed}, Fail: {failed}, Manual: {manual}, Error: {error}, Total: {total}")
    print(f"Compliance: {passed/total*100:.1f}%" if total > 0 else "Compliance: 0.0%")
    
    # Show which controls changed
    print("\n=== Control Status ===")
    for c in data:
        status = c.get("Status", "Unknown")
        control_id = c.get("ControlId", "N/A")
        title = c.get("Title", "No title")[:60]
        
        status_icon = (
            "✅" if status == "Pass" 
            else "❌" if status == "Fail" 
            else "⚠️" if status == "Manual"
            else "❓"
        )
        print(f"{status_icon} {control_id}: {title} - {status}")


def main():
    parser = argparse.ArgumentParser(description="Check M365 CIS compliance status")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("output/reports/security/m365_cis_audit_20251111_121220.json"),
        help="Path to audit JSON file"
    )
    args = parser.parse_args()
    
    check_compliance(args.input)


if __name__ == "__main__":
    main()
