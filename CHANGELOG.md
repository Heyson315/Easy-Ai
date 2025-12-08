# Changelog

All notable changes to the Share Report M365 Security Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive code review documentation (CODE_REVIEW.md)
- Python dependency management files (requirements.txt, requirements-dev.txt)
- Code quality configuration files (.pylintrc, pyproject.toml)
- Contributing guidelines (CONTRIBUTING.md)
- This changelog file

### Changed
- Improved error handling in `m365_cis_report.py` with specific exception types
- Enhanced exception handling in `generate_security_dashboard.py` for better error diagnostics
- Updated `m365_cis_report.py` to include return type hints

### Fixed
- Added file existence validation in `m365_cis_report.py`
- Added JSON parsing error handling in `m365_cis_report.py`

## [1.0.0] - 2025-10-25

### Added
- Enhanced Security Controls (15 total controls, expanded from 9)
  - CIS-PURVIEW-1: DLP policies monitoring
  - CIS-PURVIEW-2: Audit log retention checking
  - CIS-PURVIEW-3: Sensitivity labels enforcement
  - CIS-AAD-2: Azure AD Identity Protection policies
  - CIS-AAD-3: Guest user access restrictions
  - CIS-INTUNE-1: Intune device compliance policies
- Safe Remediation Workflow (`PostRemediateM365CIS.ps1`)
  - `-WhatIf` parameter for preview mode
  - Color-coded output
  - Summary reporting
  - `-Force` parameter for automation
- Before/After Comparison Tool (`Compare-M365CISResults.ps1`)
  - Status change tracking
  - Improvement percentage calculation
  - Export to CSV and HTML
- Interactive HTML Dashboard (`generate_security_dashboard.py`)
  - Summary cards by severity
  - Trend charts for historical data
  - Filterable control status table
  - Responsive design with no external dependencies
- Automated Audit Scheduling
  - `Setup-ScheduledAudit.ps1` for task creation
  - `Remove-ScheduledAudit.ps1` for cleanup
  - Support for Daily/Weekly/Monthly schedules
- Purview Compliance Integration
  - Enhanced `M365CIS.psm1` module
  - Auto-detection of Purview cmdlets
  - Graceful fallback for unavailable features
- Comprehensive Documentation
  - `docs/SECURITY_M365_CIS.md` with all controls
  - `scripts/README.md` quick reference
  - Configuration file templates
- Configuration Management
  - `config/audit_config.json` template
  - Tenant and notification configuration
  - Controls configuration options

### Changed
- Enhanced `M365CIS.psm1` module with 6 new security functions
- Updated `Invoke-M365CISAudit.ps1` with `-SkipPurview` parameter
- Complete rewrite of `PostRemediateM365CIS.ps1` with safety features
- Expanded `cis_m365_foundations_v3_level1.json` with new control definitions

### Documentation
- `IMPLEMENTATION_SUMMARY.md` documenting all features
- Quick start guides and examples
- Troubleshooting section
- Permissions and prerequisites documentation

## [0.1.0] - Initial Release

### Added
- Basic M365 CIS security auditing functionality (9 controls)
- CSV cleaning utilities
- SharePoint permissions analysis
- Excel report generation
- Basic project management workbook generator

---

## Version History Summary

- **v1.0.0** (2025-10-25): Major release with 15 security controls, automation, and comprehensive tooling
- **Unreleased**: Code quality improvements, documentation, and error handling enhancements

---

## How to Update This Changelog

When making changes:
1. Add your changes under the `[Unreleased]` section
2. Categorize changes as: Added, Changed, Deprecated, Removed, Fixed, Security
3. Use clear, concise descriptions
4. Include file names or feature names for clarity
5. Link to issues/PRs when applicable

For releases:
1. Change `[Unreleased]` to `[version] - YYYY-MM-DD`
2. Add a new `[Unreleased]` section at the top
3. Update version comparison links at the bottom

---

[Unreleased]: https://github.com/Heyson315/Easy-Ai/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Heyson315/Easy-Ai/releases/tag/v1.0.0
[0.1.0]: https://github.com/Heyson315/Easy-Ai/releases/tag/v0.1.0
