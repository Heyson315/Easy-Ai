#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Production deployment orchestration script for M365 Security Toolkit

.DESCRIPTION
    Orchestrates the complete production deployment of the M365 Security Toolkit,
    including Azure infrastructure, container deployment, and operational setup.

.PARAMETER Environment
    Target environment (production, staging, development)

.PARAMETER SubscriptionId
    Azure subscription ID for deployment

.PARAMETER ResourceGroupName
    Azure resource group name (will be created if it doesn't exist)

.PARAMETER Location
    Azure region for resource deployment

.PARAMETER TenantDomain
    M365 tenant domain for configuration

.PARAMETER WhatIf
    Preview deployment actions without executing them

.PARAMETER SkipInfrastructure
    Skip Azure infrastructure deployment (use existing resources)

.PARAMETER SkipContainer
    Skip container deployment

.PARAMETER Force
    Force deployment without confirmation prompts

.EXAMPLE
    .\Deploy-Production.ps1 -Environment production -SubscriptionId "12345678-1234-1234-1234-123456789012" -ResourceGroupName "rg-m365-toolkit-prod" -Location "East US" -TenantDomain "contoso.onmicrosoft.com"

.EXAMPLE
    .\Deploy-Production.ps1 -Environment staging -WhatIf

.NOTES
    Requires: Azure PowerShell, Docker, appropriate permissions
    Version: 1.0.0
    Author: M365 Security Toolkit Team
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("production", "staging", "development")]
    [string]$Environment,
    
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $true)]
    [ValidateSet("East US", "West US 2", "West Europe", "North Europe", "Southeast Asia")]
    [string]$Location,
    
    [Parameter(Mandatory = $true)]
    [string]$TenantDomain,
    
    [switch]$WhatIf,
    [switch]$SkipInfrastructure,
    [switch]$SkipContainer,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Script constants
$ScriptRoot = $PSScriptRoot
$ProjectRoot = Split-Path $ScriptRoot -Parent
$DeploymentRoot = $ScriptRoot
$LogPath = Join-Path $DeploymentRoot "logs\deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# Ensure logs directory exists
$null = New-Item -Path (Split-Path $LogPath -Parent) -ItemType Directory -Force

function Write-DeploymentLog {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        "INFO" { Write-Host $logEntry -ForegroundColor White }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
    }
    
    Add-Content -Path $LogPath -Value $logEntry
}

function Test-Prerequisites {
    Write-DeploymentLog "Checking deployment prerequisites..."
    
    $prerequisites = @(
        @{ Name = "Azure PowerShell"; Command = "Get-Module -Name Az -ListAvailable" },
        @{ Name = "Docker"; Command = "docker --version" },
        @{ Name = "Docker Compose"; Command = "docker-compose --version" },
        @{ Name = "Git"; Command = "git --version" }
    )
    
    $missingPrereqs = @()
    
    foreach ($prereq in $prerequisites) {
        try {
            $null = Invoke-Expression $prereq.Command
            Write-DeploymentLog "✅ $($prereq.Name) is available"
        }
        catch {
            Write-DeploymentLog "❌ $($prereq.Name) is not available" -Level "ERROR"
            $missingPrereqs += $prereq.Name
        }
    }
    
    if ($missingPrereqs.Count -gt 0) {
        throw "Missing prerequisites: $($missingPrereqs -join ', '). Please install before continuing."
    }
    
    Write-DeploymentLog "All prerequisites are available" -Level "SUCCESS"
}

function Connect-ToAzure {
    Write-DeploymentLog "Connecting to Azure subscription: $SubscriptionId"
    
    try {
        # Check if already connected
        $context = Get-AzContext
        if ($context -and $context.Subscription.Id -eq $SubscriptionId) {
            Write-DeploymentLog "Already connected to correct subscription"
            return
        }
        
        # Connect to Azure
        if ($Force) {
            Connect-AzAccount -SubscriptionId $SubscriptionId -Force
        }
        else {
            Connect-AzAccount -SubscriptionId $SubscriptionId
        }
        
        # Set subscription context
        Set-AzContext -SubscriptionId $SubscriptionId
        
        Write-DeploymentLog "Successfully connected to Azure" -Level "SUCCESS"
    }
    catch {
        Write-DeploymentLog "Failed to connect to Azure: $_" -Level "ERROR"
        throw
    }
}

function Deploy-Infrastructure {
    if ($SkipInfrastructure) {
        Write-DeploymentLog "Skipping infrastructure deployment"
        return
    }
    
    Write-DeploymentLog "Deploying Azure infrastructure..."
    
    try {
        $infraScript = Join-Path $DeploymentRoot "Deploy-Infrastructure.ps1"
        
        $infraParams = @{
            SubscriptionId = $SubscriptionId
            ResourceGroupName = $ResourceGroupName
            Location = $Location
            Environment = $Environment
            TenantDomain = $TenantDomain
        }
        
        if ($WhatIf) {
            $infraParams.WhatIf = $true
        }
        
        & $infraScript @infraParams
        
        Write-DeploymentLog "Infrastructure deployment completed" -Level "SUCCESS"
    }
    catch {
        Write-DeploymentLog "Infrastructure deployment failed: $_" -Level "ERROR"
        throw
    }
}

function Build-ContainerImage {
    Write-DeploymentLog "Building container image..."
    
    try {
        Set-Location $ProjectRoot
        
        $buildArgs = @(
            "--build-arg", "BUILD_DATE=$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')",
            "--build-arg", "VCS_REF=$(git rev-parse HEAD)",
            "--build-arg", "VERSION=1.0.0",
            "--tag", "m365-security-toolkit:1.0.0",
            "--tag", "m365-security-toolkit:latest",
            "--file", "deployment\docker\Dockerfile",
            "."
        )
        
        if ($WhatIf) {
            Write-DeploymentLog "Would execute: docker build $($buildArgs -join ' ')"
        }
        else {
            & docker build @buildArgs
            
            if ($LASTEXITCODE -ne 0) {
                throw "Docker build failed with exit code $LASTEXITCODE"
            }
        }
        
        Write-DeploymentLog "Container image built successfully" -Level "SUCCESS"
    }
    catch {
        Write-DeploymentLog "Container build failed: $_" -Level "ERROR"
        throw
    }
}

function Deploy-Container {
    if ($SkipContainer) {
        Write-DeploymentLog "Skipping container deployment"
        return
    }
    
    Write-DeploymentLog "Deploying container services..."
    
    try {
        Set-Location $DeploymentRoot
        
        # Create environment file
        $envFile = Join-Path $DeploymentRoot ".env"
        if (-not (Test-Path $envFile)) {
            Copy-Item -Path (Join-Path $DeploymentRoot ".env.template") -Destination $envFile
            Write-DeploymentLog "Created .env file from template. Please configure before running." -Level "WARNING"
        }
        
        # Set environment variables for this deployment
        $env:ENVIRONMENT = $Environment
        $env:VERSION = "1.0.0"
        $env:BUILD_DATE = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'
        $env:VCS_REF = git rev-parse HEAD
        
        if ($WhatIf) {
            Write-DeploymentLog "Would execute: docker-compose up -d"
        }
        else {
            & docker-compose up -d
            
            if ($LASTEXITCODE -ne 0) {
                throw "Docker Compose deployment failed with exit code $LASTEXITCODE"
            }
            
            # Wait for services to be healthy
            Write-DeploymentLog "Waiting for services to become healthy..."
            Start-Sleep -Seconds 30
            
            & docker-compose ps
        }
        
        Write-DeploymentLog "Container deployment completed" -Level "SUCCESS"
    }
    catch {
        Write-DeploymentLog "Container deployment failed: $_" -Level "ERROR"
        throw
    }
}

function Test-Deployment {
    Write-DeploymentLog "Testing deployment..."
    
    try {
        # Test container health
        $healthOutput = & docker-compose exec -T m365-security-toolkit powershell -File "C:\app\deployment\docker\healthcheck.ps1" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-DeploymentLog "Container health check passed" -Level "SUCCESS"
        }
        else {
            Write-DeploymentLog "Container health check failed" -Level "WARNING"
            Write-DeploymentLog "Health check output: $healthOutput" -Level "WARNING"
        }
        
        # Test basic functionality
        Write-DeploymentLog "Testing basic audit functionality..."
        & docker-compose exec -T m365-security-toolkit powershell -Command "Import-Module C:\app\scripts\powershell\modules\M365CIS.psm1; Write-Host 'Module loaded successfully'"
        
        Write-DeploymentLog "Deployment testing completed" -Level "SUCCESS"
    }
    catch {
        Write-DeploymentLog "Deployment testing failed: $_" -Level "ERROR"
        throw
    }
}

function Show-DeploymentSummary {
    Write-Host "`n" + "=" * 80
    Write-Host "🚀 M365 Security Toolkit - Production Deployment Summary" -ForegroundColor Cyan
    Write-Host "=" * 80
    
    Write-Host "`n📋 Deployment Details:" -ForegroundColor Yellow
    Write-Host "   Environment: $Environment"
    Write-Host "   Subscription: $SubscriptionId"
    Write-Host "   Resource Group: $ResourceGroupName"
    Write-Host "   Location: $Location"
    Write-Host "   Tenant Domain: $TenantDomain"
    
    Write-Host "`n🔧 Services Deployed:" -ForegroundColor Yellow
    if (-not $SkipInfrastructure) {
        Write-Host "   ✅ Azure Infrastructure (Storage, Key Vault, Monitoring)"
    }
    if (-not $SkipContainer) {
        Write-Host "   ✅ Container Services (M365 Toolkit, Nginx Proxy)"
    }
    
    Write-Host "`n📊 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Configure authentication in Key Vault"
    Write-Host "   2. Set up M365 service principal permissions"
    Write-Host "   3. Configure audit scheduling"
    Write-Host "   4. Test end-to-end audit workflow"
    Write-Host "   5. Set up monitoring dashboards"
    
    Write-Host "`n🔗 Important URLs:" -ForegroundColor Yellow
    Write-Host "   Web Dashboard: http://localhost:8080"
    Write-Host "   Container Logs: docker-compose logs -f m365-security-toolkit"
    Write-Host "   Deployment Log: $LogPath"
    
    Write-Host "`n📚 Documentation:" -ForegroundColor Yellow
    Write-Host "   Production Guide: docs/PRODUCTION_DEPLOYMENT_GUIDE.md"
    Write-Host "   Security Guide: docs/SECURITY_M365_CIS.md"
    Write-Host "   Usage Guide: docs/USAGE_SHAREPOINT.md"
    
    Write-Host "`n" + "=" * 80
}

# Main deployment execution
try {
    Write-Host "🚀 Starting M365 Security Toolkit Production Deployment" -ForegroundColor Cyan
    Write-Host "Environment: $Environment" -ForegroundColor Green
    Write-Host "Target: $ResourceGroupName in $Location" -ForegroundColor Green
    Write-Host "Log File: $LogPath" -ForegroundColor Green
    
    if (-not $Force -and -not $WhatIf) {
        $confirmation = Read-Host "`nDo you want to continue with the deployment? (y/N)"
        if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
            Write-Host "Deployment cancelled by user" -ForegroundColor Yellow
            exit 0
        }
    }
    
    Write-Host "`n" + "=" * 80
    
    # Execute deployment steps
    Test-Prerequisites
    Connect-ToAzure
    Deploy-Infrastructure
    Build-ContainerImage
    Deploy-Container
    Test-Deployment
    
    Show-DeploymentSummary
    
    Write-DeploymentLog "Production deployment completed successfully!" -Level "SUCCESS"
}
catch {
    Write-DeploymentLog "Production deployment failed: $_" -Level "ERROR"
    Write-Host "`n❌ Deployment failed. Check the log file for details: $LogPath" -ForegroundColor Red
    exit 1
}
finally {
    Set-Location $ProjectRoot
}