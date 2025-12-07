# Example Workflows for Enhanced M365 Security Action

## Example 1: Basic Audit with Security Tab Integration

```yaml
name: M365 Security Audit - Basic

on:
  schedule:
    - cron: '0 2 1 * *'  # Monthly at 2 AM
  workflow_dispatch:

jobs:
  audit:
    name: M365 Compliance Audit
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write  # Required for SARIF upload
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Security Audit
        id: audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
          upload-to-security-tab: true
          
      - name: Check Risk Score
        run: |
          RISK=${{ steps.audit.outputs.risk-score }}
          echo "Risk Score: $RISK/100"
          
          if (( $(echo "$RISK > 50" | bc -l) )); then
            echo "::error::Risk score exceeds threshold!"
            exit 1
          fi
```

## Example 2: Automated Remediation with Approval

```yaml
name: M365 Audit with Auto-Remediation

on:
  workflow_dispatch:
    inputs:
      approve-remediation:
        description: 'Auto-approve remediations?'
        required: true
        type: boolean
        default: false

jobs:
  audit-and-remediate:
    name: Audit & Remediate
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Audit with Remediation
        id: audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
          enable-auto-remediation: true
          auto-approve-remediation: ${{ inputs.approve-remediation }}
          remediation-controls: '1.1.1,1.1.3,2.1.1'  # Only fix specific controls
          
      - name: Report Remediation Results
        run: |
          echo "Remediated: ${{ steps.audit.outputs.remediated-controls }} controls"
          echo "Trend: ${{ steps.audit.outputs.compliance-trend }}"
          
      - name: Create Issue if Declined
        if: steps.audit.outputs.trend-direction == 'declining'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🔴 M365 Security Posture Declining',
              body: `## Security Alert
              
              Compliance trend: **${{ steps.audit.outputs.compliance-trend }}**
              
              - New Failures: ${{ steps.audit.outputs.new-failures }}
              - Fixed Issues: ${{ steps.audit.outputs.fixed-issues }}
              - Current Risk Score: ${{ steps.audit.outputs.risk-score }}/100
              
              [View Full Report](${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId})`,
              labels: ['security', 'compliance', 'priority-high']
            })
```

## Example 3: Multi-Tenant Batch Audit

```yaml
name: Multi-Tenant Security Audit

on:
  workflow_dispatch:

jobs:
  audit-tenants:
    name: Audit ${{ matrix.tenant.name }}
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
      
    strategy:
      fail-fast: false
      matrix:
        tenant:
          - name: "Client-Alpha"
            id: "tenant-id-1"
            spo: "https://clientalpha-admin.sharepoint.com"
          - name: "Client-Beta"
            id: "tenant-id-2"
            spo: "https://clientbeta-admin.sharepoint.com"
          - name: "Client-Gamma"
            id: "tenant-id-3"
            spo: "https://clientgamma-admin.sharepoint.com"
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Audit ${{ matrix.tenant.name }}
        id: audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ matrix.tenant.id }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
          spo-admin-url: ${{ matrix.tenant.spo }}
          output-path: output/reports/${{ matrix.tenant.name }}
          
      - name: Tenant Summary
        run: |
          echo "### ${{ matrix.tenant.name }} Results" >> $GITHUB_STEP_SUMMARY
          echo "- Compliance: ${{ steps.audit.outputs.compliance-score }}%" >> $GITHUB_STEP_SUMMARY
          echo "- Risk Score: ${{ steps.audit.outputs.risk-score }}/100" >> $GITHUB_STEP_SUMMARY
          echo "- Trend: ${{ steps.audit.outputs.compliance-trend }}" >> $GITHUB_STEP_SUMMARY
          
  aggregate-results:
    name: Aggregate Multi-Tenant Results
    needs: audit-tenants
    runs-on: ubuntu-latest
    
    steps:
      - name: Download All Reports
        uses: actions/download-artifact@v4
        with:
          pattern: m365-audit-reports-*
          path: all-reports/
          
      - name: Generate Summary Dashboard
        run: |
          # Combine all tenant reports into single dashboard
          echo "## Multi-Tenant Security Summary" > summary.md
          # Process JSONs and generate consolidated metrics
```

## Example 4: Compliance Gate for Pull Requests

```yaml
name: PR Security Compliance Check

on:
  pull_request:
    branches: [Primary, main]
    paths:
      - 'infrastructure/**'
      - '.github/workflows/**'

jobs:
  security-gate:
    name: Security Compliance Gate
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
      pull-requests: write
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Compliance Audit
        id: audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
          compare-with-baseline: true
          
      - name: Enforce Compliance Threshold
        run: |
          SCORE=${{ steps.audit.outputs.compliance-score }}
          TREND=${{ steps.audit.outputs.trend-direction }}
          
          if (( $(echo "$SCORE < 80" | bc -l) )); then
            echo "::error::Compliance score below 80% threshold"
            exit 1
          fi
          
          if [[ "$TREND" == "declining" ]]; then
            echo "::warning::Security posture is declining"
          fi
          
      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            const score = '${{ steps.audit.outputs.compliance-score }}';
            const trend = '${{ steps.audit.outputs.compliance-trend }}';
            const risk = '${{ steps.audit.outputs.risk-score }}';
            
            const body = `## 🛡️ M365 Security Audit Results
            
            | Metric | Value |
            |--------|-------|
            | Compliance Score | ${score}% |
            | Trend | ${trend} |
            | Risk Score | ${risk}/100 |
            
            ### Findings
            - 🔴 Critical: ${{ steps.audit.outputs.critical-findings }}
            - 🟠 High: ${{ steps.audit.outputs.high-findings }}
            - 🟡 Medium: ${{ steps.audit.outputs.medium-findings }}
            - �� Low: ${{ steps.audit.outputs.low-findings }}
            
            ${parseFloat(score) >= 80 ? '✅ **PASSED** - Compliance threshold met' : '❌ **FAILED** - Compliance below threshold'}`;
            
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body
            });
```

## Example 5: Teams Notification on Critical Findings

```yaml
name: M365 Audit with Teams Alerts

on:
  schedule:
    - cron: '0 8 * * 1'  # Every Monday at 8 AM

jobs:
  audit-and-alert:
    name: Audit with Teams Notification
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Security Audit
        id: audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
          security-severity-threshold: high  # Only high/critical in Security tab
          
      - name: Send Teams Notification
        if: steps.audit.outputs.critical-findings > 0 || steps.audit.outputs.high-findings > 0
        uses: aliencube/microsoft-teams-actions@v0.8.0
        with:
          webhook_uri: ${{ secrets.TEAMS_WEBHOOK }}
          title: '🚨 M365 Security Alert'
          summary: 'Critical or High severity findings detected'
          text: |
            **Compliance Score:** ${{ steps.audit.outputs.compliance-score }}%
            **Risk Score:** ${{ steps.audit.outputs.risk-score }}/100
            
            **Findings:**
            - 🔴 Critical: ${{ steps.audit.outputs.critical-findings }}
            - 🟠 High: ${{ steps.audit.outputs.high-findings }}
            
            **Trend:** ${{ steps.audit.outputs.compliance-trend }}
            
            [View Full Report](${env.GITHUB_SERVER_URL}/${env.GITHUB_REPOSITORY}/actions/runs/${env.GITHUB_RUN_ID})
          theme_color: 'FF0000'
```

## Example 6: Continuous Compliance Monitoring

```yaml
name: Continuous Compliance Monitoring

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  monitor:
    name: Compliance Monitoring
    runs-on: ubuntu-latest
    permissions:
      contents: write
      security-events: write
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Audit
        id: audit
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
          compare-with-baseline: true
          
      - name: Update Compliance Badge
        run: |
          SCORE=${{ steps.audit.outputs.compliance-score }}
          COLOR=$(python -c "
          score = float('$SCORE')
          if score >= 90: print('brightgreen')
          elif score >= 80: print('green')
          elif score >= 70: print('yellow')
          elif score >= 60: print('orange')
          else: print('red')
          ")
          
          # Generate badge
          curl "https://img.shields.io/badge/compliance-${SCORE}%25-${COLOR}" > compliance-badge.svg
          
      - name: Commit Badge
        if: github.ref == 'refs/heads/Primary'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add compliance-badge.svg
          git commit -m "chore: update compliance badge [skip ci]" || echo "No changes"
          git push
          
      - name: Create Alert if Threshold Breached
        if: steps.audit.outputs.compliance-score < 75
        run: |
          echo "::error::Compliance dropped below 75%!"
          # Trigger incident response workflow
          gh workflow run incident-response.yml \
            -f severity=high \
            -f type=compliance-breach \
            -f score=${{ steps.audit.outputs.compliance-score }}
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Required Secrets

For all workflows, configure these secrets in your repository:

```yaml
Settings → Secrets and variables → Actions → New repository secret:

M365_TENANT_ID: "your-tenant-id-guid"
M365_CLIENT_ID: "your-service-principal-client-id"
M365_CLIENT_SECRET: "your-service-principal-secret"
SPO_ADMIN_URL: "https://yourtenant-admin.sharepoint.com"
TEAMS_WEBHOOK: "https://outlook.office.com/webhook/..." (optional)
```

## Service Principal Setup

```powershell
# Create Service Principal with required permissions
az ad sp create-for-rbac --name "M365-Security-Audit" \
    --role "Security Reader" \
    --scopes "/subscriptions/{subscription-id}"

# Grant API permissions (requires admin consent):
# - Microsoft Graph:
#   - User.Read.All
#   - Policy.Read.All
#   - Directory.Read.All
#   - Organization.Read.All
# - Exchange:
#   - Exchange.ManageAsApp
# - SharePoint:
#   - Sites.FullControl.All (if analyzing SharePoint)
```
