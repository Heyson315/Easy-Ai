<#
.SYNOPSIS
Create a service principal scoped to a subscription and print .env lines for local use.

.DESCRIPTION
This script uses Az PowerShell cmdlets to create a service principal, create a client secret
and print environment variable lines you can paste into your local `.env` file. It does not
persist secrets to disk.

Usage:
  pwsh ./scripts/create_sp.ps1 -Name "mcp-sp" -SubscriptionId <id>

Parameters:
  -Name           Service principal display name (default: mcp-sp-<timestamp>)
  -SubscriptionId Subscription id to scope the role assignment (default: current context)
  -Role           Role to assign (default: Contributor)
  -Years          Secret lifetime in years (default: 2)
#>

param(
    [string]$Name = "mcp-sp-$(Get-Date -Format yyyyMMddHHmmss)",
    [string]$SubscriptionId = "",
    [string]$Role = "Contributor",
    [int]$Years = 2
)

try {
    Import-Module Az.Accounts -ErrorAction Stop
} catch {
    Write-Error "Az module not available. Install with: Install-Module -Name Az -Scope CurrentUser"
    exit 1
}

# Ensure logged in
if (-not (Get-AzContext)) {
    Write-Host "Not logged in. Running 'Connect-AzAccount'..."
    Connect-AzAccount -ErrorAction Stop
}

if (-not $SubscriptionId -or $SubscriptionId -eq "") {
    $SubscriptionId = (Get-AzContext).Subscription.Id
}

Write-Host "Using subscription: $SubscriptionId"

# Build scope
$scope = "/subscriptions/$SubscriptionId"

Write-Host "Ensuring Azure AD application for '$Name' exists..."


# Try to find existing application by exact display name
$app = Get-AzADApplication -DisplayNameStartWith $Name -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -eq $Name }
if ($app -is [System.Array]) { $app = $app[0] }
if (-not $app) {
    Write-Host "Application not found by exact name, creating new Azure AD application..."
    $app = New-AzADApplication -DisplayName $Name -ErrorAction Stop
}

if ($app -is [System.Array]) { $app = $app[0] }
if (-not $app) {
    Write-Error "Failed to create or find Azure AD application"
    exit 1
}

$appId = $app.AppId.ToString()
Write-Host "Application Id: $appId"

# Create service principal for the application if it doesn't exist
try {
    $sp = Get-AzADServicePrincipal -ApplicationId ([guid]$appId) -ErrorAction Stop
} catch {
    $sp = $null
}

if (-not $sp) {
    Write-Host "Service principal for app not found, creating..."
    $sp = New-AzADServicePrincipal -ApplicationId ([guid]$appId) -ErrorAction Stop
    # Assign role at scope
    New-AzRoleAssignment -ObjectId $sp.Id -RoleDefinitionName $Role -Scope $scope -ErrorAction Stop
}

if (-not $sp) {
    Write-Error "Failed to create or find service principal"
    exit 1
}

# Generate a strong secret and create an app credential
$plainSecret = [System.Guid]::NewGuid().ToString() + (Get-Random -Maximum 99999)

# Try to use Az module to add credential; if it fails, fallback to Azure CLI
try {
    $secureSecret = ConvertTo-SecureString -String $plainSecret -AsPlainText -Force
    New-AzADAppCredential -ApplicationId $appId -Password $secureSecret -EndDate (Get-Date).AddYears($Years) -ErrorAction Stop
} catch {
    Write-Warning "New-AzADAppCredential failed, attempting to set credential via Azure CLI. Ensure 'az' is installed and you are logged in."
    try {
        az ad app credential reset --id $appId --password $plainSecret --years $Years | Out-Null
    } catch {
        Write-Error "Failed to create app credential via Az module and Azure CLI: $_"
        exit 1
    }
}

Write-Host "Service principal created successfully.`n"

# Option 1: Upload secrets to Azure Key Vault (recommended for SOX compliance)
Write-Host "# ---- SOX Compliance: Azure Key Vault Setup ----`n" -ForegroundColor Green
Write-Host "For SOX/AICPA compliance, secrets should be stored in Azure Key Vault." -ForegroundColor Yellow
Write-Host ""
$uploadToKeyVault = Read-Host "Upload secrets to Azure Key Vault? (y/n)"

if ($uploadToKeyVault -eq 'y') {
    $keyVaultName = Read-Host "Enter your Key Vault name (e.g., my-vault)"
    
    try {
        Write-Host "Uploading secrets to Key Vault '$keyVaultName'..." -ForegroundColor Cyan
        
        # Upload M365 credentials to Key Vault
        az keyvault secret set --vault-name $keyVaultName --name "M365-TENANT-ID" --value $tenantId | Out-Null
        az keyvault secret set --vault-name $keyVaultName --name "M365-CLIENT-ID" --value $appId | Out-Null
        az keyvault secret set --vault-name $keyVaultName --name "M365-CLIENT-SECRET" --value $plainSecret | Out-Null
        
        Write-Host "✅ Secrets uploaded to Key Vault successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Add this to your .env file:" -ForegroundColor Yellow
        Write-Host "AZURE_KEY_VAULT_URL=https://$keyVaultName.vault.azure.net/"
        Write-Host ""
        Write-Host "Secrets are now stored securely in Azure Key Vault with hardware-backed encryption." -ForegroundColor Green
        Write-Host "Audit logs available in Azure Monitor for compliance tracking." -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to upload to Key Vault: $_" -ForegroundColor Red
        Write-Host "Ensure you have 'az' CLI installed and appropriate permissions." -ForegroundColor Yellow
        Write-Host "Falling back to environment variable display..." -ForegroundColor Yellow
        $uploadToKeyVault = 'n'
    }
}

# Option 2: Display secrets for manual .env entry (fallback)
if ($uploadToKeyVault -ne 'y') {
    Write-Host "# ---- Paste these into your .env (keep them secret) ----`n"
    Write-Host "M365_TENANT_ID=$tenantId"
    Write-Host "M365_CLIENT_ID=$appId"
    Write-Host "M365_CLIENT_SECRET=$plainSecret"
    Write-Host "AZURE_SUBSCRIPTION_ID=$SubscriptionId"
    Write-Host "# -----------------------------------------------------`n"
    Write-Host "⚠️  WARNING: Environment variables do not meet SOX/AICPA compliance requirements." -ForegroundColor Yellow
    Write-Host "    Consider migrating to Azure Key Vault for hardware-backed key storage." -ForegroundColor Yellow
}

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1) Grant Microsoft Graph application permissions in the Azure Portal for the app registration (API permissions → Microsoft Graph → Application permissions) and grant admin consent."
if ($uploadToKeyVault -eq 'y') {
    Write-Host "2) Configure RBAC: Assign 'Key Vault Secrets User' role to your service principal or managed identity."
    Write-Host "3) Set AZURE_KEY_VAULT_URL environment variable in your deployment environment."
} else {
    Write-Host "2) Add the printed variables to your local .env file (do NOT commit .env)."
}
Write-Host "3) Restart your devcontainer / docker-compose so the container picks up the new env vars."
