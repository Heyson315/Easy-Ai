# Git Branch Strategy - M365 Security Toolkit

## 🎯 Overview

This repository uses **Standard Git Flow** with additional **evidence/audit branches** for CPA firm compliance requirements.

**Restructured on**: November 11, 2025  
**Previous structure**: Used `evidence/2025-10-25` as default branch

---

## 🌳 Branch Structure

```
main                        ← Production-ready code (stable releases)
├── develop                 ← Active development (integration branch)
│   ├── feature/*          ← New features and enhancements
│   ├── copilot/*          ← AI-generated code branches
│   └── hotfix/*           ← Critical bug fixes
└── evidence/YYYY-MM-DD    ← Dated snapshots for audit trails
```

---

## 📋 Branch Types

### **1. Main Branch** (`main`)
- **Purpose**: Production-ready code
- **Protection**: Protected branch, requires PR reviews
- **Merges from**: `develop` (via PR) or `hotfix/*` (emergency only)
- **Never commit directly**: Always use PRs

```bash
# Deploy to production from main
git checkout main
git pull origin main
```

### **2. Develop Branch** (`develop`)
- **Purpose**: Active development and integration
- **Default for new work**: Start all features from here
- **Merges from**: `feature/*`, `copilot/*`, completed work
- **Merges to**: `main` (via PR when ready for release)

```bash
# Start working on develop
git checkout develop
git pull origin develop
```

### **3. Feature Branches** (`feature/*`)
- **Purpose**: New features and enhancements
- **Naming**: `feature/descriptive-name`
- **Created from**: `develop`
- **Merged to**: `develop` (via PR)
- **Lifetime**: Delete after merge

```bash
# Create feature branch
git checkout develop
git checkout -b feature/add-azure-integration
git push -u origin feature/add-azure-integration

# After PR merged
git checkout develop
git branch -d feature/add-azure-integration
git push origin --delete feature/add-azure-integration
```

**Examples**:
- `feature/mcp-server` - MCP server implementation
- `feature/gpt5-integration` - GPT-5 AI integration
- `feature/enhanced-reporting` - Report improvements

### **4. Copilot Branches** (`copilot/*`)
- **Purpose**: AI-generated code and fixes
- **Naming**: `copilot/descriptive-name`
- **Created from**: `develop` or specific branch
- **Merged to**: `develop` (via PR with human review)
- **Special**: Always review AI-generated code before merge

```bash
# Create copilot branch
git checkout develop
git checkout -b copilot/fix-security-audit
git push -u origin copilot/fix-security-audit
```

**Examples**:
- `copilot/fix-dotenv-linter-action` - Fix CI/CD issues
- `copilot/troubleshoot-errors-and-report` - Debug and document
- `copilot/implement-performance-benchmark` - Performance tools

### **5. Evidence Branches** (`evidence/YYYY-MM-DD`) 🆕
- **Purpose**: Dated snapshots for audit trails and compliance
- **Naming**: `evidence/YYYY-MM-DD` (ISO date format)
- **Created from**: `main` (snapshot of production state)
- **Never delete**: Keep for audit/compliance records
- **Read-only**: Don't develop on these branches

```bash
# Create monthly evidence snapshot
git checkout main
git checkout -b evidence/2025-12-31
git push -u origin evidence/2025-12-31
```

**Use cases**:
- End-of-month audit snapshots
- Quarterly compliance reviews
- Year-end tax preparation evidence
- SOX compliance documentation
- Client engagement records

**Current evidence branches**:
- `evidence/2025-10-25` - Historical (previous default branch)
- `evidence/2025-11-11` - Current snapshot

### **6. Hotfix Branches** (`hotfix/*`)
- **Purpose**: Critical production bug fixes
- **Naming**: `hotfix/critical-issue`
- **Created from**: `main`
- **Merged to**: `main` AND `develop` (both branches)
- **Lifetime**: Delete after merge

```bash
# Create emergency hotfix
git checkout main
git checkout -b hotfix/critical-security-bug
# Fix the issue
git push -u origin hotfix/critical-security-bug

# After merge to main, also merge to develop
git checkout develop
git merge hotfix/critical-security-bug
git push origin develop
```

---

## 🔄 Standard Workflows

### **1. New Feature Development**

```bash
# 1. Start from latest develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/my-new-feature

# 3. Work and commit
git add .
git commit -m "feat: implement my new feature"
git push -u origin feature/my-new-feature

# 4. Create Pull Request on GitHub
# Target: develop ← feature/my-new-feature

# 5. After PR approved and merged
git checkout develop
git pull origin develop
git branch -d feature/my-new-feature
```

### **2. Release to Production**

```bash
# 1. Develop is ready for release
git checkout develop
git pull origin develop

# 2. Create PR: main ← develop
# Review all changes since last release

# 3. After PR merged to main
git checkout main
git pull origin main

# 4. Create release tag
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0

# 5. Create evidence snapshot (optional)
git checkout -b evidence/2025-11-30
git push -u origin evidence/2025-11-30
```

### **3. AI-Assisted Development (Copilot)**

```bash
# 1. Let GitHub Copilot create branch
# Copilot will create: copilot/fix-something

# 2. Review AI-generated code carefully
git checkout copilot/fix-something
# Review every file, test thoroughly

# 3. Create PR to develop
# Add human review comments
# Target: develop ← copilot/fix-something

# 4. After merge
git checkout develop
git pull origin develop
```

### **4. Monthly Evidence Snapshot**

```bash
# At end of each month
git checkout main
git pull origin main

# Create dated snapshot
git checkout -b evidence/2025-12-31
git push -u origin evidence/2025-12-31

# Return to develop
git checkout develop
```

---

## 🛡️ Branch Protection Rules

### **Main Branch** (Protected)
- ✅ Require pull request reviews (1+ approver)
- ✅ Require status checks to pass (CI/CD)
- ✅ Require conversation resolution
- ✅ Do not allow force pushes
- ✅ Do not allow deletions

### **Develop Branch** (Semi-Protected)
- ✅ Require status checks to pass (CI/CD)
- ⚠️ Allow force pushes from admins only
- ✅ Do not allow deletions

### **Evidence Branches** (Protected)
- ✅ Do not allow force pushes
- ✅ Do not allow deletions
- 📋 Keep indefinitely for compliance

---

## 📊 Current Branch Status

Run this command to see all branches:

```bash
git branch -a
```

**Expected output**:
```
  evidence/2025-10-25
  evidence/2025-11-11
* develop
  main
  remotes/origin/develop
  remotes/origin/evidence/2025-10-25
  remotes/origin/evidence/2025-11-11
  remotes/origin/main
  remotes/origin/feature/*
  remotes/origin/copilot/*
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start new feature | `git checkout develop && git checkout -b feature/name` |
| Start AI work | `git checkout develop && git checkout -b copilot/name` |
| Create evidence snapshot | `git checkout main && git checkout -b evidence/YYYY-MM-DD` |
| Emergency fix | `git checkout main && git checkout -b hotfix/name` |
| Merge to develop | Create PR on GitHub: `develop ← feature/name` |
| Release to production | Create PR on GitHub: `main ← develop` |

---

## 🔍 Checking Out Code

```bash
# Latest development code
git checkout develop
git pull origin develop

# Latest production code
git checkout main
git pull origin main

# Historical snapshot
git checkout evidence/2025-10-25

# Specific feature
git checkout feature/mcp-server
```

---

## 🆘 Troubleshooting

### **"I'm on the wrong branch!"**
```bash
# Save your work
git stash

# Switch to correct branch
git checkout develop

# Restore your work
git stash pop
```

### **"I committed to main by mistake!"**
```bash
# Don't panic! Create a feature branch
git checkout -b feature/accidental-changes

# Push it
git push -u origin feature/accidental-changes

# Reset main to match remote
git checkout main
git reset --hard origin/main
```

### **"I need yesterday's code!"**
```bash
# Check evidence branch
git checkout evidence/2025-11-10

# Or specific commit
git log --oneline -20
git checkout <commit-hash>
```

---

## 📚 Additional Resources

- **Git Flow Guide**: https://nvie.com/posts/a-successful-git-branching-model/
- **GitHub Flow**: https://docs.github.com/en/get-started/quickstart/github-flow
- **CPA Compliance**: See audit requirements in firm documentation

---

## 📝 Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2025-11-11 | Restructured to Git Flow | Improved organization and compliance |
| 2025-10-25 | Previous structure | Used evidence branch as default |

---

**🎯 Remember**: 
- Work on `develop` for daily development
- Merge to `main` only for releases
- Create `evidence/*` branches for audit trails
- Always use PRs for merging
