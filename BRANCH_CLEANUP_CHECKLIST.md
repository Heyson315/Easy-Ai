# Branch Cleanup Checklist

**Date:** November 12, 2025  
**Repository:** Heyson315/share-report

## Quick Action Items

### ✅ Step 1: Merge Valuable Work (PRIORITY)

```bash
# 1. Merge performance benchmark implementation
git checkout main
git pull origin main
git checkout -b merge/performance-benchmark
git merge origin/copilot/implement-performance-benchmark
# Resolve conflicts if any
git push origin merge/performance-benchmark
# Create PR and merge to main

# 2. Merge Git documentation
git checkout main
git pull origin main
git checkout -b merge/git-docs
git merge origin/feature/enterprise-docs
git push origin merge/git-docs
# Create PR and merge to main

# 3. Merge development branch
git checkout main
git pull origin main
git checkout -b merge/develop
git merge origin/develop
git push origin merge/develop
# Create PR and merge to main
```

> **Note:** After merging the above PRs, delete the source branches (`copilot/implement-performance-benchmark`, `feature/enterprise-docs`) immediately or as part of the cleanup commands in Step 6 below. For `develop`, see the note in Step 6 about Git Flow vs GitHub Flow.
### ✅ Step 2: Delete Exact Duplicates

```bash
# These are exact duplicates and safe to delete immediately
git push origin --delete evidence/2025-11-11
git push origin --delete feature/mcp-server
```

### ✅ Step 3: Delete Already-Merged Branches

```bash
# These have already been merged to main
git push origin --delete copilot/troubleshoot-errors-and-report
git push origin --delete feature/powershell-compliance-final
git push origin --delete feature/automation-suite
```

### ✅ Step 4: Delete Abandoned Planning Branches

```bash
# These contain only "Initial plan" commits with no implementation
git push origin --delete copilot/fix-dotenv-linter-action
git push origin --delete copilot/fix-unused-template-content
```

### ✅ Step 5: Delete Evidence Branches (After Review)

```bash
# After confirming no unique work needed
git push origin --delete evidence/2025-10-25
```

### ✅ Step 6: Delete Completed Work Branches

```bash
# ⚠️ IMPORTANT: After merging valuable work from Step 1, delete source branches
git push origin --delete copilot/implement-performance-benchmark
git push origin --delete feature/enterprise-docs

# ⚠️ Only delete copilot/review-branches-anomalies AFTER this PR is merged to main!
# git push origin --delete copilot/review-branches-anomalies
```

**Note on develop branch:** If following Git Flow, keep `develop` as a permanent branch. If following GitHub Flow (single main branch), merge and delete it. The choice depends on your team's workflow.

### ⚠️ Step 7: Evaluate Before Deleting

```bash
# Review this branch first - 75 commits behind, may contain useful work
# git push origin --delete feature/performance-toolkit-improvements
```

## Current State vs Target State

### Current Branches (14)
- ✅ main
- ✅ develop
- ❌ copilot/fix-dotenv-linter-action
- ❌ copilot/fix-unused-template-content
- ⚠️ copilot/implement-performance-benchmark (MERGE FIRST)
- ❌ copilot/review-branches-anomalies (current - delete after complete)
- ❌ copilot/troubleshoot-errors-and-report
- ❌ evidence/2025-10-25
- ❌ evidence/2025-11-11
- ❌ feature/automation-suite
- ⚠️ feature/enterprise-docs (MERGE FIRST)
- ❌ feature/mcp-server
- ⚠️ feature/performance-toolkit-improvements (REVIEW FIRST)
- ❌ feature/powershell-compliance-final

### Target Branches (4-6)
- ✅ main (primary branch)
- ✅ develop (if using Git Flow) - otherwise merge to main and delete
- ✅ Active feature branches only (2-4 max)

## Legend
- ✅ Keep
- ❌ Delete
- ⚠️ Action Required First

## Safety Checklist

Before deleting any branch, verify:
- [ ] No open pull requests reference this branch
- [ ] No active CI/CD workflows depend on this branch
- [ ] Branch has been merged OR work is no longer needed
- [ ] Team members have been notified if collaborative work

## Verification Commands

```bash
# Check if a branch has been merged
git branch -r --merged origin/main | grep "branch-name"

# See what's unique in a branch
git log origin/main..origin/branch-name --oneline

# Check for open PRs (use GitHub UI or gh CLI)
gh pr list --base main --head branch-name

# Check branch age
git log origin/branch-name -1 --format="%ar"
```

## Notes

1. The `copilot/implement-performance-benchmark` branch contains 5 commits of completed, tested work that should definitely be merged.

2. The duplicate branches (`feature/enterprise-docs` and `feature/mcp-server`) both point to the same commit with Git documentation - only need to merge once.

3. Evidence branches appear to be snapshots - verify they're not needed for compliance/audit before deletion.

4. After cleanup, consider implementing branch protection rules and a clear branching strategy to prevent future proliferation.

## Estimated Time

- Step 1 (Merging): 30-60 minutes (depending on conflicts)
- Step 2-4 (Deletions): 5-10 minutes
- Step 5-6 (Cleanup): 5-10 minutes
- Step 7 (Review): 15-30 minutes

**Total:** ~1-2 hours for complete cleanup

## Success Criteria

- [ ] All valuable work merged to main
- [ ] All duplicate branches deleted
- [ ] All already-merged branches deleted
- [ ] Branch count reduced from 14 to 4-6
- [ ] Repository navigation is clearer
- [ ] No critical work lost

---

**Generated:** November 12, 2025  
**See also:** [BRANCH_ANOMALY_REPORT.md](BRANCH_ANOMALY_REPORT.md) for detailed analysis
