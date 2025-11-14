# SharePoint Deployment Guide

## Overview

This guide explains how to deploy the M365 Security Dashboard to SharePoint Online. SharePoint provides a modern page experience perfect for internal security dashboards and compliance reporting.

## Prerequisites

- SharePoint Online site (Team Site or Communication Site)
- Site Owner or Site Member permissions
- Modern SharePoint pages enabled (default for new sites)
- Optional: SharePoint Framework (SPFx) for advanced customizations

## Deployment Options

### Option 1: Embed HTML Web Part (Recommended for Quick Start)

**Best for:** Simple deployments, non-developers, quick testing

1. **Navigate to your SharePoint site**
   - Go to your SharePoint site (e.g., `https://tenant.sharepoint.com/sites/SecurityHub`)
   
2. **Create a new modern page**
   - Click **+ New** → **Page**
   - Choose a page template (Full-width column recommended for dashboards)
   - Name it "Security Dashboard" or similar

3. **Add Embed web part**
   - Click **+** to add a web part
   - Search for "Embed" and select the **Embed** web part
   - Paste the HTML code from `web-templates/sharepoint/examples/security-dashboard.html`
   - Click outside the web part to save

4. **Customize the content**
   - Edit the HTML to replace sample data with your actual audit results
   - Update links to point to your document libraries and reports
   - Adjust colors if needed to match your site theme

5. **Publish the page**
   - Click **Publish** in the top right
   - Set permissions as needed (all site members, specific groups, etc.)

### Option 2: Script Editor Web Part (Classic Sites)

**Best for:** Classic SharePoint sites, full HTML/CSS/JS control

> ⚠️ **Note:** Script Editor web part is only available in classic SharePoint pages

1. **Edit classic page**
   - Navigate to your classic SharePoint page
   - Click **Edit** (gear icon → Edit Page)

2. **Add Script Editor web part**
   - Click **Insert** → **Web Part**
   - Select **Media and Content** → **Script Editor**
   - Click **Add**

3. **Edit snippet**
   - Click **EDIT SNIPPET** in the Script Editor web part
   - Paste your HTML code
   - Click **Insert**

4. **Save and publish**
   - Click **Stop Editing**
   - Test the dashboard functionality

### Option 3: SharePoint Framework (SPFx) Web Part

**Best for:** Advanced customizations, production deployments, enterprise solutions

#### Prerequisites
```bash
# Install Node.js LTS (14.x or 16.x)
# Install Yeoman and SharePoint generator
npm install -g yo @microsoft/generator-sharepoint
```

#### Create SPFx Web Part

1. **Generate web part**
```bash
yo @microsoft/sharepoint
# Choose:
# - Solution name: m365-security-dashboard
# - Baseline: SharePoint Online only
# - File location: Use current folder
# - Tenant admin: Yes
# - Web part name: SecurityDashboard
# - Description: M365 Security Compliance Dashboard
# - Framework: No JavaScript framework
```

2. **Add dashboard code**
```typescript
// src/webparts/securityDashboard/SecurityDashboardWebPart.ts
import { Version } from '@microsoft/sp-core-library';
import { BaseClientSideWebPart } from '@microsoft/sp-webpart-base';

export default class SecurityDashboardWebPart extends BaseClientSideWebPart<{}> {
  public render(): void {
    // Copy HTML from web-templates/sharepoint/examples/security-dashboard.html
    this.domElement.innerHTML = `
      <!-- Paste dashboard HTML here -->
    `;
    
    // Initialize any JavaScript functionality
    this._initializeDashboard();
  }

  private _initializeDashboard(): void {
    // Add event listeners, data loading, etc.
  }
}
```

3. **Build and package**
```bash
# Build solution
gulp build

# Bundle for production
gulp bundle --ship

# Package for deployment
gulp package-solution --ship
```

4. **Deploy to SharePoint**
   - Upload `.sppkg` file to App Catalog
   - Deploy the solution
   - Add web part to any page

## Connecting to Live Data

### Method 1: Power Automate Integration

1. **Create Power Automate flow**
   - Trigger: When file is created in security reports library
   - Parse JSON from audit file
   - Update SharePoint list with results

2. **Update dashboard to read from list**
```javascript
// Fetch data from SharePoint list
fetch('/_api/web/lists/getbytitle("SecurityAuditResults")/items')
  .then(response => response.json())
  .then(data => {
    // Update dashboard with real data
    updateDashboard(data.value);
  });
```

### Method 2: Direct File Access

1. **Upload audit JSON files to document library**
   - Create "Security Reports" document library
   - Upload `m365_cis_audit.json` files from `output/reports/security/`

2. **Fetch and display data**
```javascript
// Fetch latest audit file
fetch('/sites/SecurityHub/SecurityReports/m365_cis_audit_latest.json')
  .then(response => response.json())
  .then(auditData => {
    // Populate dashboard
    renderDashboard(auditData);
  });
```

### Method 3: Microsoft Graph API

```javascript
// Requires Azure AD app registration
const graphEndpoint = 'https://graph.microsoft.com/v1.0/';
const token = await getAccessToken(); // Implement OAuth flow

fetch(graphEndpoint + 'security/alerts', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(response => response.json())
.then(data => {
  // Display security alerts
});
```

## Styling and Theming

### Apply SharePoint Theme

SharePoint themes automatically apply to modern pages. To customize:

1. **Site Settings** → **Change the look**
2. Choose a theme or create custom theme
3. Your dashboard will inherit these colors for headers, backgrounds

### Override with Custom CSS

Add custom CSS in the web part:
```css
<style>
  /* Override SharePoint theme */
  .sp-stat-card {
    background: var(--themePrimary) !important;
  }
  
  /* Use SharePoint color variables */
  .header {
    color: var(--themeDarker);
    background: var(--neutralLighterAlt);
  }
</style>
```

### SharePoint Color Variables

```css
/* Available in modern SharePoint */
--themePrimary: Main brand color
--themeDark: Darker shade
--themeLight: Lighter shade
--neutralPrimary: Main text color
--neutralLight: Light background
--neutralLighter: Lighter background
```

## Security and Permissions

### Set Page Permissions

1. **Page-level permissions**
   - Open page
   - Click **...** → **Page details**
   - Set **Permissions** to specific groups

2. **Restrict to security team**
   - Create "Security Team" SharePoint group
   - Add members
   - Set page to only be visible to this group

### Data Access Control

- Store sensitive audit files in restricted document libraries
- Use item-level permissions for granular control
- Implement role-based access in SPFx web parts

## Mobile Experience

### Test on SharePoint Mobile App

1. Download SharePoint mobile app (iOS/Android)
2. Navigate to your security dashboard page
3. Verify responsive design works correctly
4. Test filter buttons and interactive elements

### Optimize for Mobile

```css
@media (max-width: 768px) {
  .sp-stats-grid {
    grid-template-columns: 1fr;
  }
  
  .sp-stat-card {
    padding: 16px;
  }
}
```

## Automation and Scheduling

### Automatic Dashboard Updates

1. **GitHub Actions → SharePoint**
```yaml
# .github/workflows/deploy-to-sharepoint.yml
- name: Upload to SharePoint
  run: |
    # Upload generated dashboard.html
    # Update SharePoint page content
```

2. **PowerShell Script**
```powershell
# Upload audit results to SharePoint
Connect-PnPOnline -Url "https://tenant.sharepoint.com/sites/SecurityHub"
Add-PnPFile -Path "output/reports/security/m365_cis_audit.json" `
            -Folder "SecurityReports"
```

### Scheduled Page Updates

Use Power Automate to:
- Trigger on new audit file
- Parse audit results
- Update dashboard page content
- Send notification to security team

## Troubleshooting

### Script Not Running

**Issue:** JavaScript not executing in SharePoint page

**Solution:**
- Modern SharePoint pages have script restrictions
- Use SPFx web parts for JavaScript
- Or use Power Automate + SharePoint lists for data

### Styling Issues

**Issue:** CSS not applying correctly

**Solution:**
- Check for SharePoint theme overrides
- Use `!important` sparingly
- Test in private browsing mode
- Clear browser cache

### Performance Issues

**Issue:** Dashboard loading slowly

**Solution:**
- Minimize embedded CSS/JS
- Use CDN for libraries
- Implement lazy loading for charts
- Cache data in browser localStorage

## Best Practices

### Content Organization

```
SharePoint Site Structure:
├── Home (landing page)
├── Security Dashboard (this dashboard)
├── Audit History (archive of reports)
├── Documentation (security policies)
└── Remediation Tracking (issue management)
```

### Version Control

- Keep dashboard HTML in Git repository
- Track changes with commit messages
- Tag releases for major updates
- Test in dev site before production

### Accessibility

- Ensure keyboard navigation works
- Add ARIA labels to interactive elements
- Provide text alternatives for charts
- Test with screen readers

### Documentation

- Add help text to dashboard
- Create user guide page
- Document data sources and update frequency
- Provide contact information for questions

## Example Implementations

### Minimal Dashboard

Simple statistics cards only:
```html
<div class="sp-container">
  <div class="sp-stats-grid">
    <div class="sp-stat-card">
      <h3>Pass Rate</h3>
      <div class="sp-stat-value pass">92%</div>
    </div>
  </div>
</div>
```

### Full Dashboard with Data Binding

Complete dashboard with dynamic data loading:
```javascript
// Fetch latest audit data
async function loadDashboard() {
  const data = await fetchAuditData();
  const stats = calculateStatistics(data);
  renderStatCards(stats);
  renderControlsTable(data);
  renderTrendChart(historicalData);
}

loadDashboard();
```

## Additional Resources

- [SharePoint Modern Experience](https://docs.microsoft.com/en-us/sharepoint/modern-experience-overview)
- [SPFx Development](https://docs.microsoft.com/en-us/sharepoint/dev/spfx/sharepoint-framework-overview)
- [Power Automate + SharePoint](https://docs.microsoft.com/en-us/power-automate/sharepoint-overview)
- [Microsoft Graph Security API](https://docs.microsoft.com/en-us/graph/api/resources/security-api-overview)

## Support

For issues or questions:
- Check repository documentation
- Review existing GitHub issues
- Contact security team
- Submit new issue with details
