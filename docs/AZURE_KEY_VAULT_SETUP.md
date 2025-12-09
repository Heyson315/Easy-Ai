# Azure Key Vault Setup Guide for SOX Compliance

## Overview

This guide walks you through setting up Azure Key Vault for SOX/AICPA-compliant secret management in the M365 Security Toolkit. Azure Key Vault provides:

- **Hardware-backed key storage** (HSM-backed optional)
- **Comprehensive audit trails** (Azure Monitor logs)
- **RBAC-based access control** (Least privilege principle)
- **Automatic key rotation** (Optional, for enhanced security)
- **Compliance certifications** (SOC 2, ISO 27001, HIPAA, etc.)

## Prerequisites

- Azure subscription with Contributor access
- Azure CLI installed (`az --version`)
- PowerShell 7+ (for service principal creation script)
- Existing M365 tenant and service principal (or use `scripts/create_sp.ps1`)

## Step 1: Create Azure Key Vault

### Option A: Azure CLI (Recommended)

```bash
# Variables
RESOURCE_GROUP="m365-security-rg"
LOCATION="eastus"
KEYVAULT_NAME="m365-security-kv-$(date +%s)"  # Must be globally unique
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Key Vault with audit logging enabled
az keyvault create \
  --name $KEYVAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --enable-rbac-authorization \
  --enabled-for-deployment false \
  --enabled-for-disk-encryption false \
  --enabled-for-template-deployment false

# Enable diagnostic logging for audit trail (SOX requirement)
az monitor diagnostic-settings create \
  --name "keyvault-audit-logs" \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME" \
  --logs '[{"category":"AuditEvent","enabled":true,"retentionPolicy":{"enabled":true,"days":365}}]' \
  --workspace "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.OperationalInsights/workspaces/m365-security-logs" \
  --export-to-resource-specific true

echo "Key Vault URL: https://$KEYVAULT_NAME.vault.azure.net/"
```

### Option B: Azure Portal

1. Navigate to **portal.azure.com** → **Create a resource** → **Key Vault**
2. Fill in:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: `m365-security-rg` (create new)
   - **Key Vault Name**: `m365-security-kv-<unique>` (must be globally unique)
   - **Region**: Choose nearest region
   - **Pricing Tier**: Standard (Premium for HSM-backed keys)
3. **Access configuration**:
   - **Permission model**: Select **Azure role-based access control (RBAC)**
   - **Enable access to**: Uncheck all (we'll grant specific access via RBAC)
4. **Networking**: Select **Public endpoint (all networks)** or **Private endpoint** for enhanced security
5. **Review + create** → Wait for deployment

## Step 2: Configure RBAC (Role-Based Access Control)

### Assign Key Vault Secrets User Role

This role follows the **least privilege principle** required for SOX compliance.

```bash
# Get your user principal ID (for local development)
USER_PRINCIPAL_ID=$(az ad signed-in-user show --query id -o tsv)

# Assign "Key Vault Secrets User" role (read-only access to secrets)
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $USER_PRINCIPAL_ID \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME"

# For service principal (production)
SP_OBJECT_ID=$(az ad sp show --id <YOUR_SERVICE_PRINCIPAL_CLIENT_ID> --query id -o tsv)
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $SP_OBJECT_ID \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME"
```

### Role Options

| Role | Permissions | Use Case |
|------|------------|----------|
| **Key Vault Secrets User** | Read secrets | Production applications (recommended) |
| **Key Vault Secrets Officer** | Create, read, update, delete secrets | DevOps automation |
| **Key Vault Administrator** | Full access | Break-glass emergency access only |

**⚠️ Security Best Practice**: Use **Secrets User** for applications, **Secrets Officer** for CI/CD pipelines.

## Step 3: Upload Secrets to Key Vault

### Secret Naming Conventions

Azure Key Vault secret names must follow these rules:
- Alphanumeric characters and hyphens only (`^[A-Za-z0-9-]+$`)
- No underscores, dots, or special characters
- Example: `M365-CLIENT-SECRET` (not `M365_CLIENT_SECRET`)

### Option A: Using `create_sp.ps1` Script (Recommended)

The service principal creation script now supports uploading secrets directly to Key Vault:

```powershell
# Run the script
pwsh ./scripts/create_sp.ps1 -Name "m365-audit-sp"

# When prompted, enter 'y' to upload to Key Vault
# Enter your Key Vault name: m365-security-kv-<unique>
```

### Option B: Manual Upload via Azure CLI

```bash
# M365 credentials
az keyvault secret set --vault-name $KEYVAULT_NAME --name "M365-TENANT-ID" --value "<your-tenant-id>"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "M365-CLIENT-ID" --value "<your-client-id>"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "M365-CLIENT-SECRET" --value "<your-client-secret>"

# Azure OpenAI credentials
az keyvault secret set --vault-name $KEYVAULT_NAME --name "AZURE-OPENAI-API-KEY" --value "<your-api-key>"

# Verify secrets uploaded
az keyvault secret list --vault-name $KEYVAULT_NAME --query "[].name" -o table
```

### Option C: Azure Portal

1. Navigate to your Key Vault → **Secrets** → **Generate/Import**
2. Upload method: **Manual**
3. Name: `M365-CLIENT-SECRET` (use hyphens, not underscores)
4. Value: Paste your secret value
5. Content type: `text/plain`
6. Set activation/expiration dates (optional, for key rotation)
7. **Create**

## Step 4: GitHub Actions Integration (OIDC)

### Why OIDC Instead of Long-Lived Secrets?

- **No secret rotation required** (temporary tokens issued per workflow)
- **Audit trail** (Azure AD tracks every token issuance)
- **Reduced attack surface** (no long-lived PATs in GitHub Secrets)

### Configure Federated Credentials

```bash
# Get your GitHub repository details
GITHUB_ORG="your-org-or-username"
GITHUB_REPO="Easy-Ai"
SP_APP_ID="<your-service-principal-client-id>"

# Create federated credential for GitHub Actions
az ad app federated-credential create \
  --id $SP_APP_ID \
  --parameters '{
    "name": "github-actions-oidc",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'"$GITHUB_ORG/$GITHUB_REPO"':ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# For pull requests (optional)
az ad app federated-credential create \
  --id $SP_APP_ID \
  --parameters '{
    "name": "github-actions-oidc-pr",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'"$GITHUB_ORG/$GITHUB_REPO"':pull_request",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

### Configure GitHub Repository Secrets

**Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

```
AZURE_CLIENT_ID: <your-service-principal-client-id>
AZURE_TENANT_ID: <your-tenant-id>
AZURE_SUBSCRIPTION_ID: <your-subscription-id>
```

**Variables** (non-sensitive, can be public):

```
AZURE_KEY_VAULT_URL: https://<your-keyvault-name>.vault.azure.net/
```

### Update Workflow File

See Step 5 below for workflow configuration.

## Step 5: Update Application Configuration

### Local Development (.env file)

```bash
# .env (for local development only)
AZURE_KEY_VAULT_URL=https://m365-security-kv-<unique>.vault.azure.net/

# Optional: Fallback to environment variables if Key Vault unavailable
# (The application will log a warning)
M365_CLIENT_SECRET=<your-secret>  # Fallback only
AZURE_OPENAI_API_KEY=<your-key>   # Fallback only
```

### Python Application Code

```python
from src.core.secrets_manager import SecretsManager

# Initialize secrets manager (auto-detects vault URL from env)
secrets = SecretsManager(enable_fallback=True)  # Fallback to env vars for dev

# Retrieve secrets
client_secret = secrets.get_secret("M365-CLIENT-SECRET")
api_key = secrets.get_secret("AZURE-OPENAI-API-KEY")
```

### GitHub Actions Workflow

```yaml
name: M365 Security Audit

on:
  workflow_dispatch:
  schedule:
    - cron: '0 2 1 * *'  # Monthly

permissions:
  id-token: write  # Required for OIDC
  contents: read

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Azure Login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run M365 audit
        env:
          AZURE_KEY_VAULT_URL: ${{ vars.AZURE_KEY_VAULT_URL }}
          M365_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          M365_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          # M365_CLIENT_SECRET is fetched from Key Vault automatically
        run: |
          python scripts/m365_cis_report.py
```

## Step 6: Migration Guide from Environment Variables

### Phase 1: Setup (Week 1)

1. Deploy Azure Key Vault in production subscription
2. Configure RBAC roles (`Key Vault Secrets User`)
3. Upload secrets to Key Vault
4. Configure GitHub OIDC federation

### Phase 2: Test in Staging (Week 2)

1. Deploy updated application to staging environment
2. Set `AZURE_KEY_VAULT_URL` environment variable
3. Verify secrets retrieved from Key Vault (check audit logs)
4. Test fallback to environment variables (disconnect from vault)

### Phase 3: Production Deployment (Week 3)

1. Deploy to production with `AZURE_KEY_VAULT_URL` configured
2. Monitor Azure Monitor logs for secret access
3. Validate all workflows executing successfully
4. Remove secrets from GitHub Secrets (retain only OIDC credentials)

### Phase 4: Cleanup (Week 4)

1. Remove environment variable fallbacks from production config
2. Disable fallback in `SecretsManager(enable_fallback=False)`
3. Update documentation to enforce Key Vault usage
4. Schedule quarterly access reviews for compliance

## Step 7: Audit Trail and Monitoring

### View Audit Logs (Azure Portal)

1. Navigate to **Key Vault** → **Monitoring** → **Logs**
2. Query for secret access:

```kusto
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.KEYVAULT"
| where OperationName == "SecretGet"
| project TimeGenerated, CallerIPAddress, identity_claim_oid_g, ResultSignature
| order by TimeGenerated desc
```

### Set Up Alerts

```bash
# Alert on failed secret access attempts
az monitor metrics alert create \
  --name "keyvault-failed-access" \
  --resource-group $RESOURCE_GROUP \
  --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME" \
  --condition "count(AzureDiagnostics | where ResultSignature == 'Unauthorized') > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action-group "security-team-alerts"
```

## Step 8: Key Rotation (Optional)

### Automated Rotation via Azure Functions

```bash
# Create function app for key rotation
az functionapp create \
  --name "m365-key-rotation" \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4

# Deploy rotation function (see Azure Functions documentation)
```

### Manual Rotation Process

1. Generate new client secret in Azure AD
2. Upload new secret to Key Vault with version suffix: `M365-CLIENT-SECRET-v2`
3. Update application to use new secret
4. Verify all services working with new secret
5. Delete old secret after 30-day grace period

## Troubleshooting

### Error: "Insufficient permissions to access Key Vault"

**Solution**: Verify RBAC role assignment:

```bash
az role assignment list \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME" \
  --assignee $USER_PRINCIPAL_ID \
  --query "[].roleDefinitionName" -o table
```

Should see **Key Vault Secrets User** or **Key Vault Secrets Officer**.

### Error: "Key Vault not found"

**Solution**: Verify vault URL format and DNS resolution:

```bash
# Test DNS resolution
nslookup $KEYVAULT_NAME.vault.azure.net

# Verify vault exists
az keyvault show --name $KEYVAULT_NAME --query properties.vaultUri -o tsv
```

### Application Still Using Environment Variables

**Solution**: Check logs for fallback warnings:

```python
# In application logs, look for:
# "Key Vault unavailable, using environment variable"
```

Ensure `AZURE_KEY_VAULT_URL` is set in deployment environment.

## Security Best Practices

1. **✅ Use RBAC, not access policies** (modern, least privilege)
2. **✅ Enable diagnostic logging** (365-day retention for SOX)
3. **✅ Use managed identities** (no credentials in code)
4. **✅ Restrict network access** (private endpoints for production)
5. **✅ Implement key rotation** (30-90 day rotation policy)
6. **✅ Monitor access patterns** (set up Azure Monitor alerts)
7. **✅ Use separate vaults per environment** (dev, staging, prod)
8. **✅ Tag resources** (for cost tracking and compliance)

## Compliance Checklist

- [ ] Azure Key Vault deployed with RBAC enabled
- [ ] Diagnostic logging enabled (365-day retention)
- [ ] Least privilege access (Secrets User role)
- [ ] Secrets uploaded with proper naming convention
- [ ] GitHub OIDC configured (no long-lived PATs)
- [ ] Application updated to use SecretsManager
- [ ] Fallback to environment variables tested
- [ ] Audit logs reviewed and validated
- [ ] Key rotation policy documented
- [ ] Quarterly access reviews scheduled

## Additional Resources

- [Azure Key Vault Documentation](https://learn.microsoft.com/en-us/azure/key-vault/)
- [GitHub OIDC with Azure](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure)
- [SOX Compliance Best Practices](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-sox)
- [Azure Key Vault Security Baseline](https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/key-vault-security-baseline)

---

**Questions or Issues?**

Open an issue in the repository or contact the security team for Key Vault access requests.
