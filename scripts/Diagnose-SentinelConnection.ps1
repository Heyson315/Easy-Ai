#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Microsoft Sentinel Connection Diagnostics

.DESCRIPTION
    Diagnoses common Microsoft Sentinel connection issues and provides solutions

.EXAMPLE
    .\Diagnose-SentinelConnection.ps1

.NOTES
    Author: M365 Security Toolkit Team
    Version: 1.0.0
#>

function Test-AzureConnection {
    Write-Host "🔍 Testing Azure Connection..." -ForegroundColor Blue
    
    try {
        $account = az account show --output json 2>$null | ConvertFrom-Json
        if ($account) {
            Write-Host "✅ Connected to Azure" -ForegroundColor Green
            Write-Host "   Subscription: $($account.name)" -ForegroundColor Cyan
            Write-Host "   Tenant: $($account.tenantDisplayName)" -ForegroundColor Cyan
            return $true
        }
    }
    catch {
        Write-Host "❌ Not connected to Azure" -ForegroundColor Red
        Write-Host "   Run: az login" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "❌ Azure CLI not authenticated" -ForegroundColor Red
    Write-Host "   Run: az login" -ForegroundColor Yellow
    return $false
}

function Test-SentinelPermissions {
    Write-Host "🔍 Testing Sentinel Permissions..." -ForegroundColor Blue
    
    try {
        # Check if user has required permissions
        $permissions = az role assignment list --assignee (az account show --query user.name -o tsv) --output json | ConvertFrom-Json
        
        $requiredRoles = @(
            "Microsoft Sentinel Contributor",
            "Microsoft Sentinel Reader", 
            "Security Admin",
            "Security Reader",
            "Contributor",
            "Owner"
        )
        
        $hasPermissions = $false
        foreach ($assignment in $permissions) {
            if ($requiredRoles -contains $assignment.roleDefinitionName) {
                Write-Host "✅ Found permission: $($assignment.roleDefinitionName)" -ForegroundColor Green
                $hasPermissions = $true
            }
        }
        
        if (-not $hasPermissions) {
            Write-Host "❌ Missing required Sentinel permissions" -ForegroundColor Red
            Write-Host "   Required roles: $($requiredRoles -join ', ')" -ForegroundColor Yellow
        }
        
        return $hasPermissions
    }
    catch {
        Write-Host "⚠️ Could not check permissions: $_" -ForegroundColor Yellow
        return $false
    }
}

function Test-SentinelWorkspace {
    Write-Host "🔍 Checking Sentinel Workspaces..." -ForegroundColor Blue
    
    try {
        # Check for Sentinel workspaces
        $workspaces = az monitor log-analytics workspace list --output json 2>$null | ConvertFrom-Json
        
        if ($workspaces -and $workspaces.Count -gt 0) {
            Write-Host "✅ Found Log Analytics Workspaces:" -ForegroundColor Green
            foreach ($ws in $workspaces) {
                Write-Host "   - $($ws.name) (Resource Group: $($ws.resourceGroup))" -ForegroundColor Cyan
                
                # Check if Sentinel is enabled on this workspace
                try {
                    $sentinelSolutions = az resource list --resource-group $ws.resourceGroup --resource-type "Microsoft.OperationsManagement/solutions" --query "[?contains(name, 'SecurityInsights')]" --output json | ConvertFrom-Json
                    
                    if ($sentinelSolutions -and $sentinelSolutions.Count -gt 0) {
                        Write-Host "     ✅ Sentinel enabled" -ForegroundColor Green
                    } else {
                        Write-Host "     ❌ Sentinel not enabled" -ForegroundColor Red
                        Write-Host "     Enable Sentinel: https://portal.azure.com/#blade/Microsoft_Azure_Security_Insights/MainMenuBlade" -ForegroundColor Yellow
                    }
                }
                catch {
                    Write-Host "     ⚠️ Could not check Sentinel status" -ForegroundColor Yellow
                }
            }
        } else {
            Write-Host "❌ No Log Analytics Workspaces found" -ForegroundColor Red
            Write-Host "   Create workspace: az monitor log-analytics workspace create" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "❌ Error checking workspaces: $_" -ForegroundColor Red
    }
}

function Test-SentinelExtension {
    Write-Host "🔍 Checking Azure CLI Sentinel Extension..." -ForegroundColor Blue
    
    try {
        $extensions = az extension list --output json | ConvertFrom-Json
        $sentinelExt = $extensions | Where-Object { $_.name -eq "sentinel" }
        
        if ($sentinelExt) {
            Write-Host "✅ Sentinel extension installed (Version: $($sentinelExt.version))" -ForegroundColor Green
        } else {
            Write-Host "❌ Sentinel extension not installed" -ForegroundColor Red
            Write-Host "   Install: az extension add --name sentinel" -ForegroundColor Yellow
            
            # Auto-install the extension
            Write-Host "Installing Sentinel extension..." -ForegroundColor Blue
            az extension add --name sentinel --output none
            Write-Host "✅ Sentinel extension installed" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "❌ Error checking extensions: $_" -ForegroundColor Red
    }
}

function Test-NetworkConnectivity {
    Write-Host "🔍 Testing Network Connectivity..." -ForegroundColor Blue
    
    $endpoints = @(
        "management.azure.com",
        "login.microsoftonline.com",
        "graph.microsoft.com",
        "security.microsoft.com"
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $result = Test-NetConnection -ComputerName $endpoint -Port 443 -WarningAction SilentlyContinue
            if ($result.TcpTestSucceeded) {
                Write-Host "✅ $endpoint - Connected" -ForegroundColor Green
            } else {
                Write-Host "❌ $endpoint - Failed" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "⚠️ $endpoint - Could not test" -ForegroundColor Yellow
        }
    }
}

function Show-SolutionSteps {
    Write-Host ""
    Write-Host "🔧 Common Solutions for Sentinel Connection Issues:" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "1. Authentication Issues:" -ForegroundColor White
    Write-Host "   az login --tenant your-tenant-id" -ForegroundColor Gray
    Write-Host "   az account set --subscription your-subscription-id" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "2. Install Required Extensions:" -ForegroundColor White
    Write-Host "   az extension add --name sentinel" -ForegroundColor Gray
    Write-Host "   az extension add --name securityinsight" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "3. Enable Sentinel on Workspace:" -ForegroundColor White
    Write-Host "   # Via Portal: https://portal.azure.com/#blade/Microsoft_Azure_Security_Insights/MainMenuBlade" -ForegroundColor Gray
    Write-Host "   # Via CLI: az sentinel workspace create" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "4. Check Resource Permissions:" -ForegroundColor White
    Write-Host "   # Ensure you have Sentinel Contributor role" -ForegroundColor Gray
    Write-Host "   az role assignment create --assignee user@domain.com --role 'Microsoft Sentinel Contributor'" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "5. Firewall/Proxy Issues:" -ForegroundColor White
    Write-Host "   # Ensure these domains are accessible:" -ForegroundColor Gray
    Write-Host "   # - *.azure.com" -ForegroundColor Gray
    Write-Host "   # - *.microsoftonline.com" -ForegroundColor Gray
    Write-Host "   # - *.security.microsoft.com" -ForegroundColor Gray
}

# Main execution
Write-Host ""
Write-Host "🛡️ Microsoft Sentinel Connection Diagnostics" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

$azureConnected = Test-AzureConnection
$hasPermissions = Test-SentinelPermissions
Test-SentinelWorkspace
Test-SentinelExtension
Test-NetworkConnectivity

Write-Host ""
Write-Host "📊 Diagnosis Summary:" -ForegroundColor Blue
Write-Host "   Azure Connected: $(if($azureConnected){'✅'}else{'❌'})" -ForegroundColor $(if($azureConnected){'Green'}else{'Red'})
Write-Host "   Sentinel Permissions: $(if($hasPermissions){'✅'}else{'❌'})" -ForegroundColor $(if($hasPermissions){'Green'}else{'Red'})

if (-not $azureConnected -or -not $hasPermissions) {
    Show-SolutionSteps
}