import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from scripts.clean_csv import clean_csv

SAMPLE = """# Comment line should be removed

Resource Path,Item Type,Permission,User Name,User Email,User Or Group Type,Link ID,Link Type,AccessViaLinkID
"parent/path,with,comma",pdf,Contribute,John Doe,john@example.com,Internal,,,
Resource Path,Item Type,Permission,User Name,User Email,User Or Group Type,Link ID,Link Type,AccessViaLinkID
another/path,docx,Contribute,Jane Doe,jane@example.com,Internal,,,
"""


def test_clean_csv_basic():
    with TemporaryDirectory() as td:
        td = Path(td)
        inp = td / "in.csv"
        out = td / "out.csv"
        inp.write_text(SAMPLE, encoding="utf-8")

        stats = clean_csv(inp, out)
        assert stats["comment_lines"] == 1
        assert stats["blank_lines"] == 1
        assert stats["skipped_repeated_headers"] == 1
        assert stats["output_rows"] == 2

        df = pd.read_csv(out)
        assert list(df.columns) == [
            "Resource Path",
            "Item Type",
            "Permission",
            "User Name",
            "User Email",
            "User Or Group Type",
            "Link ID",
            "Link Type",
            "AccessViaLinkID",
        ]
        assert df.shape == (2, 9)
        # Quoted comma should be preserved as a single field
        assert df.iloc[0]["Resource Path"] == "parent/path,with,comma"


def test_clean_csv_empty_file():
    with TemporaryDirectory() as td:
        td = Path(td)
        inp = td / "in.csv"
        out = td / "out.csv"
        inp.write_text("", encoding="utf-8")

        stats = clean_csv(inp, out)
        assert stats["input_lines"] == 0
        assert stats["output_rows"] == 0
        assert out.read_text() == ""


def test_clean_csv_only_comments_and_blanks():
    with TemporaryDirectory() as td:
        td = Path(td)
        inp = td / "in.csv"
        out = td / "out.csv"
        inp.write_text("# comment\n\n# another comment", encoding="utf-8")

        stats = clean_csv(inp, out)
        assert stats["input_lines"] == 3
        assert stats["output_rows"] == 0
        assert stats["comment_lines"] == 2
        assert stats["blank_lines"] == 1
        assert out.read_text() == ""


def test_clean_csv_no_header():
    with TemporaryDirectory() as td:
        td = Path(td)
        inp = td / "in.csv"
        out = td / "out.csv"
        inp.write_text("a,b,c\n1,2,3", encoding="utf-8")

        stats = clean_csv(inp, out)
        assert stats["header"] == ["a", "b", "c"]
        assert stats["output_rows"] == 1
        df = pd.read_csv(out)
        assert df.shape == (1, 3)


def test_clean_csv_bom_in_data():
    with TemporaryDirectory() as td:
        td = Path(td)
        inp = td / "in.csv"
        out = td / "out.csv"
        inp.write_text('header\n\ufeffvalue', encoding="utf-8")

        stats = clean_csv(inp, out)
        assert stats["output_rows"] == 1
        df = pd.read_csv(out)
        assert df.iloc[0, 0] == "value"


def test_main_function(monkeypatch):
    with TemporaryDirectory() as td:
        td = Path(td)
        inp = td / "in.csv"
        out = td / "out.csv"
        inp.write_text("a,b,c\n1,2,3", encoding="utf-8")

        from scripts.clean_csv import main

        monkeypatch.setattr(
            "sys.argv",
            ["scripts/clean_csv.py", "--input", str(inp), "--output", str(out)],
        )
        main()

        assert out.exists()
        df = pd.read_csv(out)
        assert df.shape == (1, 3)
