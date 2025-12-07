# Example Usage: M365 Security Audit GitHub Action

This document provides examples of how to use the M365 Security & Compliance Audit action in your GitHub workflows.

## Basic Usage

```yaml
name: Monthly M365 Security Audit

on:
  schedule:
    - cron: '0 2 1 * *'  # Run at 2 AM on the 1st of each month
  workflow_dispatch:  # Allow manual trigger

jobs:
  security-audit:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
      
      - name: Run M365 Security Audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
          spo-admin-url: 'https://contoso-admin.sharepoint.com'
          timestamped: true
          generate-dashboard: true
      
      - name: Check Compliance Score
        run: |
          echo "Compliance Score: ${{ steps.audit.outputs.compliance-score }}%"
          if [ "${{ steps.audit.outputs.compliance-score }}" -lt "80" ]; then
            echo "::warning::Compliance score below 80%"
          fi
```

## Advanced Usage with Notifications

```yaml
name: M365 Compliance with Teams Notification

on:
  schedule:
    - cron: '0 8 * * 1'  # Every Monday at 8 AM
  workflow_dispatch:

jobs:
  audit-and-notify:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Run Security Audit
        id: audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
          spo-admin-url: ${{ secrets.SPO_ADMIN_URL }}
          skip-purview: false
          generate-dashboard: true
      
      - name: Send Teams Notification
        if: always()
        uses: aliencube/microsoft-teams-actions@v0.8.0
        with:
          webhook-uri: ${{ secrets.TEAMS_WEBHOOK_URI }}
          title: 'M365 Security Audit Complete'
          summary: |
            Compliance Score: ${{ steps.audit.outputs.compliance-score }}%
            Passed: ${{ steps.audit.outputs.controls-passed }}
            Failed: ${{ steps.audit.outputs.controls-failed }}
            Manual Review: ${{ steps.audit.outputs.controls-manual }}
          theme-color: ${{ steps.audit.outputs.compliance-score >= 90 && 'success' || steps.audit.outputs.compliance-score >= 70 && 'warning' || 'danger' }}
```

## Pull Request Compliance Check

```yaml
name: PR M365 Compliance Check

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  compliance-gate:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout PR
        uses: actions/checkout@v4
      
      - name: Run M365 Audit
        id: audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
          generate-dashboard: true
      
      - name: Enforce Compliance Threshold
        run: |
          SCORE=${{ steps.audit.outputs.compliance-score }}
          echo "Compliance Score: $SCORE%"
          
          if [ "$SCORE" -lt "85" ]; then
            echo "::error::Compliance score ($SCORE%) below required threshold (85%)"
            exit 1
          fi
          
          echo "✓ Compliance check passed"
      
      - name: Comment PR with Results
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🛡️ M365 Compliance Audit Results
              
              **Compliance Score:** ${{ steps.audit.outputs.compliance-score }}%
              
              | Status | Count |
              |--------|-------|
              | ✅ Passed | ${{ steps.audit.outputs.controls-passed }} |
              | ❌ Failed | ${{ steps.audit.outputs.controls-failed }} |
              | ⚠️ Manual | ${{ steps.audit.outputs.controls-manual }} |
              
              📊 [View Full Dashboard](../actions/runs/${{ github.run_id }})`
            })
```

## Multi-Tenant Audit

```yaml
name: Multi-Tenant Security Audit

on:
  workflow_dispatch:
    inputs:
      tenants:
        description: 'Comma-separated tenant names'
        required: true
        default: 'tenant1,tenant2,tenant3'

jobs:
  audit-tenants:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        tenant: ${{ fromJSON(format('["{0}"]', inputs.tenants).replace(',', '","')) }}
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Audit ${{ matrix.tenant }}
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets[format('{0}_TENANT_ID', matrix.tenant)] }}
          client-id: ${{ secrets[format('{0}_CLIENT_ID', matrix.tenant)] }}
          client-secret: ${{ secrets[format('{0}_CLIENT_SECRET', matrix.tenant)] }}
          output-path: output/reports/${{ matrix.tenant }}
      
      - name: Upload Tenant Reports
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.tenant }}-audit-reports
          path: output/reports/${{ matrix.tenant }}
```

## Required Secrets

Configure these secrets in your repository settings (Settings → Secrets and variables → Actions):

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `M365_TENANT_ID` | Azure AD Tenant ID | `12345678-1234-1234-1234-123456789012` |
| `M365_CLIENT_ID` | Service Principal Client ID | `87654321-4321-4321-4321-210987654321` |
| `M365_CLIENT_SECRET` | Service Principal Secret | `abc123...xyz789` |
| `SPO_ADMIN_URL` | SharePoint Admin Center URL | `https://contoso-admin.sharepoint.com` |

## Service Principal Setup

See [M365 Service Principal Setup Guide](docs/M365_SERVICE_PRINCIPAL_SETUP.md) for detailed instructions on creating and configuring the service principal with required permissions.

## Output Artifacts

The action uploads the following artifacts:

- **JSON Report:** Raw audit data in JSON format
- **Excel Report:** Formatted compliance report with charts
- **HTML Dashboard:** Interactive dashboard with trend analysis

Artifacts are retained for 90 days by default.

## Tips and Best Practices

1. **Use Timestamped Reports:** Enable `timestamped: true` to track audit history
2. **Schedule Regular Audits:** Run monthly or weekly for continuous monitoring
3. **Set Compliance Thresholds:** Fail builds/PRs when compliance drops below acceptable levels
4. **Archive Reports:** Store audit reports in a separate repository for compliance records
5. **Monitor Trends:** Compare multiple audit runs using the comparison script
6. **Secure Secrets:** Use GitHub Environments for production credentials
7. **Test with `-WhatIf`:** Preview remediation changes before applying

## Troubleshooting

### Authentication Errors
- Verify service principal has correct permissions
- Check client secret hasn't expired
- Ensure tenant ID is correct

### Module Installation Failures
- Check internet connectivity
- Verify PowerShell Gallery is accessible
- Try manual module installation first

### Missing Reports
- Check workflow logs for errors
- Verify output path is correct
- Ensure sufficient disk space

## Support

- 📖 [Full Documentation](https://github.com/Heyson315/Easy-Ai/tree/Primary/docs)
- 🐛 [Report Issues](https://github.com/Heyson315/Easy-Ai/issues)
- 💬 [Discussions](https://github.com/Heyson315/Easy-Ai/discussions)
