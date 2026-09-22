# De-AI and Anti-Slop Codebase Text Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strip AI writing patterns, marketing buzzwords, copula avoidance, and verbose fluff across all repository documentation, Conductor tracks, Quarto guides, notes, and Python docstrings to establish a concise, direct, professional technical voice.

**Architecture:** A multi-phase text audit and de-slop refactor guided by `humanizer`, `unslop`, and `avoid-ai-writing` pattern catalogs. Tasks group target files by domain (Conductor specs, Quarto docs, architectural references, and codebase docstrings), culminating in an automated regression script to prevent reintroduction of high-frequency AI slop tokens.

**Tech Stack:** Markdown, Quarto (`.qmd`), Python 3.11, Pydantic v2, Pytest, Ruff.

**Spec:** [docs/superpowers/plans/2026-09-22-de-ai-codebase-text.md](file:///home/thotsky/.gemini/antigravity/worktrees/StashStats/ai_engineered_portfolio_cleanup/docs/superpowers/plans/2026-09-22-de-ai-codebase-text.md)

## Global Constraints

- **Strict Register:** Professional, neutral, direct, concise. Fewer words preferred over decorative prose.
- **No Synthetic Humanizer Fluff:** Do not introduce fake first-person ("I think", "in my experience"), manufactured stakes ("now more than ever"), performed candor ("let's be honest"), or staccato rhythm fragments.
- **Banned AI Buzzwords:** Eliminate `robust`, `comprehensive`, `seamlessly`, `leverage`, `delve`, `pivotal`, `landscape`, `tapestry`, `testament`, `vibrant`, `nestled`, `showcase`, `underscore`, `foster`, `intricacies`, `elevate`.
- **Copula Restoration:** Replace copula avoidance (`serves as`, `stands as`, `boasts`, `features`) with direct verbs (`is`, `has`, `uses`, `provides`).
- **Preserve Technical Integrity:** Never modify code logic, type annotations, API signatures, URLs, test assertions, or schema field names.

---

### Task 1: Core README, Changelog, and Conductor Foundation Specs

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `conductor/product.md`
- Modify: `conductor/product-guidelines.md`
- Modify: `conductor/tech-stack.md`
- Modify: `conductor/workflow.md`
- Modify: `conductor/tracks.md`
- Modify: `conductor/index.md`

**Interfaces:**
- Consumes: Existing project specifications and README structure
- Produces: Terse, fluff-free product definitions and development guidelines

- [ ] **Step 1: Audit core specs for AI word slop and copula avoidance**

Run:
```bash
grep -E "(robust|comprehensive|seamlessly|leverage|serves as|designed to help|elevate)" README.md CHANGELOG.md conductor/product.md conductor/product-guidelines.md conductor/tech-stack.md conductor/workflow.md conductor/tracks.md conductor/index.md
```
Expected: Multiple hits showing marketing fluff and inflated significance.

- [ ] **Step 2: Rewrite `README.md` and `CHANGELOG.md`**

Replace inflated phrases with concise technical descriptions. For example:
- `An AI-Engineered Analytics Engine & Management Platform` -> `Analytics Engine and Management Platform for Yarn Stashes and Ravelry Data`
- `production-grade web application and analytical engine` -> `Web application and analytics engine`
- `connects to the Ravelry API to ingest personal yarn inventories` -> `Connects to the Ravelry API to track yarn inventories`

- [ ] **Step 3: Rewrite `conductor/*.md` foundation specs**

In `conductor/product.md`:
- Change: `building the stashies directory into a robust, comprehensive, reusable Python package`
- To: `building the stashstats package for interacting with the Ravelry API`
- Change: `seamlessly synchronize stash data back and forth with Ravelry`
- To: `synchronize stash data with Ravelry`

In `conductor/product-guidelines.md`:
- Change: `comprehensive docstrings for all classes`
- To: `clear docstrings for all public classes`

- [ ] **Step 4: Verify core files are clean of buzzwords**

Run:
```bash
grep -E "(robust|comprehensive|seamlessly|leverage|serves as|landscape|tapestry)" README.md CHANGELOG.md conductor/product.md conductor/product-guidelines.md conductor/tech-stack.md conductor/workflow.md conductor/tracks.md conductor/index.md || echo "CLEAN"
```
Expected: "CLEAN" (exit code 0).

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md conductor/*.md
git commit -m "docs: de-AI and streamline core documentation and conductor specs"
```

---

### Task 2: Conductor Track Specs and Plans

**Files:**
- Modify: `conductor/tracks/*/spec.md` (all 11 track specs)
- Modify: `conductor/tracks/*/plan.md` (all 11 track plans)

**Interfaces:**
- Consumes: Existing track documentation in `conductor/tracks/`
- Produces: Concise track definitions and checklists without AI boilerplate

- [ ] **Step 1: Audit track specifications for AI patterns**

Run:
```bash
grep -rnE "(robust|comprehensive|seamlessly|leverage|elevate|cutting-edge|pivotal)" conductor/tracks/
```
Expected: Identified hits in `pydantic_oop_refactor_20260826/spec.md`, `stash_analytics_20260824/spec.md`, `project_tab_accordion_20260830/plan.md`, etc.

- [ ] **Step 2: Rewrite `conductor/tracks/pydantic_oop_refactor_20260826/spec.md`**

Replace:
`Elevate the codebase to modern Pydantic v2 patterns and a clean, modular Object-Oriented architecture. Replace loose dictionary manipulations and defensive fallback chains with strictly validated models...`
With:
`Refactor domain models to Pydantic v2. Replace raw dictionaries with validated models, split RavelryClient into domain mixins, and use Pydantic validators.`

- [ ] **Step 3: Rewrite `conductor/tracks/stash_analytics_20260824/spec.md`**

Replace:
`Implement the comprehensive Stash Analytics dashboard and calculation engine in StashStats. This feature computes consumption velocity, periodic net stash flow...`
With:
`Add stash analytics dashboard and calculations. Computes consumption velocity, periodic net stash flow, rolling burn rates (30d/90d/365d), and projected depletion horizons.`

- [ ] **Step 4: Clean remaining track `spec.md` and `plan.md` files**

Remove filler words, "seamlessly", "robust", and excessive bolding across all track files in `conductor/tracks/*`.

- [ ] **Step 5: Verify track documentation**

Run:
```bash
grep -rnE "(robust|comprehensive|seamlessly|leverage|elevate|cutting-edge)" conductor/tracks/ || echo "CLEAN"
```
Expected: "CLEAN".

- [ ] **Step 6: Commit**

```bash
git add conductor/tracks/
git commit -m "docs(conductor): strip AI word slop and buzzwords from track specs"
```

---

### Task 3: Quarto Technical Documentation Pages

**Files:**
- Modify: `quarto/index.qmd`
- Modify: `quarto/architecture.qmd`
- Modify: `quarto/auth.qmd`
- Modify: `quarto/analytics-overview.qmd`
- Modify: `quarto/analytics-velocity.qmd`
- Modify: `quarto/analytics-distributions.qmd`
- Modify: `quarto/analytics-projects.qmd`
- Modify: `quarto/client-overview.qmd`
- Modify: `quarto/client-stash.qmd`
- Modify: `quarto/client-yarn.qmd`
- Modify: `quarto/client-projects.qmd`
- Modify: `quarto/models-overview.qmd`
- Modify: `quarto/models-stash.qmd`
- Modify: `quarto/models-yarn.qmd`
- Modify: `quarto/models-project.qmd`
- Modify: `quarto/web-app.qmd`
- Modify: `quarto/web-callbacks.qmd`
- Modify: `quarto/web-components.qmd`

**Interfaces:**
- Consumes: Quarto markdown documentation in `quarto/`
- Produces: Crisp, technical reference pages with direct explanations

- [ ] **Step 1: Scan Quarto documentation for AI patterns**

Run:
```bash
grep -rnE "(robust|comprehensive|seamlessly|leverage|orchestrated via|serves as|delve|intricate)" quarto/
```
Expected: Multiple matches across architecture, auth, models, and analytics chapters.

- [ ] **Step 2: Rewrite `quarto/architecture.qmd` and `quarto/auth.qmd`**

- In `quarto/architecture.qmd`: Change `The application environment is orchestrated via docker-compose.yml` to `Docker Compose runs the application stack`.
- In `quarto/auth.qmd`: Change `StashStats leverages HTTP Basic Auth with dual-account switching support` to `StashStats uses HTTP Basic Auth and supports switching between dev and prod accounts`.

- [ ] **Step 3: Rewrite `quarto/models-*.qmd` and `quarto/analytics-*.qmd`**

- In `quarto/models-overview.qmd`: Change `StashStats implements a comprehensive schema of Pydantic V2 models to validate incoming JSON structures...` to `StashStats uses Pydantic v2 models to validate JSON payloads and normalize nested Ravelry responses.`
- Cut throat-clearing intro sentences and generic summary headers across analytics docs.

- [ ] **Step 4: Rewrite `quarto/client-*.qmd` and `quarto/web-*.qmd`**

- Clean up RavelryClient endpoint descriptions and Dash callback documentation to be concise and direct.

- [ ] **Step 5: Verify Quarto pages**

Run:
```bash
grep -rnE "(robust|comprehensive|seamlessly|leverage|serves as|delve|intricate)" quarto/ --exclude="*.css" || echo "CLEAN"
```
Expected: "CLEAN".

- [ ] **Step 6: Commit**

```bash
git add quarto/
git commit -m "docs(quarto): de-AI documentation chapters and reduce wordiness"
```

---

### Task 4: Architecture, Reference, and Research Notes (`docs/` & `docs/notes/`)

**Files:**
- Modify: `docs/architecture.md`
- Modify: `docs/plans/*.md`
- Modify: `docs/reference/*.md`
- Modify: `docs/reviews/stash_stats_code_review.md`
- Modify: `docs/user_problem_discoveries.md`
- Modify: `docs/notes/*.md` (33 Ravelry API research notes)
- Modify: `docs/wiki/*.md`

**Interfaces:**
- Consumes: Markdown reference materials and research notes
- Produces: Streamlined, factual documentation devoid of corporate brochure tone

- [ ] **Step 1: Scan `docs/` for high-density AI patterns and promotional language**

Run:
```bash
grep -rnE "(serves as a comprehensive|robust REST API|vibrant ecosystem|incredibly robust|deeply specified|commercial anchors|delve)" docs/ | head -n 30
```
Expected: Frequent occurrences of brochure language and copula avoidance in `docs/notes/`.

- [ ] **Step 2: Rewrite `docs/notes/*.md` introductory paragraphs**

- In `docs/notes/API Features.md`: Replace `The Ravelry API serves as a comprehensive gateway to one of the world's largest community-driven databases... platform now offers a robust REST API that supports a diverse ecosystem...` with `The Ravelry REST API provides endpoints for searching patterns, managing yarn inventory, tracking projects, and accessing user data.`
- In `docs/notes/Brands and Shops.md`: Replace `Brands and Shops function as the real-world commercial anchors of the Ravelry Yarn Database, bridging the gap...` with `Brands and Shops represent manufacturers and retail stores in the Ravelry database.`
- In `docs/notes/Pattern Data.md`: Replace `enables an incredibly robust search engine` with `supports filtered search`.

- [ ] **Step 3: Rewrite `docs/plans/`, `docs/reference/`, `docs/reviews/`, and `docs/wiki/`**

- Strip throat-clearing, redundant bold headers, and empty filler phrases.
- Convert passive constructions to direct active voice.

- [ ] **Step 4: Verify `docs/` directory is clean**

Run:
```bash
grep -rnE "(robust REST API|vibrant ecosystem|incredibly robust|commercial anchors|serves as a comprehensive)" docs/ || echo "CLEAN"
```
Expected: "CLEAN".

- [ ] **Step 5: Commit**

```bash
git add docs/
git commit -m "docs: strip promotional AI writing from reference guides and research notes"
```

---

### Task 5: Python Source Code & Test Suite Docstrings

**Files:**
- Modify: `src/stashstats/**/*.py`
- Modify: `tests/**/*.py`

**Interfaces:**
- Consumes: Python module, class, and method docstrings
- Produces: Precise PEP 257 docstrings without filler or conversational fluff

- [ ] **Step 1: Audit docstrings in `src/stashstats/` and `tests/`**

Run:
```bash
find src/ tests/ -name "*.py" -exec grep -HnE "(robust|comprehensive|seamlessly|leverage|serves as|helper to allow|responsible for)" {} +
```
Expected: Identified wordy docstrings across analytics, client, and web callbacks.

- [ ] **Step 2: Streamline docstrings in `src/stashstats/`**

Refactor docstrings to single-line or concise imperative format:
- `src/stashstats/analytics/distributions.py`:
  - Before: `"""Composite distributions breakdown for a user's stash."""`
  - After: `"""Categorical distributions for a user stash."""`
- `src/stashstats/analytics/projects.py`:
  - Before: `"""Stash and project yarn consumption analytics and correlation calculator."""`
  - After: `"""Correlates project yarn usage with stash inventory."""`

- [ ] **Step 3: Run pytest and ruff to confirm no code breakage or lint regression**

Run:
```bash
uv run ruff check src/ tests/
uv run --all-extras pytest
```
Expected: All 381 tests pass; 0 lint errors.

- [ ] **Step 4: Commit**

```bash
git add src/ tests/
git commit -m "refactor(docstrings): simplify Python docstrings to direct technical English"
```

---

### Task 6: Automated De-AI & Anti-Slop Verification Script

**Files:**
- Create: `scripts/check_anti_slop.py`
- Modify: `pyproject.toml` or `README.md` (document check command)

**Interfaces:**
- Consumes: Entire repository text files (`.md`, `.qmd`, `.py`)
- Produces: Deterministic CLI linter that flags high-frequency AI slop tokens and fails CI if detected

- [ ] **Step 1: Write failing test / script for anti-slop linter**

Create `scripts/check_anti_slop.py`:
```python
"""Script to verify documentation and code are free from high-frequency AI slop."""
import re
import sys
from pathlib import Path

BANNED_WORDS = [
    r"\brobust\b",
    r"\bcomprehensive\b",
    r"\bseamlessly\b",
    r"\bleverage\b",
    r"\bdelve\b",
    r"\bpivotal\b",
    r"\btapestry\b",
    r"\btestament\b",
    r"\bvibrant\b",
    r"\bnestled\b",
    r"\bgroundbreaking\b",
    r"\belevate\b",
    r"\bserves as a\b",
    r"\bstands as a\b",
]

TARGET_DIRS = ["conductor", "quarto", "docs", "src", "tests"]
TARGET_EXTS = {".md", ".qmd", ".py"}

def main() -> int:
    pattern = re.compile("|".join(BANNED_WORDS), re.IGNORECASE)
    violations = 0

    for directory in TARGET_DIRS:
        for path in Path(directory).rglob("*"):
            if path.suffix not in TARGET_EXTS or ".venv" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for line_no, line in enumerate(text.splitlines(), 1):
                matches = pattern.findall(line)
                if matches:
                    print(f"{path}:{line_no}: Found AI slop pattern {matches}: {line.strip()[:80]}")
                    violations += len(matches)

    if violations > 0:
        print(f"\nTotal AI slop violations found: {violations}")
        return 1
    print("All documentation and code files are clean of AI slop.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run script to verify clean state across codebase**

Run:
```bash
python3 scripts/check_anti_slop.py
```
Expected: `All documentation and code files are clean of AI slop.` (exit code 0).

- [ ] **Step 3: Run full test suite and lint checks**

Run:
```bash
uv run ruff check src/ tests/ scripts/
uv run --all-extras pytest
```
Expected: 381 passed, all checks green.

- [ ] **Step 4: Commit**

```bash
git add scripts/check_anti_slop.py
git commit -m "ci: add automated anti-slop linter script"
```

