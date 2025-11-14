# Web Design Templates

This directory contains web design templates and assets for creating professional security dashboards and documentation sites for two platforms:

## 📁 Directory Structure

```
web-templates/
├── common/                    # Shared assets for both platforms
│   ├── css/
│   │   ├── base.css          # Core CSS with variables, components, utilities
│   │   └── dashboard.css     # Dashboard-specific styling
│   ├── js/                   # Common JavaScript utilities
│   └── images/               # Shared images and icons
├── sharepoint/               # SharePoint-specific templates
│   ├── css/                  # SharePoint-compatible CSS
│   ├── js/                   # SharePoint-compatible JavaScript
│   ├── examples/             # Example SharePoint pages
│   │   └── security-dashboard.html
│   └── README.md             # SharePoint deployment guide
└── godaddy/                  # Custom domain templates
    ├── css/                  # Custom CSS for static sites
    ├── js/                   # Custom JavaScript
    ├── examples/             # Example pages
    │   └── security-landing-page.html
    └── README.md             # GoDaddy deployment guide
```

## 🎨 Available Templates

### Common CSS (`common/css/`)

#### `base.css`
- **CSS Variables**: Complete theming system with color palette, typography, spacing
- **Reset Styles**: Modern CSS reset for consistency across browsers
- **Grid System**: Responsive grid layouts (1-4 columns, auto-fit)
- **Components**: Cards, buttons, badges, tables
- **Utilities**: Spacing, colors, alignment, display helpers
- **Responsive**: Mobile-first breakpoints
- **Print Styles**: Optimized for printing reports
- **Accessibility**: WCAG 2.1 AA compliant with focus states

**Usage:**
```html
<link rel="stylesheet" href="/web-templates/common/css/base.css">
```

#### `dashboard.css`
- **Dashboard Layouts**: Header, stats grid, chart containers
- **Statistics Cards**: Animated cards with hover effects
- **Filter Controls**: Button groups and search boxes
- **Data Tables**: Sortable, filterable tables with sticky headers
- **Status Indicators**: Color-coded badges for Pass/Fail/Manual
- **Loading States**: Spinners and skeleton screens
- **Tooltips**: Hover tooltips for additional information

**Usage:**
```html
<link rel="stylesheet" href="/web-templates/common/css/base.css">
<link rel="stylesheet" href="/web-templates/common/css/dashboard.css">
```

### SharePoint Templates (`sharepoint/`)

#### `examples/security-dashboard.html`
A complete security dashboard designed for SharePoint Online:
- SharePoint-compatible CSS (no unsupported properties)
- Modern SharePoint UI patterns (Fluent Design)
- Mobile-responsive for SharePoint app
- Ready to embed in SharePoint pages or SPFx web parts

**Features:**
- Statistics cards with pass/fail/manual counts
- Recent audit results table
- Quick action links to reports and documentation
- SharePoint color scheme (neutral palette)

**Deployment:**
1. Copy HTML content to a SharePoint page
2. Use Script Editor web part or SPFx
3. Customize links and data as needed
4. Test on SharePoint mobile app

### GoDaddy Templates (`godaddy/`)

#### `examples/security-landing-page.html`
A complete landing page for custom domains:
- Modern, gradient background design
- Sticky navigation bar
- Hero section with call-to-action buttons
- Live statistics with Chart.js integration
- Feature showcase grid
- Fully responsive (mobile-first)

**Features:**
- Interactive compliance trend chart
- Smooth scrolling navigation
- Feature cards with icons
- Dynamic date updates
- SEO-optimized meta tags
- Open Graph tags for social sharing

**Deployment:**
1. Upload HTML file to GoDaddy hosting (public_html)
2. Create `/css`, `/js`, `/images` directories
3. Configure DNS and SSL certificate
4. Test across browsers and devices

## 🚀 Quick Start

### For SharePoint

1. **Create a new page** in SharePoint Online
2. **Add a Script Editor** web part or create an SPFx web part
3. **Copy HTML from** `sharepoint/examples/security-dashboard.html`
4. **Customize data** to match your audit results
5. **Publish page** and test

### For GoDaddy

1. **Access cPanel** or FTP to your GoDaddy hosting
2. **Upload files** to `public_html` directory:
   ```
   public_html/
   ├── index.html (from godaddy/examples/security-landing-page.html)
   ├── css/
   ├── js/
   └── images/
   ```
3. **Configure domain** and SSL in GoDaddy control panel
4. **Visit your domain** to view the site

## 🎯 Using with Python Dashboard Generator

The `scripts/generate_security_dashboard.py` script generates HTML dashboards using similar patterns to these templates.

**Customize the generator:**
```python
# In generate_security_dashboard.py, modify the CSS to use common/css/base.css patterns
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/web-templates/common/css/base.css">
    <link rel="stylesheet" href="/web-templates/common/css/dashboard.css">
    ...
</head>
```

## 🎨 Customization Guide

### Theming

Both platforms support CSS variables for easy theming:

```css
:root {
    --primary-color: #0078d4;    /* Change brand color */
    --success-color: #28a745;    /* Change success indicator */
    --danger-color: #dc3545;     /* Change error indicator */
    --font-family-base: 'Your Font', sans-serif;
}
```

### Colors

**Microsoft 365 / SharePoint Colors:**
- Primary: `#0078d4` (Microsoft Blue)
- Success: `#107c10` (Green)
- Danger: `#d13438` (Red)
- Neutrals: `#323130`, `#605e5c`, `#8a8886`

**Custom Brand Colors:**
Modify in CSS variables or create a separate `theme.css` file.

### Responsive Breakpoints

```css
/* Mobile: < 576px */
/* Tablet: 576px - 768px */
/* Desktop: 768px - 992px */
/* Large Desktop: > 992px */
```

## 📚 Best Practices

### Performance
- ✅ Use CDN for libraries (Chart.js, etc.)
- ✅ Minify CSS/JS for production
- ✅ Optimize images (WebP format, proper sizing)
- ✅ Enable browser caching
- ✅ Use system fonts (no external font loading)

### Accessibility
- ✅ Semantic HTML5 elements
- ✅ ARIA labels for screen readers
- ✅ Keyboard navigation support
- ✅ Sufficient color contrast (4.5:1 minimum)
- ✅ Focus indicators on interactive elements

### Security
- ✅ Always use HTTPS
- ✅ Validate all user inputs
- ✅ Sanitize data before rendering
- ✅ Set proper CSP headers
- ✅ Regular security audits

### SEO (for GoDaddy)
- ✅ Descriptive page titles
- ✅ Meta descriptions
- ✅ Semantic heading hierarchy (H1 → H6)
- ✅ Alt text for images
- ✅ Clean, readable URLs

## 🔧 Development Workflow

### Testing
1. **Local testing:** Open HTML files in browser
2. **Browser testing:** Test on Chrome, Firefox, Safari, Edge
3. **Device testing:** Test on mobile, tablet, desktop
4. **Validation:** Use W3C HTML/CSS validators
5. **Accessibility:** Use WAVE or axe DevTools
6. **Performance:** Run Lighthouse audits

### Version Control
- Store templates in Git repository
- Use branches for major redesigns
- Document changes in commit messages
- Tag releases for production deployments

## 📖 Additional Resources

- **Web Design Guide:** `docs/WEB_DESIGN_GUIDE.md`
- **SharePoint Documentation:** `docs/USAGE_SHAREPOINT.md`
- **Python Dashboard Generator:** `scripts/generate_security_dashboard.py`
- **Copilot Instructions:** `.github/copilot-instructions.md`

## 🤝 Contributing

When adding new templates:
1. Follow existing file structure
2. Use CSS variables for theming
3. Ensure mobile responsiveness
4. Test accessibility
5. Document usage in README
6. Include example data

## 📝 License

MIT License - See LICENSE file in repository root
