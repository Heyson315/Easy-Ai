# GoDaddy Custom Domain Deployment Guide

## Overview

This guide explains how to deploy the M365 Security Dashboard to a custom domain hosted on GoDaddy. This approach provides complete control over design and functionality for external-facing security portals and public compliance reporting.

## Prerequisites

- GoDaddy hosting account (Shared, WordPress, or VPS)
- Domain name registered with GoDaddy
- FTP/SFTP access credentials
- Basic knowledge of HTML/CSS/JavaScript
- Optional: cPanel access for advanced configuration

## Deployment Methods

### Method 1: FTP/SFTP Upload (Recommended)

**Best for:** Quick deployment, static HTML sites

#### 1. Prepare Your Files

Organize your website files:
```
website/
├── index.html (from web-templates/godaddy/examples/)
├── css/
│   ├── base.css
│   └── dashboard.css
├── js/
│   └── main.js
├── images/
│   ├── logo.png
│   └── favicon.png
└── reports/
    └── dashboard.html (generated from audit data)
```

#### 2. Connect via FTP

**Using FileZilla (Recommended FTP Client):**

1. Download and install FileZilla: https://filezilla-project.org/
2. Get FTP credentials from GoDaddy:
   - Login to GoDaddy account
   - Go to **Web Hosting** → **Manage**
   - Find **FTP/SFTP** section
   - Note: Hostname, Username, Password, Port

3. Connect to server:
   ```
   Host: ftp.yourdomain.com
   Username: your-username@yourdomain.com
   Password: your-password
   Port: 21 (FTP) or 22 (SFTP)
   ```

4. Navigate to `public_html` directory (this is your web root)

#### 3. Upload Files

1. Drag files from local computer to `public_html` folder
2. Maintain directory structure:
   ```
   public_html/
   ├── index.html
   ├── css/
   ├── js/
   ├── images/
   └── reports/
   ```

3. Set file permissions (via FileZilla):
   - Files: 644 (rw-r--r--)
   - Directories: 755 (rwxr-xr-x)

4. Test your site: `https://yourdomain.com`

### Method 2: cPanel File Manager

**Best for:** No FTP client available, browser-based management

1. **Access cPanel**
   - GoDaddy Dashboard → **Web Hosting** → **Manage**
   - Click **cPanel Admin**

2. **Open File Manager**
   - Navigate to **Files** section
   - Click **File Manager**
   - Go to `public_html` directory

3. **Upload Files**
   - Click **Upload** button
   - Select files to upload
   - Wait for upload to complete

4. **Extract ZIP (optional)**
   - Upload ZIP file of your website
   - Right-click ZIP → **Extract**
   - Move files to `public_html`

### Method 3: Git Deployment

**Best for:** Version control, automated deployments, team collaboration

#### Setup Git on GoDaddy

1. **Enable SSH access** (VPS or some shared hosting)
2. **Connect via SSH:**
   ```bash
   ssh username@yourdomain.com
   ```

3. **Clone repository:**
   ```bash
   cd ~/public_html
   git clone https://github.com/yourusername/your-repo.git .
   ```

4. **Set up deployment script:**
   ```bash
   #!/bin/bash
   # deploy.sh
   cd ~/public_html
   git pull origin main
   # Copy generated reports
   cp output/reports/security/*.html reports/
   ```

5. **Automate with webhook:**
   - GitHub webhook → trigger deploy.sh on push

## Domain Configuration

### DNS Settings

1. **Access DNS Management**
   - GoDaddy Dashboard → **Domains** → **Manage**
   - Find your domain → **DNS**

2. **Configure A Record** (points domain to hosting server)
   ```
   Type: A
   Name: @
   Value: [Your hosting IP address]
   TTL: 600 seconds
   ```

3. **Configure WWW subdomain**
   ```
   Type: CNAME
   Name: www
   Value: @
   TTL: 1 Hour
   ```

4. **Wait for propagation** (can take 24-48 hours)

### SSL Certificate Setup

**GoDaddy provides free SSL with hosting plans**

1. **Access SSL Management**
   - GoDaddy Dashboard → **Web Hosting** → **Manage**
   - Find **SSL Certificate** section

2. **Enable SSL**
   - Click **Set Up** or **Manage**
   - Choose domain
   - Click **Install**

3. **Force HTTPS** (add to .htaccess):
   ```apache
   # Force HTTPS
   RewriteEngine On
   RewriteCond %{HTTPS} off
   RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
   ```

### Custom Domain Email

Set up professional email (e.g., security@yourdomain.com):

1. GoDaddy offers email hosting plans
2. Or use Microsoft 365 with custom domain
3. Configure MX records for email routing

## Website Optimization

### Performance Optimization

#### 1. Enable Caching (.htaccess)

```apache
# Browser Caching
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 1 hour"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType text/javascript "access plus 1 month"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
</IfModule>

# GZIP Compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css text/javascript
  AddOutputFilterByType DEFLATE application/javascript application/json
</IfModule>
```

#### 2. Minify CSS/JS

**Using online tools:**
- CSS: https://cssminifier.com/
- JS: https://jscompress.com/

**Or use build tools:**
```bash
npm install -g clean-css-cli uglify-js
cleancss -o style.min.css style.css
uglifyjs main.js -o main.min.js
```

#### 3. Optimize Images

- Use WebP format for better compression
- Resize images to actual display size
- Use lazy loading for images below the fold

```html
<img src="image.webp" loading="lazy" alt="Dashboard screenshot">
```

### SEO Optimization

#### Meta Tags (in `<head>`)

```html
<!-- Basic SEO -->
<title>M365 Security Dashboard | Enterprise Compliance Reporting</title>
<meta name="description" content="Comprehensive M365 security auditing and compliance reporting dashboard">
<meta name="keywords" content="M365, Security, Compliance, CIS Benchmark, Audit">

<!-- Open Graph (social sharing) -->
<meta property="og:title" content="M365 Security Dashboard">
<meta property="og:description" content="Enterprise security compliance reporting">
<meta property="og:image" content="https://yourdomain.com/images/preview.png">
<meta property="og:url" content="https://yourdomain.com">
<meta property="og:type" content="website">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="M365 Security Dashboard">
<meta name="twitter:description" content="Enterprise security compliance reporting">
<meta name="twitter:image" content="https://yourdomain.com/images/preview.png">
```

#### Robots.txt

Create `/public_html/robots.txt`:
```
User-agent: *
Allow: /
Disallow: /reports/ # Don't index audit reports
Sitemap: https://yourdomain.com/sitemap.xml
```

#### Sitemap.xml

Create `/public_html/sitemap.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://yourdomain.com/</loc>
    <lastmod>2024-11-14</lastmod>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://yourdomain.com/reports/</loc>
    <lastmod>2024-11-14</lastmod>
    <priority>0.8</priority>
  </url>
</urlset>
```

## Security Configuration

### Secure .htaccess

```apache
# Disable directory listing
Options -Indexes

# Protect sensitive files
<FilesMatch "^\.">
  Order allow,deny
  Deny from all
</FilesMatch>

# Protect wp-config.php (if using WordPress)
<Files wp-config.php>
  Order allow,deny
  Deny from all
</Files>

# Set security headers
<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set X-Frame-Options "SAMEORIGIN"
  Header set X-XSS-Protection "1; mode=block"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
```

### Password Protect Reports Directory

Create `/public_html/reports/.htaccess`:
```apache
AuthType Basic
AuthName "Restricted Area"
AuthUserFile /home/username/.htpasswd
Require valid-user
```

Create password file:
```bash
htpasswd -c /home/username/.htpasswd admin
# Enter password when prompted
```

### Content Security Policy

Add to `<head>` of HTML:
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; 
               style-src 'self' 'unsafe-inline';">
```

## Automated Updates

### Method 1: GitHub Actions → FTP

`.github/workflows/deploy-to-godaddy.yml`:
```yaml
name: Deploy to GoDaddy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Generate Dashboard
        run: |
          python scripts/generate_security_dashboard.py
      
      - name: FTP Deploy
        uses: SamKirkland/FTP-Deploy-Action@4.3.0
        with:
          server: ${{ secrets.FTP_SERVER }}
          username: ${{ secrets.FTP_USERNAME }}
          password: ${{ secrets.FTP_PASSWORD }}
          local-dir: ./
          server-dir: /public_html/
```

### Method 2: rsync over SSH

```bash
#!/bin/bash
# deploy.sh
rsync -avz --delete \
  --exclude '.git' \
  --exclude 'node_modules' \
  ./ username@yourdomain.com:~/public_html/
```

### Method 3: Scheduled PowerShell Upload

```powershell
# upload-to-godaddy.ps1
$ftpUri = "ftp://ftp.yourdomain.com/public_html/"
$username = "your-username"
$password = "your-password"

# Upload dashboard
$localFile = "output/reports/security/dashboard.html"
$remoteFile = "$ftpUri/reports/dashboard.html"

$webclient = New-Object System.Net.WebClient
$webclient.Credentials = New-Object System.Net.NetworkCredential($username, $password)
$webclient.UploadFile($remoteFile, $localFile)
```

## Monitoring and Analytics

### Google Analytics

Add to `<head>` before `</head>`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Uptime Monitoring

Free monitoring services:
- **UptimeRobot**: https://uptimerobot.com/
- **Pingdom**: https://www.pingdom.com/
- **StatusCake**: https://www.statuscake.com/

### Error Tracking

Add error logging:
```javascript
window.onerror = function(msg, url, line, col, error) {
  // Log to external service or send to admin
  console.error('Error:', msg, 'at', url, line, col);
  // Optional: Send to logging service
};
```

## Backup Strategy

### Automatic Backups

1. **GoDaddy cPanel Backups**
   - cPanel → **Backup Wizard**
   - Schedule automatic backups
   - Download backup files regularly

2. **Git Version Control**
   ```bash
   # Backup website to Git
   cd ~/public_html
   git add .
   git commit -m "Backup $(date +%Y-%m-%d)"
   git push origin main
   ```

3. **External Backup Script**
   ```bash
   #!/bin/bash
   # backup.sh
   DATE=$(date +%Y%m%d_%H%M%S)
   rsync -avz username@yourdomain.com:~/public_html/ \
         ./backups/backup_$DATE/
   ```

## Troubleshooting

### Common Issues

**Site Not Loading**
- Check DNS propagation: https://www.whatsmydns.net/
- Verify A record points to correct IP
- Ensure files are in `public_html` directory
- Check file permissions (644 for files, 755 for directories)

**SSL Certificate Issues**
- Verify SSL is installed in GoDaddy hosting panel
- Check .htaccess for HTTPS redirect
- Clear browser cache and test in incognito mode
- Use SSL checker: https://www.sslshopper.com/ssl-checker.html

**403 Forbidden Error**
- Check file permissions
- Ensure index.html exists in public_html
- Review .htaccess for blocking rules
- Disable directory listing protection temporarily

**500 Internal Server Error**
- Check .htaccess syntax
- Review error logs in cPanel
- Temporarily rename .htaccess to test
- Contact GoDaddy support if persists

### Performance Issues

**Slow Loading**
- Enable caching in .htaccess
- Minify CSS/JS files
- Optimize and compress images
- Use CDN for static assets
- Check hosting plan limits

## Best Practices

### File Organization
- Keep backups of all files
- Use version control (Git)
- Document changes in CHANGELOG.md
- Separate production and staging environments

### Security
- Regular security audits
- Keep software updated
- Use strong passwords
- Enable two-factor authentication on GoDaddy account
- Monitor access logs

### Maintenance
- Check site weekly
- Update audit data regularly
- Monitor uptime and performance
- Review analytics monthly
- Renew domain/hosting before expiration

## Example Use Cases

### Public Compliance Portal
- Display high-level compliance status
- No sensitive data
- SEO optimized for discovery
- Professional branding

### Client Reporting Dashboard
- Password-protected area
- Detailed audit results
- Export capabilities
- Custom branding per client

### Marketing Landing Page
- Showcase security features
- Lead generation forms
- Integration with CRM
- A/B testing for conversions

## Additional Resources

- [GoDaddy Help Center](https://www.godaddy.com/help)
- [cPanel Documentation](https://docs.cpanel.net/)
- [FileZilla Guide](https://wiki.filezilla-project.org/)
- [Let's Encrypt SSL](https://letsencrypt.org/)

## Support

For deployment assistance:
- GoDaddy Support: 24/7 phone and chat
- Repository Issues: https://github.com/Heyson315/Easy-Ai/issues
- Community Forums: Stack Overflow, Reddit r/webdev
