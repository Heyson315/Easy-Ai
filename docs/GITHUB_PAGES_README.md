# GitHub Pages Website - M365 Security Toolkit

This directory contains the GitHub Pages website for the M365 Security Toolkit.

## 🌐 Live Site

The website is deployed at: **https://heyson315.github.io/Easy-Ai/**

## 📁 Directory Structure

```
docs/
├── _config.yml              # Jekyll configuration
├── index.html              # Homepage with hero section and features
├── live-dashboard.html     # Interactive security dashboard
├── features.html           # Detailed feature breakdown
├── documentation.html      # Documentation hub
├── demo.html              # Interactive demo (coming soon)
├── pricing.html           # Pricing and contact form
├── privacy.html           # Privacy policy
├── terms.html             # Terms of service
├── sitemap.xml            # SEO sitemap
├── robots.txt             # Search engine directives
├── api/
│   └── sample-audit.json  # Sample audit data for dashboard
└── assets/
    ├── css/
    │   └── main.css       # Main stylesheet
    ├── js/
    │   ├── app.js         # Interactive functionality
    │   └── data-loader.js # Data fetching and processing
    └── images/            # Website images (add your own)
```

## 🚀 Local Development

### Test Locally with Python

```bash
# Navigate to docs directory
cd docs

# Start HTTP server
python3 -m http.server 8000

# Open browser to http://localhost:8000
```

### Test Locally with Jekyll

```bash
# Install Jekyll (one time)
gem install jekyll bundler

# Navigate to docs directory
cd docs

# Serve with Jekyll
jekyll serve --baseurl ''

# Open browser to http://localhost:4000
```

## 🎨 Customization

### Update Branding

1. **Colors**: Edit CSS variables in `assets/css/main.css`:
   ```css
   :root {
       --primary-color: #0078d4;  /* Your brand color */
       --secondary-color: #667eea;
   }
   ```

2. **Logo**: Add logo images to `assets/images/` and update navbar in all HTML files

3. **Content**: Edit HTML files directly (no build step required)

### Update Sample Data

Replace `api/sample-audit.json` with real audit data:

```bash
# Copy latest audit results
cp ../output/reports/security/m365_cis_audit.json api/sample-audit.json
```

### Add Images

Add the following to `assets/images/`:
- `favicon-16x16.png` and `favicon-32x32.png`
- `og-image.png` (1200x630 for social sharing)
- `twitter-card.png` (1200x600)
- Screenshots for features page

## 🔧 Configuration

### Jekyll (`_config.yml`)

```yaml
title: "M365 Security Toolkit - Rahman Finance and Accounting P.L.LLC"
description: "Enterprise-grade Microsoft 365 security auditing"
baseurl: "/Easy-Ai"  # Update if using custom domain
url: "https://heyson315.github.io"
```

### Contact Form

Update the Formspree action URL in `pricing.html`:

```html
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
```

Get your form ID at https://formspree.io

### Google Analytics (Optional)

Add to `_config.yml`:

```yaml
google_analytics: UA-XXXXXXXXX-X
```

## 📊 Features

### Homepage (`index.html`)
- Hero section with value proposition
- Live compliance score widget
- Key features showcase
- Quick start examples
- Call-to-action buttons

### Live Dashboard (`live-dashboard.html`)
- Real-time audit data visualization
- Interactive charts (Chart.js)
- Filterable controls table
- Export to CSV/JSON
- Mobile-responsive design

### Features Page (`features.html`)
- Detailed feature breakdown
- Technical specifications
- Code examples
- Comparison tables
- Screenshots placeholders

### Documentation Hub (`documentation.html`)
- Links to all documentation
- Categorized by topic
- Search-ready structure

### Pricing/Contact (`pricing.html`)
- Three-tier pricing model
- Contact form (Formspree)
- FAQ section

## 🔒 Security & Privacy

- No client-side data collection
- No cookies or tracking (unless you add analytics)
- All audit data stays local
- Privacy policy compliant with GDPR concepts

## 📱 Mobile Responsive

All pages are fully responsive:
- Mobile-first design
- Tested on phones, tablets, desktops
- Touch-friendly controls
- Fast load times (&lt;3 seconds)

## 🚀 Deployment

The site automatically deploys via GitHub Actions (`.github/workflows/deploy-pages.yml`) when changes are pushed to the `Primary` or `main` branches.

### Enable GitHub Pages

1. Go to repository Settings → Pages
2. Source: GitHub Actions
3. The site will be available at `https://heyson315.github.io/Easy-Ai/`

### Custom Domain (Optional)

1. Add CNAME file: `echo "yourdomain.com" > CNAME`
2. Configure DNS:
   ```
   A Record: 185.199.108.153
   A Record: 185.199.109.153
   A Record: 185.199.110.153
   A Record: 185.199.111.153
   ```
3. Update `_config.yml` baseurl and url

## 🔍 SEO Optimization

- **Meta Tags**: All pages have proper title, description, keywords
- **Open Graph**: Social media sharing optimized
- **Sitemap**: `sitemap.xml` for search engines
- **Robots.txt**: Search engine directives
- **Structured Data**: Schema.org markup on homepage
- **Semantic HTML**: Proper heading hierarchy, alt text

## 📈 Analytics

To track site usage:

1. Add Google Analytics to `_config.yml`
2. Or use GitHub's built-in traffic analytics (Settings → Insights → Traffic)

## 🐛 Troubleshooting

### Pages Not Loading

Check:
- Jekyll build errors in Actions tab
- Correct baseurl in `_config.yml`
- GitHub Pages enabled in settings

### Charts Not Showing

- Ensure Chart.js CDN is accessible
- Check browser console for errors
- Verify `sample-audit.json` is valid JSON

### Form Not Working

- Update Formspree action URL
- Verify email settings
- Check spam folder

## 📝 License

Website content is part of the M365 Security Toolkit project, licensed under MIT License.

## 🤝 Contributing

To improve the website:

1. Edit HTML/CSS/JS files
2. Test locally with `python3 -m http.server`
3. Commit and push to trigger deployment
4. Check Actions tab for deployment status

## 📞 Support

- **Documentation**: See main repo README.md
- **Issues**: https://github.com/Heyson315/Easy-Ai/issues
- **Email**: support@rahmanfinance.com

---

**Built with ❤️ by Rahman Finance and Accounting P.L.LLC**
