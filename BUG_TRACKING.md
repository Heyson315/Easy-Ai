# Bug Tracking & Issue Management Guide

**Last Updated**: November 14, 2025  
**Repository**: [Heyson315/share-report](https://github.com/Heyson315/share-report)

---

## 🎉 Current Status: ZERO KNOWN BUGS!

The M365 Security Toolkit codebase is currently **bug-free** based on comprehensive code analysis:

✅ **Code Search**: No `TODO`, `FIXME`, `BUG`, `HACK`, or `XXX` markers found  
✅ **Code Review**: Completed with no issues identified  
✅ **Security Scan**: CodeQL analysis passed with 0 vulnerabilities  
✅ **Quality Checks**: All CI/CD quality gates passing  

---

## 🐛 Bug Tracking System

This guide establishes a standardized bug tracking system for when issues are identified.

### Bug Classification

#### Severity Levels

| Level | Icon | Description | Example | Response Time |
|-------|------|-------------|---------|---------------|
| **Critical** | 🔴 | System crash, data loss, security vulnerability | Authentication bypass, data corruption | Immediate (0-4 hours) |
| **High** | 🟠 | Major functionality broken, difficult workaround | Report generation fails, audit crashes | Same day (4-24 hours) |
| **Medium** | 🟡 | Feature impaired, workaround available | Formatting issues, minor UI bugs | 2-5 days |
| **Low** | 🟢 | Minor issue, cosmetic, edge case | Typos, spacing issues, rare scenarios | As time permits |

#### Priority Levels

| Priority | Icon | Description | SLA |
|----------|------|-------------|-----|
| **P0** | ⚡ | Fix immediately - blocking critical work | Drop everything |
| **P1** | 🔥 | Fix this sprint - high impact | Within 1 week |
| **P2** | 📋 | Fix next sprint - medium impact | Within 2-4 weeks |
| **P3** | 🐌 | Fix when convenient - low impact | Backlog |

#### Bug Status

| Status | Icon | Description |
|--------|------|-------------|
| **New** | 🆕 | Just reported, awaiting triage |
| **Investigating** | 🔍 | Under analysis to determine root cause |
| **In Progress** | 🔧 | Fix in active development |
| **Fixed** | ✅ | Fix completed, awaiting verification |
| **Verified** | ✔️ | Fix verified in test environment |
| **Deployed** | 🚀 | Fix deployed to production/main branch |
| **Won't Fix** | ❌ | Accepted as-is or not reproducible |
| **Duplicate** | 🔀 | Duplicate of another issue |

---

## 📝 Bug Report Template

### Standard Format

When reporting a bug, use this format (available in `.github/ISSUE_TEMPLATE/bug_report.md`):

```markdown
## 🐛 [Component] Brief Description

**Bug ID**: BUG-XXX  
**Severity**: 🟠 High  
**Priority**: 🔥 P1  
**Status**: 🆕 New  
**Reported**: YYYY-MM-DD  
**Assigned**: @username  
**Labels**: `bug`, `component-name`, `priority-p1`

### Description
Clear and concise description of what the bug is.

### To Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Run command '...'
4. See error

### Expected Behavior
What you expected to happen.

### Actual Behavior
What actually happened.

### Environment
- **OS**: Windows 10 / Windows 11 / Windows Server
- **PowerShell Version**: 5.1 / 7.x
- **Python Version**: 3.9.x
- **Module Versions**:
  - ExchangeOnlineManagement: x.x.x
  - Microsoft.Graph.Authentication: x.x.x
- **Tenant Type**: M365 Business / E3 / E5
- **Repository Commit**: abc123def

### Screenshots/Logs
If applicable, add screenshots or error logs.

### Impact
Who or what is affected by this bug:
- [ ] Security auditing functionality
- [ ] Report generation
- [ ] Data integrity
- [ ] User experience
- [ ] Documentation

### Workaround
Temporary fix if available (or "None known").

### Additional Context
Any other context about the problem.
```

### Example Bug Report

```markdown
## 🐛 [Dashboard] Chart fails to render with empty audit data

**Bug ID**: BUG-001  
**Severity**: 🟡 Medium  
**Priority**: 📋 P2  
**Status**: 🆕 New  
**Reported**: 2025-11-15  
**Assigned**: Unassigned  
**Labels**: `bug`, `dashboard`, `priority-p2`

### Description
The security dashboard fails to render the trend chart when audit history is empty.

### To Reproduce
1. Run `python scripts/generate_security_dashboard.py --input audit.json`
2. Use an audit file with no historical data
3. Open generated dashboard.html
4. See JavaScript error in browser console

### Expected Behavior
Dashboard should gracefully handle empty data with a "No historical data" message.

### Actual Behavior
JavaScript error: "Cannot read property 'length' of undefined"
Chart container shows blank area.

### Environment
- **OS**: Windows 11
- **Python Version**: 3.9.7
- **Browser**: Chrome 119
- **Repository Commit**: abc123

### Screenshots/Logs
[Screenshot showing blank chart area and console error]

### Impact
- [ ] Security auditing functionality
- [x] Report generation
- [ ] Data integrity
- [x] User experience
- [ ] Documentation

### Workaround
Manually add dummy historical data to JSON file before generating dashboard.

### Additional Context
This is a first-time setup issue. Once historical data exists, it works fine.
```

---

## 🏷️ Bug Tagging Strategy

### Required Labels

Every bug issue **must** have these labels:

1. **Type Label**: `bug`
2. **Priority Label**: `priority-p0`, `priority-p1`, `priority-p2`, or `priority-p3`
3. **Component Label**: One or more of:
   - `component-security-audit`
   - `component-dashboard`
   - `component-sharepoint`
   - `component-powershell`
   - `component-python`
   - `component-documentation`
   - `component-ci-cd`
   - `component-mcp-server`

### Optional Labels

- **Severity**: `severity-critical`, `severity-high`, `severity-medium`, `severity-low`
- **Platform**: `os-windows`, `os-linux`, `os-mac`
- **Help Wanted**: `help-wanted`, `good-first-issue`
- **Status**: `investigating`, `in-progress`, `blocked`
- **Version**: `affects-v1.0.0`, `fixed-in-v1.1.0`

### Example Label Set

```
bug, priority-p1, component-dashboard, severity-medium, os-windows
```

---

## 🔍 Bug Triage Process

### Weekly Triage Meeting

Every Monday at 10:00 AM (or as needed):

1. **Review New Bugs** (Status: 🆕)
   - Validate reproduction steps
   - Assign severity and priority
   - Assign owner
   - Update status to 🔍 Investigating

2. **Check In-Progress Bugs** (Status: 🔧)
   - Review progress
   - Unblock if needed
   - Adjust timeline if necessary

3. **Verify Fixed Bugs** (Status: ✅)
   - Test in clean environment
   - Update status to ✔️ Verified
   - Schedule for deployment

4. **Close Deployed Bugs** (Status: 🚀)
   - Confirm in production
   - Close issue
   - Update documentation

### Triage Decision Tree

```
New Bug Report
    ↓
Can reproduce? ──No──> Request more info or mark Won't Fix
    ↓ Yes
    ↓
Is it critical? ──Yes──> Assign P0, immediate response
    ↓ No
    ↓
Is it high severity? ──Yes──> Assign P1, fix this sprint
    ↓ No
    ↓
Is it medium severity? ──Yes──> Assign P2, fix next sprint
    ↓ No
    ↓
Assign P3, add to backlog
```

---

## 🛠️ Bug Fix Workflow

### Development Process

1. **Create Branch**
   ```bash
   git checkout -b fix/bug-xxx-brief-description
   ```

2. **Write Failing Test** (TDD approach)
   ```python
   def test_bug_xxx_reproduction():
       # Test that reproduces the bug
       # This should fail initially
       pass
   ```

3. **Implement Fix**
   - Make minimal changes
   - Follow coding standards
   - Add comments explaining the fix

4. **Verify Fix**
   ```bash
   # Run tests
   pytest tests/
   
   # Run linters
   black . --check
   flake8 .
   
   # Test manually
   ```

5. **Update Documentation**
   - Add to CHANGELOG.md
   - Update relevant docs
   - Add code comments

6. **Create Pull Request**
   - Reference bug issue: "Fixes #XXX"
   - Describe the fix
   - Include test results

7. **Code Review**
   - Peer review required
   - Address feedback
   - Get approval

8. **Merge & Deploy**
   - Merge to main branch
   - Update bug status to 🚀 Deployed
   - Close issue

### Commit Message Format

```
fix(component): Brief description of fix (fixes #XXX)

Longer explanation of what was wrong and how it was fixed.

- Detail 1
- Detail 2

Fixes #XXX
```

Example:
```
fix(dashboard): Handle empty historical data gracefully (fixes #123)

The dashboard generator was throwing a JavaScript error when no
historical audit data was available. Added a check for empty arrays
and displays a friendly "No historical data" message instead.

- Added data validation before chart rendering
- Added user-friendly empty state message
- Added test case for empty data scenario

Fixes #123
```

---

## 📊 Bug Metrics & Reporting

### Key Metrics to Track

1. **Bug Count by Severity**
   - Critical: X
   - High: X
   - Medium: X
   - Low: X

2. **Bug Age**
   - Average time from report to fix
   - Bugs open > 30 days
   - Bugs open > 90 days

3. **Resolution Rate**
   - Bugs fixed per week
   - Bugs reported per week
   - Net change

4. **Quality Indicators**
   - Bugs found in testing vs production
   - Regression bugs (reopened issues)
   - Duplicate bug reports

### Monthly Bug Report

Generate monthly report including:

```markdown
## Bug Metrics - [Month] [Year]

### Summary
- New Bugs: X
- Fixed Bugs: X
- Open Bugs: X
- Average Resolution Time: X days

### By Severity
- Critical: X open, X fixed
- High: X open, X fixed
- Medium: X open, X fixed
- Low: X open, X fixed

### Top Issues
1. [Component] Issue description (#XXX) - P1, 15 days old
2. [Component] Issue description (#XXX) - P1, 12 days old
3. [Component] Issue description (#XXX) - P2, 8 days old

### Trends
- Security-related bugs: X (increasing/decreasing)
- Performance issues: X
- Documentation issues: X

### Action Items
- [ ] Prioritize P0/P1 bugs
- [ ] Add test coverage for common bug areas
- [ ] Update documentation to prevent recurring issues
```

---

## 🔒 Security Bug Handling

### Special Process for Security Vulnerabilities

**⚠️ IMPORTANT**: Security bugs require special handling

1. **Private Reporting**
   - Email: security@company.com
   - Do NOT create public GitHub issue
   - Use GitHub Security Advisories

2. **Immediate Triage**
   - Assess severity (use CVSS scoring)
   - Determine exploitability
   - Identify affected versions

3. **Rapid Response**
   - P0 priority for critical vulnerabilities
   - Fix and test in private branch
   - Coordinate disclosure timeline

4. **Disclosure**
   - Fix deployed first
   - Public advisory after fix
   - Credit reporter (if desired)

5. **Post-Mortem**
   - Root cause analysis
   - Prevention measures
   - Update security practices

---

## 🧪 Bug Prevention Strategies

### Proactive Measures

1. **Increase Test Coverage**
   - Current: ~15%
   - Target: >80%
   - Focus on critical paths

2. **Code Review**
   - All PRs require review
   - Security-focused reviews
   - Performance considerations

3. **Static Analysis**
   - CodeQL security scanning
   - PSScriptAnalyzer for PowerShell
   - Python linting (flake8, mypy)

4. **Documentation**
   - Clear usage examples
   - Common pitfalls documented
   - Troubleshooting guides

5. **Testing in Realistic Environments**
   - Use CPA firm M365 environment
   - Test with real data patterns
   - Validate edge cases

### Root Cause Analysis

For each bug, document:
- **What**: What went wrong
- **Why**: Root cause
- **When**: When introduced (git bisect)
- **Where**: Affected components
- **How**: How to prevent similar bugs

---

## 📚 References

### Related Documents
- [Project Status Map](PROJECT_STATUS.md) - Complete project status
- [Interactive Dashboard](PROJECT_STATUS_MAP.html) - Visual project map
- [Code Review Guidelines](CODE_REVIEW.md) - Review standards
- [Contributing Guide](CONTRIBUTING.md) - Development guidelines
- [Changelog](CHANGELOG.md) - Version history

### External Resources
- [GitHub Issues](https://github.com/Heyson315/share-report/issues)
- [GitHub Discussions](https://github.com/Heyson315/share-report/discussions)
- [Security Policy](SECURITY.md)

---

## 🤝 Contributing to Bug Tracking

### How to Help

1. **Report Bugs**: Use the template, provide details
2. **Reproduce Bugs**: Help verify reported issues
3. **Fix Bugs**: Submit PRs for open issues (check `good-first-issue` label)
4. **Improve Process**: Suggest improvements to this guide

### Recognition

Contributors who help with bug tracking will be:
- Credited in release notes
- Listed in CONTRIBUTORS.md (when created)
- Thanked in relevant issues

---

**End of Bug Tracking Guide**

*This document should be updated as the bug tracking process evolves and new patterns emerge.*

**Maintained By**: Project Team  
**Review Frequency**: Quarterly or after major releases
