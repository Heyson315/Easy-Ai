# GitHub Action Troubleshooting Guide

## Issue 1: Missing or Incorrect Secrets

### Problem
```
❌ tenant-id appears to be a test value. Use actual Azure AD Tenant ID from secrets.
❌ client-id appears to be a test value. Use actual Service Principal Client ID from secrets.
❌ client-secret appears to be a test value. Use actual secret from GitHub secrets.
```

### Root Cause
The action was being called with hardcoded test values like `"test-tenant-id"` instead of actual Azure credentials from GitHub Secrets.

### Solution

#### Step 1: Create Service Principal in Azure AD

```powershell
# Login to Azure
Connect-AzAccount

# Create Service Principal
$sp = New-AzADServicePrincipal -DisplayName "M365-Security-Audit-GitHub"

# Save these values securely
Write-Host "Tenant ID: $(Get-AzContext).Tenant.Id"
Write-Host "Client ID: $($sp.AppId)"
Write-Host "Client Secret: $($sp.PasswordCredentials.SecretText)"
```

#### Step 2: Grant Required Permissions

In Azure Portal → Azure AD → App registrations → Your App → API permissions:

**Microsoft Graph:**
- `User.Read.All` (Application)
- `Policy.Read.All` (Application)
- `Directory.Read.All` (Application)
- `Organization.Read.All` (Application)

**Exchange Online:**
- `Exchange.ManageAsApp` (Application)

**SharePoint:**
- `Sites.FullControl.All` (Application) - if auditing SharePoint

**Click "Grant admin consent"**

#### Step 3: Add Secrets to GitHub

Repository → Settings → Secrets and variables → Actions → New repository secret:

1. **M365_TENANT_ID**: Your Azure AD Tenant ID (GUID)
2. **M365_CLIENT_ID**: Service Principal Application/Client ID (GUID)
3. **M365_CLIENT_SECRET**: Service Principal Secret Value (string)
4. **SPO_ADMIN_URL**: SharePoint Admin URL (optional)

#### Step 4: Use Secrets in Workflow

```yaml
- uses: Heyson315/Easy-Ai@v1
  with:
    tenant-id: ${{ secrets.M365_TENANT_ID }}      # ✅ From secrets
    client-id: ${{ secrets.M365_CLIENT_ID }}      # ✅ From secrets
    client-secret: ${{ secrets.M365_CLIENT_SECRET }}  # ✅ From secrets
    
    # ❌ NEVER DO THIS:
    # tenant-id: 'test-tenant-id'
    # client-id: 'my-actual-client-id-123'  # Exposed in logs!
```

### Validation

The action now includes input validation that will fail fast if test values are detected:

```powershell
if ("${{ inputs.tenant-id }}" -match "test|dummy|example") {
  Write-Host "❌ tenant-id appears to be a test value" -ForegroundColor Red
  exit 1
}
```

---

## Issue 2: Artifact Not Found

### Problem
```
Error: Artifact not found for name: baseline-audit
```

### Root Cause
1. Artifact name mismatch between upload and download steps
2. Artifact retention expired (default 90 days)
3. First run has no baseline yet

### Solution

#### Fixed Artifact Naming (Consistent)

```yaml
# Upload baseline (after audit)
- uses: actions/upload-artifact@v4
  with:
    name: compliance-baseline-audit  # ✅ Fixed name
    path: output/reports/m365_cis_audit.json
    retention-days: 365

# Download baseline (before audit)
- uses: actions/download-artifact@v4
  with:
    name: compliance-baseline-audit  # ✅ Same name
    path: baseline/
```

#### Handle Missing Baseline Gracefully

```yaml
- name: Download Baseline Artifact
  if: inputs.compare-with-baseline == 'true'
  uses: actions/download-artifact@v4
  continue-on-error: true  # ✅ Don't fail if missing
  id: download-baseline
  with:
    name: compliance-baseline-audit

- name: Compare with Baseline
  if: inputs.compare-with-baseline == 'true' && steps.download-baseline.outcome == 'success'  # ✅ Only if found
  # ... comparison logic
```

#### First Run Behavior

On first run, no baseline exists yet. The action will:
1. ⚠️ Skip trend comparison (no baseline)
2. ✅ Complete audit normally
3. ✅ Save current results as new baseline
4. ✅ Future runs will compare against this baseline

---

## Issue 3: PowerShell Connect-ExchangeOnline Error

### Problem
```
A parameter cannot be found that matches parameter name 'CertificateThumbprint'
```

### Root Cause
Using `CertificateThumbprint` parameter with **client secret authentication**. This parameter only works with **certificate-based authentication**.

### Solution

#### For Client Secret Auth (Fixed in v1.2.0)

```powershell
# ✅ CORRECT: Client Secret Authentication
$secureSecret = ConvertTo-SecureString $env:CLIENT_SECRET -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($env:CLIENT_ID, $secureSecret)

Connect-MgGraph -TenantId $env:TENANT_ID -ClientSecretCredential $credential

# For Exchange, use access token from Graph
try {
  Connect-ExchangeOnline `
    -Organization $env:TENANT_ID `
    -AppId $env:CLIENT_ID `
    -AccessToken (Get-MgAccessToken)  # ✅ No CertificateThumbprint needed
} catch {
  Write-Host "⚠️ Exchange connection failed: $_" -ForegroundColor Yellow
}
```

#### For Certificate Auth (Alternative)

If you prefer certificate-based auth:

1. **Create Self-Signed Certificate**:
```powershell
$cert = New-SelfSignedCertificate `
  -Subject "CN=M365SecurityAudit" `
  -CertStoreLocation "Cert:\CurrentUser\My" `
  -KeySpec Signature `
  -KeyLength 2048 `
  -NotAfter (Get-Date).AddYears(2)

# Export public key (.cer)
Export-Certificate -Cert $cert -FilePath "M365SecurityAudit.cer"

# Upload to Azure AD → App registrations → Certificates
```

2. **Store Certificate in GitHub Secret**:
```yaml
# Export private key as base64
$pfxBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Pfx, "password")
$pfxBase64 = [Convert]::ToBase64String($pfxBytes)
# Save $pfxBase64 to secret: CERT_PFX_BASE64
```

3. **Use in Workflow**:
```powershell
# Import certificate from secret
$pfxBytes = [Convert]::FromBase64String($env:CERT_PFX_BASE64)
$cert = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($pfxBytes, "password")

# Connect with certificate
Connect-ExchangeOnline `
  -Organization $env:TENANT_ID `
  -AppId $env:CLIENT_ID `
  -CertificateThumbprint $cert.Thumbprint
```

**Recommendation**: Stick with client secret auth (already fixed) - simpler and works reliably.

---

## Security Best Practices

### ✅ DO:
- Store all credentials in GitHub Encrypted Secrets
- Use service principal with minimum required permissions
- Enable audit logging in Azure AD
- Rotate secrets regularly (90 days)
- Use `continue-on-error` for optional steps
- Validate inputs before use
- Never log secret values

### ❌ DON'T:
- Hardcode credentials in workflow files
- Use personal accounts for automation
- Grant excessive permissions ("Global Admin")
- Expose secrets in logs or outputs
- Use test/dummy values in production

---

## Testing the Fixes

### 1. Validate Locally (YAML Syntax)
```powershell
python -c "import yaml; yaml.safe_load(open('action.yml'))"
```

### 2. Test in GitHub Actions

**Option A: Validate Only** (no secrets needed)
```yaml
- uses: Heyson315/Easy-Ai@v1
  with:
    tenant-id: ${{ secrets.M365_TENANT_ID || 'will-fail-validation' }}
    # ... will fail fast with helpful error
```

**Option B: Full Audit** (requires secrets)
```yaml
on:
  workflow_dispatch:  # Manual trigger for testing

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
```

### 3. Check Security Tab

After successful run:
1. Go to repository → Security → Code scanning
2. Verify SARIF findings uploaded
3. Check severity filtering works

---

## Quick Reference

| Issue | Error Message | Fix |
|-------|--------------|-----|
| Missing secrets | "tenant-id is required" | Add secrets to GitHub |
| Test values | "appears to be a test value" | Use actual Azure credentials |
| Artifact not found | "Artifact not found for name: baseline-audit" | Fixed naming + `continue-on-error` |
| Certificate param | "parameter name 'CertificateThumbprint'" | Removed (use client secret) |
| Permission denied | "Insufficient privileges" | Grant API permissions + admin consent |

---

## Additional Resources

- **Setup Guide**: [docs/M365_SERVICE_PRINCIPAL_SETUP.md](docs/M365_SERVICE_PRINCIPAL_SETUP.md)
- **Workflow Examples**: [.github/WORKFLOW_EXAMPLES.md](.github/WORKFLOW_EXAMPLES.md)
- **Action Documentation**: [.github/copilot-instructions.md](.github/copilot-instructions.md)
- **Microsoft Docs**: [Register an application with Azure AD](https://learn.microsoft.com/en-us/graph/auth-register-app-v2)

---

**Fixed in**: action.yml v1.2.1 (December 5, 2025)
