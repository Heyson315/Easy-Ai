import argparse
import json
import sys
from pathlib import Path

def analyze_compliance(report_path: Path):
    """
    Analyzes the compliance from a JSON audit report.

    Args:
        report_path: The path to the JSON audit report.
    """
    if not report_path.exists():
        print(f"Error: Report file not found at {report_path}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(report_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {report_path}: {e}", file=sys.stderr)
        sys.exit(1)

    statuses = [c.get("Status", "Unknown") for c in data]
    passed = statuses.count("Pass")
    failed = statuses.count("Fail")
    manual = statuses.count("Manual")
    total = len(statuses)

    print(f"Pass: {passed}, Fail: {failed}, Manual: {manual}, Total: {total}")
    if total > 0:
        compliance_score = (passed / total) * 100
        print(f"Compliance: {compliance_score:.1f}%")
    else:
        print("Compliance: N/A (no controls found)")

    # Show which controls changed
    print("\n=== Control Status ===")
    for c in data:
        status = c.get("Status", "Unknown")
        status_icon = "✅" if status == "Pass" else "❌" if status == "Fail" else "⚠️"
        control_id = c.get("ControlId", "N/A")
        title = c.get("Title", "No Title")
        print(f"{status_icon} {control_id}: {title[:60]} - {status}")


def main():
    """Main function to parse arguments and run analysis."""
    parser = argparse.ArgumentParser(description="Check compliance from an M365 CIS audit JSON report.")
    parser.add_argument(
        "report_file",
        type=str,
        help="Path to the M365 CIS audit JSON report file.",
    )
    args = parser.parse_args()

    report_path = Path(args.report_file)
    analyze_compliance(report_path)


if __name__ == "__main__":
    main()

