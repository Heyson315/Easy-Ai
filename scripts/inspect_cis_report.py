import argparse
from pathlib import Path
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', type=Path, default=Path('output/reports/security/m365_cis_audit.xlsx'), help='Path to m365_cis_audit Excel report')
    args = ap.parse_args()

    report = Path(args.report)
    if not report.exists():
        print('Report not found:', report)
        raise SystemExit(1)

    xf = pd.ExcelFile(report)
    print('Report:', report)
    print('Sheets:', xf.sheet_names)
    for sheet in xf.sheet_names:
        df = xf.parse(sheet)
        print(f'\nSheet: {sheet}  shape={df.shape}')
        print(df.head(10).to_string(index=False))

if __name__ == '__main__':
    main()
