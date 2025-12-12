import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.m365_cis_report import build_report


class TestM365CisReport(unittest.TestCase):
    @patch("scripts.m365_cis_report.pd.ExcelWriter")
    @patch("scripts.m365_cis_report.normalize_audit_data")
    @patch("scripts.m365_cis_report.load_json_with_bom")
    def test_build_report(self, mock_load_json, mock_normalize_data, mock_excel_writer):
        # Arrange
        mock_data = {
            "Controls": [
                {"ControlId": "1.1", "Severity": "High", "Status": "Fail"},
                {"ControlId": "1.2", "Severity": "Medium", "Status": "Pass"},
            ]
        }
        mock_load_json.return_value = mock_data

        mock_normalized_rows = [
            {
                "ControlId": "1.1",
                "Title": "Control 1",
                "Severity": "High",
                "Expected": "X",
                "Actual": "Y",
                "Status": "Fail",
                "Evidence": "E1",
                "Reference": "R1",
                "Timestamp": "T1",
            },
            {
                "ControlId": "1.2",
                "Title": "Control 2",
                "Severity": "Medium",
                "Expected": "A",
                "Actual": "A",
                "Status": "Pass",
                "Evidence": "E2",
                "Reference": "R2",
                "Timestamp": "T2",
            },
        ]
        mock_normalize_data.return_value = mock_normalized_rows

        # This mock setup is for pandas >= 1.4.0
        mock_writer_instance = MagicMock()
        mock_excel_writer.return_value.__enter__.return_value = mock_writer_instance

        json_path = Path("dummy.json")
        xlsx_path = Path("dummy.xlsx")

        # Act
        with patch("pandas.DataFrame.to_excel") as mock_to_excel:
            build_report(json_path, xlsx_path)

        # Assert
        mock_load_json.assert_called_once_with(json_path)
        mock_normalize_data.assert_called_once_with(mock_data)
        mock_excel_writer.assert_called_once_with(xlsx_path, engine="openpyxl")

        self.assertEqual(mock_to_excel.call_count, 2)

        # Check the call arguments for the 'Overview' sheet
        overview_call_args = mock_to_excel.call_args_list[0]
        self.assertEqual(overview_call_args[1]["sheet_name"], "Overview")

        # Check the call arguments for the 'Controls' sheet
        controls_call_args = mock_to_excel.call_args_list[1]
        self.assertEqual(controls_call_args[1]["sheet_name"], "Controls")


if __name__ == "__main__":
    unittest.main()
