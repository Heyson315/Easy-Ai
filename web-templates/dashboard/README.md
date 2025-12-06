# M365 CIS Security Dashboard

Interactive web dashboard for visualizing Microsoft 365 CIS security audit results.

## Features

- 📊 **Real-time Metrics**: Compliance score, risk score, control statistics
- 📈 **Interactive Charts**: Status distribution and severity breakdown
- 🔍 **Search & Filter**: Find specific controls quickly
- 🎨 **Modern Design**: Dark theme with smooth animations
- �� **Responsive**: Works on desktop, tablet, and mobile

## Usage

### Option 1: Local Viewing

1. Run the M365 CIS audit to generate `m365_cis_audit.json`
2. Copy the JSON file to the dashboard directory:
   ```powershell
   Copy-Item output/reports/security/m365_cis_audit.json web-templates/dashboard/data/
   ```
3. Open `index.html` in your browser

### Option 2: GitHub Pages

The dashboard is automatically published to GitHub Pages after each audit run.

Access it at: `https://[your-username].github.io/[your-repo]/`

## Dashboard Sections

### Key Metrics
- **Compliance Score**: Percentage of passed controls
- **Risk Score**: Severity-weighted failure score (0-100)
- **Total Controls**: Number of CIS controls audited
- **Critical Findings**: Number of critical and high-severity failures

### Charts
- **Status Distribution**: Pie chart showing passed/failed/manual controls
- **Severity Breakdown**: Bar chart of failures by severity level

### Controls Table
- Filterable and searchable list of all controls
- Status badges (Pass/Fail/Manual)
- Severity indicators (Critical/High/Medium/Low)
- Detailed evidence and recommendations

## File Structure

```
web-templates/dashboard/
├── index.html          # Main dashboard
├── data/               # JSON data files
│   └── m365_cis_audit.json
└── README.md          # This file
```

## Requirements

- Modern web browser (Chrome, Firefox, Edge, Safari)
- Internet connection (for Chart.js CDN)
- Valid m365_cis_audit.json file

## Customization

The dashboard uses CSS variables for easy theming. Edit the `:root` section in `index.html`:

```css
:root {
    --primary: #0078d4;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    /* ... */
}
```

## Troubleshooting

**"Error Loading Data"**: Ensure m365_cis_audit.json is in the correct location
**Charts not showing**: Check browser console for JavaScript errors
**Slow performance**: Large audit files (1000+ controls) may take a few seconds to load

## License

Part of the Easy-Ai project. See main repository LICENSE file.
