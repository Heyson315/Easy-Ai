#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build and Deploy M365 Security Toolkit Container

.DESCRIPTION
    This script builds the Docker container and deploys it to Azure Container Registry

.PARAMETER ResourceGroupName
    Name of the Azure resource group

.PARAMETER ContainerRegistryName
    Name of the Azure Container Registry

.PARAMETER ImageTag
    Tag for the container image (default: latest)

.PARAMETER PushToRegistry
    Push the built image to Azure Container Registry

.EXAMPLE
    .\Build-Container.ps1 -ResourceGroupName "rg-m365-security-prod" -ContainerRegistryName "crm365securitytoolkitprod" -PushToRegistry

.NOTES
    Author: M365 Security Toolkit Team
    Version: 1.0.0
    Requires: Docker, Azure CLI
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $true)]
    [string]$ContainerRegistryName,
    
    [Parameter(Mandatory = $false)]
    [string]$ImageTag = "latest",
    
    [Parameter(Mandatory = $false)]
    [switch]$PushToRegistry
)

# Error handling
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Script configuration
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptPath
$ImageName = "m365-security-toolkit"

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
    
    # Check if Docker is running
    try {
        docker version | Out-Null
        Write-Host "✅ Docker is running" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Docker is not running or not installed"
        exit 1
    }
    
    # Check if Azure CLI is installed
    try {
        az version | Out-Null
        Write-Host "✅ Azure CLI is available" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Azure CLI is not installed"
        exit 1
    }
    
    # Check if Dockerfile exists
    $dockerFile = Join-Path $ProjectRoot "Dockerfile"
    if (-not (Test-Path $dockerFile)) {
        Write-Error "❌ Dockerfile not found at: $dockerFile"
        exit 1
    }
    Write-Host "✅ Dockerfile found" -ForegroundColor Green
}

function Build-DockerImage {
    Write-Host "🔨 Building Docker image..." -ForegroundColor Blue
    
    try {
        Push-Location $ProjectRoot
        
        $fullImageName = "$ImageName`:$ImageTag"
        Write-Host "Building image: $fullImageName" -ForegroundColor Cyan
        
        docker build -t $fullImageName . --no-cache
        
        if ($LASTEXITCODE -ne 0) {
            throw "Docker build failed with exit code $LASTEXITCODE"
        }
        
        Write-Host "✅ Docker image built successfully: $fullImageName" -ForegroundColor Green
        return $fullImageName
    }
    catch {
        Write-Error "❌ Failed to build Docker image: $_"
        exit 1
    }
    finally {
        Pop-Location
    }
}

function Push-ToContainerRegistry {
    param([string]$LocalImageName)
    
    if (-not $PushToRegistry) {
        Write-Host "⏭️ Skipping push to container registry" -ForegroundColor Yellow
        return
    }
    
    Write-Host "📤 Pushing to Azure Container Registry..." -ForegroundColor Blue
    
    try {
        # Login to Azure Container Registry
        Write-Host "🔐 Logging in to Azure Container Registry..." -ForegroundColor Blue
        az acr login --name $ContainerRegistryName
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to login to Azure Container Registry"
        }
        
        # Get the login server
        $loginServer = az acr show --name $ContainerRegistryName --resource-group $ResourceGroupName --query "loginServer" --output tsv
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to get container registry login server"
        }
        
        # Tag image for registry
        $registryImageName = "$loginServer/$ImageName`:$ImageTag"
        Write-Host "Tagging image for registry: $registryImageName" -ForegroundColor Cyan
        
        docker tag $LocalImageName $registryImageName
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to tag image for registry"
        }
        
        # Push image
        Write-Host "Pushing image to registry..." -ForegroundColor Cyan
        docker push $registryImageName
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to push image to registry"
        }
        
        Write-Host "✅ Image pushed successfully: $registryImageName" -ForegroundColor Green
        return $registryImageName
    }
    catch {
        Write-Error "❌ Failed to push to container registry: $_"
        exit 1
    }
}

function Show-NextSteps {
    param([string]$RegistryImageName)
    
    Write-Host ""
    Write-Host "🎉 Container build completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Test the container locally:" -ForegroundColor White
    Write-Host "   docker run -it --rm $ImageName`:$ImageTag" -ForegroundColor Gray
    Write-Host ""
    
    if ($RegistryImageName) {
        Write-Host "2. Deploy to Azure Container Instances:" -ForegroundColor White
        Write-Host "   az container create --resource-group $ResourceGroupName --name m365-security-toolkit --image $RegistryImageName" -ForegroundColor Gray
        Write-Host ""
        Write-Host "3. Or use with Docker Compose:" -ForegroundColor White
        Write-Host "   Update docker-compose.yml to use: $RegistryImageName" -ForegroundColor Gray
    }
    else {
        Write-Host "2. Push to registry:" -ForegroundColor White
        Write-Host "   .\Build-Container.ps1 -ResourceGroupName '$ResourceGroupName' -ContainerRegistryName '$ContainerRegistryName' -PushToRegistry" -ForegroundColor Gray
    }
}

# Main execution
try {
    Write-Banner "M365 Security Toolkit - Container Build"
    
    Write-Host "🎯 Build Configuration:" -ForegroundColor Blue
    Write-Host "  Resource Group: $ResourceGroupName" -ForegroundColor Cyan
    Write-Host "  Container Registry: $ContainerRegistryName" -ForegroundColor Cyan
    Write-Host "  Image Tag: $ImageTag" -ForegroundColor Cyan
    Write-Host "  Push to Registry: $PushToRegistry" -ForegroundColor Cyan
    Write-Host "  Project Root: $ProjectRoot" -ForegroundColor Cyan
    Write-Host ""
    
    Test-Prerequisites
    $localImage = Build-DockerImage
    $registryImage = Push-ToContainerRegistry -LocalImageName $localImage
    Show-NextSteps -RegistryImageName $registryImage
    
    Write-Host ""
    Write-Host "✅ Container build script completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "❌ Container build failed: $_" -ForegroundColor Red
    Write-Host "Stack trace:" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}