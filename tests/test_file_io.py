"""Tests for core file I/O utilities."""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

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

    def test_normalize_list(self):
        """Test that list input is returned as-is."""
        data = [{"a": 1}, {"b": 2}]
        result = normalize_audit_data(data)
        assert result == data

    def test_normalize_single_dict(self):
        """Test that single dict is wrapped in a list."""
        data = {"ControlId": "CIS-1", "Status": "Pass"}
        result = normalize_audit_data(data)
        assert result == [data]

    def test_normalize_empty_list(self):
        """Test that empty list is returned as-is."""
        result = normalize_audit_data([])
        assert result == []


class TestEnsureParentDir:
    """Tests for ensure_parent_dir function."""

    def test_creates_parent_directory(self):
        """Test that parent directory is created."""
        with TemporaryDirectory() as td:
            nested_path = Path(td) / "a" / "b" / "c" / "file.txt"
            assert not nested_path.parent.exists()

            result = ensure_parent_dir(nested_path)

            assert nested_path.parent.exists()
            assert result == nested_path

    def test_existing_directory_is_ok(self):
        """Test that existing directory doesn't cause error."""
        with TemporaryDirectory() as td:
            file_path = Path(td) / "file.txt"
            assert file_path.parent.exists()

            result = ensure_parent_dir(file_path)
            assert result == file_path


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
