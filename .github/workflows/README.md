# GitHub Actions Setup Guide for M365 Security Toolkit

This guide explains how to configure GitHub Actions for your M365 Security & SharePoint Analysis Toolkit.

## 🚀 Workflows Included

### 1. **M365 Security Toolkit CI/CD** (`m365-security-ci.yml`)
**Triggers:** Push to `evidence/2025-10-25`, feature branches, PRs  
**Purpose:** Continuous integration and quality checks

**Features:**
- ✅ Python code quality checks (flake8, black)
- ✅ PowerShell script analysis (PSScriptAnalyzer)
- ✅ Security vulnerability scanning (safety, bandit)
- ✅ Performance benchmarking
- ✅ Documentation linting
- ✅ Integration testing pipeline

### 2. **Automated M365 Security Audit** (`m365-automated-audit.yml`)
**Triggers:** Monthly schedule, manual dispatch  
**Purpose:** Automated M365 CIS compliance auditing

**Features:**
- 🛡️ Monthly automated M365 CIS audits
- 📊 Excel and HTML report generation
- 🔧 Remediation preview (dry-run)
- 📋 Automatic issue creation with results
- 📁 Artifact retention (90 days)

### 3. **Dependency Updates** (`dependency-updates.yml`)
**Triggers:** Weekly schedule  
**Purpose:** Keep dependencies secure and updated

## ⚙️ Configuration Required

### For Basic CI/CD (Works Immediately)
No additional configuration needed! The CI/CD workflow will run automatically.

### For Automated M365 Audits (Optional)
To enable automated M365 auditing, you need to configure:

#### 1. **Repository Variables** (Settings → Secrets and variables → Actions → Variables)
- `M365_TENANT_ID`: Your Microsoft 365 tenant ID
- `M365_CLIENT_ID`: Service principal application (client) ID

#### 2. **Repository Secrets** (Settings → Secrets and variables → Actions → Secrets)
- `M365_CLIENT_SECRET`: Service principal client secret

#### 3. **Service Principal Setup**
Use the provided script to create a service principal:

```powershell
./deployment/Setup-M365ServicePrincipal.ps1
```

This script will:
- Create an Azure AD application
- Configure required API permissions
- Generate credentials for GitHub Actions

## 🔒 Security Permissions

### Required Microsoft 365 Permissions
The service principal needs these Microsoft Graph permissions:
- `Organization.Read.All`
- `Directory.Read.All`
- `Policy.Read.All`
- `User.Read.All`
- `RoleManagement.Read.All`

### Exchange Online Permissions
- Exchange Administrator or Security Reader role

### SharePoint Online Permissions (if using SPO checks)
- SharePoint Administrator or Security Reader role

## 📊 Workflow Outputs

### CI/CD Artifacts
- **Build Summary**: Overall build status and validation results
- **Security Reports**: Vulnerability scan results (safety, bandit)
- **Coverage Reports**: Python test coverage data

### Audit Artifacts
- **Excel Reports**: Detailed CIS compliance reports
- **HTML Dashboards**: Interactive security dashboards  
- **JSON Data**: Raw audit results for analysis
- **Remediation Plans**: Suggested fixes for failed controls

## 🎯 Customization Options

### Adjusting Audit Frequency
Edit the cron schedule in `m365-automated-audit.yml`:
```yaml
schedule:
  # Monthly on 1st at 6 AM UTC
  - cron: '0 6 1 * *'
  
  # Weekly on Mondays at 9 AM UTC
  # - cron: '0 9 * * 1'
  
  # Daily at 2 AM UTC  
  # - cron: '0 2 * * *'
```

### Audit Scope Selection
Run manual audits with specific scopes:
- **Full**: All M365 services (default)
- **Exchange**: Exchange Online only
- **SharePoint**: SharePoint Online only  
- **Purview**: Microsoft Purview only

### Adding Custom Checks
1. Add new controls to `scripts/powershell/modules/M365CIS.psm1`
2. Update CIS benchmark metadata in `config/benchmarks/`
3. Workflow will automatically include new checks

## 🚨 Troubleshooting

### Common Issues

#### 1. **PowerShell Module Installation Fails**
**Error:** `Install-Module` fails in GitHub Actions  
**Solution:** Check if module is available in PowerShell Gallery and update workflow

#### 2. **M365 Authentication Fails**
**Error:** Service principal can't authenticate  
**Solutions:**
- Verify tenant ID, client ID, and secret are correct
- Check service principal hasn't expired
- Ensure required API permissions are granted and admin-consented

#### 3. **Audit Results Empty**
**Error:** No controls return results  
**Solutions:**
- Check service principal has required permissions
- Verify M365 services are accessible
- Review audit logs in workflow output

#### 4. **Report Generation Fails**
**Error:** Excel/HTML generation fails  
**Solutions:**
- Check Python dependencies are installed
- Verify input JSON structure is valid
- Check disk space and memory limits

### Getting Help

1. **Check workflow logs** in GitHub Actions tab
2. **Review artifact uploads** for detailed error information
3. **Run scripts locally** to debug specific issues
4. **Check service principal permissions** in Azure portal

## 📈 Monitoring & Metrics

### Key Metrics Tracked
- **Compliance Rate**: Percentage of passed CIS controls
- **Security Trends**: Month-over-month improvement
- **Failed Controls**: Critical security gaps requiring attention
- **Manual Reviews**: Controls needing human assessment

### Issue Automation
Workflows automatically create GitHub issues for:
- 🛡️ **Audit Results**: Monthly compliance reports
- ⚠️ **Security Alerts**: High-priority failures
- 📅 **Reminders**: Next audit scheduling
- 🔧 **Action Items**: Remediation tasks

## 🎉 Success Indicators

Your GitHub Actions are working correctly when you see:
- ✅ Green checkmarks on all CI/CD checks
- 📊 Monthly audit issues created automatically
- 📁 Audit artifacts uploaded successfully
- 📈 Compliance trends visible over time

---

**Next Steps:**
1. Commit these workflow files
2. Set up service principal (if doing automated audits)
3. Configure repository secrets/variables
4. Test with a manual workflow run
5. Monitor first automated audit results