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
        [string]$SPOAdminUrl,
        [switch]$SkipPurview
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

    # Optional Purview Compliance connection (if module is available)
    if (-not $SkipPurview) {
        try {
            Connect-PurviewCompliance
        } catch {
            Write-CISLog "Purview Compliance connect failed: $($_.Exception.Message)" 'Warn'
        }
    }
}

function Connect-PurviewCompliance {
    [CmdletBinding()]
    param()
    
    try {
        # Check if ExchangeOnlineManagement module is available (provides Security & Compliance cmdlets)
        if (Get-Module -ListAvailable ExchangeOnlineManagement) {
            Write-CISLog 'Connecting to Purview Compliance (Security & Compliance PowerShell)...' 'Info'
            Import-Module ExchangeOnlineManagement -ErrorAction Stop
            # Connect-IPPSSession is for Security & Compliance Center
            Connect-IPPSSession -ErrorAction Stop | Out-Null
            Write-CISLog 'Connected to Purview Compliance.' 'Info'
        } else {
            Write-CISLog 'ExchangeOnlineManagement module not found. Install-Module ExchangeOnlineManagement -Scope CurrentUser' 'Warn'
        }
    } catch {
        Write-CISLog "Purview Compliance connection not available or failed: $($_.Exception.Message)" 'Warn'
        Write-CISLog 'Purview-related checks will fall back to Manual status.' 'Info'
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

function Test-CIS-Defender-SafeLink {
    [CmdletBinding()] param()
    $id='CIS-DEF-1'; $name='Ensure Safe Links policy is enabled'; $sev='High'; $ref='CIS M365 Foundations v3.0 L1; Defender for Office'
    try {
        if (-not (Get-Module ExchangeOnlineManagement)) { throw 'Not connected to EXO' }

        # Prefer checking Safe Links RULES to reduce false negatives from preset policies that lack a simple Enabled flag
        $rules = @()
        try { $rules = Get-SafeLinksRule -ErrorAction Stop } catch { $rules = @() }

        $enabledRules = @()
        if ($rules) {
            # Some environments expose State (Enabled/Disabled); others may expose Enabled:$true/$false
            $enabledRules = $rules | Where-Object { $_.State -eq 'Enabled' -or $_.Enabled -eq $true }
        }

        $enabledRuleCount = ($enabledRules | Measure-Object).Count

        # Fallback to policy check only if no rules are returned (older tenants or permission scope)
        $polEnabledCount = 0
        $polEvidence = $null
        if ($enabledRuleCount -eq 0) {
            $policies = @()
            try { $policies = Get-SafeLinksPolicy -ErrorAction Stop } catch { $policies = @() }
            if (-not $policies) { throw 'No Safe Links rules or policies found' }
            $polEnabledCount = ($policies | Where-Object { $_.Enabled -eq $true } | Measure-Object).Count
            $polEvidence = ($policies | Select-Object Name,Enabled)
        }

        $expected = 'At least one Safe Links rule or policy is enabled'
        $actual = "EnabledRules=$enabledRuleCount; EnabledPolicies=$polEnabledCount"
        $status = if ( ($enabledRuleCount -gt 0) -or ($polEnabledCount -gt 0) ) { 'Pass' } else { 'Fail' }

        $evidence = @()
        if ($rules) { $evidence += ($rules | Select-Object Name,State,Enabled) }
        if ($polEvidence) { $evidence += $polEvidence }

        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($evidence | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Safe Links enabled' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-Defender-SafeAttachment {
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

function Test-CIS-Purview-DLPPoliciesEnabled {
    [CmdletBinding()] param()
    $id='CIS-PURVIEW-1'; $name='Ensure DLP policies are enabled for data protection'; $sev='High'; $ref='CIS M365 Foundations v3.0 L1; Purview DLP'
    try {
        # Requires ExchangeOnlineManagement (Connect-IPPSSession)
        $policies = @()
        try { $policies = Get-DlpCompliancePolicy -ErrorAction Stop } catch { throw 'Not connected to Purview or DLP cmdlets unavailable' }
        if (-not $policies) { throw 'No DLP policies found' }
        $enabled = ($policies | Where-Object { $_.Enabled -eq $true } | Measure-Object).Count
        $expected = 'At least one DLP policy enabled'
        $actual = "EnabledPolicies=$enabled"
        $status = if ($enabled -gt 0) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($policies | Select-Object Name,Enabled | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'DLP policies enabled' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-AAD-RiskPoliciesEnabled {
    [CmdletBinding()] param()
    $id='CIS-AAD-2'; $name='Ensure Azure AD Identity Protection risk policies are configured'; $sev='High'; $ref='CIS M365 Foundations v3.0 L1; AAD Identity Protection'
    try {
        $ctx = $null
        try { $ctx = Get-MgContext } catch { $ctx = $null }
        if (-not $ctx) { throw 'Not connected to Graph' }
        # Check for Conditional Access policies that use risk-based conditions
        $policies = Get-MgIdentityConditionalAccessPolicy -All
        $riskPolicies = $policies | Where-Object {
            ($_.Conditions.UserRiskLevels -or $_.Conditions.SignInRiskLevels) -and $_.State -eq 'enabled'
        }
        $count = ($riskPolicies | Measure-Object).Count
        $expected = 'At least one risk-based CA policy enabled (user or sign-in risk)'
        $actual = "RiskBasedPolicies=$count"
        $status = if ($count -gt 0) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($riskPolicies | Select-Object DisplayName,State | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Risk policies enabled' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-Intune-CompliancePolicy {
    [CmdletBinding()] param()
    $id='CIS-INTUNE-1'; $name='Ensure Intune device compliance policies exist and are enforced'; $sev='Medium'; $ref='CIS M365 Foundations v3.0 L1; Intune MDM'
    try {
        $ctx = $null
        try { $ctx = Get-MgContext } catch { $ctx = $null }
        if (-not $ctx) { throw 'Not connected to Graph' }
        # Check for device compliance policies via Graph
        $policies = @()
        try {
            Import-Module Microsoft.Graph.DeviceManagement -ErrorAction Stop
            $policies = Get-MgDeviceManagementDeviceCompliancePolicy -ErrorAction Stop
        } catch {
            throw 'Intune cmdlets unavailable or insufficient permissions'
        }
        $count = ($policies | Measure-Object).Count
        $expected = 'At least one device compliance policy configured'
        $actual = "CompliancePolicies=$count"
        $status = if ($count -gt 0) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($policies | Select-Object DisplayName,Id | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Compliance policies configured' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-AAD-GuestUserRestriction {
    [CmdletBinding()] param()
    $id='CIS-AAD-3'; $name='Ensure guest user access restrictions are configured'; $sev='Medium'; $ref='CIS M365 Foundations v3.0 L1; AAD Guest Access'
    try {
        $ctx = $null
        try { $ctx = Get-MgContext } catch { $ctx = $null }
        if (-not $ctx) { throw 'Not connected to Graph' }
        # Check Authorization Policy for guest user settings
        $authPolicy = Get-MgPolicyAuthorizationPolicy
        $guestUserRole = $authPolicy.GuestUserRoleId
        # Recommended: guestUserRole should be restrictive (e.g., not Member role)
        # GuestUserRoleId: 10dae51f-b6af-4016-8d66-8c2a99b929b3 is Guest role (restrictive)
        # GuestUserRoleId: a0b1b346-4d3e-4e8b-98f8-753987be4970 is Member role (less restrictive)
        $expected = 'Guest user role is restrictive (not Member role)'
        $actual = "GuestUserRoleId=$guestUserRole"
        $isRestrictive = $guestUserRole -eq '10dae51f-b6af-4016-8d66-8c2a99b929b3'
        $status = if ($isRestrictive) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($authPolicy | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Guest access restrictive' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-Purview-AuditLogRetention {
    [CmdletBinding()] param()
    $id='CIS-PURVIEW-2'; $name='Ensure audit logs are retained for compliance (90+ days recommended)'; $sev='Medium'; $ref='CIS M365 Foundations v3.0 L1; Purview Auditing'
    try {
        # Check unified audit log retention policy
        $policies = @()
        try { $policies = Get-UnifiedAuditLogRetentionPolicy -ErrorAction Stop } catch { throw 'Not connected to Purview or audit cmdlets unavailable' }
        if (-not $policies) { throw 'No audit log retention policies found' }
        # Check for policies with RetentionDuration >= 90 days
        $compliantPolicies = $policies | Where-Object { $_.RetentionDuration -ge 90 }
        $count = ($compliantPolicies | Measure-Object).Count
        $expected = 'At least one audit log retention policy with 90+ days'
        $actual = "CompliantPolicies=$count"
        $status = if ($count -gt 0) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($policies | Select-Object Name,RetentionDuration | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Audit log retention 90+ days' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Test-CIS-Purview-SensitivityLabelsPublished {
    [CmdletBinding()] param()
    $id='CIS-PURVIEW-3'; $name='Ensure sensitivity labels are published and enforced'; $sev='Medium'; $ref='CIS M365 Foundations v3.0 L1; Purview Information Protection'
    try {
        # Check for published sensitivity label policies
        $policies = @()
        try { $policies = Get-LabelPolicy -ErrorAction Stop } catch { throw 'Not connected to Purview or label cmdlets unavailable' }
        if (-not $policies) { throw 'No sensitivity label policies found' }
        $enabled = ($policies | Where-Object { $_.Enabled -eq $true } | Measure-Object).Count
        $expected = 'At least one sensitivity label policy published'
        $actual = "PublishedPolicies=$enabled"
        $status = if ($enabled -gt 0) { 'Pass' } else { 'Fail' }
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected $expected -Actual $actual -Status $status -Evidence ($policies | Select-Object Name,Enabled | Out-String) -Reference $ref
    } catch {
        New-CISResult -ControlId $id -Title $name -Severity $sev -Expected 'Sensitivity labels published' -Actual 'Unknown' -Status 'Manual' -Evidence $_.Exception.Message -Reference $ref
    }
}

function Invoke-M365CISAudit {
    [CmdletBinding()]
    param(
        [string]$OutputJson,
        [string]$OutputCsv
    )
    $results = @()
    # Original controls (9)
    $results += Test-CIS-EXO-BasicAuthDisabled
    $results += Test-CIS-EXO-ExternalForwardingDisabled
    $results += Test-CIS-EXO-MailboxAuditingEnabled
    $results += Test-CIS-EXO-LegacyProtocolsPerMailbox
    $results += Test-CIS-SPO-ExternalSharingPolicy
    $results += Test-CIS-AAD-GlobalAdminCount
    $results += Test-CIS-Defender-SafeLink
    $results += Test-CIS-Defender-SafeAttachment
    $results += Test-CIS-CA-MFAEnabled
    
    # New enhanced controls (6)
    $results += Test-CIS-Purview-DLPPoliciesEnabled
    $results += Test-CIS-AAD-RiskPoliciesEnabled
    $results += Test-CIS-Intune-CompliancePolicy
    $results += Test-CIS-AAD-GuestUserRestriction
    $results += Test-CIS-Purview-AuditLogRetention
    $results += Test-CIS-Purview-SensitivityLabelsPublished

    if ($OutputJson) { $results | ConvertTo-Json -Depth 5 | Out-File -Encoding utf8 $OutputJson }
    if ($OutputCsv)  { $results | Export-Csv -Path $OutputCsv -NoTypeInformation -Encoding utf8 }
    return $results
}

Export-ModuleMember -Function *
