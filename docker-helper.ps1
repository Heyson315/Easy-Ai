#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick Docker operations for M365 Security Toolkit

.DESCRIPTION
    Helper script for common Docker operations with the M365 Security Toolkit

.PARAMETER Action
    Action to perform: build, run, stop, logs, status

.PARAMETER Tag
    Image tag (default: latest)

.EXAMPLE
    .\docker-helper.ps1 -Action build
    .\docker-helper.ps1 -Action run
    .\docker-helper.ps1 -Action status

.NOTES
    Author: M365 Security Toolkit Team
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("build", "run", "stop", "logs", "status", "clean")]
    [string]$Action,
    
    [Parameter(Mandatory = $false)]
    [string]$Tag = "latest"
)

$ImageName = "m365-security-toolkit"
$ContainerName = "m365-security-toolkit"

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️ $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

switch ($Action) {
    "build" {
        Write-Info "Building Docker image: $ImageName`:$Tag"
        docker build -f Dockerfile.python -t "$ImageName`:$Tag" .
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Image built successfully"
        } else {
            Write-Error "Build failed"
        }
    }
    
    "run" {
        Write-Info "Running container: $ContainerName"
        
        # Stop existing container if running
        $existing = docker ps -q -f name=$ContainerName
        if ($existing) {
            Write-Info "Stopping existing container..."
            docker stop $ContainerName | Out-Null
            docker rm $ContainerName | Out-Null
        }
        
        # Run new container
        docker run -d `
            --name $ContainerName `
            -v "${PWD}/data:/app/data" `
            -v "${PWD}/output:/app/output" `
            -v "${PWD}/config:/app/config:ro" `
            "$ImageName`:$Tag"
            
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Container started successfully"
            Write-Info "Use 'docker-helper.ps1 -Action logs' to view logs"
        } else {
            Write-Error "Failed to start container"
        }
    }
    
    "stop" {
        Write-Info "Stopping container: $ContainerName"
        docker stop $ContainerName
        docker rm $ContainerName
        Write-Success "Container stopped and removed"
    }
    
    "logs" {
        Write-Info "Showing logs for container: $ContainerName"
        docker logs -f $ContainerName
    }
    
    "status" {
        Write-Info "Docker status:"
        Write-Host ""
        Write-Host "Images:" -ForegroundColor Cyan
        docker images | Select-String $ImageName
        Write-Host ""
        Write-Host "Containers:" -ForegroundColor Cyan
        docker ps -a | Select-String $ContainerName
        Write-Host ""
        Write-Host "Running containers:" -ForegroundColor Cyan
        docker ps | Select-String $ContainerName
    }
    
    "clean" {
        Write-Info "Cleaning up Docker resources..."
        
        # Stop and remove container
        $existing = docker ps -aq -f name=$ContainerName
        if ($existing) {
            docker stop $ContainerName | Out-Null
            docker rm $ContainerName | Out-Null
            Write-Success "Removed container: $ContainerName"
        }
        
        # Remove image
        $existingImage = docker images -q $ImageName
        if ($existingImage) {
            docker rmi "$ImageName`:$Tag" | Out-Null
            Write-Success "Removed image: $ImageName`:$Tag"
        }
        
        Write-Success "Cleanup completed"
    }
}