# Workflow: StashStats

## Branching Strategy
- **Trunk-based Development**: The `main` branch is always in a deployable state. All feature development happens in short-lived branches that are merged back to `main` as quickly as possible.

## Pull Requests & Code Review
- **Solo Developer Mode ("Ship It")**: Designed for fast iteration. While creating PRs for organization is encouraged, direct commits to `main` or merging unreviewed PRs are perfectly acceptable and part of the expected workflow.

## CI/CD & Automation
- **Automated Linting & Testing**: Ruff, Black, and pytest are configured to run automatically to ensure code quality and prevent regressions.
- **Automated Deployments**: Code merged to `main` will automatically trigger the build and deployment of Docker containers to the target environment.
