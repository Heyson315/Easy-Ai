# Microsoft 365 CIS Foundations Level 1 (v3.0) – Audit Toolkit

This repo includes a PowerShell-based audit for a subset of CIS Microsoft 365 Foundations v3.0 Level 1 controls. It connects to Microsoft 365 services, evaluates configurations, and produces JSON/CSV reports plus an Excel summary.

Important: This toolkit provides technical checks and is not a substitute for a full compliance program. Always review results with your security and compliance teams.

## Prerequisites

- Windows PowerShell 5.1 or PowerShell 7+
- Modules installed (CurrentUser scope is fine):
  - ExchangeOnlineManagement
  - Microsoft.Graph
  - (Optional) Microsoft.Online.SharePoint.PowerShell (for SPO tenant checks)
- Appropriate admin roles/permissions:
  - Exchange Admin (EXO checks)
  - Global Reader / Security Reader (Graph queries)
  - SharePoint Admin (SPO tenant checks)

## Files

- `scripts/powershell/modules/M365CIS.psm1` – audit functions
- `scripts/powershell/Invoke-M365CISAudit.ps1` – orchestrator (connect + run + export)
- `config/benchmarks/cis_m365_foundations_v3_level1.json` – metadata for controls
- `scripts/m365_cis_report.py` – builds an Excel report from JSON output
- Output directory: `output/reports/security/`

## Run – Audit (read-only)

```powershell
# From the repo root
pwsh -File scripts/powershell/Invoke-M365CISAudit.ps1

# Include SharePoint tenant checks by connecting to the SPO admin URL
pwsh -File scripts/powershell/Invoke-M365CISAudit.ps1 -SPOAdminUrl "https://<tenant>-admin.sharepoint.com"

# Or skip certain services if not available
pwsh -File scripts/powershell/Invoke-M365CISAudit.ps1 -SkipExchange

# To generate timestamped outputs (useful for historical tracking)
pwsh -File scripts/powershell/Invoke-M365CISAudit.ps1 -Timestamped
```

This generates:

- `output/reports/security/m365_cis_audit.json` (or `m365_cis_audit_YYYYMMDD_HHMMSS.json` if -Timestamped)
- `output/reports/security/m365_cis_audit.csv` (or `m365_cis_audit_YYYYMMDD_HHMMSS.csv` if -Timestamped)

## Build Excel summary (optional)

```powershell
# Use Python to convert JSON → Excel (auto-names Excel from JSON filename)
python scripts/m365_cis_report.py

# Or for a specific timestamped JSON
python scripts/m365_cis_report.py --input "output/reports/security/m365_cis_audit_20251025_073705.json"
```

It writes: `output/reports/security/m365_cis_audit.xlsx` (or timestamped equivalent)

## Controls included

**Exchange Online (EXO):**

- Modern auth enabled and basic auth blocked (Auth Policies)
- External auto-forwarding disabled
- Mailbox auditing enabled (org-level)
- Legacy protocols disabled per mailbox (POP/IMAP/MAPI - sample check)

**SharePoint Online (SPO):**

- Restrict external sharing at the tenant level

Note: For SPO checks, install the module and connect to your tenant admin URL:

```powershell
Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser
Connect-SPOService -Url "https://<tenant>-admin.sharepoint.com"
```

You can also pass the admin URL to the audit runner using `-SPOAdminUrl` and it will connect automatically if the module is installed.

**Azure AD/Entra ID:**

- Limit Global Administrator assignments

**Microsoft Defender for Office 365:**

- Safe Links policy enabled
- Safe Attachments policy enabled

**Conditional Access:**

- MFA policy exists for all users

Total checks: 9 controls

## GLBA note

GLBA is a legal and regulatory framework, not a technical benchmark. Many CIS controls support GLBA safeguards (e.g., access control, authentication, logging). Use this toolkit as a technical input into your GLBA compliance efforts, but coordinate with your legal/compliance teams for scoping, documentation, and risk management.

## Safety and change control

- The provided scripts are read-only (audit) by default.
- If you extend with remediation, start with `-WhatIf`.
- Test in a non-production tenant first.
- Review output before applying changes.
