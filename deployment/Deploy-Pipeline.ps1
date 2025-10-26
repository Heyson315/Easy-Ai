#!/usr/bin/env pwsh
<#
.SYNOPSIS
    CI/CD pipeline script for M365 Security Toolkit automated deployment

.DESCRIPTION
    Automated build, test, and deployment pipeline for the M365 Security Toolkit.
    Designed to run in GitHub Actions, Azure DevOps, or other CI/CD systems.

.PARAMETER Stage
    Pipeline stage to execute (build, test, deploy)

.PARAMETER Environment
    Target environment (development, staging, production)

.PARAMETER BuildNumber
    Build number for versioning

.PARAMETER SourceBranch
    Source branch being built

.PARAMETER WhatIf
    Preview actions without executing them

.EXAMPLE
    .\Deploy-Pipeline.ps1 -Stage build -Environment development -BuildNumber "1.0.$(Build.BuildNumber)"

.EXAMPLE
    .\Deploy-Pipeline.ps1 -Stage deploy -Environment production -BuildNumber "1.0.100" -SourceBranch "main"

.NOTES
    Designed for automated CI/CD execution
    Version: 1.0.0
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("build", "test", "deploy", "all")]
    [string]$Stage,
    
    [Parameter(Mandatory = $true)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment,
    
    [Parameter(Mandatory = $true)]
    [string]$BuildNumber,
    
    [string]$SourceBranch = "main",
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

# Pipeline constants
$ScriptRoot = $PSScriptRoot
$ProjectRoot = Split-Path $ScriptRoot -Parent
$ArtifactsPath = Join-Path $ProjectRoot "artifacts"
$LogPath = Join-Path $ArtifactsPath "pipeline-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# Ensure artifacts directory exists
$null = New-Item -Path $ArtifactsPath -ItemType Directory -Force

function Write-PipelineLog {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # GitHub Actions logging format
    switch ($Level) {
        "INFO" { 
            Write-Host $logEntry
            Write-Host "::notice::$Message"
        }
        "WARNING" { 
            Write-Host $logEntry -ForegroundColor Yellow
            Write-Host "::warning::$Message"
        }
        "ERROR" { 
            Write-Host $logEntry -ForegroundColor Red
            Write-Host "::error::$Message"
        }
        "SUCCESS" { 
            Write-Host $logEntry -ForegroundColor Green
            Write-Host "::notice::✅ $Message"
        }
    }
    
    Add-Content -Path $LogPath -Value $logEntry
}

function Invoke-BuildStage {
    Write-PipelineLog "Starting build stage..."
    
    try {
        # Set version information
        $version = $BuildNumber
        $buildDate = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'
        $vcsRef = if (Get-Command git -ErrorAction SilentlyContinue) { git rev-parse HEAD } else { "unknown" }
        
        Write-PipelineLog "Build version: $version"
        Write-PipelineLog "Build date: $buildDate"
        Write-PipelineLog "VCS ref: $vcsRef"
        
        # Validate code structure
        Write-PipelineLog "Validating project structure..."
        
        $requiredFiles = @(
            "config/production_config.json",
            "scripts/powershell/modules/M365CIS.psm1",
            "deployment/docker/Dockerfile",
            "deployment/Deploy-Infrastructure.ps1"
        )
        
        foreach ($file in $requiredFiles) {
            $filePath = Join-Path $ProjectRoot $file
            if (-not (Test-Path $filePath)) {
                throw "Required file missing: $file"
            }
        }
        
        # Build container image
        Write-PipelineLog "Building container image..."
        Set-Location $ProjectRoot
        
        $buildArgs = @(
            "--build-arg", "BUILD_DATE=$buildDate",
            "--build-arg", "VCS_REF=$vcsRef",
            "--build-arg", "VERSION=$version",
            "--tag", "m365-security-toolkit:$version",
            "--tag", "m365-security-toolkit:latest",
            "--file", "deployment/docker/Dockerfile",
            "."
        )
        
        if ($WhatIf) {
            Write-PipelineLog "Would execute: docker build $($buildArgs -join ' ')"
        }
        else {
            & docker build @buildArgs
            
            if ($LASTEXITCODE -ne 0) {
                throw "Docker build failed with exit code $LASTEXITCODE"
            }
        }
        
        # Save build artifacts
        $buildInfo = @{
            Version = $version
            BuildDate = $buildDate
            VcsRef = $vcsRef
            SourceBranch = $SourceBranch
            Environment = $Environment
        }
        
        $buildInfoPath = Join-Path $ArtifactsPath "build-info.json"
        $buildInfo | ConvertTo-Json -Depth 10 | Set-Content -Path $buildInfoPath
        
        Write-PipelineLog "Build stage completed successfully" -Level "SUCCESS"
    }
    catch {
        Write-PipelineLog "Build stage failed: $_" -Level "ERROR"
        throw
    }
}

function Invoke-TestStage {
    Write-PipelineLog "Starting test stage..."
    
    try {
        Set-Location $ProjectRoot
        
        # Run PowerShell tests
        Write-PipelineLog "Running PowerShell module tests..."
        
        if (Get-Module -Name Pester -ListAvailable) {
            $pesterConfig = @{
                Run = @{
                    Path = "tests"
                    PassThru = $true
                }
                Output = @{
                    Verbosity = "Detailed"
                }
                TestResult = @{
                    Enabled = $true
                    OutputPath = Join-Path $ArtifactsPath "test-results.xml"
                    OutputFormat = "NUnitXml"
                }
                CodeCoverage = @{
                    Enabled = $true
                    OutputPath = Join-Path $ArtifactsPath "coverage.xml"
                    OutputFormat = "JaCoCo"
                }
            }
            
            $testResults = Invoke-Pester -Configuration $pesterConfig
            
            if ($testResults.FailedCount -gt 0) {
                throw "PowerShell tests failed: $($testResults.FailedCount) failures"
            }
            
            Write-PipelineLog "PowerShell tests passed: $($testResults.PassedCount) tests" -Level "SUCCESS"
        }
        else {
            Write-PipelineLog "Pester not available, skipping PowerShell tests" -Level "WARNING"
        }
        
        # Run Python tests
        Write-PipelineLog "Running Python tests..."
        
        if (Get-Command python -ErrorAction SilentlyContinue) {
            # Install test dependencies
            & python -m pip install pytest pytest-cov pytest-xdist
            
            # Run pytest with coverage
            $pytestArgs = @(
                "-v",
                "--cov=src",
                "--cov-report=xml:$ArtifactsPath/python-coverage.xml",
                "--cov-report=html:$ArtifactsPath/python-coverage-html",
                "--junit-xml=$ArtifactsPath/python-test-results.xml",
                "tests/"
            )
            
            & python -m pytest @pytestArgs
            
            if ($LASTEXITCODE -ne 0) {
                throw "Python tests failed with exit code $LASTEXITCODE"
            }
            
            Write-PipelineLog "Python tests passed" -Level "SUCCESS"
        }
        else {
            Write-PipelineLog "Python not available, skipping Python tests" -Level "WARNING"
        }
        
        # Test container health
        Write-PipelineLog "Testing container health..."
        
        if ($WhatIf) {
            Write-PipelineLog "Would test container health"
        }
        else {
            # Start container for testing
            Set-Location (Join-Path $ProjectRoot "deployment")
            & docker-compose -f docker-compose.yml up -d
            
            # Wait for container to be ready
            Start-Sleep -Seconds 30
            
            # Run health check
            $healthResult = & docker-compose exec -T m365-security-toolkit powershell -File "C:\app\deployment\docker\healthcheck.ps1"
            
            if ($LASTEXITCODE -eq 0) {
                Write-PipelineLog "Container health check passed" -Level "SUCCESS"
            }
            else {
                Write-PipelineLog "Container health check failed" -Level "ERROR"
                throw "Container health check failed"
            }
            
            # Clean up test container
            & docker-compose down
        }
        
        Write-PipelineLog "Test stage completed successfully" -Level "SUCCESS"
    }
    catch {
        Write-PipelineLog "Test stage failed: $_" -Level "ERROR"
        throw
    }
}

function Invoke-DeployStage {
    Write-PipelineLog "Starting deploy stage..."
    
    try {
        # Validate deployment environment
        if ($Environment -eq "production" -and $SourceBranch -ne "main") {
            throw "Production deployments are only allowed from main branch"
        }
        
        # Load build information
        $buildInfoPath = Join-Path $ArtifactsPath "build-info.json"
        if (Test-Path $buildInfoPath) {
            $buildInfo = Get-Content $buildInfoPath | ConvertFrom-Json
            Write-PipelineLog "Deploying version: $($buildInfo.Version)"
        }
        else {
            Write-PipelineLog "Build info not found, using current build number" -Level "WARNING"
        }
        
        # Set deployment parameters based on environment
        $deployParams = switch ($Environment) {
            "development" {
                @{
                    SubscriptionId = $env:AZURE_DEV_SUBSCRIPTION_ID
                    ResourceGroupName = "rg-m365-toolkit-dev"
                    Location = "East US"
                    TenantDomain = $env:M365_DEV_TENANT_DOMAIN
                }
            }
            "staging" {
                @{
                    SubscriptionId = $env:AZURE_STAGING_SUBSCRIPTION_ID
                    ResourceGroupName = "rg-m365-toolkit-staging"
                    Location = "East US"
                    TenantDomain = $env:M365_STAGING_TENANT_DOMAIN
                }
            }
            "production" {
                @{
                    SubscriptionId = $env:AZURE_PROD_SUBSCRIPTION_ID
                    ResourceGroupName = "rg-m365-toolkit-prod"
                    Location = "East US"
                    TenantDomain = $env:M365_PROD_TENANT_DOMAIN
                }
            }
        }
        
        # Execute deployment
        $deployScript = Join-Path $ScriptRoot "Deploy-Production.ps1"
        
        $deployParams.Environment = $Environment
        $deployParams.Force = $true
        
        if ($WhatIf) {
            $deployParams.WhatIf = $true
        }
        
        Write-PipelineLog "Executing deployment with parameters: $($deployParams | ConvertTo-Json -Compress)"
        
        & $deployScript @deployParams
        
        # Post-deployment verification
        Write-PipelineLog "Running post-deployment verification..."
        
        if (-not $WhatIf) {
            # Wait for services to stabilize
            Start-Sleep -Seconds 60
            
            # Test deployed services
            Set-Location (Join-Path $ProjectRoot "deployment")
            $serviceStatus = & docker-compose ps --format json | ConvertFrom-Json
            
            foreach ($service in $serviceStatus) {
                if ($service.State -ne "running") {
                    throw "Service $($service.Service) is not running: $($service.State)"
                }
                Write-PipelineLog "Service $($service.Service) is running" -Level "SUCCESS"
            }
        }
        
        Write-PipelineLog "Deploy stage completed successfully" -Level "SUCCESS"
    }
    catch {
        Write-PipelineLog "Deploy stage failed: $_" -Level "ERROR"
        throw
    }
}

# Main pipeline execution
try {
    Write-Host "🚀 M365 Security Toolkit - CI/CD Pipeline" -ForegroundColor Cyan
    Write-Host "Stage: $Stage" -ForegroundColor Green
    Write-Host "Environment: $Environment" -ForegroundColor Green
    Write-Host "Build: $BuildNumber" -ForegroundColor Green
    Write-Host "Branch: $SourceBranch" -ForegroundColor Green
    Write-Host "=" * 80
    
    switch ($Stage) {
        "build" {
            Invoke-BuildStage
        }
        "test" {
            Invoke-TestStage
        }
        "deploy" {
            Invoke-DeployStage
        }
        "all" {
            Invoke-BuildStage
            Invoke-TestStage
            Invoke-DeployStage
        }
    }
    
    Write-PipelineLog "Pipeline stage '$Stage' completed successfully!" -Level "SUCCESS"
    Write-Host "::set-output name=success::true"
}
catch {
    Write-PipelineLog "Pipeline stage '$Stage' failed: $_" -Level "ERROR"
    Write-Host "::set-output name=success::false"
    exit 1
}
finally {
    Set-Location $ProjectRoot
}