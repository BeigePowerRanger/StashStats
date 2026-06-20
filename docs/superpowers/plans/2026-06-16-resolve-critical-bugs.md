# Resolve Critical Bugs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify and resolve the remaining critical bugs listed in StashStats.md.

**Architecture:** We will systematically check the code for the 4 critical bugs, verify if they have already been resolved by previous commits, run tests to verify correctness, and mark them as resolved in StashStats.md.

**Tech Stack:** Python, pytest

---

### Task 1: Verify and Update critical bugs list

**Files:**
- Modify: `StashStats.md`

- [ ] **Step 1: Check Optional/List import in search_results.py**
  Verify that `Optional` and `List` are imported at the top of `stashies/components/search_results.py`.
  If they are imported, mark `[x]` for `Optional/List not imported` in `StashStats.md`.

- [ ] **Step 2: Check data['yarns'] key guard in model.py**
  Verify that `data.get('yarns')` is used with a safe guard in `stashies/model.py`.
  If verified, mark `[x]` for `data['yarns'] no key guard` in `StashStats.md`.

- [ ] **Step 3: Check USERNAME environment variable usage**
  Verify that `os.getenv("RAVELRY_USERNAME")` is used instead of `os.getenv("USERNAME")` in all Python and configuration files.
  If verified, mark `[x]` for `os.getenv("USERNAME") collides with Linux shell variable` in `StashStats.md`.

- [ ] **Step 4: Check MagicMock import in test_e2e.py**
  Verify that `MagicMock` is imported at the top of `tests/test_e2e.py` before its first use.
  If verified, mark `[x]` for `MagicMock imported after use` in `StashStats.md`.

- [ ] **Step 5: Run tests**
  Run pytest to ensure all tests pass.
  Command: `.venv/bin/pytest`
  Expected output: `11 passed`

- [ ] **Step 6: Commit changes**
  Stage and commit `StashStats.md`.
  Command: `git add StashStats.md && git commit -m "docs: mark critical bugs as resolved in StashStats.md"`
