#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Entry point script for M365 Security Toolkit container

.DESCRIPTION
    Handles container startup, configuration validation, and service initialization
    for the M365 Security Toolkit production deployment.

.NOTES
    This script is the primary entry point for the Docker container
#>

param(
    [string]$Mode = "audit",  # audit, daemon, shell
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

# Set up logging
$LogPath = "C:\app\logs\startup-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$null = New-Item -Path (Split-Path $LogPath -Parent) -ItemType Directory -Force

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path $LogPath -Value $logEntry
}

function Initialize-Environment {
    Write-Log "Initializing M365 Security Toolkit environment..."
    
    # Set environment variables
    $env:M365_TOOLKIT_ROOT = "C:\app"
    $env:M365_TOOLKIT_CONFIG_PATH = "C:\app\config\production_config.json"
    $env:M365_TOOLKIT_LOG_PATH = "C:\app\logs"
    $env:M365_TOOLKIT_DATA_PATH = "C:\app\data"
    $env:M365_TOOLKIT_OUTPUT_PATH = "C:\app\output"
    
    # Set working directory
    Set-Location $env:M365_TOOLKIT_ROOT
    
    # Create required directories
    $directories = @(
        "data\raw\security",
        "data\processed\security", 
        "data\archive",
        "output\reports\security",
        "output\reports\business",
        "output\dashboards",
        "logs",
        "temp"
    )
    
    foreach ($dir in $directories) {
        $fullPath = Join-Path $env:M365_TOOLKIT_ROOT $dir
        if (-not (Test-Path $fullPath)) {
            $null = New-Item -Path $fullPath -ItemType Directory -Force
            Write-Log "Created directory: $fullPath"
        }
    }
    
    Write-Log "Environment initialization complete"
}

function Test-Configuration {
    Write-Log "Validating configuration..."
    
    $configPath = $env:M365_TOOLKIT_CONFIG_PATH
    if (-not (Test-Path $configPath)) {
        throw "Configuration file not found: $configPath"
    }
    
    try {
        $config = Get-Content $configPath -Raw | ConvertFrom-Json
        
        # Validate required configuration sections
        $requiredSections = @("production", "azure", "m365", "audit", "logging")
        foreach ($section in $requiredSections) {
            if (-not $config.$section) {
                throw "Missing required configuration section: $section"
            }
        }
        
        Write-Log "Configuration validation successful"
        return $config
    }
    catch {
        throw "Configuration validation failed: $_"
    }
}

function Initialize-Authentication {
    param($Config)
    
    Write-Log "Initializing authentication..."
    
    # Import authentication module
    Import-Module "$env:M365_TOOLKIT_ROOT\scripts\powershell\modules\M365CIS.psm1" -Force
    
    # Set up Azure authentication if running in production
    if ($Config.production.enableAzureAuth) {
        try {
            $keyVaultName = $Config.azure.keyVault.name
            
            Write-Log "Connecting to Azure Key Vault: $keyVaultName"
            
            # In production, the container should be running with managed identity
            # or have credentials provided via environment variables
            Connect-AzAccount -Identity -ErrorAction SilentlyContinue
            
            Write-Log "Azure authentication initialized"
        }
        catch {
            Write-Log "Azure authentication failed: $_" -Level "WARNING"
            Write-Log "Continuing with interactive authentication mode" -Level "WARNING"
        }
    }
}

function Start-AuditMode {
    param($Config, [switch]$WhatIf)
    
    Write-Log "Starting audit mode..."
    
    try {
        $auditScript = "$env:M365_TOOLKIT_ROOT\scripts\powershell\Invoke-M365CISAudit.ps1"
        
        $auditParams = @{
            FilePath = "powershell.exe"
            ArgumentList = @(
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-File", $auditScript,
                "-Timestamped"
            )
            Wait = $true
            PassThru = $true
            WorkingDirectory = $env:M365_TOOLKIT_ROOT
        }
        
        if ($WhatIf) {
            $auditParams.ArgumentList += "-WhatIf"
        }
        
        if ($Config.audit.includeSharePoint) {
            $spoUrl = $Config.m365.sharepoint.adminUrl
            if ($spoUrl) {
                $auditParams.ArgumentList += "-SPOAdminUrl", $spoUrl
            }
        }
        
        if ($Config.audit.skipPurview) {
            $auditParams.ArgumentList += "-SkipPurview"
        }
        
        Write-Log "Executing audit with parameters: $($auditParams.ArgumentList -join ' ')"
        
        $process = Start-Process @auditParams
        
        if ($process.ExitCode -eq 0) {
            Write-Log "Audit completed successfully"
            
            # Generate reports if configured
            if ($Config.audit.generateReports) {
                Write-Log "Generating Excel report..."
                & python "$env:M365_TOOLKIT_ROOT\scripts\m365_cis_report.py"
                
                Write-Log "Generating HTML dashboard..."
                & python "$env:M365_TOOLKIT_ROOT\scripts\generate_security_dashboard.py"
            }
        }
        else {
            throw "Audit failed with exit code: $($process.ExitCode)"
        }
    }
    catch {
        Write-Log "Audit mode failed: $_" -Level "ERROR"
        throw
    }
}

function Start-DaemonMode {
    param($Config)
    
    Write-Log "Starting daemon mode..."
    
    while ($true) {
        try {
            Write-Log "Running scheduled audit..."
            Start-AuditMode -Config $Config
            
            $intervalHours = $Config.audit.scheduleIntervalHours
            Write-Log "Audit complete. Sleeping for $intervalHours hours..."
            Start-Sleep -Seconds ($intervalHours * 3600)
        }
        catch {
            Write-Log "Daemon audit failed: $_" -Level "ERROR"
            Write-Log "Retrying in 1 hour..." -Level "WARNING"
            Start-Sleep -Seconds 3600
        }
    }
}

function Start-InteractiveShell {
    Write-Log "Starting interactive shell mode..."
    
    Write-Host @"
🔒 M365 Security & Compliance Toolkit - Interactive Mode
======================================================

Available Commands:
  audit     - Run CIS M365 Foundation security audit
  report    - Generate Excel reports from existing data
  dashboard - Generate HTML security dashboard
  test      - Run health checks
  help      - Show this help message

Environment:
  Root: $env:M365_TOOLKIT_ROOT
  Config: $env:M365_TOOLKIT_CONFIG_PATH
  Logs: $env:M365_TOOLKIT_LOG_PATH

Type 'exit' to quit.
"@

    while ($true) {
        $userInput = Read-Host "M365-Toolkit"
        
        switch ($userInput.ToLower()) {
            "audit" {
                Start-AuditMode -Config (Test-Configuration)
            }
            "report" {
                & python "$env:M365_TOOLKIT_ROOT\scripts\m365_cis_report.py"
            }
            "dashboard" {
                & python "$env:M365_TOOLKIT_ROOT\scripts\generate_security_dashboard.py"
            }
            "test" {
                & "$env:M365_TOOLKIT_ROOT\deployment\docker\healthcheck.ps1"
            }
            "help" {
                Write-Host "Available commands: audit, report, dashboard, test, help, exit"
            }
            "exit" {
                Write-Log "Exiting interactive shell"
                break
            }
            default {
                Write-Host "Unknown command: $userInput. Type 'help' for available commands."
            }
        }
    }
}

# Main execution
try {
    Write-Log "Starting M365 Security Toolkit container..."
    Write-Log "Mode: $Mode, WhatIf: $WhatIf"
    
    # Initialize environment
    Initialize-Environment
    
    # Validate configuration
    $config = Test-Configuration
    
    # Initialize authentication
    Initialize-Authentication -Config $config
    
    # Start requested mode
    switch ($Mode.ToLower()) {
        "audit" {
            Start-AuditMode -Config $config -WhatIf:$WhatIf
        }
        "daemon" {
            Start-DaemonMode -Config $config
        }
        "shell" {
            Start-InteractiveShell
        }
        default {
            throw "Unknown mode: $Mode. Valid modes are: audit, daemon, shell"
        }
    }
    
    Write-Log "Container execution completed successfully"
}
catch {
    Write-Log "Container startup failed: $_" -Level "ERROR"
    Write-Log "Check logs at: $LogPath" -Level "ERROR"
    exit 1
}