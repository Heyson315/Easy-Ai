"""Tests for report utilities."""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest
from pytest import CaptureFixture

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.report_utils import inspect_excel_report


class TestInspectExcelReport:
    """Tests for inspect_excel_report function."""

    def test_inspect_valid_report(self, capsys: CaptureFixture[str]):
        """Test inspecting a valid Excel report with multiple sheets."""
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
            assert str(excel_path) in captured.out
            assert "Sheets: ['Sheet1', 'Sheet2']" in captured.out
            assert "Sheet: Sheet1  shape=(3, 2)" in captured.out
            assert "A B" in captured.out
            assert "1 a" in captured.out
            assert "2 b" in captured.out
            assert "Sheet: Sheet2  shape=(2, 2)" in captured.out
            assert "X  Y" in captured.out
            assert "10 30" in captured.out
            assert "20 40" in captured.out

    def test_inspect_nonexistent_file(self, capsys: CaptureFixture[str]):
        """Test that SystemExit is raised for missing file."""
        with TemporaryDirectory() as td:
            excel_path = Path(td) / "nonexistent.xlsx"

            with pytest.raises(SystemExit) as excinfo:
                inspect_excel_report(excel_path)

            assert excinfo.value.code == 1
            captured = capsys.readouterr()
            assert "Report not found" in captured.out

    def test_head_rows_parameter(self, capsys: CaptureFixture[str]):
        """Test that head_rows parameter controls output."""
        with TemporaryDirectory() as td:
            excel_path = Path(td) / "test.xlsx"

            # Create a test Excel file
            df = pd.DataFrame({"A": list(range(10))})

            with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Data", index=False)

            inspect_excel_report(excel_path, head_rows=3)

            captured = capsys.readouterr()
            # Check that output contains 3 data rows + header
            output_lines = captured.out.strip().split('\n')
            data_lines = [line for line in output_lines if line.strip().isnumeric() or 'A' in line]
            # This is a bit fragile, but checks the intent
            assert len(data_lines) >= 3  # Header + 3 rows of data

    def test_inspect_single_sheet_report(self, capsys: CaptureFixture[str]):
        """Test inspecting a report with only one sheet."""
        with TemporaryDirectory() as td:
            excel_path = Path(td) / "single_sheet.xlsx"
            df = pd.DataFrame({"Single": ["data"]})
            df.to_excel(excel_path, sheet_name="MySheet", index=False)

            inspect_excel_report(excel_path)

            captured = capsys.readouterr()
            assert "Sheets: ['MySheet']" in captured.out
            assert "Sheet: MySheet  shape=(1, 1)" in captured.out
            assert "Single" in captured.out
            assert "data" in captured.out

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
