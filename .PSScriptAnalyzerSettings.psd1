# PSScriptAnalyzer settings for M365 Security Toolkit
# Write-Host is acceptable in user-facing scripts for console output
# ShouldProcess is not needed for read-only functions like New-CISResult

@{
    Severity = @('Error', 'Warning')
    
    # Exclude rules that are acceptable for this project
    ExcludeRules = @(
        'PSAvoidUsingWriteHost',  # Write-Host is used intentionally for user-facing output
        'PSUseShouldProcessForStateChangingFunctions',  # New-CISResult doesn't change system state
        'PSUseBOMForUnicodeEncodedFile'  # UTF-8 without BOM is preferred
    )
    
    # Include specific rules
    IncludeRules = @(
        'PSUseApprovedVerbs',
        'PSAvoidUsingCmdletAliases',
        'PSAvoidUsingPlainTextForPassword',
        'PSAvoidUsingComputerNameHardcoded',
        'PSAvoidUsingEmptyCatchBlock',
        'PSAvoidUsingInvokeExpression',
        'PSAvoidUsingPositionalParameters',
        'PSUseDeclaredVarsMoreThanAssignments'
    )
}
