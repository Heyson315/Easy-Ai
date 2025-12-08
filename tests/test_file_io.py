"""Tests for core file I/O utilities."""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, List, Dict

import pytest
from pytest import CaptureFixture, MonkeyPatch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.file_io import (
    CIS_AUDIT_COLUMNS,
    ensure_parent_dir,
    load_json_with_bom,
    normalize_audit_data,
)


class TestLoadJsonWithBom:
    """Tests for load_json_with_bom function."""

    def test_load_regular_json(self):
        """Test loading regular JSON without BOM."""
        with TemporaryDirectory() as td:
            json_path = Path(td) / "test.json"
            data = [{"key": "value"}]
            json_path.write_text(json.dumps(data), encoding="utf-8")

            result = load_json_with_bom(json_path, exit_on_error=False)
            assert result == data

    def test_load_json_with_bom(self):
        """Test loading JSON with UTF-8 BOM (PowerShell-style)."""
        with TemporaryDirectory() as td:
            json_path = Path(td) / "test.json"
            data = [{"key": "value"}]
            # Write with BOM (utf-8-sig encoding writes BOM)
            json_path.write_text(json.dumps(data), encoding="utf-8-sig")

            result = load_json_with_bom(json_path, exit_on_error=False)
            assert result == data

    def test_load_json_permission_error(self, monkeypatch: MonkeyPatch):
        """Test that PermissionError is raised for an unreadable file."""
        with TemporaryDirectory() as td:
            json_path = Path(td) / "unreadable.json"
            json_path.write_text("{}", encoding="utf-8")

            def mock_read_text(*args: Any, **kwargs: Any) -> None:
                raise PermissionError("Permission denied")

            monkeypatch.setattr(Path, "read_text", mock_read_text)

            with pytest.raises(PermissionError):
                load_json_with_bom(json_path, exit_on_error=False)

    def test_load_json_permission_error_exits(
        self, monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
    ):
        """Test that sys.exit is called for an unreadable file when exit_on_error=True."""
        with TemporaryDirectory() as td:
            json_path = Path(td) / "unreadable.json"
            json_path.write_text("{}", encoding="utf-8")

            def mock_read_text(*args: Any, **kwargs: Any) -> None:
                raise PermissionError("Permission denied")

            monkeypatch.setattr(Path, "read_text", mock_read_text)

            with pytest.raises(SystemExit) as e:
                load_json_with_bom(json_path, exit_on_error=True)

            assert e.type == SystemExit
            assert e.value.code == 1
            captured = capsys.readouterr()
            assert "ERROR: Cannot read" in captured.err

    def test_load_json_file_not_found_exits(self, capsys: CaptureFixture[str]):
        """Test that sys.exit is called for a missing file when exit_on_error=True."""
        with TemporaryDirectory() as td:
            json_path = Path(td) / "nonexistent.json"

            with pytest.raises(SystemExit) as e:
                load_json_with_bom(json_path, exit_on_error=True)

            assert e.type == SystemExit
            assert e.value.code == 1
            captured = capsys.readouterr()
            assert "ERROR: Input file not found" in captured.err

    def test_load_json_invalid_json_exits(self, capsys: CaptureFixture[str]):
        """Test that sys.exit is called for invalid JSON when exit_on_error=True."""
        with TemporaryDirectory() as td:
            json_path = Path(td) / "invalid.json"
            json_path.write_text("not valid json {{{", encoding="utf-8")

            with pytest.raises(SystemExit) as e:
                load_json_with_bom(json_path, exit_on_error=True)

            assert e.type == SystemExit
            assert e.value.code == 1
            captured = capsys.readouterr()
            assert "ERROR: Invalid JSON" in captured.err

    def test_load_json_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with TemporaryDirectory() as td:
            json_path = Path(td) / "nonexistent.json"

            with pytest.raises(FileNotFoundError):
                load_json_with_bom(json_path, exit_on_error=False)

    def test_load_json_invalid_json(self):
        """Test that JSONDecodeError is raised for invalid JSON."""
        with TemporaryDirectory() as td:
            json_path = Path(td) / "invalid.json"
            json_path.write_text("not valid json {{{", encoding="utf-8")

            with pytest.raises(json.JSONDecodeError):
                load_json_with_bom(json_path, exit_on_error=False)

    def test_load_single_object(self):
        """Test loading a single JSON object (not an array)."""
        with TemporaryDirectory() as td:
            json_path = Path(td) / "test.json"
            data = {"ControlId": "CIS-1", "Status": "Pass"}
            json_path.write_text(json.dumps(data), encoding="utf-8")

            result = load_json_with_bom(json_path, exit_on_error=False)
            assert result == data


class TestNormalizeAuditData:
    """Tests for normalize_audit_data function."""

    def test_normalize_empty_input(self):
        """Test that empty input returns an empty list."""
        assert normalize_audit_data(None) == []
        assert normalize_audit_data([]) == []

    def test_normalize_single_dict(self):
        """Test normalizing a single audit result dictionary."""
        single_item = {"ControlId": "1.1", "Status": "Pass"}
        result = normalize_audit_data(single_item)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["ControlId"] == "1.1"
        assert result[0]["Status"] == "Pass"
        # Check that all standard columns are present
        assert all(col in result[0] for col in CIS_AUDIT_COLUMNS)

    def test_normalize_list_of_dicts(self):
        """Test normalizing a list of audit result dictionaries."""
        list_of_items = [
            {"ControlId": "1.1", "Status": "Pass"},
            {"ControlId": "1.2", "Severity": "High"},
        ]
        result = normalize_audit_data(list_of_items)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["Status"] == "Pass"
        assert result[1]["Severity"] == "High"
        assert all(col in result[1] for col in CIS_AUDIT_COLUMNS)

    def test_normalize_preserves_existing_data(self):
        """Test that existing data and extra fields are preserved."""
        item = {
            "ControlId": "1.1",
            "Title": "My Title",
            "ExtraField": "ExtraValue",
        }
        result = normalize_audit_data([item])

        assert result[0]["Title"] == "My Title"
        assert result[0]["ExtraField"] == "ExtraValue"

    def test_normalize_fills_missing_columns_with_empty_string(self):
        """Test that missing standard columns are filled with empty strings."""
        item = {"ControlId": "1.1"}
        result = normalize_audit_data(item)

        assert result[0]["Title"] == ""
        assert result[0]["Severity"] == ""


class TestEnsureParentDir:
    """Tests for ensure_parent_dir function."""

    def test_directory_creation(self):
        """Test that parent directory is created if it doesn't exist."""
        with TemporaryDirectory() as td:
            # Path to a file in a non-existent directory
            file_path = Path(td) / "new_dir" / "file.txt"

            # Ensure the directory doesn't exist initially
            assert not file_path.parent.exists()

            # Run the function
            ensure_parent_dir(file_path)

            # Check that the directory was created
            assert file_path.parent.exists()
            assert file_path.parent.is_dir()

    def test_parent_directory_already_exists(self):
        """Test that the function does nothing if the parent directory already exists."""
        with TemporaryDirectory() as td:
            # Path to a file in an existing directory
            file_path = Path(td) / "file.txt"

            # Ensure the directory exists
            assert file_path.parent.exists()

            # Run the function
            ensure_parent_dir(file_path)

            # No error should be raised, and the directory should still exist
            assert file_path.parent.exists()

    def test_ensure_parent_dir_creates_directory(self):
        """Test that the parent directory is created if it doesn't exist."""
        with TemporaryDirectory() as td:
            base_path = Path(td)
            new_dir = base_path / "new_parent" / "child.txt"

            # Pre-condition: directory does not exist
            assert not new_dir.parent.exists()

            ensure_parent_dir(new_dir)

            # Post-condition: directory exists
            assert new_dir.parent.exists()
            assert new_dir.parent.is_dir()

    def test_ensure_parent_dir_does_not_fail_if_exists(self):
        """Test that the function does not fail if the directory already exists."""
        with TemporaryDirectory() as td:
            base_path = Path(td)
            existing_dir = base_path / "existing_parent"
            existing_dir.mkdir()
            file_path = existing_dir / "child.txt"

            # Pre-condition: directory exists
            assert file_path.parent.exists()

            # Should run without error
            ensure_parent_dir(file_path)

            # Post-condition: directory still exists
            assert file_path.parent.exists()


class TestCisAuditColumns:
    """Tests for CIS_AUDIT_COLUMNS constant."""

    def test_column_names(self):
        """Test that expected column names are present."""
        assert "ControlId" in CIS_AUDIT_COLUMNS
        assert "Title" in CIS_AUDIT_COLUMNS
        assert "Severity" in CIS_AUDIT_COLUMNS
        assert "Status" in CIS_AUDIT_COLUMNS
        assert "Evidence" in CIS_AUDIT_COLUMNS
        assert "Timestamp" in CIS_AUDIT_COLUMNS

    def test_column_count(self):
        """Test that expected number of columns is defined."""
        assert len(CIS_AUDIT_COLUMNS) == 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
