# M365 Security Toolkit - Production Deployment Guide

## 🚀 Production Deployment Overview

This guide provides step-by-step instructions for deploying the M365 Security Toolkit to a production environment with enterprise-grade infrastructure, monitoring, and operational procedures.

## 📋 Deployment Prerequisites

### Required Permissions
- **Azure Subscription** with Contributor/Owner rights
- **M365 Global Administrator** or equivalent permissions for:
  - Exchange Online Management
  - Microsoft Graph API access
  - SharePoint Online Administration (optional)
  - Security & Compliance Center (optional)

### Technical Requirements
- **PowerShell 5.1+** or **PowerShell 7.x**
- **Python 3.9+** with pip package manager
- **Azure CLI** or **Azure PowerShell** modules
- **Git** for version control and deployment

### Network Requirements
- **Outbound HTTPS (443)** to Microsoft 365 endpoints
- **Azure public endpoints** access
- **GitHub** access for CI/CD integration

## 🏗️ Phase 1: Infrastructure Setup

### 1.1 Azure Infrastructure Deployment

#### Resource Group Creation
```powershell
# Create resource group for M365 Security Toolkit
$resourceGroup = "rg-m365-security-toolkit-prod"
$location = "East US 2"  # Choose appropriate region

New-AzResourceGroup -Name $resourceGroup -Location $location -Tag @{
    Environment = "Production"
    Application = "M365SecurityToolkit"
    Owner = "SecurityTeam"
    CostCenter = "IT-Security"
}
```

#### Storage Account for Reports and Logs
```powershell
# Create storage account for toolkit outputs
$storageAccountName = "m365sectoolkitprod"  # Must be globally unique
$skuName = "Standard_LRS"

$storageAccount = New-AzStorageAccount `
    -ResourceGroupName $resourceGroup `
    -Name $storageAccountName `
    -Location $location `
    -SkuName $skuName `
    -Kind "StorageV2" `
    -AccessTier "Hot" `
    -EnableHttpsTrafficOnly $true `
    -Tag @{Environment="Production"}

# Create containers for organized storage
$ctx = $storageAccount.Context
New-AzStorageContainer -Name "audit-reports" -Context $ctx -Permission Blob
New-AzStorageContainer -Name "sharepoint-reports" -Context $ctx -Permission Blob
New-AzStorageContainer -Name "security-dashboards" -Context $ctx -Permission Blob
New-AzStorageContainer -Name "logs" -Context $ctx -Permission Off
New-AzStorageContainer -Name "backups" -Context $ctx -Permission Off
```

#### Azure Key Vault for Secrets Management
```powershell
# Create Key Vault for secure credential storage
$keyVaultName = "kv-m365-security-toolkit"  # Must be globally unique

$keyVault = New-AzKeyVault `
    -Name $keyVaultName `
    -ResourceGroupName $resourceGroup `
    -Location $location `
    -EnabledForDeployment `
    -EnabledForTemplateDeployment `
    -EnabledForDiskEncryption `
    -EnableSoftDelete `
    -SoftDeleteRetentionInDays 90 `
    -Tag @{Environment="Production"}

# Configure access policies (add your user/service principals)
Set-AzKeyVaultAccessPolicy `
    -VaultName $keyVaultName `
    -UserPrincipalName "your-admin@yourdomain.com" `
    -PermissionsToSecrets get,list,set,delete `
    -PermissionsToCertificates get,list,create,delete
```

### 1.2 Azure App Registration for M365 Access

#### Create Service Principal
```powershell
# Create Azure AD App Registration
$appName = "M365-Security-Toolkit-Production"

# Note: This requires Azure AD PowerShell or Graph PowerShell
# Install-Module AzureAD -Force
Connect-AzureAD

$app = New-AzureADApplication `
    -DisplayName $appName `
    -HomePage "https://m365-security-toolkit.yourdomain.com" `
    -ReplyUrls @("https://localhost:8080/auth/callback")

# Create service principal
$servicePrincipal = New-AzureADServicePrincipal -AppId $app.AppId

# Generate client secret (save this securely!)
$clientSecret = New-AzureADApplicationPasswordCredential `
    -ObjectId $app.ObjectId `
    -CustomKeyIdentifier "ProductionSecret" `
    -EndDate (Get-Date).AddYears(2)

Write-Host "Application ID: $($app.AppId)"
Write-Host "Client Secret: $($clientSecret.Value)" -ForegroundColor Yellow
Write-Host "Tenant ID: $((Get-AzureADTenantDetail).ObjectId)"
```

#### Required API Permissions
```powershell
# Microsoft Graph API Permissions Required:
# - User.Read.All (Read all users' full profiles)
# - Policy.Read.All (Read your organization's policies)
# - Directory.Read.All (Read directory data)
# - Organization.Read.All (Read organization information)
# - AuditLog.Read.All (Read audit log data)
# - SecurityEvents.Read.All (Read your organization's security events)

# Exchange Online Permissions:
# - Exchange.ManageAsApp (Access Exchange Online as application)

# SharePoint Online Permissions:
# - Sites.Read.All (Read items in all site collections)
# - Sites.FullControl.All (Full control of all site collections) # Optional for advanced features
```

### 1.3 Log Analytics Workspace for Monitoring

#### Create Log Analytics Workspace
```powershell
# Create Log Analytics workspace for centralized logging
$workspaceName = "law-m365-security-toolkit"

$workspace = New-AzOperationalInsightsWorkspace `
    -ResourceGroupName $resourceGroup `
    -Name $workspaceName `
    -Location $location `
    -Sku "PerGB2018" `
    -RetentionInDays 90 `
    -Tag @{Environment="Production"}

Write-Host "Workspace ID: $($workspace.ResourceId)"
```

## 🔧 Phase 2: Application Deployment

### 2.1 Virtual Machine Setup (Option 1: VM-based deployment)

#### Create Production VM
```powershell
# Create VM for hosting the toolkit
$vmName = "vm-m365-security-toolkit"
$vmSize = "Standard_D2s_v3"  # 2 vCPUs, 8 GB RAM
$adminUsername = "m365admin"

# Create VM configuration
$vmConfig = New-AzVMConfig -VMName $vmName -VMSize $vmSize

# Set OS configuration (Windows Server 2022)
$cred = Get-Credential -UserName $adminUsername -Message "Enter VM administrator password"
$vmConfig = Set-AzVMOperatingSystem `
    -VM $vmConfig `
    -Windows `
    -ComputerName $vmName `
    -Credential $cred `
    -ProvisionVMAgent `
    -EnableAutoUpdate

# Configure networking (simplified - create VNet first in production)
$vnetName = "vnet-m365-security"
$subnetName = "subnet-toolkit"

# Network security group with minimal required ports
$nsg = New-AzNetworkSecurityGroup `
    -ResourceGroupName $resourceGroup `
    -Location $location `
    -Name "nsg-$vmName"

# Add RDP rule (restrict source IPs in production)
$nsg | Add-AzNetworkSecurityRuleConfig `
    -Name "AllowRDP" `
    -Description "Allow RDP" `
    -Access Allow `
    -Protocol Tcp `
    -Direction Inbound `
    -Priority 1000 `
    -SourceAddressPrefix "YOUR_PUBLIC_IP/32" `
    -SourcePortRange * `
    -DestinationAddressPrefix * `
    -DestinationPortRange 3389 | Set-AzNetworkSecurityGroup
```

### 2.2 Container Deployment (Option 2: Recommended)

#### Azure Container Instances
```powershell
# Create container group for the toolkit
$containerGroupName = "aci-m365-security-toolkit"
$imageName = "mcr.microsoft.com/powershell:lts-windowsservercore-ltsc2022"

# Create container with mounted storage
$containerGroup = New-AzContainerGroup `
    -ResourceGroupName $resourceGroup `
    -Name $containerGroupName `
    -Location $location `
    -Image $imageName `
    -OsType Windows `
    -Memory 4 `
    -Cpu 2 `
    -RestartPolicy OnFailure `
    -Tag @{Environment="Production"}
```

## 📊 Phase 3: Monitoring and Alerting Setup

### 3.1 Application Insights Configuration
```powershell
# Create Application Insights for performance monitoring
$appInsightsName = "ai-m365-security-toolkit"

$appInsights = New-AzApplicationInsights `
    -ResourceGroupName $resourceGroup `
    -Name $appInsightsName `
    -Location $location `
    -Kind web `
    -WorkspaceResourceId $workspace.ResourceId

# Get instrumentation key for application configuration
$instrumentationKey = $appInsights.InstrumentationKey
Write-Host "Application Insights Key: $instrumentationKey"
```

### 3.2 Alert Rules Configuration
```powershell
# Create alert rules for operational monitoring

# Alert for failed audit runs
$failureAlert = New-AzMetricAlertRuleV2 `
    -Name "M365-Audit-Failures" `
    -ResourceGroupName $resourceGroup `
    -WindowSize (New-TimeSpan -Minutes 15) `
    -Frequency (New-TimeSpan -Minutes 5) `
    -TargetResourceId $appInsights.Id `
    -MetricName "exceptions/count" `
    -Operator GreaterThan `
    -Threshold 5 `
    -Severity 2

# Alert for performance degradation
$performanceAlert = New-AzMetricAlertRuleV2 `
    -Name "M365-Performance-Degradation" `
    -ResourceGroupName $resourceGroup `
    -WindowSize (New-TimeSpan -Minutes 30) `
    -Frequency (New-TimeSpan -Minutes 15) `
    -TargetResourceId $appInsights.Id `
    -MetricName "performanceCounters/requestExecutionTime" `
    -Operator GreaterThan `
    -Threshold 300000 `  # 5 minutes in milliseconds
    -Severity 3
```

## 🔐 Phase 4: Security Configuration

### 4.1 Network Security
```powershell
# Configure network security groups
$securityRules = @(
    @{
        Name = "AllowHTTPS"
        Protocol = "Tcp"
        SourcePortRange = "*"
        DestinationPortRange = "443"
        Access = "Allow"
        Direction = "Outbound"
        Priority = 1000
    },
    @{
        Name = "AllowM365Endpoints"
        Protocol = "Tcp"
        SourcePortRange = "*"
        DestinationPortRange = "443"
        Access = "Allow"
        Direction = "Outbound"
        Priority = 1100
    }
)
```

### 4.2 Key Vault Secret Storage
```powershell
# Store sensitive configuration in Key Vault
$secrets = @{
    "M365-TenantId" = (Get-AzureADTenantDetail).ObjectId
    "M365-ApplicationId" = $app.AppId
    "M365-ClientSecret" = $clientSecret.Value
    "StorageAccount-ConnectionString" = $storageAccount.Context.ConnectionString
    "AppInsights-InstrumentationKey" = $instrumentationKey
}

foreach ($secretName in $secrets.Keys) {
    $secureSecret = ConvertTo-SecureString $secrets[$secretName] -AsPlainText -Force
    Set-AzKeyVaultSecret -VaultName $keyVaultName -Name $secretName -SecretValue $secureSecret
}
```

## 🚀 Phase 5: Application Configuration

### 5.1 Production Configuration File
```json
{
  "production": {
    "azure": {
      "keyVault": {
        "name": "kv-m365-security-toolkit",
        "resourceGroup": "rg-m365-security-toolkit-prod"
      },
      "storage": {
        "accountName": "m365sectoolkitprod",
        "containers": {
          "auditReports": "audit-reports",
          "sharepointReports": "sharepoint-reports",
          "dashboards": "security-dashboards",
          "logs": "logs",
          "backups": "backups"
        }
      },
      "monitoring": {
        "logAnalyticsWorkspace": "law-m365-security-toolkit",
        "applicationInsights": "ai-m365-security-toolkit"
      }
    },
    "m365": {
      "authentication": {
        "method": "ServicePrincipal",
        "tenantIdSecret": "M365-TenantId",
        "applicationIdSecret": "M365-ApplicationId",
        "clientSecretSecret": "M365-ClientSecret"
      },
      "endpoints": {
        "exchangeOnline": "https://outlook.office365.com/powershell-liveid/",
        "microsoftGraph": "https://graph.microsoft.com/",
        "sharepointAdmin": "https://yourtenant-admin.sharepoint.com"
      }
    },
    "audit": {
      "schedule": {
        "daily": "07:00",
        "weekly": "Sunday 02:00",
        "monthly": "1st 01:00"
      },
      "retention": {
        "auditResults": "365 days",
        "dashboards": "90 days",
        "logs": "90 days"
      }
    },
    "notifications": {
      "email": {
        "enabled": true,
        "recipients": ["security-team@yourdomain.com"],
        "severity": ["Critical", "High"]
      },
      "teams": {
        "enabled": true,
        "webhook": "https://outlook.office.com/webhook/..."
      }
    }
  }
}
```

## 📚 Next Steps

1. **Environment Variables Setup** - Configure application settings
2. **Automated Deployment** - Create CI/CD pipeline for updates
3. **Backup Configuration** - Set up automated backups
4. **Disaster Recovery** - Document recovery procedures
5. **User Training** - Prepare operational documentation

## 🔍 Validation Checklist

- [ ] Azure resources created successfully
- [ ] Service principal configured with required permissions
- [ ] Key Vault secrets stored securely
- [ ] Monitoring and alerting configured
- [ ] Network security rules applied
- [ ] Application configuration validated
- [ ] Initial audit run successful
- [ ] Dashboard generation verified
- [ ] Backup procedures tested

---

**Next:** Proceed to deployment automation and operational setup phases.