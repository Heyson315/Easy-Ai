<#
.SYNOPSIS
    Post-remediation helper for CIS M365 L1 controls with -WhatIf support

.DESCRIPTION
    Minimal post-remediation helper for CIS M365 L1 controls referenced in audit:
    - EXO-2: Disable external auto-forwarding (TransportConfig, HOSFP)
    - EXO-4: Disable legacy protocols per mailbox (sample flagged)
    - DEF-1: Ensure Safe Links rule is enabled (prefer enabling built-in rule if present)
    - SPO-1: Restrict SharePoint external sharing (Tenant level)

.PARAMETER SPOAdminUrl
    SharePoint Online admin URL (e.g., https://tenant-admin.sharepoint.com)

.PARAMETER SharingCapability
    SharePoint tenant sharing capability level

.PARAMETER Force
    Skip confirmations in production runs

.EXAMPLE
    .\PostRemediateM365CIS.ps1 -WhatIf
    Preview what changes would be made without applying them

.EXAMPLE
    .\PostRemediateM365CIS.ps1 -Force
    Apply all remediation changes without confirmation prompts

.NOTES
    Run in an elevated PowerShell session with Exchange/Graph/SPO permissions.
#>

[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
  [string]$JsonPath,
  [string]$Controls, # Comma-separated list of control IDs to remediate
  [switch]$Force
)

# Initialize counters for summary
$script:SuccessCount = 0
$script:FailureCount = 0
$script:SkippedCount = 0
$script:PreviewCount = 0

function Write-RemediationLog {
  [CmdletBinding()]
  param(
    [string]$Message,
    [ValidateSet('Preview', 'Applied', 'Error', 'Info')]
    [string]$Type = 'Info'
  )

  $color = switch ($Type) {
    'Preview' { 'Yellow' }
    'Applied' { 'Green' }
    'Error' { 'Red' }
    default { 'Cyan' }
  }

  $prefix = switch ($Type) {
    'Preview' { '[PREVIEW]' }
    'Applied' { '[APPLIED]' }
    'Error' { '[ERROR]  ' }
    default { '[INFO]   ' }
  }

  Write-Host "$prefix $Message" -ForegroundColor $color
}

# --- Helper to check if a control should be run ---
function Should-Run-Control {
  param([string]$ControlId)
  if (-not $Controls) { return $true } # If no specific controls are listed, run all
  return ($Controls -split ',').Trim() -contains $ControlId
}


Write-RemediationLog "Starting M365 CIS remediation..." "Info"
if ($PSCmdlet.ShouldProcess("M365 Tenant", "Apply Security Remediations")) {
  if ($Force) {
    Write-RemediationLog "Running in FORCE mode. Changes will be applied." "Info"
  }
}
else {
  Write-RemediationLog "Running in PREVIEW mode (-WhatIf). No changes will be applied." "Preview"
  $WhatIfPreference = $true
}


# --- Load audit data ---
if (-not (Test-Path $JsonPath)) {
  Write-RemediationLog "Audit JSON not found at $JsonPath. Cannot determine which controls failed." "Error"
  exit 1
}
$failedControls = (Get-Content $JsonPath | ConvertFrom-Json).Controls | Where-Object { $_.Status -eq 'Fail' }
$failedControlIds = $failedControls | Select-Object -ExpandProperty ControlId

Write-RemediationLog "Found $($failedControlIds.Count) failed controls in audit report." "Info"


Write-RemediationLog "Loading modules and connecting..." "Info"
try {
  Import-Module ExchangeOnlineManagement -ErrorAction Stop
  Connect-ExchangeOnline -ShowBanner:$false -ErrorAction Stop | Out-Null
  Write-RemediationLog "Connected to Exchange Online" "Applied"
}
catch {
  Write-RemediationLog "Exchange connection failed: $($_.Exception.Message)" "Error"
}

# --- EXO-2: External auto-forwarding off ---
if (Should-Run-Control -ControlId 'CIS-EXO-2' -and 'CIS-EXO-2' -in $failedControlIds) {
  Write-RemediationLog "Enforcing EXO-2: External auto-forwarding disabled" "Info"

  # TransportConfig
  try {
    if ($PSCmdlet.ShouldProcess("TransportConfig", "Set ExternalClientForwardingDisabled=True")) {
      Set-TransportConfig -ExternalClientForwardingDisabled $true -ErrorAction Stop
      Write-RemediationLog "Set-TransportConfig ExternalClientForwardingDisabled=True" "Applied"
      $script:SuccessCount++
    }
    else {
      Write-RemediationLog "Would set TransportConfig ExternalClientForwardingDisabled=True" "Preview"
      $script:PreviewCount++
    }
  }
  catch {
    Write-RemediationLog "Set-TransportConfig failed: $($_.Exception.Message)" "Error"
    $script:FailureCount++
  }

  # Outbound spam filter policy
  try {
    if ($PSCmdlet.ShouldProcess("HostedOutboundSpamFilterPolicy", "Set AutoForwardingMode=Off")) {
      Set-HostedOutboundSpamFilterPolicy -Identity (Get-HostedOutboundSpamFilterPolicy).Identity -AutoForwardingMode Off -ErrorAction Stop
      Write-RemediationLog "Set-HostedOutboundSpamFilterPolicy AutoForwardingMode=Off" "Applied"
      $script:SuccessCount++
    }
    else {
      Write-RemediationLog "Would set HostedOutboundSpamFilterPolicy AutoForwardingMode=Off" "Preview"
      $script:PreviewCount++
    }
  }
  catch {
    Write-RemediationLog "Set-HostedOutboundSpamFilterPolicy failed: $($_.Exception.Message)" "Error"
    $script:FailureCount++
  }
}
else {
  Write-RemediationLog "Skipping EXO-2: Not specified or did not fail in audit." "Info"
  $script:SkippedCount++
}


# --- EXO-4: Disable legacy protocols per mailbox ---
if (Should-Run-Control -ControlId 'CIS-EXO-4' -and 'CIS-EXO-4' -in $failedControlIds) {
  Write-RemediationLog "Enforcing EXO-4: Disabling legacy protocols for flagged mailboxes" "Info"
  try {
    # Get the mailboxes that failed the check from the audit evidence
    $failedMailboxEvidence = ($failedControls | Where-Object { $_.ControlId -eq 'CIS-EXO-4' }).Evidence
    # This is a simplified parsing. A real implementation might need more robust parsing.
    $mailboxNames = $failedMailboxEvidence -split '\r?\n' | Select-String -Pattern '\S+' | ForEach-Object { ($_ -split '\s+')[0] } | Where-Object { $_ }

    foreach ($mbxName in $mailboxNames) {
      if ($PSCmdlet.ShouldProcess($mbxName, "Disable POP/IMAP/MAPI")) {
        Set-CasMailbox -Identity $mbxName -PopEnabled $false -ImapEnabled $false -MAPIEnabled $false -ErrorAction Stop
        Write-RemediationLog "Disabled legacy protocols for $mbxName" "Applied"
        $script:SuccessCount++
      }
      else {
        Write-RemediationLog "Would disable legacy protocols for $mbxName" "Preview"
        $script:PreviewCount++
      }
    }
  }
  catch {
    Write-RemediationLog "Set-CasMailbox failed: $($_.Exception.Message)" "Error"
    $script:FailureCount++
  }
}
else {
  Write-RemediationLog "Skipping EXO-4: Not specified or did not fail in audit." "Info"
  $script:SkippedCount++
}


# --- DEF-1: Enable Safe Links ---
if (Should-Run-Control -ControlId 'CIS-DEF-1' -and 'CIS-DEF-1' -in $failedControlIds) {
  Write-RemediationLog "Enforcing DEF-1: Enabling Safe Links" "Info"
  try {
    # Prefer enabling the built-in protection rule if it exists
    $builtInRule = Get-SafeLinksRule -Identity "Built-in protection" -ErrorAction SilentlyContinue
    if ($builtInRule) {
      if ($PSCmdlet.ShouldProcess("SafeLinksRule 'Built-in protection'", "Enable")) {
        Enable-SafeLinksRule -Identity $builtInRule.Identity -ErrorAction Stop
        Write-RemediationLog "Enabled 'Built-in protection' Safe Links rule" "Applied"
        $script:SuccessCount++
      }
      else {
        Write-RemediationLog "Would enable 'Built-in protection' Safe Links rule" "Preview"
        $script:PreviewCount++
      }
    }
    else {
      # Fallback: Enable the first available policy if no built-in rule
      $policy = (Get-SafeLinksPolicy | Select-Object -First 1)
      if ($policy) {
        if ($PSCmdlet.ShouldProcess("SafeLinksPolicy '$($policy.Name)'", "Enable")) {
          Set-SafeLinksPolicy -Identity $policy.Identity -Enable $true -ErrorAction Stop
          Write-RemediationLog "Enabled Safe Links policy '$($policy.Name)'" "Applied"
          $script:SuccessCount++
        }
        else {
          Write-RemediationLog "Would enable Safe Links policy '$($policy.Name)'" "Preview"
          $script:PreviewCount++
        }
      }
      else {
        Write-RemediationLog "No Safe Links policies found to enable." "Error"
        $script:FailureCount++
      }
    }
  }
  catch {
    Write-RemediationLog "Enable-SafeLinksRule/Set-SafeLinksPolicy failed: $($_.Exception.Message)" "Error"
    $script:FailureCount++
  }
}
else {
  Write-RemediationLog "Skipping DEF-1: Not specified or did not fail in audit." "Info"
  $script:SkippedCount++
}


# --- SPO-1: Restrict SharePoint external sharing ---
if (Should-Run-Control -ControlId 'CIS-SPO-1' -and 'CIS-SPO-1' -in $failedControlIds) {
  Write-RemediationLog "Enforcing SPO-1: Restricting SharePoint external sharing" "Info"
  try {
    Import-Module Microsoft.Online.SharePoint.PowerShell -ErrorAction Stop
    Connect-SPOService -Url $SPOAdminUrl -ErrorAction Stop
    if ($PSCmdlet.ShouldProcess("SPO Tenant '$SPOAdminUrl'", "Set SharingCapability=$SharingCapability")) {
      Set-SPOTenant -SharingCapability $SharingCapability -ErrorAction Stop
      Write-RemediationLog "Set SPO tenant sharing to $SharingCapability" "Applied"
      $script:SuccessCount++
    }
    else {
      Write-RemediationLog "Would set SPO tenant sharing to $SharingCapability" "Preview"
      $script:PreviewCount++
    }
  }
  catch {
    Write-RemediationLog "Set-SPOTenant failed: $($_.Exception.Message)" "Error"
    $script:FailureCount++
  }
}
else {
  Write-RemediationLog "Skipping SPO-1: Not specified or did not fail in audit." "Info"
  $script:SkippedCount++
}


# --- Summary ---
Write-RemediationLog "----------------------------------------" "Info"
Write-RemediationLog "Remediation Summary:" "Info"
Write-RemediationLog "  Applied: $script:SuccessCount" "Applied"
Write-RemediationLog "  Previewed: $script:PreviewCount" "Preview"
Write-RemediationLog "  Skipped: $script:SkippedCount" "Info"
Write-RemediationLog "  Failed: $script:FailureCount" "Error"
Write-RemediationLog "----------------------------------------" "Info"

if ($script:FailureCount -gt 0) {
  exit 1
}
