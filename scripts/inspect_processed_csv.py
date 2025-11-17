import pandas as pd
from pathlib import Path

p = Path("data/processed/sharepoint_permissions_clean.csv")
df = pd.read_csv(p)
print("Shape:", df.shape)
print("Columns:", list(df.columns))
print("\nHead (5 rows):")
print(df.head(5).to_string(index=False))
print("\nUnique item types (first 10):", sorted(df["Item Type"].dropna().unique().tolist())[:10])
print("Top 5 permissions by count:", df["Permission"].dropna().value_counts().head(5).to_dict())
