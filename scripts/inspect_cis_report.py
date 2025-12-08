import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.report_utils import inspect_excel_report  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("output/reports/security/m365_cis_audit.xlsx"),
        help="Path to m365_cis_audit Excel report",
    )
    args = parser.parse_args()

    inspect_excel_report(args.report, head_rows=10)


if __name__ == "__main__":
    main()
