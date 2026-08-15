# Workflow: StashStats

## Branching Strategy
- **Trunk-based Development**: The `main` branch is always in a deployable state. All feature development happens in short-lived branches that are merged back to `main` as quickly as possible.

## Pull Requests & Code Review
- **Solo Developer Mode ("Ship It")**: Designed for fast iteration. While creating PRs for organization is encouraged, direct commits to `main` or merging unreviewed PRs are perfectly acceptable and part of the expected workflow.

## CI/CD & Automation
- **Automated Linting & Testing**: Ruff, Black, and pytest are configured to run automatically to ensure code quality and prevent regressions.
- **Automated Deployments**: Code merged to `main` will automatically trigger the build and deployment of Docker containers to the target environment.

## Subtracks & Phased Planning Protocol
- **Parent Tracks**: High-level feature roadmap. Defines milestones, cross-phase architecture, and links active subtracks.
- **Phased Subtracks**: Each phase of a large track executes as an isolated subtrack in `<track_dir>/subtracks/<subtrack_id>/`.
- **Iterative Planning**: Subtracks are planned strictly sequentially. Phase $N+1$ spec and plan are drafted only after Phase $N$ completes verification, using the concrete codebase state and learnings from Phase $N$.
- **Subtrack Lifecycle**:
  1. Initialize subtrack folder (`metadata.json`, `spec.md`, `plan.md`, `index.md`).
  2. Implement tasks following TDD (write test -> implement -> verify).
  3. Run verification and checkpoint.
  4. Mark subtrack complete in parent track index and initialize next subtrack.

