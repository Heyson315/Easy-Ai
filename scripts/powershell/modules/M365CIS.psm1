# M365CIS.psm1 - Microsoft 365 CIS Foundations L1 (v3.0) audit helpers
# NOTE: Requires appropriate admin roles and modules installed (ExchangeOnlineManagement, Microsoft.Graph).
# This module provides read-only audit functions. Remediation should be run with -WhatIf until validated.

function Write-CISLog {
    param(
        [string]$Message,
        [ValidateSet('Info','Warn','Error')][string]$Level = 'Info'
    )
    $ts = (Get-Date).ToString('s')
    Write-Host "[$ts][$Level] $Message"
}

function Connect-M365CIS {
    [CmdletBinding()]
    param(
        [switch]$SkipExchange,
        [switch]$SkipGraph,
        [string]$SPOAdminUrl
    )
    
    # Fix PSModulePath for OneDrive-synced modules
    $userModulePath = "$env:USERPROFILE\OneDrive - Rahman Finance and Accounting P.L.LC\Documents\WindowsPowerShell\Modules"
    if ((Test-Path $userModulePath) -and ($env:PSModulePath -notlike "*$userModulePath*")) {
        $env:PSModulePath += ";$userModulePath"
        Write-CISLog "Added OneDrive module path to PSModulePath" "Info"
    }
    
    if (-not $SkipExchange) {
        try {
            Write-CISLog 'Connecting to Exchange Online...'
            Import-Module ExchangeOnlineManagement -ErrorAction Stop
            Connect-ExchangeOnline -ShowBanner:$false -ErrorAction Stop | Out-Null
            Write-CISLog 'Connected to Exchange Online.'
        } catch {
            Write-CISLog "Exchange Online connect failed: $($_.Exception.Message)" 'Warn'
        }
    }
    if (-not $SkipGraph) {
        try {
            Write-CISLog 'Connecting to Microsoft Graph (User.Read.All, Policy.Read.All, Directory.Read.All)...'
            Import-Module Microsoft.Graph.Authentication -ErrorAction Stop
            Import-Module Microsoft.Graph.Identity.DirectoryManagement -ErrorAction Stop
            Import-Module Microsoft.Graph.Identity.SignIns -ErrorAction Stop
            Connect-MgGraph -Scopes 'User.Read.All','Policy.Read.All','Directory.Read.All','Organization.Read.All' -ErrorAction Stop | Out-Null
            Select-MgProfile -Name 'v1.0' | Out-Null
            Write-CISLog 'Connected to Microsoft Graph.'
        } catch {
            Write-CISLog "Graph connect failed: $($_.Exception.Message)" 'Warn'
        }
    }

    # Optional SharePoint Online admin connection (if module is available)
    if ($SPOAdminUrl) {
        try {
            if (Get-Module -ListAvailable Microsoft.Online.SharePoint.PowerShell) {
                Import-Module Microsoft.Online.SharePoint.PowerShell -ErrorAction Stop
                Write-CISLog "Connecting to SharePoint Online Admin: $SPOAdminUrl" 'Info'
                Connect-SPOService -Url $SPOAdminUrl -ErrorAction Stop
                Write-CISLog 'Connected to SharePoint Online Admin.' 'Info'
            } else {
                Write-CISLog 'SPO module not found: Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser' 'Warn'
            }
        } catch {
            Write-CISLog "SharePoint Online connect failed: $($_.Exception.Message)" 'Warn'
        }
    } else {
        # Provide a gentle hint if SPO checks are enabled but no connection was requested
        if (Get-Module -ListAvailable Microsoft.Online.SharePoint.PowerShell) {
            Write-CISLog 'SPO module detected. To include SPO tenant checks, provide -SPOAdminUrl https://<tenant>-admin.sharepoint.com' 'Info'
        }
    }
}

function New-CISResult {
    param(
        [string]$ControlId,
        [string]$Title,
        [string]$Severity,
        [string]$Expected,
        [string]$Actual,
        [ValidateSet('Pass','Fail','Manual','Error')][string]$Status,
        [string]$Evidence,
        [string]$Reference
    )
    [PSCustomObject]@{
        ControlId = $ControlId
        Title     = $Title
        Severity  = $Severity
        Expected  = $Expected
        Actual    = $Actual
        Status    = $Status
        Evidence  = $Evidence
        Reference = $Reference
        Timestamp = (Get-Date).ToString('s')
    }
}

function Test-CIS-EXO-BasicAuthDisabled {
    [CmdletBinding()] param()
    $id   = 'CIS-EXO-1'
    $name = 'Ensure modern auth is enabled and basic auth blocked (EXO)'
    $sev  = 'High'
    $ref  = 'CIS M365 Foundations v3.0 L1; EXO Auth Policies'
    try {
        if (-not (Get-Module ExchangeOnlineManagement)) { throw 'Not connected to EXO' }
        $org = Get-OrganizationConfig
        $oauth = $org.OAuth2ClientProfileEnabled
        # Authentication policies for basic auth
        $policies = Get-AuthenticationPolicy | Select-Object Name, AllowBasicAuthPop, AllowBasicAuthImap, AllowBasicAuthSmtp, AllowBasicAuthMapi, AllowBasicAuthAutodiscover, AllowBasicAuthEws, AllowBasicAuthActiveSync, AllowBasicAuthRpc
        $basicAllowed = $false
        foreach ($p in $policies) {
            if ($p.AllowBasicAuthPop -or $p.AllowBasicAuthImap -or $p.AllowBasicAuthSmtp -or $p.AllowBasicAuthMapi -or $p.AllowBasicAuthAutodiscover -or $p.AllowBasicAuthEws -or $p.AllowBasicAuthActiveSync -or $p.AllowBasicAuthRpc) {
                $basicAllowed = $true; break
            }
        }
        $expected = 'OAuth2 enabled; All Basic Auth protocols disabled via Authentication Policies'
        $actual = "OAuth2ClientProfileEnabled=$oauth; BasicAllowed=$basicAllowed"
        $status = if ($oauth -and (-not $basicAllowed)) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($policies | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'OAuth2 on; basic off' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-EXO-ExternalForwardingDisabled {
    [CmdletBinding()] param()
    $id='CIS-EXO-2'; $name='Disable external auto-forwarding (TransportConfig)'; $sev='High'; $ref='CIS M365 Foundations v3.0 L1; EXO TransportConfig'
    try {
        if (-not (Get-Module ExchangeOnlineManagement)) { throw 'Not connected to EXO' }
        $tc = Get-TransportConfig
        $expected = 'ExternalClientForwardingDisabled=True'
        $actual = "ExternalClientForwardingDisabled=$($tc.ExternalClientForwardingDisabled)"
        $status = if ($tc.ExternalClientForwardingDisabled) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($tc | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'External forwarding disabled' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-EXO-MailboxAuditingEnabled {
    [CmdletBinding()] param()
    $id='CIS-EXO-3'; $name='Ensure mailbox auditing is enabled'; $sev='Medium'; $ref='CIS M365 Foundations v3.0 L1; EXO Auditing'
    try {
        if (-not (Get-Module ExchangeOnlineManagement)) { throw 'Not connected to EXO' }
        $org = Get-OrganizationConfig
        $auditDisabled = $org.AuditDisabled
        $expected = 'Organization AuditDisabled=False'
        $actual = "AuditDisabled=$auditDisabled"
        $status = if (-not $auditDisabled) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($org | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Mailbox auditing enabled' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-SPO-ExternalSharingPolicy {
    [CmdletBinding()] param()
    $id='CIS-SPO-1'; $name='Restrict SharePoint external sharing (Tenant)'; $sev='High'; $ref='CIS M365 Foundations v3.0 L1; SPO Sharing'
    try {
        if (-not (Get-Module Microsoft.Online.SharePoint.PowerShell -ListAvailable)) {
            throw 'Microsoft.Online.SharePoint.PowerShell module not found. Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser'
        }
        # Requires prior Connect-SPOService -Url https://<tenant>-admin.sharepoint.com
        $tenant = Get-SPOTenant
        $expected = 'SharingCapability: ExternalUserSharingOnly or more restrictive'
        $actual = "SharingCapability=$($tenant.SharingCapability)"
        $status = if ($tenant.SharingCapability -in ('Disabled','ExternalUserSharingOnly')) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($tenant | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Restrictive external sharing' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-AAD-GlobalAdminCount {
    [CmdletBinding()] param()
    $id='CIS-AAD-1'; $name='Limit Global Administrator role assignments'; $sev='High'; $ref='CIS M365 Foundations v3.0 L1; AAD Roles'
    try {
        $ctx = $null
        try { $ctx = Get-MgContext } catch { $ctx = $null }
        if (-not $ctx) { throw 'Not connected to Graph' }
        $ga = Get-MgRoleManagementDirectoryRoleDefinition -Filter "displayName eq 'Global Administrator'" | Select-Object -First 1
        if (-not $ga) { throw 'Global Administrator role definition not found' }
        $assignments = Get-MgRoleManagementDirectoryRoleAssignment -Filter "roleDefinitionId eq '$($ga.Id)'"
        $count = ($assignments | Measure-Object).Count
        $expected = 'Global Admin assignments minimal (<= 2-4)'
        $actual = "GlobalAdminCount=$count"
        $status = if ($count -le 4) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($assignments | Select-Object principalId,roleDefinitionId | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Minimal GA assignments' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-Defender-SafeLinks {
    [CmdletBinding()] param()
    $id='CIS-DEF-1'; $name='Ensure Safe Links policy is enabled'; $sev='High'; $ref='CIS M365 Foundations v3.0 L1; Defender for Office'
    try {
        if (-not (Get-Module ExchangeOnlineManagement)) { throw 'Not connected to EXO' }
        $policies = Get-SafeLinksPolicy
        if (-not $policies) { throw 'No Safe Links policies found' }
        $enabled = ($policies | Where-Object { $_.Enabled -eq $true } | Measure-Object).Count
        $expected = 'At least one Safe Links policy enabled'
        $actual = "EnabledPolicies=$enabled"
        $status = if ($enabled -gt 0) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($policies | Select-Object Name,Enabled | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Safe Links enabled' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-Defender-SafeAttachments {
    [CmdletBinding()] param()
    $id='CIS-DEF-2'; $name='Ensure Safe Attachments policy is enabled'; $sev='High'; $ref='CIS M365 Foundations v3.0 L1; Defender for Office'
    try {
        if (-not (Get-Module ExchangeOnlineManagement)) { throw 'Not connected to EXO' }
        $policies = Get-SafeAttachmentPolicy
        if (-not $policies) { throw 'No Safe Attachments policies found' }
        $enabled = ($policies | Where-Object { $_.Enable -eq $true } | Measure-Object).Count
        $expected = 'At least one Safe Attachments policy enabled'
        $actual = "EnabledPolicies=$enabled"
        $status = if ($enabled -gt 0) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($policies | Select-Object Name,Enable | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Safe Attachments enabled' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-CA-MFAEnabled {
    [CmdletBinding()] param()
    $id='CIS-CA-1'; $name='Ensure Conditional Access MFA policy exists for all users'; $sev='High'; $ref='CIS M365 Foundations v3.0 L1; Conditional Access'
    try {
        $ctx = $null
        try { $ctx = Get-MgContext } catch { $ctx = $null }
        if (-not $ctx) { throw 'Not connected to Graph' }
        $policies = Get-MgIdentityConditionalAccessPolicy -All
        $mfaPolicies = $policies | Where-Object {
            $_.GrantControls.BuiltInControls -contains 'mfa' -and $_.State -eq 'enabled'
        }
        $count = ($mfaPolicies | Measure-Object).Count
        $expected = 'At least one enabled CA policy requiring MFA for all users'
        $actual = "MFAPolicies=$count"
        $status = if ($count -gt 0) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($mfaPolicies | Select-Object DisplayName,State | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'MFA policy enabled' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-EXO-LegacyProtocolsPerMailbox {
    [CmdletBinding()] param()
    $id='CIS-EXO-4'; $name='Ensure legacy protocols disabled per mailbox (sample check)'; $sev='Medium'; $ref='CIS M365 Foundations v3.0 L1; EXO Mailbox Protocols'
    try {
        if (-not (Get-Module ExchangeOnlineManagement)) { throw 'Not connected to EXO' }
        # Sample first 100 mailboxes to avoid long run times; expand as needed
        $mailboxes = Get-CasMailbox -ResultSize 100 | Where-Object {
            $_.PopEnabled -or $_.ImapEnabled -or $_.MAPIEnabled
        }
        $count = ($mailboxes | Measure-Object).Count
        $expected = 'Legacy protocols (POP/IMAP/MAPI) disabled on all mailboxes'
        $actual = "MailboxesWithLegacyProtocols=$count (sample of 100)"
        $status = if ($count -eq 0) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($mailboxes | Select-Object DisplayName,PopEnabled,ImapEnabled,MAPIEnabled | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Legacy protocols disabled' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Invoke-M365CISAudit {
    [CmdletBinding()]
    param(
        [string]$OutputJson,
        [string]$OutputCsv
    )
    $results = @()
    $results += Test-CIS-EXO-BasicAuthDisabled
    $results += Test-CIS-EXO-ExternalForwardingDisabled
    $results += Test-CIS-EXO-MailboxAuditingEnabled
    $results += Test-CIS-EXO-LegacyProtocolsPerMailbox
    $results += Test-CIS-SPO-ExternalSharingPolicy
    $results += Test-CIS-AAD-GlobalAdminCount
    $results += Test-CIS-Defender-SafeLinks
    $results += Test-CIS-Defender-SafeAttachments
    $results += Test-CIS-CA-MFAEnabled

    if ($OutputJson) { $results | ConvertTo-Json -Depth 5 | Out-File -Encoding utf8 $OutputJson }
    if ($OutputCsv)  { $results | Export-Csv -Path $OutputCsv -NoTypeInformation -Encoding utf8 }
    return $results
}

Export-ModuleMember -Function *
