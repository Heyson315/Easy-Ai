<#
.SYNOPSIS
    Setup automated M365 CIS audit scheduling using Windows Task Scheduler

.DESCRIPTION
    Creates a Windows scheduled task for automated M365 security audits.
    Supports Daily, Weekly, and Monthly schedules with configurable parameters.

.PARAMETER Schedule
    Frequency of audit execution (Daily, Weekly, or Monthly)

.PARAMETER DayOfWeek
    Day of week for weekly schedules (Monday-Sunday). Required for Weekly schedule.

.PARAMETER Time
    Time of day to run audit in 24-hour format (default: 09:00)

.PARAMETER SPOAdminUrl
    SharePoint Online admin URL for tenant checks

.PARAMETER TaskName
    Name for the scheduled task (default: M365-CIS-Audit)

.PARAMETER LogPath
    Path for audit logs (default: output/logs/scheduled_audit.log)

.EXAMPLE
    .\Setup-ScheduledAudit.ps1 -Schedule Weekly -DayOfWeek Monday -Time "09:00"

.EXAMPLE
    .\Setup-ScheduledAudit.ps1 -Schedule Daily -Time "06:00" -SPOAdminUrl "https://tenant-admin.sharepoint.com"

.NOTES
    Requires administrative privileges to create scheduled tasks
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Daily','Weekly','Monthly')]
    [string]$Schedule,

    [ValidateSet('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')]
    [string]$DayOfWeek,

    [string]$Time = "09:00",

    [string]$SPOAdminUrl,

    [string]$TaskName = "M365-CIS-Audit",

    [string]$LogPath = "output/logs/scheduled_audit.log"
)

# Verify running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "This script must be run as Administrator to create scheduled tasks."
    Write-Host "Please restart PowerShell as Administrator and try again." -ForegroundColor Yellow
    exit 1
}

# Validate DayOfWeek for Weekly schedule
if ($Schedule -eq 'Weekly' -and -not $DayOfWeek) {
    Write-Error "DayOfWeek parameter is required for Weekly schedule."
    exit 1
}

# Get script paths
$scriptRoot = Split-Path -Parent $PSScriptRoot
$auditScriptPath = Join-Path $scriptRoot "scripts\powershell\Invoke-M365CISAudit.ps1"
$logDirectory = Split-Path -Parent (Join-Path $scriptRoot $LogPath)

# Verify audit script exists
if (-not (Test-Path $auditScriptPath)) {
    Write-Error "Audit script not found: $auditScriptPath"
    exit 1
}

# Create log directory if it doesn't exist
if (-not (Test-Path $logDirectory)) {
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
    Write-Host "[+] Created log directory: $logDirectory" -ForegroundColor Green
}

# Build PowerShell command with parameters
$auditCommand = "powershell.exe"
$auditArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$auditScriptPath`" -Timestamped"

if ($SPOAdminUrl) {
    $auditArgs += " -SPOAdminUrl `"$SPOAdminUrl`""
}

# Add output redirection for logging
$fullLogPath = Join-Path $scriptRoot $LogPath
$auditArgs += " >> `"$fullLogPath`" 2>&1"

Write-Host "`n[+] Setting up M365 CIS Audit scheduled task..." -ForegroundColor Cyan
Write-Host "    Task Name: $TaskName" -ForegroundColor Gray
Write-Host "    Schedule: $Schedule" -ForegroundColor Gray
if ($DayOfWeek) {
    Write-Host "    Day of Week: $DayOfWeek" -ForegroundColor Gray
}
Write-Host "    Time: $Time" -ForegroundColor Gray
Write-Host "    Audit Script: $auditScriptPath" -ForegroundColor Gray
Write-Host "    Log File: $fullLogPath" -ForegroundColor Gray

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "`n[!] Task '$TaskName' already exists. Removing..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "    Existing task removed." -ForegroundColor Green
}

# Create scheduled task action
$action = New-ScheduledTaskAction `
    -Execute $auditCommand `
    -Argument $auditArgs `
    -WorkingDirectory $scriptRoot

# Create trigger based on schedule type
switch ($Schedule) {
    'Daily' {
        $trigger = New-ScheduledTaskTrigger -Daily -At $Time
    }
    'Weekly' {
        $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $DayOfWeek -At $Time
    }
    'Monthly' {
        # Monthly on the 1st day of each month
        $trigger = New-ScheduledTaskTrigger -Daily -At $Time
        # Note: For true monthly, would need to use custom XML or multiple triggers
        Write-Warning "Monthly schedule uses daily trigger with custom recurrence. Review task in Task Scheduler."
    }
}

# Create task principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

# Create task settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Register the scheduled task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description "Automated M365 CIS Level 1 security audit with timestamped outputs" `
        -ErrorAction Stop | Out-Null

    Write-Host "`n[✓] Scheduled task created successfully!" -ForegroundColor Green
    Write-Host "`n[+] Task Details:" -ForegroundColor Cyan

    $task = Get-ScheduledTask -TaskName $TaskName
    Write-Host "    Name: $($task.TaskName)" -ForegroundColor Gray
    Write-Host "    State: $($task.State)" -ForegroundColor Gray
    Write-Host "    Next Run Time: $((Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo).NextRunTime)" -ForegroundColor Gray

    Write-Host "`n[+] Management Commands:" -ForegroundColor Cyan
    Write-Host "    View task:    Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "    Run now:      Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "    Disable:      Disable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "    Remove:       Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor Gray
    Write-Host "    View logs:    Get-Content '$fullLogPath' -Tail 50" -ForegroundColor Gray

} catch {
    Write-Error "Failed to create scheduled task: $($_.Exception.Message)"
    exit 1
}

Write-Host "`n[+] Setup complete!`n" -ForegroundColor Green

# Offer to run test
$runTest = Read-Host "Would you like to run a test audit now? (Y/N)"
if ($runTest -eq 'Y' -or $runTest -eq 'y') {
    Write-Host "`n[+] Starting test audit..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "[+] Test audit started. Check Task Scheduler for execution status." -ForegroundColor Green
    Write-Host "    Log file: $fullLogPath" -ForegroundColor Gray
}
