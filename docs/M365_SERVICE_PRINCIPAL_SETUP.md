# M365 Service Principal Setup for Automated Auditing

## Overview

This guide provides step-by-step instructions for setting up Azure AD Service Principal authentication to enable automated M365 CIS security auditing without interactive login prompts.

## Prerequisites

- **Azure AD Global Administrator** or **Privileged Role Administrator** access
- **PowerShell 5.1+** with the following modules:
  - `Az.Accounts`
  - `Az.Resources`
  - `Microsoft.Graph.Authentication`
  - `ExchangeOnlineManagement`

## Step 1: Create Azure AD Application Registration

### Via Azure Portal

1. Navigate to **Azure Portal** → **Azure Active Directory** → **App registrations**
2. Click **"New registration"**
3. Configure the application:
   - **Name**: `M365-Security-Audit-Tool`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: Leave blank
4. Click **"Register"**

### Via PowerShell

```powershell
# Connect to Azure AD
Connect-AzAccount

# Create the application registration
$app = New-AzADApplication -DisplayName "M365-Security-Audit-Tool" -HomePage "https://localhost"

# Create a service principal
$sp = New-AzADServicePrincipal -ApplicationId $app.ApplicationId

Write-Host "Application ID: $($app.ApplicationId)"
Write-Host "Service Principal ID: $($sp.Id)"
```

## Step 2: Configure API Permissions

### Required Microsoft Graph Permissions

Add the following **Application permissions** (not Delegated):

#### Core Security Audit Permissions
- `Directory.Read.All` - Read directory data
- `Organization.Read.All` - Read organization information
- `Policy.Read.All` - Read organization policies
- `User.Read.All` - Read all users' profiles
- `Group.Read.All` - Read all groups
- `Application.Read.All` - Read applications

#### Advanced Security Permissions (Optional)
- `SecurityEvents.Read.All` - Read security events
- `ThreatIndicators.Read.All` - Read threat indicators
- `Reports.Read.All` - Read all usage reports

#### Intune Permissions (if using Intune checks)
- `DeviceManagementConfiguration.Read.All` - Read device configuration
- `DeviceManagementManagedDevices.Read.All` - Read managed devices

### PowerShell Configuration

```powershell
# Required permission scopes
$requiredScopes = @(
    "Directory.Read.All",
    "Organization.Read.All", 
    "Policy.Read.All",
    "User.Read.All",
    "Group.Read.All",
    "Application.Read.All"
)

# Get the Microsoft Graph service principal
$graphServicePrincipal = Get-AzADServicePrincipal -Filter "displayName eq 'Microsoft Graph'"

foreach ($scope in $requiredScopes) {
    $permission = $graphServicePrincipal.AppRole | Where-Object { $_.Value -eq $scope }
    if ($permission) {
        New-AzADAppRoleAssignment -ObjectId $sp.Id -PrincipalId $sp.Id -ResourceId $graphServicePrincipal.Id -Id $permission.Id
        Write-Host "✅ Assigned permission: $scope"
    }
}
```

## Step 3: Grant Admin Consent

### Via Azure Portal
1. Go to **App registrations** → Select your app → **API permissions**
2. Click **"Grant admin consent for [Your Organization]"**
3. Confirm by clicking **"Yes"**

### Via PowerShell
```powershell
# Grant admin consent for all configured permissions
$tenantId = (Get-AzContext).Tenant.Id
$appId = $app.ApplicationId

# This requires Global Administrator privileges
Start-Process "https://login.microsoftonline.com/$tenantId/adminconsent?client_id=$appId"
```

## Step 4: Create Application Secret

### Via Azure Portal
1. Go to **App registrations** → Select your app → **Certificates & secrets**
2. Click **"New client secret"**
3. Configure:
   - **Description**: `M365-Audit-Secret-2025`
   - **Expires**: `24 months` (recommended)
4. **Important**: Copy the secret value immediately - it won't be shown again

### Via PowerShell
```powershell
# Create a client secret (valid for 2 years)
$secretEndDate = (Get-Date).AddYears(2)
$secret = New-AzADAppCredential -ObjectId $app.Id -EndDate $secretEndDate

Write-Host "🔐 Client Secret: $($secret.SecretText)"
Write-Host "⚠️  Store this secret securely - it won't be displayed again!"
```

## Step 5: Assign Exchange Online Permissions

Service principals need explicit Exchange Online access:

```powershell
# Connect to Exchange Online as admin
Connect-ExchangeOnline -UserPrincipalName admin@yourtenant.onmicrosoft.com

# Create a new management role assignment
New-ManagementRoleAssignment -Role "View-Only Organization Management" -App $app.ApplicationId

# Verify the assignment
Get-ManagementRoleAssignment -GetEffectiveUsers | Where-Object {$_.User -like "*$($app.ApplicationId)*"}
```

## Step 6: Configure Audit Script

Update your audit configuration to use service principal authentication:

### Create Secure Configuration File

```powershell
# Create secure credential storage
$tenantId = "your-tenant-id"
$clientId = $app.ApplicationId
$clientSecret = $secret.SecretText

# Store in audit configuration
$auditConfig = @{
    TenantId = $tenantId
    ClientId = $clientId
    ClientSecret = $clientSecret | ConvertTo-SecureString -AsPlainText -Force
    SPOAdminUrl = "https://yourtenant-admin.sharepoint.com"
}

$auditConfig | Export-Clixml -Path "config/service_principal_config.xml"
```

### Update M365CIS Module

Add service principal connection function to `scripts/powershell/modules/M365CIS.psm1`:

```powershell
function Connect-M365CIS-ServicePrincipal {
    param(
        [Parameter(Mandatory=$true)]
        [string]$TenantId,
        
        [Parameter(Mandatory=$true)]
        [string]$ClientId,
        
        [Parameter(Mandatory=$true)]
        [SecureString]$ClientSecret
    )
    
    try {
        # Convert SecureString to credential
        $credential = New-Object System.Management.Automation.PSCredential($ClientId, $ClientSecret)
        
        # Connect to Microsoft Graph
        Connect-MgGraph -TenantId $TenantId -ClientSecretCredential $credential -NoWelcome
        
        # Connect to Exchange Online
        Connect-ExchangeOnline -AppId $ClientId -CertificateThumbprint $TenantId -Organization "$TenantId.onmicrosoft.com" -ShowBanner:$false
        
        Write-Host "✅ Successfully connected to M365 services using service principal" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "❌ Failed to connect using service principal: $($_.Exception.Message)"
        return $false
    }
}
```

## Step 7: Test Automated Connection

Create a test script to validate the setup:

```powershell
# Test service principal authentication
$config = Import-Clixml -Path "config/service_principal_config.xml"

if (Connect-M365CIS-ServicePrincipal -TenantId $config.TenantId -ClientId $config.ClientId -ClientSecret $config.ClientSecret) {
    
    # Test Graph API access
    $org = Get-MgOrganization
    Write-Host "✅ Organization: $($org.DisplayName)"
    
    # Test Exchange Online access
    $domains = Get-AcceptedDomain
    Write-Host "✅ Exchange domains: $($domains.Count)"
    
    # Run a sample CIS check
    $result = Test-CIS-EXO-PasswordPolicy
    Write-Host "✅ Sample audit result: $($result.Status)"
    
} else {
    Write-Error "❌ Service principal authentication failed"
}
```

## Step 8: Update GitHub Actions Secrets

For automated CI/CD auditing, add these secrets to your GitHub repository:

1. Go to **GitHub** → **Your Repository** → **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:
   - `AZURE_TENANT_ID`: Your tenant ID
   - `AZURE_CLIENT_ID`: Application (client) ID
   - `AZURE_CLIENT_SECRET`: Client secret value

### Update GitHub Actions Workflow

Modify `.github/workflows/m365-automated-audit.yml`:

```yaml
jobs:
  automated-audit:
    runs-on: windows-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Setup PowerShell modules
      shell: powershell
      run: |
        Install-Module -Name Microsoft.Graph.Authentication -Force -Scope CurrentUser
        Install-Module -Name ExchangeOnlineManagement -Force -Scope CurrentUser
    
    - name: Run M365 CIS Audit
      shell: powershell
      env:
        AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
        AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
        AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      run: |
        # Convert secret to SecureString
        $secureSecret = ConvertTo-SecureString $env:AZURE_CLIENT_SECRET -AsPlainText -Force
        
        # Import audit module
        Import-Module "scripts/powershell/modules/M365CIS.psm1" -Force
        
        # Connect using service principal
        Connect-M365CIS-ServicePrincipal -TenantId $env:AZURE_TENANT_ID -ClientId $env:AZURE_CLIENT_ID -ClientSecret $secureSecret
        
        # Run the audit
        $results = Invoke-M365CISAudit -Timestamped
        
        # Export results
        $results | ConvertTo-Json -Depth 10 | Out-File "output/reports/security/automated-audit-$(Get-Date -Format 'yyyy-MM-dd-HHmm').json"
```

## Security Best Practices

### Secret Management
- **Never commit secrets to code** - Use secure storage (Azure Key Vault, GitHub Secrets)
- **Rotate secrets regularly** - Set 12-24 month expiration periods
- **Use certificate-based authentication** when possible (more secure than secrets)
- **Monitor service principal usage** in Azure AD sign-in logs

### Least Privilege Access
- **Only assign required permissions** - Start minimal, add as needed
- **Use Application permissions** - Not Delegated permissions for automated scenarios
- **Regular access reviews** - Audit service principal permissions quarterly

### Monitoring & Alerting
- **Enable Azure AD audit logs** - Monitor service principal sign-ins
- **Set up alerts** for failed authentication attempts
- **Log audit execution** in your monitoring system

## Troubleshooting

### Common Issues

#### "Insufficient privileges to complete the operation"
- **Cause**: Missing admin consent or required permissions
- **Solution**: Grant admin consent and verify all permissions are assigned

#### "AADSTS700016: Application with identifier 'xxx' was not found"
- **Cause**: Incorrect client ID or application not found
- **Solution**: Verify the client ID matches your app registration

#### "AADSTS7000215: Invalid client secret is provided"
- **Cause**: Expired or incorrect client secret
- **Solution**: Generate a new client secret and update configuration

#### Exchange Online connection fails
- **Cause**: Service principal lacks Exchange permissions
- **Solution**: Assign "View-Only Organization Management" role

### Diagnostic Commands

```powershell
# Check service principal permissions
Get-AzADServicePrincipal -ApplicationId $clientId | Get-AzADServicePrincipalAppRoleAssignment

# Test Graph API connectivity
Test-MgGraph

# Verify Exchange Online role assignments
Get-ManagementRoleAssignment -GetEffectiveUsers | Where-Object {$_.User -like "*$clientId*"}
```

## Conclusion

With proper service principal configuration, the M365 Security Toolkit can run automated audits without interactive authentication, enabling:

- **Scheduled auditing** via GitHub Actions or Azure Automation
- **Continuous compliance monitoring** with automated reports
- **Enterprise-scale deployment** across multiple tenants
- **Integration** with SIEM and monitoring platforms

For additional support, refer to the [Microsoft Graph authentication documentation](https://docs.microsoft.com/en-us/graph/auth/auth-concepts) and [Exchange Online PowerShell documentation](https://docs.microsoft.com/en-us/powershell/exchange/app-only-auth-powershell-v2).
# Microsoft 365 Service Principal Setup for MCP Server

This guide will help you set up a Microsoft 365 service principal for the MCP server integration.

## Overview

The MCP server requires a service principal (app registration) in Azure AD to access Microsoft 365 APIs securely. This setup provides the necessary credentials for authentication.

## Prerequisites

- Azure AD tenant with administrative access
- Global Administrator or Application Administrator role
- Access to Azure portal (portal.azure.com)

## Step 1: Create App Registration

1. **Navigate to Azure Portal**
   - Go to [Azure Portal](https://portal.azure.com)
   - Sign in with your administrator account

2. **Access App Registrations**
   - Search for "App registrations" in the search bar
   - Click on "App registrations" service

3. **Create New Registration**
   - Click "New registration"
   - Fill in the following details:
     ```
     Name: M365 Security Toolkit MCP Server
     Supported account types: Accounts in this organizational directory only
     Redirect URI: Not required for this setup
     ```
   - Click "Register"

## Step 2: Get Application Details

After creating the app registration, you'll need three key values:

### Tenant ID
1. In the app registration overview page
2. Copy the "Directory (tenant) ID" value
3. This will be your `M365_TENANT_ID`

### Client ID
1. In the same overview page
2. Copy the "Application (client) ID" value
3. This will be your `M365_CLIENT_ID`

### Client Secret
1. Go to "Certificates & secrets" in the left menu
2. Click "New client secret"
3. Add description: "MCP Server Secret"
4. Set expiration (recommended: 24 months)
5. Click "Add"
6. **IMPORTANT**: Copy the secret value immediately (it won't be shown again)
7. This will be your `M365_CLIENT_SECRET`

## Step 3: Configure API Permissions

The MCP server needs specific permissions to access Microsoft 365 data:

1. **Go to API Permissions**
   - Click "API permissions" in the left menu
   - Click "Add a permission"

2. **Add Microsoft Graph Permissions**
   - Select "Microsoft Graph"
   - Choose "Application permissions"
   - Add the following permissions:
     ```
     Directory.Read.All
     Organization.Read.All
     Policy.Read.All
     User.Read.All
     SecurityEvents.Read.All
     AuditLog.Read.All
     Reports.Read.All
     ```

3. **Grant Admin Consent**
   - Click "Grant admin consent for [Your Organization]"
   - Click "Yes" to confirm
   - Ensure all permissions show "Granted" status

## Step 4: Configure Environment Variables

1. **Open your .env file**
   ```bash
   notepad .env
   ```

2. **Replace the placeholder values**
   ```env
   # Microsoft 365 Configuration
   M365_TENANT_ID=your-actual-tenant-id-here
   M365_CLIENT_ID=your-actual-client-id-here
   M365_CLIENT_SECRET=your-actual-client-secret-here
   ```

3. **Save the file**

## Step 5: Test the Connection

Run the MCP server test to verify your configuration:

```powershell
python setup_mcp_server.py --test-connection
```

If successful, you'll see:
```
✅ MCP Server Dependencies: Installed
✅ Environment Configuration: Valid
✅ Microsoft Graph Connection: Successful
✅ MCP Server: Ready for use
```

## Security Best Practices

### 🔒 **Credential Security**
- Never commit the `.env` file with real credentials to version control
- Store credentials securely (consider Azure Key Vault for production)
- Rotate client secrets regularly (every 12-24 months)

### 🛡️ **Access Control**
- Use least privilege principle
- Regularly review app permissions
- Monitor app usage in Azure AD logs

### 📋 **Compliance**
- Document app registration for compliance audits
- Include in your organization's app inventory
- Follow your organization's app governance policies

## Troubleshooting

### Common Issues

**Authentication Failed**
- Verify tenant ID, client ID, and client secret are correct
- Check that admin consent was granted for all permissions
- Ensure the service principal is not disabled

**Permission Denied**
- Verify all required API permissions are granted
- Check that admin consent was properly applied
- Confirm your account has sufficient privileges

**Connection Timeout**
- Check network connectivity
- Verify firewall settings allow Microsoft Graph API access
- Try again after a few minutes (temporary service issues)

### Getting Help

If you encounter issues:
1. Check the error messages in the MCP server logs
2. Verify permissions in Azure portal
3. Test with a simple Graph API call manually
4. Consult Microsoft Graph documentation

## Next Steps

Once your service principal is configured:

1. **Test MCP Integration**
   ```powershell
   python scripts/test_mcp_integration.py
   ```

2. **Run Security Audit**
   ```powershell
   python -m src.mcp.m365_security_server --audit
   ```

3. **Explore Available Tools**
   - User enumeration and analysis
   - Security policy assessment
   - Conditional access review
   - Audit log analysis

## Reference Links

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/)
- [Azure App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Microsoft Graph Permissions Reference](https://docs.microsoft.com/en-us/graph/permissions-reference)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)

---

**Security Notice**: This service principal will have read access to your Microsoft 365 tenant data. Ensure proper security controls and monitoring are in place.