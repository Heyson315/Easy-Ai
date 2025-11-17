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

[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
param(
  [string]$SPOAdminUrl = "https://rahmanfinanceandaccounting-admin.sharepoint.com",
  [ValidateSet('Disabled','ExistingExternalUserSharingOnly','ExternalUserSharingOnly','AnonymousLinkSharing')]
  [string]$SharingCapability = 'ExistingExternalUserSharingOnly',
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
        [ValidateSet('Preview','Applied','Error','Info')]
        [string]$Type = 'Info'
    )

    $color = switch ($Type) {
        'Preview' { 'Yellow' }
        'Applied' { 'Green' }
        'Error'   { 'Red' }
        default   { 'Cyan' }
    }

    $prefix = switch ($Type) {
        'Preview' { '[PREVIEW]' }
        'Applied' { '[APPLIED]' }
        'Error'   { '[ERROR]  ' }
        default   { '[INFO]   ' }
    }

    Write-Host "$prefix $Message" -ForegroundColor $color
}

Write-RemediationLog "Starting M365 CIS remediation..." "Info"
if ($WhatIfPreference) {
    Write-RemediationLog "Running in PREVIEW mode (-WhatIf). No changes will be applied." "Preview"
}

Write-RemediationLog "Loading modules and connecting..." "Info"
try {
  Import-Module ExchangeOnlineManagement -ErrorAction Stop
  Connect-ExchangeOnline -ShowBanner:$false -ErrorAction Stop | Out-Null
  Write-RemediationLog "Connected to Exchange Online" "Applied"
} catch {
  Write-RemediationLog "Exchange connection failed: $($_.Exception.Message)" "Error"
}

# --- EXO-2: External auto-forwarding off ---
Write-RemediationLog "Enforcing EXO-2: External auto-forwarding disabled" "Info"

# TransportConfig
try {
  if ($PSCmdlet.ShouldProcess("TransportConfig", "Set ExternalClientForwardingDisabled=True")) {
    Set-TransportConfig -ExternalClientForwardingDisabled $true -ErrorAction Stop
    Write-RemediationLog "Set-TransportConfig ExternalClientForwardingDisabled=True" "Applied"
    $script:SuccessCount++
  } else {
    Write-RemediationLog "Would set TransportConfig ExternalClientForwardingDisabled=True" "Preview"
    $script:PreviewCount++
  }
} catch {
  Write-RemediationLog "Set-TransportConfig failed: $($_.Exception.Message)" "Error"
  $script:FailureCount++
}

# Hosted Outbound Spam Filter Policy
try {
  if ($PSCmdlet.ShouldProcess("HostedOutboundSpamFilterPolicy 'Default'", "Set AutoForwardingMode=Off")) {
    Set-HostedOutboundSpamFilterPolicy -Identity "Default" -AutoForwardingMode Off -ErrorAction Stop
    Write-RemediationLog "Set-HostedOutboundSpamFilterPolicy Default AutoForwardingMode=Off" "Applied"
    $script:SuccessCount++
  } else {
    Write-RemediationLog "Would set HostedOutboundSpamFilterPolicy Default AutoForwardingMode=Off" "Preview"
    $script:PreviewCount++
  }
} catch {
  Write-RemediationLog "Set-HostedOutboundSpamFilterPolicy failed: $($_.Exception.Message)" "Error"
  $script:FailureCount++
}

# --- EXO-4: Disable legacy POP/IMAP/MAPI on flagged mailboxes ---
Write-RemediationLog "Enforcing EXO-4: Disable legacy protocols on flagged mailboxes" "Info"
$flagged = @(
  'Discovery Search Mailbox',
  'Hassan Rahman'
)
foreach ($mbx in $flagged) {
  try {
    if ($PSCmdlet.ShouldProcess("Mailbox '$mbx'", "Disable legacy protocols (POP/IMAP/MAPI)")) {
      Set-CASMailbox -Identity $mbx -PopEnabled:$false -ImapEnabled:$false -MAPIEnabled:$false -ErrorAction Stop
      Write-RemediationLog "Legacy protocols disabled for '$mbx'" "Applied"
      $script:SuccessCount++
    } else {
      Write-RemediationLog "Would disable legacy protocols for '$mbx'" "Preview"
      $script:PreviewCount++
    }
  } catch {
    Write-RemediationLog "Set-CASMailbox failed for '$mbx': $($_.Exception.Message)" "Error"
    $script:FailureCount++
  }
}

# --- DEF-1: Ensure Safe Links has an enabled rule ---
Write-RemediationLog "Enforcing DEF-1: Ensure Safe Links rule enabled" "Info"
try {
  $slRule = Get-SafeLinksRule -Identity "Built-In Protection Rule" -ErrorAction SilentlyContinue
  if ($slRule) {
    try {
      if ($PSCmdlet.ShouldProcess("SafeLinksRule '$($slRule.Name)'", "Enable rule")) {
        Enable-SafeLinksRule -Identity $slRule.Name -ErrorAction Stop
        Write-RemediationLog "Enabled Safe Links rule: $($slRule.Name)" "Applied"
        $script:SuccessCount++
      } else {
        Write-RemediationLog "Would enable Safe Links rule: $($slRule.Name)" "Preview"
        $script:PreviewCount++
      }
    } catch {
      Write-RemediationLog $_.Exception.Message "Error"
      $script:FailureCount++
    }
  } else {
    # Fallback: attempt to enable any existing disabled rule
    $anyRule = Get-SafeLinksRule | Where-Object { $_.State -ne 'Enabled' -and $_.Enabled -ne $true } | Select-Object -First 1
    if ($anyRule) {
      try {
        if ($PSCmdlet.ShouldProcess("SafeLinksRule '$($anyRule.Name)'", "Enable rule")) {
          Enable-SafeLinksRule -Identity $anyRule.Name -ErrorAction Stop
          Write-RemediationLog "Enabled Safe Links rule: $($anyRule.Name)" "Applied"
          $script:SuccessCount++
        } else {
          Write-RemediationLog "Would enable Safe Links rule: $($anyRule.Name)" "Preview"
          $script:PreviewCount++
        }
      } catch {
        Write-RemediationLog $_.Exception.Message "Error"
        $script:FailureCount++
      }
    } else {
      Write-RemediationLog "No Safe Links rule found to enable. Consider creating a policy+rule in the Defender portal." "Info"
      $script:SkippedCount++
    }
  }
} catch {
  Write-RemediationLog "Safe Links remediation skipped: $($_.Exception.Message)" "Error"
  $script:SkippedCount++
}

# --- SPO-1: Restrict SharePoint external sharing ---
Write-RemediationLog "Enforcing SPO-1: Restrict SharePoint tenant sharing" "Info"
try {
  if ($SPOAdminUrl) {
    if (Get-Module -ListAvailable Microsoft.Online.SharePoint.PowerShell) {
      Import-Module Microsoft.Online.SharePoint.PowerShell -ErrorAction Stop
      Connect-SPOService -Url $SPOAdminUrl -ErrorAction Stop
      if ($PSCmdlet.ShouldProcess("SPOTenant", "Set SharingCapability=$SharingCapability")) {
        Set-SPOTenant -SharingCapability $SharingCapability -ErrorAction Stop
        Write-RemediationLog "Set-SPOTenant SharingCapability=$SharingCapability" "Applied"
        $script:SuccessCount++
      } else {
        Write-RemediationLog "Would set SPOTenant SharingCapability=$SharingCapability" "Preview"
        $script:PreviewCount++
      }
    } else {
      Write-RemediationLog "Microsoft.Online.SharePoint.PowerShell not installed. Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser" "Error"
      $script:SkippedCount++
    }
  } else {
    Write-RemediationLog "SPOAdminUrl not provided, skipping SharePoint remediation" "Info"
    $script:SkippedCount++
  }
} catch {
  Write-RemediationLog "SPO remediation skipped: $($_.Exception.Message)" "Error"
  $script:FailureCount++
}

# --- Summary Report ---
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "    REMEDIATION SUMMARY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
if ($WhatIfPreference) {
    Write-Host "Previewed changes:  $script:PreviewCount" -ForegroundColor Yellow
} else {
    Write-Host "Successfully applied: $script:SuccessCount" -ForegroundColor Green
    Write-Host "Failed:              $script:FailureCount" -ForegroundColor Red
}
Write-Host "Skipped:            $script:SkippedCount" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($WhatIfPreference) {
    Write-RemediationLog "Preview complete. Run without -WhatIf to apply changes." "Info"
} else {
    Write-RemediationLog "Post-remediation steps attempted. Re-run the audit script to validate results." "Info"
}
