<#
.SYNOPSIS
    Remove M365 CIS audit scheduled task

.DESCRIPTION
    Removes the automated M365 CIS audit scheduled task from Windows Task Scheduler.

.PARAMETER TaskName
    Name of the scheduled task to remove (default: M365-CIS-Audit)

.PARAMETER Force
    Skip confirmation prompt

.EXAMPLE
    .\Remove-ScheduledAudit.ps1
    
.EXAMPLE
    .\Remove-ScheduledAudit.ps1 -TaskName "M365-CIS-Audit" -Force

.NOTES
    Requires administrative privileges to remove scheduled tasks
#>

[CmdletBinding()]
param(
    [string]$TaskName = "M365-CIS-Audit",
    [switch]$Force
)

# Verify running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "This script must be run as Administrator to remove scheduled tasks."
    Write-Host "Please restart PowerShell as Administrator and try again." -ForegroundColor Yellow
    exit 1
}

# Check if task exists
$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if (-not $task) {
    Write-Host "[!] Scheduled task '$TaskName' not found." -ForegroundColor Yellow
    Write-Host "    No action needed." -ForegroundColor Gray
    exit 0
}

# Display task details
Write-Host "`n[+] Found scheduled task: $TaskName" -ForegroundColor Cyan
Write-Host "    State: $($task.State)" -ForegroundColor Gray
Write-Host "    Description: $($task.Description)" -ForegroundColor Gray

$taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
Write-Host "    Last Run Time: $($taskInfo.LastRunTime)" -ForegroundColor Gray
Write-Host "    Next Run Time: $($taskInfo.NextRunTime)" -ForegroundColor Gray

# Confirm removal
if (-not $Force) {
    Write-Host ""
    $confirm = Read-Host "Are you sure you want to remove this task? (Y/N)"
    if ($confirm -ne 'Y' -and $confirm -ne 'y') {
        Write-Host "[!] Removal cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Remove the task
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop
    Write-Host "`n[✓] Scheduled task '$TaskName' removed successfully!" -ForegroundColor Green
} catch {
    Write-Error "Failed to remove scheduled task: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
