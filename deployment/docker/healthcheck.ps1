#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Health check script for M365 Security Toolkit container

.DESCRIPTION
    Performs health checks to ensure the M365 Security Toolkit container is running properly
    and can connect to required services.

.NOTES
    This script is called by Docker's HEALTHCHECK instruction
    Exit codes: 0 = healthy, 1 = unhealthy
#>

$ErrorActionPreference = "SilentlyContinue"

function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $pythonVersion -match "Python 3\.1[1-9]") {
            Write-Host "✅ Python environment: $pythonVersion"
            return $true
        }
        else {
            Write-Host "❌ Python environment check failed"
            return $false
        }
    }
    catch {
        Write-Host "❌ Python not available: $_"
        return $false
    }
}

function Test-PowerShellModules {
    try {
        $requiredModules = @(
            "ExchangeOnlineManagement",
            "Microsoft.Graph.Authentication", 
            "Az.KeyVault"
        )
        
        $moduleStatus = $true
        foreach ($module in $requiredModules) {
            $moduleInfo = Get-Module -Name $module -ListAvailable
            if ($moduleInfo) {
                Write-Host "✅ PowerShell module: $module"
            }
            else {
                Write-Host "❌ PowerShell module missing: $module"
                $moduleStatus = $false
            }
        }
        
        return $moduleStatus
    }
    catch {
        Write-Host "❌ PowerShell module check failed: $_"
        return $false
    }
}

function Test-ApplicationFiles {
    try {
        $criticalFiles = @(
            "/app/config/production_config.json",
            "/app/scripts/powershell/modules/M365CIS.psm1",
            "/app/scripts/m365_cis_report.py",
            "/app/scripts/generate_security_dashboard.py"
        )
        
        $fileStatus = $true
        foreach ($file in $criticalFiles) {
            if (Test-Path $file) {
                Write-Host "✅ Application file: $file"
            }
            else {
                Write-Host "❌ Application file missing: $file"
                $fileStatus = $false
            }
        }
        
        return $fileStatus
    }
    catch {
        Write-Host "❌ Application file check failed: $_"
        return $false
    }
}

function Test-DirectoryStructure {
    try {
        $requiredDirs = @(
            "/app/data",
            "/app/logs", 
            "/app/output",
            "/app/temp"
        )
        
        $dirStatus = $true
        foreach ($dir in $requiredDirs) {
            if (Test-Path $dir) {
                Write-Host "✅ Directory: $dir"
            }
            else {
                Write-Host "❌ Directory missing: $dir"
                $dirStatus = $false
            }
        }
        
        return $dirStatus
    }
    catch {
        Write-Host "❌ Directory structure check failed: $_"
        return $false
    }
}

function Test-ConfigurationAccess {
    try {
        # Test if we can read the configuration file
        $configPath = $env:M365_TOOLKIT_CONFIG_PATH
        if ($configPath -and (Test-Path $configPath)) {
            $config = Get-Content $configPath -Raw | ConvertFrom-Json
            if ($config.production) {
                Write-Host "✅ Configuration file accessible"
                return $true
            }
            else {
                Write-Host "❌ Configuration file invalid format"
                return $false
            }
        }
        else {
            Write-Host "❌ Configuration file not found: $configPath"
            return $false
        }
    }
    catch {
        Write-Host "❌ Configuration access failed: $_"
        return $false
    }
}

function Test-NetworkConnectivity {
    try {
        # Test connectivity to key Microsoft endpoints
        $endpoints = @(
            "graph.microsoft.com",
            "login.microsoftonline.com"
        )
        
        $networkStatus = $true
        foreach ($endpoint in $endpoints) {
            try {
                $result = Test-NetConnection -ComputerName $endpoint -Port 443 -InformationLevel Quiet
                if ($result) {
                    Write-Host "✅ Network connectivity: $endpoint"
                }
                else {
                    Write-Host "❌ Network connectivity failed: $endpoint"
                    $networkStatus = $false
                }
            }
            catch {
                Write-Host "⚠️ Network test skipped for: $endpoint"
            }
        }
        
        return $networkStatus
    }
    catch {
        Write-Host "⚠️ Network connectivity check skipped: $_"
        return $true  # Don't fail health check for network issues
    }
}

# Main health check execution
try {
    Write-Host "🏥 M365 Security Toolkit - Health Check $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host "=" * 60
    
    $checks = @(
        @{ Name = "Python Environment"; Test = { Test-PythonEnvironment } },
        @{ Name = "PowerShell Modules"; Test = { Test-PowerShellModules } },
        @{ Name = "Application Files"; Test = { Test-ApplicationFiles } },
        @{ Name = "Directory Structure"; Test = { Test-DirectoryStructure } },
        @{ Name = "Configuration Access"; Test = { Test-ConfigurationAccess } },
        @{ Name = "Network Connectivity"; Test = { Test-NetworkConnectivity } }
    )
    
    $overallHealth = $true
    
    foreach ($check in $checks) {
        Write-Host "`n🔍 Checking: $($check.Name)"
        $result = & $check.Test
        
        if (-not $result) {
            $overallHealth = $false
        }
    }
    
    Write-Host "`n" + "=" * 60
    
    if ($overallHealth) {
        Write-Host "✅ Overall Health: HEALTHY" -ForegroundColor Green
        exit 0
    }
    else {
        Write-Host "❌ Overall Health: UNHEALTHY" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Health check failed with exception: $_" -ForegroundColor Red
    exit 1
}