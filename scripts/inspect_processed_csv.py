#!/usr/bin/env python3
"""
Inspect processed SharePoint CSV file for validation and debugging.
"""
import sys
from pathlib import Path

import pandas as pd

DEFAULT_CSV = Path("data/processed/sharepoint_permissions_clean.csv")


def inspect_csv(csv_path: Path) -> None:
    """Inspect and display information about processed CSV file."""
    if not csv_path.exists():
        print(f"ERROR: File not found: {csv_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        df = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError:
        print(f"ERROR: CSV file is empty: {csv_path}", file=sys.stderr)
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"ERROR: Failed to parse CSV: {e}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"ERROR: Encoding issue while reading CSV: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: I/O error while reading CSV: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate DataFrame is not empty
    if df.empty:
        print(f"WARNING: CSV file contains no data rows: {csv_path}", file=sys.stderr)
        return
    
    print(f"File: {csv_path}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nHead (5 rows):")
    print(df.head(5).to_string(index=False))
    
    # Safely check for expected columns
    if "Item Type" in df.columns:
        item_types = sorted(df["Item Type"].dropna().unique().tolist())
        print(f"\nUnique item types (first 10): {item_types[:10]}")
    else:
        print("\nWARNING: 'Item Type' column not found")
    
    if "Permission" in df.columns:
        permissions = df["Permission"].dropna().value_counts().head(5).to_dict()
        print(f"Top 5 permissions by count: {permissions}")
    else:
        print("WARNING: 'Permission' column not found")


if __name__ == "__main__":
    import argparse
    
    ap = argparse.ArgumentParser(description="Inspect processed SharePoint CSV file")
    ap.add_argument("--input", type=Path, default=DEFAULT_CSV, help="Path to CSV file")
    args = ap.parse_args()
    
    inspect_csv(args.input)
