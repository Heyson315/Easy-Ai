#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Configure M365 Service Principal for Production Deployment

.DESCRIPTION
    This script creates and configures an Azure AD service principal with the required
    permissions for the M365 Security Toolkit to access Microsoft 365 services.

.PARAMETER AppName
    Name for the Azure AD application registration

.PARAMETER TenantId
    Azure AD tenant ID (optional - will be detected if not provided)

.PARAMETER KeyVaultName
    Name of the Key Vault to store credentials

.PARAMETER CertificatePath
    Path to certificate file for certificate-based authentication (optional)

.PARAMETER Interactive
    Use interactive authentication for setup

.EXAMPLE
    .\Setup-M365ServicePrincipal.ps1 -AppName "M365-Security-Toolkit-Prod" -KeyVaultName "kv-m365-security-toolkit"

.NOTES
    Author: M365 Security Toolkit Team
    Version: 1.0.0
    Requires: Microsoft Graph PowerShell, Azure PowerShell
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$AppName,
    
    [Parameter(Mandatory = $false)]
    [string]$TenantId,
    
    [Parameter(Mandatory = $true)]
    [string]$KeyVaultName,
    
    [Parameter(Mandatory = $false)]
    [string]$CertificatePath,
    
    [Parameter(Mandatory = $false)]
    [switch]$Interactive
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Banner {
    param([string]$Message)
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Test-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Blue
    
    # Check Microsoft Graph PowerShell
    try {
        Import-Module Microsoft.Graph.Applications -Force -ErrorAction Stop
        Import-Module Microsoft.Graph.Authentication -Force -ErrorAction Stop
        Write-Host "✅ Microsoft Graph PowerShell modules loaded" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Microsoft Graph PowerShell not found. Install: Install-Module Microsoft.Graph -Scope CurrentUser"
        exit 1
    }
    
    # Check Azure PowerShell
    try {
        Import-Module Az.KeyVault -Force -ErrorAction Stop
        Write-Host "✅ Azure PowerShell modules loaded" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Azure PowerShell not found. Install: Install-Module Az -Scope CurrentUser"
        exit 1
    }
}

function Connect-ToServices {
    Write-Host "🔐 Connecting to Microsoft services..." -ForegroundColor Blue
    
    # Connect to Microsoft Graph with required scopes
    $graphScopes = @(
        "Application.ReadWrite.All",
        "Directory.ReadWrite.All", 
        "AppRoleAssignment.ReadWrite.All"
    )
    
    try {
        if ($TenantId) {
            Connect-MgGraph -TenantId $TenantId -Scopes $graphScopes -ErrorAction Stop
        }
        else {
            Connect-MgGraph -Scopes $graphScopes -ErrorAction Stop
        }
        
        $context = Get-MgContext
        Write-Host "✅ Connected to Microsoft Graph (Tenant: $($context.TenantId))" -ForegroundColor Green
        
        # Set TenantId if not provided
        if (-not $TenantId) {
            $script:TenantId = $context.TenantId
        }
    }
    catch {
        Write-Error "❌ Failed to connect to Microsoft Graph: $_"
        exit 1
    }
    
    # Connect to Azure
    try {
        if ($TenantId) {
            Connect-AzAccount -TenantId $TenantId -ErrorAction Stop | Out-Null
        }
        else {
            Connect-AzAccount -ErrorAction Stop | Out-Null
        }
        Write-Host "✅ Connected to Azure" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to connect to Azure: $_"
        exit 1
    }
}

function New-ServicePrincipal {
    Write-Host "📝 Creating service principal..." -ForegroundColor Blue
    
    try {
        # Check if app already exists
        $existingApp = Get-MgApplication -Filter "displayName eq '$AppName'" -ErrorAction SilentlyContinue
        if ($existingApp) {
            Write-Host "⚠️ Application '$AppName' already exists. Using existing application." -ForegroundColor Yellow
            $app = $existingApp
        }
        else {
            # Create new application
            $appParams = @{
                DisplayName = $AppName
                Description = "M365 Security Toolkit - Production Service Principal"
                SignInAudience = "AzureADMyOrg"
                Web = @{
                    RedirectUris = @("https://localhost:8080/auth/callback")
                }
                RequiredResourceAccess = @(
                    # Microsoft Graph permissions
                    @{
                        ResourceAppId = "00000003-0000-0000-c000-000000000000"  # Microsoft Graph
                        ResourceAccess = @(
                            @{ Id = "df021288-bdef-4463-88db-98f22de89214"; Type = "Role" },  # User.Read.All
                            @{ Id = "246dd0d5-5bd0-4def-940b-0421030a5b68"; Type = "Role" },  # Policy.Read.All
                            @{ Id = "7ab1d382-f21e-4acd-a863-ba3e13f7da61"; Type = "Role" },  # Directory.Read.All
                            @{ Id = "498476ce-e0fe-48b0-b801-37ba7e2685c6"; Type = "Role" },  # Organization.Read.All
                            @{ Id = "b0afded3-3588-46d8-8b3d-9842eff778da"; Type = "Role" },  # AuditLog.Read.All
                            @{ Id = "bf394140-e372-4bf9-a898-299cfc7564e5"; Type = "Role" },  # SecurityEvents.Read.All
                            @{ Id = "332a536c-c7ef-4017-ab91-336970924f0d"; Type = "Role" }   # Sites.Read.All
                        )
                    }
                )
            }
            
            $app = New-MgApplication @appParams
            Write-Host "✅ Created application: $($app.DisplayName)" -ForegroundColor Green
        }
        
        # Create or get service principal
        $servicePrincipal = Get-MgServicePrincipal -Filter "appId eq '$($app.AppId)'" -ErrorAction SilentlyContinue
        if (-not $servicePrincipal) {
            $servicePrincipal = New-MgServicePrincipal -AppId $app.AppId -DisplayName $AppName
            Write-Host "✅ Created service principal" -ForegroundColor Green
        }
        else {
            Write-Host "✅ Service principal already exists" -ForegroundColor Green
        }
        
        return @{
            Application = $app
            ServicePrincipal = $servicePrincipal
        }
    }
    catch {
        Write-Error "❌ Failed to create service principal: $_"
        exit 1
    }
}

function New-ClientSecret {
    param([object]$Application)
    
    Write-Host "🔑 Creating client secret..." -ForegroundColor Blue
    
    try {
        # Create client secret (valid for 2 years)
        $secretParams = @{
            ApplicationId = $Application.Id
            PasswordCredential = @{
                DisplayName = "Production Secret - $(Get-Date -Format 'yyyy-MM-dd')"
                EndDateTime = (Get-Date).AddYears(2)
            }
        }
        
        $secret = Add-MgApplicationPassword @secretParams
        Write-Host "✅ Client secret created (expires: $($secret.EndDateTime))" -ForegroundColor Green
        
        return $secret.SecretText
    }
    catch {
        Write-Error "❌ Failed to create client secret: $_"
        exit 1
    }
}

function Grant-AdminConsent {
    param([object]$ServicePrincipal)
    
    Write-Host "🔐 Granting admin consent for API permissions..." -ForegroundColor Blue
    
    try {
        # Get Microsoft Graph service principal
        $graphServicePrincipal = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"
        
        # Required permission IDs
        $requiredPermissions = @(
            "df021288-bdef-4463-88db-98f22de89214",  # User.Read.All
            "246dd0d5-5bd0-4def-940b-0421030a5b68",  # Policy.Read.All
            "7ab1d382-f21e-4acd-a863-ba3e13f7da61",  # Directory.Read.All
            "498476ce-e0fe-48b0-b801-37ba7e2685c6",  # Organization.Read.All
            "b0afded3-3588-46d8-8b3d-9842eff778da",  # AuditLog.Read.All
            "bf394140-e372-4bf9-a898-299cfc7564e5",  # SecurityEvents.Read.All
            "332a536c-c7ef-4017-ab91-336970924f0d"   # Sites.Read.All
        )
        
        foreach ($permissionId in $requiredPermissions) {
            try {
                # Check if consent already granted
                $existingGrant = Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $ServicePrincipal.Id -ErrorAction SilentlyContinue | 
                    Where-Object { $_.AppRoleId -eq $permissionId }
                
                if (-not $existingGrant) {
                    $grantParams = @{
                        ServicePrincipalId = $ServicePrincipal.Id
                        AppRoleAssignment = @{
                            PrincipalId = $ServicePrincipal.Id
                            ResourceId = $graphServicePrincipal.Id
                            AppRoleId = $permissionId
                        }
                    }
                    
                    New-MgServicePrincipalAppRoleAssignment @grantParams | Out-Null
                    Write-Host "✅ Granted permission: $permissionId" -ForegroundColor Green
                }
                else {
                    Write-Host "✅ Permission already granted: $permissionId" -ForegroundColor Green
                }
            }
            catch {
                Write-Warning "⚠️ Failed to grant permission $permissionId : $_"
            }
        }
        
        Write-Host "✅ Admin consent process completed" -ForegroundColor Green
    }
    catch {
        Write-Warning "⚠️ Failed to grant admin consent automatically. Manual consent may be required: $_"
        Write-Host "Please visit: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/CallAnAPI/appId/$($ServicePrincipal.AppId)" -ForegroundColor Yellow
    }
}

function Set-KeyVaultCredentials {
    param(
        [string]$TenantId,
        [string]$ApplicationId,
        [string]$ClientSecret
    )
    
    Write-Host "💾 Storing credentials in Key Vault..." -ForegroundColor Blue
    
    try {
        # Store M365 credentials
        $secrets = @{
            "M365-TenantId" = $TenantId
            "M365-ApplicationId" = $ApplicationId
            "M365-ClientSecret" = $ClientSecret
        }
        
        foreach ($secretName in $secrets.Keys) {
            $secureValue = ConvertTo-SecureString $secrets[$secretName] -AsPlainText -Force
            Set-AzKeyVaultSecret -VaultName $KeyVaultName -Name $secretName -SecretValue $secureValue | Out-Null
            Write-Host "✅ Stored secret: $secretName" -ForegroundColor Green
        }
        
        Write-Host "✅ All credentials stored in Key Vault" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to store credentials in Key Vault: $_"
        
        # Provide manual instructions
        Write-Host "Manual Key Vault configuration required:" -ForegroundColor Yellow
        Write-Host "Tenant ID: $TenantId" -ForegroundColor Cyan
        Write-Host "Application ID: $ApplicationId" -ForegroundColor Cyan
        Write-Host "Client Secret: [HIDDEN - Check console output above]" -ForegroundColor Cyan
    }
}

function Test-ServicePrincipal {
    param(
        [string]$TenantId,
        [string]$ApplicationId,
        [string]$ClientSecret
    )
    
    Write-Host "🧪 Testing service principal authentication..." -ForegroundColor Blue
    
    try {
        # Test Graph API access
        $secureSecret = ConvertTo-SecureString $ClientSecret -AsPlainText -Force
        $credential = New-Object System.Management.Automation.PSCredential($ApplicationId, $secureSecret)
        
        Disconnect-MgGraph -ErrorAction SilentlyContinue
        Connect-MgGraph -TenantId $TenantId -ClientSecretCredential $credential -ErrorAction Stop
        
        # Test a basic Graph API call
        $organization = Get-MgOrganization -ErrorAction Stop
        Write-Host "✅ Service principal authentication successful" -ForegroundColor Green
        Write-Host "✅ Organization: $($organization[0].DisplayName)" -ForegroundColor Green
        
        Disconnect-MgGraph
        return $true
    }
    catch {
        Write-Warning "⚠️ Service principal authentication test failed: $_"
        Write-Host "This may be due to pending admin consent or permission propagation delays" -ForegroundColor Yellow
        return $false
    }
}

function Show-Summary {
    param(
        [object]$Application,
        [string]$TenantId,
        [string]$ClientSecret
    )
    
    Write-Host ""
    Write-Host "📋 Service Principal Configuration Summary" -ForegroundColor Yellow
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "Application Name: $($Application.DisplayName)" -ForegroundColor White
    Write-Host "Application ID: $($Application.AppId)" -ForegroundColor White
    Write-Host "Tenant ID: $TenantId" -ForegroundColor White
    Write-Host "Object ID: $($Application.Id)" -ForegroundColor White
    Write-Host "Client Secret: [Stored in Key Vault]" -ForegroundColor White
    Write-Host ""
    Write-Host "🔗 Management Links:" -ForegroundColor Yellow
    Write-Host "Azure Portal: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Overview/appId/$($Application.AppId)" -ForegroundColor Cyan
    Write-Host "API Permissions: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/CallAnAPI/appId/$($Application.AppId)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Verify API permissions have admin consent" -ForegroundColor White
    Write-Host "2. Test authentication with the M365 Security Toolkit" -ForegroundColor White
    Write-Host "3. Configure any additional permissions as needed" -ForegroundColor White
    Write-Host "4. Set up monitoring and alerts for the service principal" -ForegroundColor White
    Write-Host ""
}

# Main execution
try {
    Write-Banner "M365 Security Toolkit - Service Principal Setup"
    
    Write-Host "🎯 Configuration:" -ForegroundColor Blue
    Write-Host "  Application Name: $AppName" -ForegroundColor Cyan
    Write-Host "  Key Vault: $KeyVaultName" -ForegroundColor Cyan
    Write-Host "  Tenant ID: $(if ($TenantId) { $TenantId } else { 'Auto-detect' })" -ForegroundColor Cyan
    Write-Host ""
    
    if (-not $Interactive) {
        $confirm = Read-Host "Do you want to proceed with service principal creation? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Host "❌ Setup cancelled by user" -ForegroundColor Yellow
            exit 0
        }
    }
    
    Test-Prerequisites
    Connect-ToServices
    
    $spResult = New-ServicePrincipal
    $clientSecret = New-ClientSecret -Application $spResult.Application
    Grant-AdminConsent -ServicePrincipal $spResult.ServicePrincipal
    Set-KeyVaultCredentials -TenantId $TenantId -ApplicationId $spResult.Application.AppId -ClientSecret $clientSecret
    
    # Test the service principal
    Write-Host ""
    Test-ServicePrincipal -TenantId $TenantId -ApplicationId $spResult.Application.AppId -ClientSecret $clientSecret
    
    Show-Summary -Application $spResult.Application -TenantId $TenantId -ClientSecret $clientSecret
    
    Write-Host "✅ Service principal setup completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "❌ Service principal setup failed: $_" -ForegroundColor Red
    Write-Host "Stack trace:" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}