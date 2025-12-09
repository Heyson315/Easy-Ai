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
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        input_file = temp_dir / "in.csv"
        output_file = temp_dir / "out.csv"
        input_file.write_text(SAMPLE, encoding="utf-8")

        stats = clean_csv(input_file, output_file)
        assert stats["comment_lines"] == 1
        assert stats["blank_lines"] == 1
        assert stats["skipped_repeated_headers"] == 1
        assert stats["output_rows"] == 2

        dataframe = pd.read_csv(output_file)
        assert list(dataframe.columns) == [
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
        assert dataframe.shape == (2, 9)
        # Quoted comma should be preserved as a single field
        assert dataframe.iloc[0]["Resource Path"] == "parent/path,with,comma"
