import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.report_utils import inspect_excel_report

report = Path("output/reports/business/sharepoint_permissions_report.xlsx")
inspect_excel_report(report, head_rows=5)
