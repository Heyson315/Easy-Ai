# Pester Unit Tests for M365CIS PowerShell Module
# Run with: Invoke-Pester -Path tests/powershell/

BeforeAll {
    # Define module path once for all tests
    $script:ModulePath = Join-Path $PSScriptRoot "../../scripts/powershell/modules/M365CIS.psm1"

    # Import the M365CIS module if it exists
    if (Test-Path $script:ModulePath) {
        Import-Module $script:ModulePath -Force
    }
}

Describe "M365CIS Module Tests" {
    Context "Module Import" {
        It "Should import the M365CIS module without errors" {
            { Import-Module $script:ModulePath -Force } | Should -Not -Throw
        }

        It "Should export expected functions" {
            Import-Module $script:ModulePath -Force
            $commands = Get-Command -Module M365CIS
            $commands | Should -Not -BeNullOrEmpty
        }
    }

    Context "Module File Structure" {
        It "Should have the module file present" {
            Test-Path $script:ModulePath | Should -Be $true
        }

        It "Should have valid PowerShell syntax" {
            $errors = $null
            $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $script:ModulePath -Raw), [ref]$errors)
            $errors.Count | Should -Be 0
        }
    }

    Context "New-CISResult Function" {
        It "Should create a CIS result object when function exists" {
            Import-Module $script:ModulePath -Force
            $command = Get-Command -Name "New-CISResult" -ErrorAction SilentlyContinue
            if ($command) {
                $result = New-CISResult -ControlId "TEST-001" -Title "Test Control" -Severity "Medium" -Expected "Expected Value" -Actual "Actual Value" -Status "Pass"
                $result | Should -Not -BeNullOrEmpty
                $result.ControlId | Should -Be "TEST-001"
                $result.Status | Should -Be "Pass"
            } else {
                Set-ItResult -Skipped -Because "New-CISResult function not found in module"
            }
        }
    }
}

Describe "PowerShell Script Syntax Validation" {
    $scriptPath = Join-Path $PSScriptRoot "../../scripts/powershell"
    $scripts = Get-ChildItem -Path $scriptPath -Filter "*.ps1" -Recurse -ErrorAction SilentlyContinue

    foreach ($script in $scripts) {
        Context "Script: $($script.Name)" {
            It "Should have valid PowerShell syntax" {
                $errors = $null
                $content = Get-Content $script.FullName -Raw
                $null = [System.Management.Automation.PSParser]::Tokenize($content, [ref]$errors)
                $errors.Count | Should -Be 0
            }
        }
    }
}
