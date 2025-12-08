# Quick Release Checklist

Use this checklist when ready to publish v1.0.0 to GitHub Actions Marketplace.

## Pre-Release Verification

- [ ] All changes committed and pushed to `Primary` branch
- [ ] CI/CD pipeline passing (check Actions tab)
- [ ] `action.yml` file present in repository root
- [ ] README.md includes installation instructions
- [ ] Usage examples documented in `.github/ACTION_USAGE_EXAMPLES.md`
- [ ] License file present (MIT License confirmed ✓)
- [ ] No sensitive data in repository

## Release Tagging

### Step 1: Create Annotated Tag

```bash
git tag -a v1.0.0 -m "Release v1.0.0: M365 Security & Compliance Audit

Initial stable release with:
- CIS M365 security compliance auditing
- SharePoint permissions analysis  
- Excel report generation
- Interactive HTML dashboards
- Service principal authentication
- GitHub Actions integration
- Comprehensive AI development docs
- MCP server support (optional extension)

Tested in enterprise CPA environment."
```

### Step 2: Push Tag to GitHub

```bash
git push origin v1.0.0
```

### Step 3: Create Major Version Tag

```bash
# This allows users to use @v1 for auto-updates
git tag -fa v1 -m "Latest v1.x.x release"
git push origin v1 --force
```

### Step 4: Create GitHub Release (Manual)

1. Go to: https://github.com/Heyson315/Easy-Ai/releases/new
2. Select tag: `v1.0.0`
3. Release title: `v1.0.0 - Initial Stable Release`
4. Description:

```markdown
## 🎉 Initial Stable Release

Enterprise-ready Microsoft 365 security auditing and SharePoint permissions analysis toolkit with GitHub Actions integration.

### ✨ Key Features

- 🔐 **CIS M365 Compliance**: Automated security control assessments
- 📊 **SharePoint Analysis**: Detailed permissions reporting
- 🤖 **GitHub Actions**: Pre-built workflow integration
- 📈 **Interactive Dashboards**: HTML reports with trend analysis
- 🔧 **Service Principal**: Unattended automation support
- 🧠 **AI Development Ready**: Comprehensive Copilot instructions

### 🚀 Quick Start

#### Use in GitHub Actions

```yaml
- name: Run M365 Security Audit
  uses: Heyson315/Easy-Ai@v1
  with:
    tenant-id: ${{ secrets.M365_TENANT_ID }}
    client-id: ${{ secrets.M365_CLIENT_ID }}
    client-secret: ${{ secrets.M365_CLIENT_SECRET }}
    generate-dashboard: true
```

See [Action Usage Examples](.github/ACTION_USAGE_EXAMPLES.md) for more patterns.

#### Install Locally

```bash
git clone https://github.com/Heyson315/Easy-Ai.git
cd Easy-Ai
pip install -r requirements.txt
```

### 📚 Documentation

- [Getting Started](README.md#-quick-start)
- [Security Auditing Guide](docs/SECURITY_M365_CIS.md)
- [SharePoint Analysis](docs/USAGE_SHAREPOINT.md)
- [AI Development Guide](.github/copilot-instructions.md)
- [Custom MCP Server](docs/CUSTOM_MCP_SERVER_GUIDE.md)

### 🏢 Enterprise Features

Developed and tested in wholly owned CPA firm environment with:
- Multi-user professional services scenarios
- Real compliance requirements (SOX, AICPA)
- Integration with accounting software ecosystems

### 🔒 Security

- Service principal authentication
- Secure secret management
- No hardcoded credentials
- CodeQL security scanning
- Dependabot updates

### 📊 What's Included

**Core Components:**
- M365 CIS audit PowerShell module (483+ lines)
- CSV cleaning utilities
- Excel report generation
- HTML dashboard creation
- GitHub Actions workflow

**Optional Extensions:**
- MCP server for AI assistant integration
- GPT-5 integration utilities
- Performance benchmarking tools

### 🙏 Acknowledgments

Built with:
- GitHub Copilot for AI-assisted development
- Microsoft Graph API
- Exchange Online PowerShell
- SharePoint Online Management Shell
- Python data processing libraries

### 📝 License

MIT License - See [LICENSE](LICENSE) for details

### 🐛 Issues & Support

- [Report Issues](https://github.com/Heyson315/Easy-Ai/issues)
- [Discussions](https://github.com/Heyson315/Easy-Ai/discussions)
- [Documentation](docs/README.md)

---

**Full Changelog**: https://github.com/Heyson315/Easy-Ai/commits/v1.0.0
```

5. **Assets**: Leave empty (no compiled binaries)
6. **Check**: "Set as the latest release"
7. Click "Publish release"

## Post-Release Verification

### Verify Action in Marketplace

- [ ] Navigate to: https://github.com/marketplace
- [ ] Search for: "M365 Security" or "Easy-Ai"
- [ ] Confirm action appears in search results
- [ ] Check action page displays correctly
- [ ] Verify usage instructions are clear

### Test Action from Marketplace

Create a test repository with this workflow:

```yaml
name: Test M365 Action

on: workflow_dispatch

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test Action
        uses: Heyson315/Easy-Ai@v1
        with:
          tenant-id: ${{ secrets.M365_TENANT_ID }}
          client-id: ${{ secrets.M365_CLIENT_ID }}
          client-secret: ${{ secrets.M365_CLIENT_SECRET }}
```

- [ ] Workflow runs successfully
- [ ] Reports generated correctly
- [ ] Outputs available in subsequent steps

### Update Documentation

- [ ] Add "Latest Release" badge to README:
  ```markdown
  [![Latest Release](https://img.shields.io/github/v/release/Heyson315/Easy-Ai)](https://github.com/Heyson315/Easy-Ai/releases/latest)
  ```

- [ ] Update CHANGELOG.md with v1.0.0 entry

- [ ] Tweet/announce release (optional)

## Common Issues & Solutions

### Issue: Tag Already Exists

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0

# Recreate tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Issue: Action Not Appearing in Marketplace

- Verify `action.yml` is in repository root (not in subdirectory)
- Check `name` field in action.yml is unique
- Wait 5-10 minutes for indexing
- Verify repository is public

### Issue: Action Failing for Users

- Check `runs.using: composite` is set correctly
- Verify all step `shell` properties are defined
- Test action with clean repository clone
- Review logs in Actions tab

## Future Version Strategy

### Patch Releases (v1.0.x)
- Bug fixes only
- No new features
- Update v1 tag to point to latest patch

### Minor Releases (v1.x.0)
- New features (backwards compatible)
- Documentation improvements
- Update v1 tag to point to latest minor

### Major Releases (v2.0.0)
- Breaking changes
- Major architectural changes
- Do NOT update v1 tag

### Tagging Pattern

```bash
# For v1.0.1 (bug fix)
git tag -a v1.0.1 -m "Fix: CSV parsing error"
git push origin v1.0.1
git tag -fa v1 -m "Latest v1.x.x"
git push origin v1 --force

# For v1.1.0 (new feature)
git tag -a v1.1.0 -m "Feature: Add Purview integration"
git push origin v1.1.0
git tag -fa v1 -m "Latest v1.x.x"
git push origin v1 --force

# For v2.0.0 (breaking change)
git tag -a v2.0.0 -m "Breaking: Rename action inputs"
git push origin v2.0.0
# Do NOT update v1 tag
```

## Success Metrics

Track these after release:

- **Stars**: Target 50+ in first month
- **Forks**: Indicates customization interest
- **Action Uses**: Track in Actions insights
- **Issues**: Quality of bug reports
- **PRs**: Community contributions
- **Discussions**: Questions and use cases

## Marketing Checklist (Optional)

- [ ] Post on Reddit (r/PowerShell, r/sysadmin)
- [ ] Tweet with #GitHub #M365 #Security
- [ ] LinkedIn post
- [ ] Dev.to article
- [ ] Add to awesome lists (awesome-powershell, awesome-security)
- [ ] Submit to Product Hunt
- [ ] Create demo video
- [ ] Write blog post about development process

---

## Quick Command Summary

```bash
# Complete release process
git tag -a v1.0.0 -m "Release v1.0.0: Initial stable release"
git push origin v1.0.0
git tag -fa v1 -m "Latest v1.x.x release"
git push origin v1 --force

# Then create release on GitHub web interface
```

**That's it!** Your action will be live in the GitHub Actions Marketplace! 🎉

---

**Ready to Publish?** Run the commands above when ready!

**Questions?** Review [MARKETPLACE_STATUS.md](MARKETPLACE_STATUS.md) for full details.
