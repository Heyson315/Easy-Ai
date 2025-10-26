# M365 Security Toolkit - Native Windows Deployment Guide

## 🚀 Simplified Production Deployment (No Docker)

This guide provides a streamlined approach to deploying the M365 Security Toolkit directly on Windows Server without containerization.

## 📋 Prerequisites

### System Requirements
- **Windows Server 2019/2022** or **Windows 10/11 Pro**
- **PowerShell 5.1+** (included with Windows)
- **Python 3.9+** from python.org
- **4GB RAM minimum, 8GB recommended**
- **50GB free disk space**

### Network Requirements
- **Outbound HTTPS (443)** to Microsoft 365 endpoints
- **Azure endpoints** access (login.microsoftonline.com, graph.microsoft.com)

## 🔧 Phase 1: System Setup

### 1.1 Install Prerequisites

```powershell
# Install Python 3.11
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe" -OutFile "python-installer.exe"
Start-Process -FilePath "python-installer.exe" -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
Remove-Item "python-installer.exe"

# Install Git (optional, for updates)
Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe" -OutFile "git-installer.exe"
Start-Process -FilePath "git-installer.exe" -ArgumentList "/SILENT" -Wait
Remove-Item "git-installer.exe"

# Restart PowerShell session to pick up path changes
```

### 1.2 Install PowerShell Modules

```powershell
# Set PSGallery as trusted repository
Set-PSRepository -Name PSGallery -InstallationPolicy Trusted

# Install required M365 modules
Install-Module -Name ExchangeOnlineManagement -Scope AllUsers -Force
Install-Module -Name Microsoft.Graph.Authentication -Scope AllUsers -Force
Install-Module -Name Microsoft.Graph.Identity.SignIns -Scope AllUsers -Force
Install-Module -Name Microsoft.Graph.Identity.DirectoryManagement -Scope AllUsers -Force
Install-Module -Name Microsoft.Graph.Users -Scope AllUsers -Force

# Install Azure modules (optional, for Key Vault integration)
Install-Module -Name Az.KeyVault -Scope AllUsers -Force
Install-Module -Name Az.Storage -Scope AllUsers -Force

# Install SharePoint module (optional)
Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Scope AllUsers -Force
```

### 1.3 Install Python Dependencies

```powershell
# Navigate to toolkit directory
cd "C:\M365SecurityToolkit"

# Install Python packages
python -m pip install --upgrade pip
python -m pip install pandas openpyxl requests python-dateutil

# Install optional packages for enhanced functionality
python -m pip install azure-identity azure-keyvault-secrets
```

## 🏗️ Phase 2: Application Deployment

### 2.1 Create Directory Structure

```powershell
# Create application directories
$toolkitPath = "C:\M365SecurityToolkit"
New-Item -ItemType Directory -Path $toolkitPath -Force
New-Item -ItemType Directory -Path "$toolkitPath\data\raw\security" -Force
New-Item -ItemType Directory -Path "$toolkitPath\data\processed\security" -Force
New-Item -ItemType Directory -Path "$toolkitPath\data\archive" -Force
New-Item -ItemType Directory -Path "$toolkitPath\output\reports\security" -Force
New-Item -ItemType Directory -Path "$toolkitPath\output\reports\business" -Force
New-Item -ItemType Directory -Path "$toolkitPath\output\dashboards" -Force
New-Item -ItemType Directory -Path "$toolkitPath\logs" -Force
New-Item -ItemType Directory -Path "$toolkitPath\config" -Force

# Set permissions for service account
icacls $toolkitPath /grant "NT AUTHORITY\NETWORK SERVICE:(OI)(CI)F" /T
```

### 2.2 Deploy Application Files

```powershell
# Copy toolkit files to production directory
# (Assuming you're deploying from development/staging environment)

Copy-Item -Path ".\scripts" -Destination "$toolkitPath\scripts" -Recurse -Force
Copy-Item -Path ".\src" -Destination "$toolkitPath\src" -Recurse -Force
Copy-Item -Path ".\config" -Destination "$toolkitPath\config" -Recurse -Force
Copy-Item -Path ".\templates" -Destination "$toolkitPath\templates" -Recurse -Force

# Copy production configuration
Copy-Item -Path ".\config\production_config.json" -Destination "$toolkitPath\config\production_config.json" -Force
```

## ⏰ Phase 3: Automation Setup

### 3.1 Windows Task Scheduler Configuration

```powershell
# Create scheduled task for daily audit
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"C:\M365SecurityToolkit\scripts\powershell\Invoke-M365CISAudit.ps1`" -Timestamped"

$trigger = New-ScheduledTaskTrigger -Daily -At "06:00"

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

$principal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\NETWORK SERVICE" -LogonType ServiceAccount

Register-ScheduledTask -TaskName "M365-Security-Audit-Daily" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Daily M365 CIS security audit"
```

### 3.2 IIS Setup for Dashboard Hosting (Optional)

```powershell
# Install IIS (if not already installed)
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole, IIS-WebServer, IIS-CommonHttpFeatures, IIS-HttpErrors, IIS-HttpRedirect, IIS-ApplicationDevelopment, IIS-NetFxExtensibility45, IIS-HealthAndDiagnostics, IIS-HttpLogging, IIS-Security, IIS-RequestFiltering, IIS-Performance, IIS-WebServerManagementTools, IIS-ManagementConsole, IIS-IIS6ManagementCompatibility, IIS-Metabase

# Create IIS site for dashboards
Import-Module WebAdministration
New-Website -Name "M365-Security-Dashboard" -Port 8080 -PhysicalPath "C:\M365SecurityToolkit\output\dashboards"

# Configure authentication (Windows Authentication recommended)
Set-WebConfigurationProperty -Filter "system.webServer/security/authentication/windowsAuthentication" -Name enabled -Value $true -PSPath "IIS:" -Location "M365-Security-Dashboard"
Set-WebConfigurationProperty -Filter "system.webServer/security/authentication/anonymousAuthentication" -Name enabled -Value $false -PSPath "IIS:" -Location "M365-Security-Dashboard"
```

## 📊 Phase 4: Monitoring Setup

### 4.1 Event Log Configuration

```powershell
# Create custom event log for M365 Toolkit
New-EventLog -LogName "M365SecurityToolkit" -Source "M365Audit"

# Create performance counters (optional)
$counterCategory = "M365 Security Toolkit"
if (-not [System.Diagnostics.PerformanceCounterCategory]::Exists($counterCategory)) {
    $counters = New-Object System.Diagnostics.CounterCreationDataCollection
    
    $auditCounter = New-Object System.Diagnostics.CounterCreationData
    $auditCounter.CounterName = "Audits Completed"
    $auditCounter.CounterType = [System.Diagnostics.PerformanceCounterType]::NumberOfItems32
    $counters.Add($auditCounter)
    
    [System.Diagnostics.PerformanceCounterCategory]::Create($counterCategory, "M365 Security Toolkit Counters", "MultiInstance", $counters)
}
```

### 4.2 Health Check Script

```powershell
# Create health check script for monitoring
$healthCheckScript = @'
param([switch]$Detailed)

$errors = @()
$warnings = @()

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.1[1-9]") {
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } else {
        $errors += "Python version check failed"
    }
} catch {
    $errors += "Python not available"
}

# Check PowerShell modules
$requiredModules = @("ExchangeOnlineManagement", "Microsoft.Graph.Authentication")
foreach ($module in $requiredModules) {
    if (Get-Module -Name $module -ListAvailable) {
        Write-Host "✅ PowerShell Module: $module" -ForegroundColor Green
    } else {
        $errors += "PowerShell module missing: $module"
    }
}

# Check scheduled tasks
$scheduledTask = Get-ScheduledTask -TaskName "M365-Security-Audit-Daily" -ErrorAction SilentlyContinue
if ($scheduledTask) {
    Write-Host "✅ Scheduled Task: M365-Security-Audit-Daily" -ForegroundColor Green
} else {
    $warnings += "Scheduled task not found"
}

# Return status
if ($errors.Count -eq 0) {
    Write-Host "`n✅ System Health: HEALTHY" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n❌ System Health: UNHEALTHY" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    exit 1
}
'@

$healthCheckScript | Out-File -FilePath "C:\M365SecurityToolkit\scripts\Test-SystemHealth.ps1" -Encoding UTF8
```

## 🔒 Phase 5: Security Configuration

### 5.1 Service Account Setup

```powershell
# Create dedicated service account (recommended for production)
$password = ConvertTo-SecureString "ComplexPassword123!" -AsPlainText -Force
New-LocalUser -Name "svc-m365toolkit" -Password $password -Description "M365 Security Toolkit Service Account" -PasswordNeverExpires

# Grant necessary permissions
Add-LocalGroupMember -Group "Log on as a service" -Member "svc-m365toolkit"

# Update scheduled task to use service account
Set-ScheduledTask -TaskName "M365-Security-Audit-Daily" -Principal (New-ScheduledTaskPrincipal -UserId "svc-m365toolkit" -LogonType Password)
```

### 5.2 Firewall Configuration

```powershell
# Configure Windows Firewall (if hosting dashboard)
New-NetFirewallRule -DisplayName "M365 Security Dashboard" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

## 🚀 Phase 6: Deployment Validation

### 6.1 Test Basic Functionality

```powershell
# Test audit execution
cd "C:\M365SecurityToolkit"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\powershell\Invoke-M365CISAudit.ps1" -WhatIf

# Test report generation
python .\scripts\m365_cis_report.py --help

# Test system health
powershell -File ".\scripts\Test-SystemHealth.ps1"
```

### 6.2 Validate Scheduled Execution

```powershell
# Test scheduled task
Start-ScheduledTask -TaskName "M365-Security-Audit-Daily"

# Check task history
Get-ScheduledTask -TaskName "M365-Security-Audit-Daily" | Get-ScheduledTaskInfo
```

## 📈 Operational Procedures

### Daily Operations
1. **Check scheduled task execution** via Task Scheduler
2. **Review audit logs** in `C:\M365SecurityToolkit\logs`
3. **Monitor system health** using health check script
4. **Review generated reports** in output directories

### Weekly Operations
1. **Update PowerShell modules** if needed
2. **Review and archive old reports**
3. **Check disk space usage**
4. **Validate authentication tokens**

### Monthly Operations
1. **Update Python packages**
2. **Review security findings trends**
3. **Update configuration if needed**
4. **Backup configuration and historical data**

## 🔧 Maintenance Commands

```powershell
# Update PowerShell modules
Update-Module -Name ExchangeOnlineManagement, Microsoft.Graph.Authentication -Force

# Update Python packages
python -m pip install --upgrade pandas openpyxl requests

# Archive old reports (keep last 90 days)
$archiveDate = (Get-Date).AddDays(-90)
Get-ChildItem "C:\M365SecurityToolkit\output\reports" -Recurse | Where-Object {$_.CreationTime -lt $archiveDate} | Move-Item -Destination "C:\M365SecurityToolkit\data\archive"

# Clean temporary files
Remove-Item "C:\M365SecurityToolkit\temp\*" -Recurse -Force
```

## 🎯 Benefits of Native Deployment

- ✅ **Simpler setup** - No container orchestration
- ✅ **Lower resource usage** - Direct execution
- ✅ **Familiar administration** - Standard Windows tools
- ✅ **Easier troubleshooting** - Native Windows logging
- ✅ **Cost effective** - No container hosting fees
- ✅ **Quick deployment** - Minimal infrastructure complexity

## 📚 Next Steps

1. **Configure authentication** with M365 service principal
2. **Set up monitoring** dashboards
3. **Train operations team** on maintenance procedures
4. **Document custom configurations**
5. **Plan disaster recovery** procedures