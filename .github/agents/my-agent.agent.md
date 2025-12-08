---
# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config

name: agile nmiver
description:
---

# My Agent

Describe what your agent does here...
Here are the agent instructions for setting up your Agile workflow and automation:

✅ Agent Instruction Summary
This guide tells your GitHub Copilot agent (or any automation bot) what to do when initializing your repositories and project management system.

1. Create Agile Board
Use GitHub Projects (Beta) at the organization level. 
Configure:
Columns: Backlog, To Do, In Progress, Review, Done. 
Custom fields: Priority, Sprint, Story Points, Status. 
Import JSON configuration: 
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  "/orgs/<ORG_NAME>/projects" \
  -f name="Agile Workflow" \
  -f body="Agile board for managing all repos"

2. Add Onboarding Guide
Create /docs/onboarding-guide.md in each repo. 
Include:
Agile template 
Copilot prompts 
GitHub Actions automation snippets 
CI/CD workflow 
JSON config for Agile board 

3. Configure GitHub Actions
Add workflows:
issue-automation.yml → Moves issues between columns based on PR status. 
auto-label.yml → Adds labels based on issue title. 
ci.yml → Runs linting and tests on push/PR. 

4. Copilot Jumpstart Prompts
Include two prompts in README or /docs:
CPA Website (React + Vite + Tailwind + Microsoft 365 integrations) 
React Analytics Dashboard (Charts, Dark Mode, State Management) 

5. Optional Enhancements
Add shell script (setup-agile-board.sh) to automate:
Agile board creation 
JSON config import 
Extend script to:
Upload onboarding guide 
Commit GitHub Actions workflows 

✅ generate a single ZIP package containing:
/docs/onboarding-guide.md 
setup-agile-board.sh 
.github/workflows/issue-automation.yml 
.github/workflows/auto-label.yml 
.github/workflows/ci.yml 
agile-board.json 
download and push everything to repo in one go?
