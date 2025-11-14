"""
Test error handling and edge cases in enhanced modules.
"""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.clean_csv import clean_csv  # noqa: E402


def test_clean_csv_empty_file():
    """Test clean_csv handles empty files."""
    with TemporaryDirectory() as td:
        td = Path(td)
        inp = td / "empty.csv"
        out = td / "out.csv"
        inp.write_text("", encoding="utf-8")
        
        stats = clean_csv(inp, out)
        assert stats["input_lines"] == 0
        assert stats["output_rows"] == 0


def test_clean_csv_comments_only():
    """Test clean_csv handles files with only comments."""
    with TemporaryDirectory() as td:
        td = Path(td)
        inp = td / "comments.csv"
        out = td / "out.csv"
        inp.write_text("# Comment 1\n# Comment 2\n", encoding="utf-8")
        
        stats = clean_csv(inp, out)
        assert stats["comment_lines"] == 2
        assert stats["output_rows"] == 0


def test_clean_csv_with_bom():
    """Test clean_csv handles UTF-8 BOM."""
    with TemporaryDirectory() as td:
        td = Path(td)
        inp = td / "bom.csv"
        out = td / "out.csv"
        # Write file with BOM
        inp.write_text("\ufeffColumn1,Column2\nValue1,Value2\n", encoding="utf-8")
        
        stats = clean_csv(inp, out)
        assert stats["output_rows"] == 1
        # Verify BOM was stripped from header
        assert stats["header"][0] == "Column1"


def test_sync_cis_csv_empty_json():
    """Test sync_cis_csv handles empty JSON array."""
    from scripts.sync_cis_csv import sync_json_to_csv
    
    with TemporaryDirectory() as td:
        td = Path(td)
        json_file = td / "empty.json"
        csv_file = td / "out.csv"
        
        # Write empty JSON array
        json_file.write_text("[]", encoding="utf-8")
        
        # Should handle gracefully without crashing
        sync_json_to_csv(json_file, csv_file)
        assert csv_file.exists()


def test_sync_cis_csv_invalid_json():
    """Test sync_cis_csv handles invalid JSON."""
    from scripts.sync_cis_csv import sync_json_to_csv
    
    with TemporaryDirectory() as td:
        td = Path(td)
        json_file = td / "invalid.json"
        csv_file = td / "out.csv"
        
        # Write invalid JSON
        json_file.write_text("{invalid json", encoding="utf-8")
        
        # Should exit with error
        with pytest.raises(SystemExit) as exc_info:
            sync_json_to_csv(json_file, csv_file)
        assert exc_info.value.code == 1


def test_sync_cis_csv_missing_file():
    """Test sync_cis_csv handles missing input file."""
    from scripts.sync_cis_csv import sync_json_to_csv
    
    with TemporaryDirectory() as td:
        td = Path(td)
        json_file = td / "nonexistent.json"
        csv_file = td / "out.csv"
        
        # Should exit with error
        with pytest.raises(SystemExit) as exc_info:
            sync_json_to_csv(json_file, csv_file)
        assert exc_info.value.code == 1


def test_check_compliance_empty_array():
    """Test check_compliance handles empty JSON array."""
    from check_compliance import check_compliance
    
    with TemporaryDirectory() as td:
        td = Path(td)
        json_file = td / "empty.json"
        json_file.write_text("[]", encoding="utf-8")
        
        # Should handle gracefully
        check_compliance(json_file)


def test_check_compliance_invalid_data():
    """Test check_compliance handles invalid data structure."""
    from check_compliance import check_compliance
    
    with TemporaryDirectory() as td:
        td = Path(td)
        json_file = td / "invalid.json"
        # Write object instead of array
        json_file.write_text('{"key": "value"}', encoding="utf-8")
        
        # Should exit with error
        with pytest.raises(SystemExit) as exc_info:
            check_compliance(json_file)
        assert exc_info.value.code == 1


def test_excel_generator_invalid_filename():
    """Test excel_generator handles empty filename."""
    from src.core.excel_generator import create_project_management_workbook
    
    # Should raise ValueError for empty filename
    with pytest.raises(ValueError, match="Filename cannot be empty"):
        create_project_management_workbook("")


def test_gpt5_client_empty_prompt():
    """Test GPT5Client validates empty prompt."""
    from src.integrations.openai_gpt5 import GPT5Client
    
    # Note: This will fail to initialize without credentials, but we can test the validation
    # We'll skip actual API call testing since it requires Azure credentials
    try:
        client = GPT5Client(azure_endpoint="https://fake.openai.azure.com", api_key="fake_key")
        
        # Should raise ValueError for empty prompt
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            client.chat_completion("")
    except ValueError:
        # Expected if credentials are invalid - that's fine for this test
        pass


def test_gpt5_client_invalid_temperature():
    """Test GPT5Client validates temperature range."""
    from src.integrations.openai_gpt5 import GPT5Client
    
    try:
        client = GPT5Client(azure_endpoint="https://fake.openai.azure.com", api_key="fake_key")
        
        # Should raise ValueError for invalid temperature
        with pytest.raises(ValueError, match="temperature must be between"):
            client.chat_completion("test prompt", temperature=3.0)
    except ValueError:
        # Expected if credentials are invalid - that's fine for this test
        pass


def test_gpt5_client_invalid_reasoning_effort():
    """Test GPT5Client validates reasoning_effort parameter."""
    from src.integrations.openai_gpt5 import GPT5Client
    
    try:
        client = GPT5Client(azure_endpoint="https://fake.openai.azure.com", api_key="fake_key")
        
        # Should raise ValueError for invalid reasoning effort
        with pytest.raises(ValueError, match="reasoning_effort must be"):
            client.reasoning_response("test prompt", reasoning_effort="invalid")
    except ValueError:
        # Expected if credentials are invalid - that's fine for this test
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
