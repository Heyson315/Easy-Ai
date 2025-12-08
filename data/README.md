# Data Processing

## Overview

The `data/` directory manages data processing workflows for M365 security audits and SharePoint permissions analysis. This directory handles raw data ingestion, cleaning transformations, and historical archiving while maintaining compliance with data privacy regulations.

**Data Processing Philosophy:**
- **Raw → Processed → Reports:** Three-stage pipeline ensures data quality
- **Privacy-first:** Sanitize PII before processing
- **Audit trail:** Track all data transformations
- **Compliance:** GDPR/CCPA-compliant data handling

## Directory Structure

```
data/
├── raw/                           # Unprocessed data exports
│   ├── sharepoint/                # SharePoint permission exports
│   │   ├── site_permissions_YYYYMMDD.csv
│   │   ├── user_access_YYYYMMDD.csv
│   │   └── external_sharing_YYYYMMDD.csv
│   ├── azure_ad/                  # Azure AD exports
│   │   ├── users_YYYYMMDD.csv
│   │   ├── groups_YYYYMMDD.csv
│   │   └── guest_users_YYYYMMDD.csv
│   └── exchange/                  # Exchange Online exports
│       ├── mailbox_permissions_YYYYMMDD.csv
│       └── transport_rules_YYYYMMDD.csv
├── processed/                     # Cleaned and validated data
│   ├── sharepoint_clean_YYYYMMDD.csv
│   ├── azure_ad_clean_YYYYMMDD.csv
│   └── exchange_clean_YYYYMMDD.csv
├── external/                      # Third-party data sources
│   ├── threat_intelligence/       # Security threat feeds
│   └── compliance/                # External compliance data
└── archive/                       # Historical data snapshots
    └── YYYY/                      # Year-based organization
        └── MM/                    # Month-based organization
            └── data_YYYYMMDD.zip  # Compressed historical data
```

## Data Workflow

### Stage 1: Raw Data Ingestion

**Sources:**
- SharePoint Online permission exports
- Azure AD user/group exports
- Exchange Online mailbox permissions
- M365 audit logs
- Third-party security feeds

**Export methods:**

**PowerShell export:**
```powershell
# Export SharePoint permissions
Connect-PnPOnline -Url "https://contoso.sharepoint.com" -Interactive

Get-PnPSiteCollectionAdmin -All | 
    Export-Csv "data/raw/sharepoint/site_admins_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation

# Export Azure AD users
Connect-MgGraph -Scopes "User.Read.All"

Get-MgUser -All | 
    Select-Object DisplayName, UserPrincipalName, UserType, AccountEnabled |
    Export-Csv "data/raw/azure_ad/users_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

**Microsoft 365 Admin Center:**
1. Navigate to **Users → Active Users**
2. Click **Export users**
3. Save to `data/raw/azure_ad/`

**SharePoint Permissions Report:**
1. Site Settings → Site Permissions
2. Export to Excel
3. Save as CSV to `data/raw/sharepoint/`

### Stage 2: Data Cleaning

**Common data quality issues:**
- ❌ UTF-8 BOM (Byte Order Mark) in CSV files
- ❌ Comment lines starting with `#`
- ❌ Repeated CSV headers across pages
- ❌ Quoted commas in file paths
- ❌ Empty rows
- ❌ Inconsistent date formats
- ❌ PII in unexpected fields

**Cleaning script:**
```bash
# Clean SharePoint export
python scripts/clean_csv.py \
    --input "data/raw/sharepoint/site_permissions_20251207.csv" \
    --output "data/processed/sharepoint_clean_20251207.csv"
```

**What clean_csv.py does:**
1. **Remove BOM:** Handles UTF-8-BOM encoding
2. **Filter comments:** Removes lines starting with `#`
3. **Deduplicate headers:** Removes repeated header rows
4. **Preserve quoted commas:** Maintains integrity of quoted fields
5. **Remove blank lines:** Cleans up formatting
6. **Validate structure:** Ensures consistent column count

**Example transformation:**

**Before (raw):**
```csv
# Comment line should be removed

Resource Path,Item Type,Permission,User Name,User Email
"parent/path,with,comma",pdf,Contribute,John Doe,john@example.com
Resource Path,Item Type,Permission,User Name,User Email
another/path,docx,Contribute,Jane Doe,jane@example.com

```

**After (cleaned):**
```csv
Resource Path,Item Type,Permission,User Name,User Email
"parent/path,with,comma",pdf,Contribute,John Doe,john@example.com
another/path,docx,Contribute,Jane Doe,jane@example.com
```

**Validation:**
```python
import pandas as pd

# Validate cleaned data
df = pd.read_csv("data/processed/sharepoint_clean_20251207.csv")

print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"Null values: {df.isnull().sum().sum()}")
print(f"Duplicate rows: {df.duplicated().sum()}")
```

### Stage 3: Data Processing

**Generate business reports:**
```bash
# SharePoint permissions analysis
python -m src.integrations.sharepoint_connector \
    --input "data/processed/sharepoint_clean_20251207.csv" \
    --output "output/reports/business/sharepoint_permissions_20251207.xlsx"
```

**Processing capabilities:**
- Permission aggregation by user/site
- External sharing detection
- Orphaned user identification
- Access pattern analysis
- Risk scoring

## Privacy & Compliance

### GDPR Considerations

**Personal data in exports:**
- User principal names (emails)
- Display names
- Phone numbers
- Department/title information
- IP addresses (in audit logs)

**Compliance measures:**

**Data minimization:**
```python
# Only export necessary fields
df = pd.read_csv("data/raw/azure_ad/users.csv")
df_minimal = df[['UserPrincipalName', 'UserType', 'AccountEnabled']]
df_minimal.to_csv("data/processed/users_minimal.csv", index=False)
```

**Anonymization:**
```python
import hashlib

def anonymize_email(email):
    """Hash email addresses for analysis while preserving uniqueness"""
    return hashlib.sha256(email.encode()).hexdigest()[:16]

df['UserHash'] = df['UserPrincipalName'].apply(anonymize_email)
df = df.drop(columns=['UserPrincipalName', 'DisplayName'])
```

**Access controls:**
```powershell
# Set restrictive permissions on data directory
icacls "data\raw" /inheritance:r
icacls "data\raw" /grant:r "Administrators:(OI)(CI)F"
icacls "data\raw" /grant:r "SYSTEM:(OI)(CI)F"
```

### Data Retention

**Retention policies:**
```json
{
  "dataRetention": {
    "rawData": {
      "retentionDays": 30,
      "reason": "Temporary staging for processing"
    },
    "processedData": {
      "retentionDays": 90,
      "reason": "Reprocessing and analysis"
    },
    "archivedData": {
      "retentionDays": 2555,
      "reason": "SOX/AICPA compliance (7 years)"
    }
  }
}
```

**Cleanup script:**
```powershell
# scripts/powershell/Cleanup-OldData.ps1
param(
    [int]$RawDataRetentionDays = 30,
    [int]$ProcessedDataRetentionDays = 90,
    [switch]$WhatIf
)

$rawCutoff = (Get-Date).AddDays(-$RawDataRetentionDays)
$processedCutoff = (Get-Date).AddDays(-$ProcessedDataRetentionDays)

# Clean raw data
Get-ChildItem "data/raw" -Recurse -File |
    Where-Object { $_.LastWriteTime -lt $rawCutoff } |
    ForEach-Object {
        if ($WhatIf) {
            Write-Host "Would delete: $($_.FullName)" -ForegroundColor Yellow
        } else {
            Remove-Item $_.FullName -Force
            Write-Host "Deleted: $($_.FullName)" -ForegroundColor Red
        }
    }

# Clean processed data
Get-ChildItem "data/processed" -Recurse -File |
    Where-Object { $_.LastWriteTime -lt $processedCutoff } |
    ForEach-Object {
        if ($WhatIf) {
            Write-Host "Would delete: $($_.FullName)" -ForegroundColor Yellow
        } else {
            Remove-Item $_.FullName -Force
            Write-Host "Deleted: $($_.FullName)" -ForegroundColor Red
        }
    }
```

### Right to Erasure (GDPR Article 17)

**Handling data deletion requests:**

```powershell
function Remove-UserDataFromExports {
    param(
        [string]$UserEmail,
        [switch]$WhatIf
    )
    
    $dataFiles = Get-ChildItem "data" -Recurse -Filter "*.csv"
    
    foreach ($file in $dataFiles) {
        $content = Import-Csv $file.FullName
        $filtered = $content | Where-Object { 
            $_.UserPrincipalName -ne $UserEmail -and
            $_.UserEmail -ne $UserEmail
        }
        
        if ($filtered.Count -lt $content.Count) {
            if ($WhatIf) {
                Write-Host "Would remove $UserEmail from $($file.Name)"
            } else {
                $filtered | Export-Csv $file.FullName -NoTypeInformation
                Write-Host "Removed $UserEmail from $($file.Name)" -ForegroundColor Green
            }
        }
    }
}

# Usage
Remove-UserDataFromExports -UserEmail "user@contoso.com" -WhatIf
```

## Data Quality

### Validation Rules

**Schema validation:**
```python
# scripts/validate_data.py
import pandas as pd
import sys

def validate_sharepoint_export(csv_path):
    """Validate SharePoint permissions export structure"""
    required_columns = [
        'Resource Path',
        'Item Type',
        'Permission',
        'User Name',
        'User Email',
        'User Or Group Type'
    ]
    
    try:
        df = pd.read_csv(csv_path)
        
        # Check required columns
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        
        # Check for empty dataframe
        if len(df) == 0:
            print("❌ Export is empty")
            return False
        
        # Check for null values in critical columns
        null_counts = df[required_columns].isnull().sum()
        if null_counts.sum() > 0:
            print(f"⚠️ Null values found: {null_counts.to_dict()}")
        
        print(f"✅ Validation passed: {len(df)} rows, {len(df.columns)} columns")
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_data.py <csv_file>")
        sys.exit(1)
    
    is_valid = validate_sharepoint_export(sys.argv[1])
    sys.exit(0 if is_valid else 1)
```

**Usage:**
```bash
python scripts/validate_data.py data/raw/sharepoint/site_permissions_20251207.csv
```

### Data Profiling

**Profile data quality:**
```python
import pandas as pd

def profile_dataset(csv_path):
    """Generate data quality profile"""
    df = pd.read_csv(csv_path)
    
    profile = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
        'null_counts': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'data_types': df.dtypes.astype(str).to_dict()
    }
    
    print("=" * 50)
    print(f"Data Profile: {csv_path}")
    print("=" * 50)
    print(f"Rows: {profile['total_rows']:,}")
    print(f"Columns: {profile['total_columns']}")
    print(f"Memory: {profile['memory_usage_mb']:.2f} MB")
    print(f"Duplicates: {profile['duplicate_rows']}")
    print(f"\nNull Values:")
    for col, count in profile['null_counts'].items():
        if count > 0:
            print(f"  {col}: {count}")
    
    return profile
```

## Cleanup Guidelines

### Automatic Cleanup

**Scheduled cleanup (Windows Task Scheduler):**
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File 'C:\path\to\Cleanup-OldData.ps1'"

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 4am

Register-ScheduledTask -TaskName "M365-Data-Cleanup" `
    -Action $action `
    -Trigger $trigger `
    -Description "Clean up old M365 data exports"
```

**GitHub Actions workflow:**
```yaml
name: Data Cleanup

on:
  schedule:
    - cron: '0 4 * * 0'  # Weekly on Sunday at 4 AM

jobs:
  cleanup:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Clean old data
        shell: pwsh
        run: |
          .\scripts\powershell\Cleanup-OldData.ps1 `
            -RawDataRetentionDays 30 `
            -ProcessedDataRetentionDays 90
```

### Manual Cleanup

**Delete all raw data:**
```powershell
# CAUTION: This deletes all raw data
Remove-Item "data/raw/*" -Recurse -Force
```

**Archive before cleanup:**
```powershell
# Archive data older than 30 days
$archiveDate = (Get-Date).AddDays(-30)
$archivePath = "data/archive/$(Get-Date -Format 'yyyy/MM')"

New-Item -ItemType Directory -Path $archivePath -Force

Get-ChildItem "data/raw" -Recurse -File |
    Where-Object { $_.LastWriteTime -lt $archiveDate } |
    Compress-Archive -DestinationPath "$archivePath/raw_data_$(Get-Date -Format 'yyyyMMdd').zip"
```

## Best Practices

**DO:**
- ✅ Always clean raw data before processing
- ✅ Validate data schema after import
- ✅ Minimize PII in exports (only export necessary fields)
- ✅ Archive data before cleanup
- ✅ Encrypt sensitive data at rest
- ✅ Log all data access for audit trails
- ✅ Use timestamped filenames for versioning

**DON'T:**
- ❌ Process raw data directly (always clean first)
- ❌ Store unencrypted PII long-term
- ❌ Share data exports via email
- ❌ Commit data files to source control (.gitignore excludes data/)
- ❌ Keep raw data longer than necessary
- ❌ Mix raw and processed data in same directory

## Data Security

### Encryption at Rest

**Windows (BitLocker):**
```powershell
# Enable BitLocker on data drive
Enable-BitLocker -MountPoint "D:" `
    -EncryptionMethod XtsAes256 `
    -UsedSpaceOnly `
    -RecoveryPasswordProtector
```

**Azure Blob Storage:**
```powershell
# Enable encryption for blob storage
$storageAccount = Get-AzStorageAccount -ResourceGroupName "RG" -Name "Storage"
Set-AzStorageAccount -ResourceGroupName "RG" `
    -Name "Storage" `
    -EnableHttpsTrafficOnly $true `
    -EnableBlobEncryption $true
```

### Access Controls

**File system permissions:**
```powershell
# Restrict access to data directory
icacls "data" /inheritance:r
icacls "data" /grant:r "Administrators:(OI)(CI)F"
icacls "data" /grant:r "SYSTEM:(OI)(CI)F"
icacls "data" /grant:r "AuditTeam:(OI)(CI)R"
```

**Audit access:**
```powershell
# Enable file access auditing
$acl = Get-Acl "data"
$auditRule = New-Object System.Security.AccessControl.FileSystemAuditRule(
    "Everyone",
    "Read,Write,Delete",
    "ContainerInherit,ObjectInherit",
    "None",
    "Success,Failure"
)
$acl.AddAuditRule($auditRule)
Set-Acl "data" $acl
```

## Performance Considerations

### Large Dataset Handling

**Chunked processing:**
```python
import pandas as pd

def process_large_csv(input_path, output_path, chunk_size=10000):
    """Process large CSV files in chunks"""
    chunks = []
    
    for chunk in pd.read_csv(input_path, chunksize=chunk_size):
        # Process chunk
        processed = clean_and_transform(chunk)
        chunks.append(processed)
    
    # Combine results
    result = pd.concat(chunks, ignore_index=True)
    result.to_csv(output_path, index=False)
    
    print(f"Processed {len(result):,} rows")
```

**Memory-efficient filtering:**
```python
# Use generators for large files
def filter_external_users(csv_path):
    """Filter external users without loading entire file"""
    with open(csv_path, 'r') as f_in, open('external_users.csv', 'w') as f_out:
        header = next(f_in)
        f_out.write(header)
        
        for line in f_in:
            if '#EXT#' in line or 'External' in line:
                f_out.write(line)
```

## Cross-References

### Related Documentation

- **Parent README:** [`../README.md`](../README.md) - Project overview
- **Output Directory:** [`../output/README.md`](../output/README.md) - Report generation
- **Scripts Documentation:** [`../scripts/README.md`](../scripts/README.md) - Data processing scripts
- **Source Code:** [`../src/README.md`](../src/README.md) - Processing modules
- **Configuration:** [`../config/README.md`](../config/README.md) - Data retention settings

### External Resources

- **GDPR Compliance:** [GDPR Data Protection](https://gdpr.eu/)
- **CCPA Compliance:** [California Consumer Privacy Act](https://oag.ca.gov/privacy/ccpa)
- **Pandas Documentation:** [pandas.pydata.org](https://pandas.pydata.org/)
- **CSV Best Practices:** [RFC 4180](https://tools.ietf.org/html/rfc4180)

---

**🔐 Privacy First:** Always minimize PII in exports, anonymize when possible, and encrypt sensitive data at rest.

**🧹 Regular Cleanup:** Implement automated cleanup to maintain compliance with retention policies (30 days raw, 90 days processed, 7 years archived).

**✅ Data Quality:** Always clean raw data before processing. Use `scripts/clean_csv.py` to handle BOM, comments, and repeated headers.
