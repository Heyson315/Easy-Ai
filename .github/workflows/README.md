# GitHub Actions Workflows

This directory contains automated workflows for the M365 Security & SharePoint Analysis Toolkit. These workflows handle continuous integration, dependency management, and release automation.

## 🔄 Workflow Overview

### 1. CI/CD Pipeline (`ci-cd.yml`)
**Triggers:** Push to main/develop branches, pull requests
**Purpose:** Comprehensive quality assurance and testing

**Jobs:**
- **Python Testing Matrix** - Tests across Python 3.9-3.12 on Windows/Ubuntu
- **PowerShell Analysis** - PSScriptAnalyzer linting and testing
- **Security Scanning** - CodeQL analysis, dependency vulnerability checks
- **Integration Tests** - End-to-end workflow validation
- **Release Automation** - Automated releases on version tags

**Key Features:**
- Cross-platform testing (Windows PowerShell + Linux Python)
- Security-first approach with multiple scanners
- Automated artifact generation for releases
- Comprehensive test coverage reporting

### 2. Dependency Updates (`dependency-updates.yml`)
**Triggers:** Weekly schedule (Mondays 9 AM UTC), manual dispatch
**Purpose:** Automated dependency management and security monitoring

**Jobs:**
- **Python Dependencies** - pip-tools for Python package updates
- **Security Auditing** - safety and pip-audit for vulnerability detection
- **Automated PRs** - Creates pull requests for dependency updates

**Key Features:**
- Weekly security scanning
- Automated dependency version bumping
- Integration with GitHub security advisories
- Automated PR creation with change summaries

### 3. Release Management (`release.yml`)
**Triggers:** Version tags (v*), manual workflow dispatch
**Purpose:** Automated release creation and artifact distribution

**Jobs:**
- **Prepare Release** - Changelog generation, version management
- **Build Artifacts** - Standalone executables, PowerShell modules, documentation
- **Create Release** - GitHub release with artifacts and changelog
- **Post-Release** - Version updates, development branch creation
- **Notifications** - Success/failure notifications

**Key Features:**
- Automatic changelog generation from commit messages
- Cross-platform executable building
- PowerShell module packaging
- Development branch management

## 🛠️ Configuration Files

### CodeQL Configuration (`.github/codeql/codeql-config.yml`)
- **Security Analysis** - Static code analysis for security vulnerabilities
- **Custom Queries** - Enhanced security scanning with community queries
- **Path Filters** - Focused scanning on critical code paths

### Markdown Configuration
- **`.markdownlint.json`** - Consistent documentation formatting
- **`.markdown-link-check.json`** - Automated link validation

## 🚀 Usage Guide

### Running CI/CD Pipeline
The pipeline runs automatically on:
- Pushes to `main` or `develop` branches
- Pull requests to `main`
- Manual trigger via GitHub Actions UI

### Creating Releases
1. **Automatic Release:**
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```

2. **Manual Release:**
   - Go to GitHub Actions → Release Management
   - Click "Run workflow"
   - Enter version (e.g., `v1.2.0`)

### Dependency Updates
- Runs automatically every Monday at 9 AM UTC
- Can be triggered manually via GitHub Actions UI
- Creates PRs for security updates and dependency bumps

## 📋 Workflow Requirements

### Secrets Required
The workflows use standard GitHub tokens and don't require additional secrets.

### Repository Settings
- **Actions permissions:** Read and write permissions for Actions
- **Pull request creation:** Allow GitHub Actions to create PRs
- **Security scanning:** Enable CodeQL and dependency review

### Branch Protection
Recommended settings for `main` branch:
- Require status checks (CI/CD pipeline)
- Require up-to-date branches
- Require CodeQL analysis
- Dismiss stale reviews on new commits

## 🔍 Monitoring and Debugging

### Viewing Workflow Results
1. Go to **Actions** tab in GitHub repository
2. Select the specific workflow
3. Click on individual runs to see detailed logs

### Common Issues and Solutions

#### Python Test Failures
- **Issue:** Tests fail on Windows due to file locking
- **Solution:** Ensure proper file cleanup in test teardown
- **Debug:** Check test logs for specific error messages

#### PowerShell Analysis Warnings
- **Issue:** PSScriptAnalyzer reports style violations
- **Solution:** Review PowerShell scripts for best practices
- **Debug:** Run PSScriptAnalyzer locally before pushing

#### Security Scan Alerts
- **Issue:** CodeQL or dependency scanners find vulnerabilities
- **Solution:** Review security alerts and update dependencies
- **Debug:** Check security tab in repository for details

#### Release Failures
- **Issue:** Release workflow fails during artifact creation
- **Solution:** Verify all required files exist and are accessible
- **Debug:** Check build logs and artifact upload steps

### Performance Monitoring
- **Average runtime:** CI/CD pipeline ~15-20 minutes
- **Peak usage:** Release workflow ~25-30 minutes
- **Optimization:** Parallel job execution reduces total time

## 📊 Workflow Metrics

### Success Rates
- **CI/CD Pipeline:** Target >95% success rate
- **Security Scanning:** Zero tolerance for high-severity findings
- **Dependency Updates:** Weekly execution with <24h PR creation

### Coverage Targets
- **Code Coverage:** Maintain >70% test coverage
- **Security Coverage:** 100% of critical paths scanned
- **Documentation:** All workflows documented and maintained

## 🔄 Maintenance

### Regular Tasks
- **Monthly:** Review workflow performance and optimization opportunities
- **Quarterly:** Update GitHub Actions versions and dependencies
- **Annually:** Review and update security scanning configurations

### Workflow Updates
When updating workflows:
1. Test changes in a feature branch
2. Use workflow_dispatch for manual testing
3. Monitor first few runs after changes
4. Document any breaking changes

### Version Management
- **Workflow files:** Use semantic versioning for major changes
- **Action versions:** Pin to specific versions for stability
- **Dependencies:** Regular updates via automated PRs

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [PowerShell Module Guidelines](https://docs.microsoft.com/en-us/powershell/scripting/developer/module/writing-a-powershell-module)
- [Python Packaging Guidelines](https://packaging.python.org/guides/)

## 🆘 Support

For workflow issues:
1. Check existing GitHub Issues
2. Review workflow logs and error messages
3. Test locally before reporting issues
4. Include relevant logs and error messages in issue reports