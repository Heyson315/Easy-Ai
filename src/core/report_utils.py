"""
Shared report inspection utilities for M365 Security Toolkit.

Provides consistent Excel report inspection functionality.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def inspect_excel_report(report_path: Path, head_rows: int = 5) -> None:
    """
    Inspect an Excel report by printing sheet information and sample data.

    Args:
        report_path: Path to the Excel file
        head_rows: Number of rows to display from each sheet (default: 5)
    """
    report_path = Path(report_path)

    if not report_path.exists():
        print("Report not found:", report_path)
        raise SystemExit(1)

    excel_file = pd.ExcelFile(report_path)
    print("Report:", report_path)
    print("Sheets:", excel_file.sheet_names)

    for sheet in excel_file.sheet_names:
        sheet_dataframe = excel_file.parse(sheet)
        print(f"\nSheet: {sheet}  shape={sheet_dataframe.shape}")
        print(sheet_dataframe.head(head_rows).to_string(index=False))
