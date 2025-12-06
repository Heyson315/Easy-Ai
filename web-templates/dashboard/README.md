# M365 CIS Security Audit Dashboard

Interactive, single-page web dashboard for visualizing Microsoft 365 CIS security audit results.

## Features

### 📊 Real-Time Metrics

- **Compliance Score**: Overall pass percentage
- **Passed Controls**: Count and percentage
- **Failed Controls**: Count and percentage  
- **Manual Review Required**: Count and percentage

### 📈 Interactive Charts

- **Status Distribution**: Doughnut chart showing Pass/Fail/Manual breakdown
- **Severity Breakdown**: Bar chart showing High/Medium/Low severity counts
- Powered by Chart.js for smooth animations

### 🔍 Searchable Control Table

- All CIS controls in a sortable table
- Real-time search across all columns
- Filter buttons: All, Pass, Fail, Manual, High Severity
- Color-coded status badges
- Severity indicators
- Evidence tooltips on hover
- Responsive design for mobile/tablet

## Quick Start

### Open Dashboard Locally

```bash
# Option 1: Direct open
start web-templates/dashboard/index.html

# Option 2: Python server
cd web-templates/dashboard
python -m http.server 8000
# Open http://localhost:8000

# Option 3: VS Code Live Server
# Right-click index.html -> Open with Live Server
```

## Files

- `index.html` - Complete dashboard (single-page app, ~20KB)
- `sample-data.json` - Latest audit results from GitHub Actions
- `README.md` - This file

## How It Works

The dashboard loads `sample-data.json` and displays:

- **4 metric cards** with compliance statistics
- **2 interactive charts** (doughnut + bar)
- **1 filterable table** with all 15 CIS controls

No backend required - runs entirely in the browser!

## Next Steps

Deploy to:

- ✅ **GitHub Pages** (already configured in workflow)
- ✅ **SharePoint** (see `../sharepoint/README.md`)
- ✅ **Custom Domain** (see `../godaddy/README.md`)
