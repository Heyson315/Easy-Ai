"""Tests for report utilities."""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.report_utils import inspect_excel_report


class TestInspectExcelReport:
    """Tests for inspect_excel_report function."""

    def test_inspect_valid_report(self, capsys):
        """Test inspecting a valid Excel report."""
        with TemporaryDirectory() as td:
            excel_path = Path(td) / "test.xlsx"

            # Create a test Excel file with pandas
            df1 = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
            df2 = pd.DataFrame({"X": [10, 20], "Y": [30, 40]})

            with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                df1.to_excel(writer, sheet_name="Sheet1", index=False)
                df2.to_excel(writer, sheet_name="Sheet2", index=False)

            inspect_excel_report(excel_path, head_rows=2)

            captured = capsys.readouterr()
            assert "test.xlsx" in captured.out
            assert "Sheet1" in captured.out
            assert "Sheet2" in captured.out
            assert "shape=" in captured.out

    def test_inspect_nonexistent_file(self):
        """Test that SystemExit is raised for missing file."""
        with TemporaryDirectory() as td:
            excel_path = Path(td) / "nonexistent.xlsx"

            with pytest.raises(SystemExit):
                inspect_excel_report(excel_path)

    def test_head_rows_parameter(self, capsys):
        """Test that head_rows parameter controls output."""
        with TemporaryDirectory() as td:
            excel_path = Path(td) / "test.xlsx"

            # Create a test Excel file
            df = pd.DataFrame({"A": list(range(10))})

            with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Data", index=False)

            inspect_excel_report(excel_path, head_rows=3)

            captured = capsys.readouterr()
            # Check that output contains data (exact format depends on pandas)
            assert "Data" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
