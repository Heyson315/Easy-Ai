#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy M365 Security Toolkit Production Infrastructure

.DESCRIPTION
    This script automates the deployment of Azure infrastructure for the M365 Security Toolkit
    including storage, monitoring, security, and container hosting capabilities.

.PARAMETER SubscriptionId
    Azure subscription ID for deployment

.PARAMETER ResourceGroupName
    Name of the Azure resource group (will be created if it doesn't exist)

.PARAMETER Location
    Azure region for resource deployment

.PARAMETER AdminUserPrincipalName
    UPN of the administrator user for Key Vault access

.PARAMETER ProjectName
    Project name used for resource naming (default: m365-security-toolkit)

.PARAMETER Environment
    Environment designation (dev, test, prod)

.PARAMETER WhatIf
    Preview deployment without making changes

.EXAMPLE
    .\Deploy-Infrastructure.ps1 -SubscriptionId "12345678-1234-1234-1234-123456789012" -ResourceGroupName "rg-m365-security-prod" -AdminUserPrincipalName "admin@contoso.com"

.EXAMPLE
    .\Deploy-Infrastructure.ps1 -SubscriptionId "12345678-1234-1234-1234-123456789012" -ResourceGroupName "rg-m365-security-prod" -AdminUserPrincipalName "admin@contoso.com" -WhatIf

.NOTES
    Author: M365 Security Toolkit Team
    Version: 1.0.0
    Requires: Azure PowerShell module, appropriate Azure permissions
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $false)]
    [string]$Location = "East US 2",
    
    [Parameter(Mandatory = $true)]
    [string]$AdminUserPrincipalName,
    
    [Parameter(Mandatory = $false)]
    [string]$ProjectName = "m365-security-toolkit",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment = "prod",
    
    [Parameter(Mandatory = $false)]
    [switch]$WhatIf
)

# Error handling
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Script configuration
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$TemplateFile = Join-Path $ScriptPath "main-infrastructure.json"
$DeploymentName = "M365SecurityToolkit-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

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
    
    # Check if Azure PowerShell is installed
    try {
        Import-Module Az -Force -ErrorAction Stop
        Write-Host "✅ Azure PowerShell module loaded" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Azure PowerShell module not found. Please install: Install-Module -Name Az -Scope CurrentUser"
        exit 1
    }
    
    # Check if template file exists
    if (-not (Test-Path $TemplateFile)) {
        Write-Error "❌ ARM template not found at: $TemplateFile"
        exit 1
    }
    Write-Host "✅ ARM template found" -ForegroundColor Green
    
    # Validate template
    try {
        Get-Content $TemplateFile -Raw | ConvertFrom-Json | Out-Null
        Write-Host "✅ ARM template is valid JSON" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ ARM template is not valid JSON: $_"
        exit 1
    }
}

function Connect-ToAzure {
    Write-Host "🔐 Connecting to Azure..." -ForegroundColor Blue
    
    try {
        # Check if already connected
        $context = Get-AzContext
        if ($context -and $context.Subscription.Id -eq $SubscriptionId) {
            Write-Host "✅ Already connected to subscription: $($context.Subscription.Name)" -ForegroundColor Green
            return
        }
    }
    catch {
        # Not connected, need to authenticate
    }
    
    try {
        Connect-AzAccount -SubscriptionId $SubscriptionId -ErrorAction Stop
        Write-Host "✅ Connected to Azure subscription: $SubscriptionId" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to connect to Azure: $_"
        exit 1
    }
}

function New-ResourceGroupIfNotExists {
    Write-Host "📦 Checking resource group..." -ForegroundColor Blue
    
    $resourceGroup = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue
    
    if (-not $resourceGroup) {
        if ($WhatIf) {
            Write-Host "🔍 WHAT-IF: Would create resource group: $ResourceGroupName in $Location" -ForegroundColor Yellow
        }
        else {
            Write-Host "📦 Creating resource group: $ResourceGroupName" -ForegroundColor Blue
            $resourceGroup = New-AzResourceGroup -Name $ResourceGroupName -Location $Location -Tag @{
                Environment = $Environment
                Application = "M365SecurityToolkit"
                CreatedBy = "PowerShell-Deployment"
                CreatedDate = (Get-Date -Format "yyyy-MM-dd")
            }
            Write-Host "✅ Resource group created: $($resourceGroup.ResourceGroupName)" -ForegroundColor Green
        }
    }
    else {
        Write-Host "✅ Resource group exists: $($resourceGroup.ResourceGroupName)" -ForegroundColor Green
    }
}

function Get-AdminUserObjectId {
    param([string]$UserPrincipalName)
    
    Write-Host "👤 Looking up admin user object ID..." -ForegroundColor Blue
    
    try {
        # Try using Azure AD PowerShell first
        try {
            Import-Module AzureAD -ErrorAction Stop
            $user = Get-AzureADUser -Filter "UserPrincipalName eq '$UserPrincipalName'" -ErrorAction Stop
            if ($user) {
                Write-Host "✅ Found user via AzureAD module: $($user.DisplayName)" -ForegroundColor Green
                return $user.ObjectId
            }
        }
        catch {
            Write-Host "⚠️ AzureAD module not available, trying Microsoft.Graph..." -ForegroundColor Yellow
        }
        
        # Try using Microsoft Graph PowerShell
        try {
            Import-Module Microsoft.Graph.Users -ErrorAction Stop
            Connect-MgGraph -Scopes "User.Read.All" -ErrorAction Stop
            $user = Get-MgUser -Filter "UserPrincipalName eq '$UserPrincipalName'" -ErrorAction Stop
            if ($user) {
                Write-Host "✅ Found user via Microsoft.Graph: $($user.DisplayName)" -ForegroundColor Green
                return $user.Id
            }
        }
        catch {
            Write-Host "⚠️ Microsoft.Graph module not available or insufficient permissions" -ForegroundColor Yellow
        }
        
        # Fallback: ask user to provide Object ID manually
        Write-Host "❌ Could not automatically lookup user Object ID" -ForegroundColor Red
        Write-Host "Please find the Object ID for $UserPrincipalName in the Azure Portal:" -ForegroundColor Yellow
        Write-Host "Azure Portal > Azure Active Directory > Users > Search for user > Object ID" -ForegroundColor Yellow
        $objectId = Read-Host "Enter the Object ID"
        
        if ([string]::IsNullOrWhiteSpace($objectId) -or $objectId.Length -ne 36) {
            Write-Error "Invalid Object ID provided. Must be a valid GUID."
            exit 1
        }
        
        return $objectId
    }
    catch {
        Write-Error "❌ Failed to get admin user Object ID: $_"
        exit 1
    }
}

function Deploy-Infrastructure {
    Write-Host "🚀 Deploying infrastructure..." -ForegroundColor Blue
    
    # Get admin user Object ID
    $adminObjectId = Get-AdminUserObjectId -UserPrincipalName $AdminUserPrincipalName
    
    # Prepare deployment parameters
    $templateParameters = @{
        projectName = $ProjectName
        environment = $Environment
        location = $Location
        adminUserPrincipalName = $AdminUserPrincipalName
        adminObjectId = $adminObjectId
    }
    
    if ($WhatIf) {
        Write-Host "🔍 WHAT-IF: Validating deployment..." -ForegroundColor Yellow
        
        try {
            $validation = Test-AzResourceGroupDeployment `
                -ResourceGroupName $ResourceGroupName `
                -TemplateFile $TemplateFile `
                -TemplateParameterObject $templateParameters `
                -ErrorAction Stop
            
            if ($validation) {
                Write-Host "❌ Template validation failed:" -ForegroundColor Red
                $validation | ForEach-Object { Write-Host "  - $($_.Message)" -ForegroundColor Red }
                exit 1
            }
            else {
                Write-Host "✅ Template validation passed" -ForegroundColor Green
            }
        }
        catch {
            Write-Error "❌ Template validation failed: $_"
            exit 1
        }
        
        Write-Host "🔍 WHAT-IF: Would deploy the following resources:" -ForegroundColor Yellow
        Write-Host "  - Storage Account: st$($ProjectName.Replace('-',''))$Environment" -ForegroundColor Cyan
        Write-Host "  - Key Vault: kv-$ProjectName-$Environment" -ForegroundColor Cyan
        Write-Host "  - Log Analytics: law-$ProjectName-$Environment" -ForegroundColor Cyan
        Write-Host "  - Application Insights: ai-$ProjectName-$Environment" -ForegroundColor Cyan
        Write-Host "  - Container Registry: cr$($ProjectName.Replace('-',''))$Environment" -ForegroundColor Cyan
        Write-Host "  - Alert Rules: 2 metric alerts" -ForegroundColor Cyan
        return
    }
    
    try {
        Write-Host "📋 Deployment parameters:" -ForegroundColor Blue
        $templateParameters.GetEnumerator() | ForEach-Object {
            if ($_.Key -eq "adminObjectId") {
                Write-Host "  $($_.Key): $($_.Value.Substring(0,8))..." -ForegroundColor Cyan
            }
            else {
                Write-Host "  $($_.Key): $($_.Value)" -ForegroundColor Cyan
            }
        }
        
        $deployment = New-AzResourceGroupDeployment `
            -ResourceGroupName $ResourceGroupName `
            -Name $DeploymentName `
            -TemplateFile $TemplateFile `
            -TemplateParameterObject $templateParameters `
            -Mode Incremental `
            -Force `
            -ErrorAction Stop
        
        Write-Host "✅ Infrastructure deployment completed successfully!" -ForegroundColor Green
        
        # Display important outputs
        Write-Host "📋 Deployment outputs:" -ForegroundColor Blue
        if ($deployment.Outputs) {
            $deployment.Outputs.GetEnumerator() | ForEach-Object {
                if ($_.Key -like "*Key*" -or $_.Key -like "*Secret*") {
                    Write-Host "  $($_.Key): [HIDDEN]" -ForegroundColor Cyan
                }
                else {
                    Write-Host "  $($_.Key): $($_.Value.Value)" -ForegroundColor Cyan
                }
            }
        }
        
        return $deployment
    }
    catch {
        Write-Error "❌ Infrastructure deployment failed: $_"
        
        # Get detailed error information
        $deploymentOperation = Get-AzResourceGroupDeploymentOperation -ResourceGroupName $ResourceGroupName -Name $DeploymentName -ErrorAction SilentlyContinue
        if ($deploymentOperation) {
            Write-Host "❌ Deployment operation details:" -ForegroundColor Red
            $deploymentOperation | Where-Object { $_.Properties.ProvisioningState -eq "Failed" } | ForEach-Object {
                Write-Host "  Resource: $($_.Properties.TargetResource.ResourceType) - $($_.Properties.TargetResource.ResourceName)" -ForegroundColor Red
                Write-Host "  Error: $($_.Properties.StatusMessage.Error.Message)" -ForegroundColor Red
            }
        }
        
        exit 1
    }
}

function Set-KeyVaultSecrets {
    param([object]$DeploymentOutputs)
    
    if ($WhatIf) {
        Write-Host "🔍 WHAT-IF: Would configure Key Vault secrets" -ForegroundColor Yellow
        return
    }
    
    Write-Host "🔐 Configuring Key Vault secrets..." -ForegroundColor Blue
    
    try {
        $keyVaultName = $DeploymentOutputs.keyVaultName.Value
        
        # Basic configuration secrets (user will need to add M365 credentials separately)
        $secrets = @{
            "StorageAccount-Name" = $DeploymentOutputs.storageAccountName.Value
            "StorageAccount-Key" = $DeploymentOutputs.storageAccountKey.Value
            "AppInsights-InstrumentationKey" = $DeploymentOutputs.appInsightsInstrumentationKey.Value
            "AppInsights-ConnectionString" = $DeploymentOutputs.appInsightsConnectionString.Value
            "LogAnalytics-WorkspaceId" = $DeploymentOutputs.logAnalyticsWorkspaceId.Value
        }
        
        foreach ($secretName in $secrets.Keys) {
            $secureValue = ConvertTo-SecureString $secrets[$secretName] -AsPlainText -Force
            Set-AzKeyVaultSecret -VaultName $keyVaultName -Name $secretName -SecretValue $secureValue | Out-Null
            Write-Host "✅ Set secret: $secretName" -ForegroundColor Green
        }
        
        Write-Host "✅ Key Vault secrets configured" -ForegroundColor Green
        Write-Host "⚠️ Note: You still need to manually add M365 authentication secrets:" -ForegroundColor Yellow
        Write-Host "  - M365-TenantId" -ForegroundColor Yellow
        Write-Host "  - M365-ApplicationId" -ForegroundColor Yellow
        Write-Host "  - M365-ClientSecret" -ForegroundColor Yellow
    }
    catch {
        Write-Warning "⚠️ Failed to configure Key Vault secrets: $_"
        Write-Host "You can configure these manually in the Azure Portal" -ForegroundColor Yellow
    }
}

function Show-NextSteps {
    param([object]$DeploymentOutputs)
    
    Write-Host ""
    Write-Host "🎉 Infrastructure deployment completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Configure M365 Service Principal:" -ForegroundColor White
    Write-Host "   - Create Azure AD App Registration" -ForegroundColor Gray
    Write-Host "   - Grant required API permissions" -ForegroundColor Gray
    Write-Host "   - Add credentials to Key Vault" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Deploy Application:" -ForegroundColor White
    Write-Host "   - Build container image" -ForegroundColor Gray
    Write-Host "   - Push to Container Registry" -ForegroundColor Gray
    Write-Host "   - Deploy to Container Instances" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Configure Monitoring:" -ForegroundColor White
    Write-Host "   - Set up alert actions" -ForegroundColor Gray
    Write-Host "   - Configure notification channels" -ForegroundColor Gray
    Write-Host "   - Test monitoring and alerting" -ForegroundColor Gray
    Write-Host ""
    
    if ($DeploymentOutputs) {
        Write-Host "🔗 Important URLs:" -ForegroundColor Yellow
        Write-Host "Key Vault: https://portal.azure.com/#resource$($ResourceGroupName)/providers/Microsoft.KeyVault/vaults/$($DeploymentOutputs.keyVaultName.Value)" -ForegroundColor Cyan
        Write-Host "Storage Account: https://portal.azure.com/#resource$($ResourceGroupName)/providers/Microsoft.Storage/storageAccounts/$($DeploymentOutputs.storageAccountName.Value)" -ForegroundColor Cyan
        Write-Host "Container Registry: https://portal.azure.com/#resource$($ResourceGroupName)/providers/Microsoft.ContainerRegistry/registries/$($DeploymentOutputs.containerRegistryName.Value)" -ForegroundColor Cyan
    }
}

# Main execution
try {
    Write-Banner "M365 Security Toolkit - Infrastructure Deployment"
    
    Write-Host "🎯 Deployment Configuration:" -ForegroundColor Blue
    Write-Host "  Subscription: $SubscriptionId" -ForegroundColor Cyan
    Write-Host "  Resource Group: $ResourceGroupName" -ForegroundColor Cyan
    Write-Host "  Location: $Location" -ForegroundColor Cyan
    Write-Host "  Environment: $Environment" -ForegroundColor Cyan
    Write-Host "  Project: $ProjectName" -ForegroundColor Cyan
    Write-Host "  Admin User: $AdminUserPrincipalName" -ForegroundColor Cyan
    Write-Host "  What-If Mode: $WhatIf" -ForegroundColor Cyan
    Write-Host ""
    
    if (-not $WhatIf) {
        $confirm = Read-Host "Do you want to proceed with the deployment? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Host "❌ Deployment cancelled by user" -ForegroundColor Yellow
            exit 0
        }
    }
    
    Test-Prerequisites
    Connect-ToAzure
    New-ResourceGroupIfNotExists
    $deployment = Deploy-Infrastructure
    
    if (-not $WhatIf -and $deployment) {
        Set-KeyVaultSecrets -DeploymentOutputs $deployment.Outputs
        Show-NextSteps -DeploymentOutputs $deployment.Outputs
    }
    
    Write-Host ""
    Write-Host "✅ Deployment script completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
    Write-Host "Stack trace:" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}