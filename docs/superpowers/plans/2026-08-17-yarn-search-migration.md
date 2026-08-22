# Yarn Search Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the Yarn Search functionality of StashStats to use the new 2Stash2Stats backend architecture with Redis caching and SQLite reference data.

**Architecture:** We will copy the `stashstats` package from `2Stash2Stats` into the `StashStats` repository. We will then implement a Redis cache layer for yarn search operations, an SQLite store for static reference data, and wire up the Dash UI to utilize this new backend while removing PostgreSQL.

**Tech Stack:** Python 3.12, Dash, dash-bootstrap-components, httpx, Pydantic v2, Redis, SQLite.

## Global Constraints

- Must work in the `/home/thotsky/Vaults/CodeVault/RavelryCode/StashStats` directory.
- `2Stash2Stats` source is located at `/home/thotsky/Vaults/CodeVault/RavelryCode/2Stash2Stats`.
- No PostgreSQL dependencies or services.

---

### Task 1: Package Port & Infrastructure Setup

**Files:**
- Create: `src/stashstats/` (copied from `../2Stash2Stats/src/stashstats/`)
- Modify: `docker-compose.yml:23-48`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: The core `stashstats.client.RavelryClient` and Pydantic models ready for use in StashStats.

- [ ] **Step 1: Copy stashstats package**

```bash
mkdir -p src
cp -r ../2Stash2Stats/src/stashstats src/
```

- [ ] **Step 2: Remove PostgreSQL from docker-compose.yml**

```yaml
# In docker-compose.yml, remove the 'db' service, pgdata volume, and DATABASE_URL env var.
# Keep the 'cache' (redis) service and 'web' service.
```

- [ ] **Step 3: Update pyproject.toml dependencies**

```toml
# Merge dependencies from 2Stash2Stats into StashStats/pyproject.toml
# Add httpx, pydantic, pydantic-settings, redis.
# Remove psycopg2-binary.
```

- [ ] **Step 4: Commit**

```bash
git add src/stashstats docker-compose.yml pyproject.toml
git commit -m "chore: port 2Stash2Stats backend and drop postgres"
```

### Task 2: Redis Cache Layer for Yarn Search

**Files:**
- Create: `src/stashstats/cache.py`
- Modify: `src/stashstats/client.py`
- Create: `tests/test_cache.py`

**Interfaces:**
- Consumes: `redis.Redis` client.
- Produces: `get_cached_yarn_search` and `get_cached_yarn_details` methods in `RavelryClient`.

- [ ] **Step 1: Write failing test for cache behavior**

```python
# In tests/test_cache.py
def test_yarn_search_caching():
    # Write a test asserting that a second call to search_yarns hits the cache and avoids HTTP request.
    pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cache.py -v`
Expected: FAIL

- [ ] **Step 3: Implement Redis wrapper in cache.py**

```python
# src/stashstats/cache.py
import json
import os
import redis
from stashstats.models import YarnSearchResponse, YarnDetailResponse

def get_redis_client():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(redis_url, decode_responses=True)

# Add cache getters/setters for YarnSearchResponse
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cache.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/stashstats/cache.py src/stashstats/client.py tests/test_cache.py
git commit -m "feat: implement redis cache for yarn search"
```

### Task 3: SQLite Reference Data Store

**Files:**
- Create: `src/stashstats/reference_db.py`
- Modify: `src/stashstats/client.py`

**Interfaces:**
- Produces: SQLite-backed methods `get_yarn_weights`, `get_color_families`, `get_fiber_categories`.

- [ ] **Step 1: Write failing test for reference db**

```python
# In tests/test_reference_db.py
def test_sqlite_reference_population():
    # Test that calling get_yarn_weights populates SQLite if empty, then reads from it
    pass
```

- [ ] **Step 2: Implement SQLite reference DB**

```python
# src/stashstats/reference_db.py
import sqlite3
import json
from pathlib import Path

DB_PATH = Path("data/reference.db")

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS reference_data (key TEXT PRIMARY KEY, value TEXT)")
        
# Add get/set methods
```

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest tests/test_reference_db.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add src/stashstats/reference_db.py src/stashstats/client.py tests/test_reference_db.py
git commit -m "feat: add sqlite store for static reference data"
```

### Task 4: Port Dash Web App Yarn Search

**Files:**
- Modify: `app.py`
- Create: `src/stashstats/web/search_tab.py` (or adapt existing layout to replace old `stashies.app_controller`)

**Interfaces:**
- Consumes: `RavelryClient` with Redis caching.
- Produces: The Yarn Search layout and callbacks.

- [ ] **Step 1: Replace old search callbacks in app.py**

```python
# Remove old `from stashies.app_controller import AppController`
# Wire up `from stashstats.web.layouts.search import create_yarn_search_layout`
# Register search callbacks using `RavelryClient`.
```

- [ ] **Step 2: Verify UI visually or via Dash testing**

Run: `python app.py` (Verify the Yarn Search tab loads and queries Ravelry correctly).

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: wire yarn search tab to new api backend"
```

### Task 5: Clean Up Legacy StashStats Code

**Files:**
- Delete: `stashies/db.py`, `stashies/app_controller.py`, `stashies/model.py`, `stashies/base.py`, etc.
- Modify: `tests/` (Remove old postgres/db tests)

**Interfaces:**
- Removes obsolete files.

- [ ] **Step 1: Delete old legacy files**

```bash
rm -rf stashies/db.py stashies/model.py stashies/app_controller.py
rm -f tests/test_db*.py tests/test_mock_analytics.py
```

- [ ] **Step 2: Run test suite to ensure no lingering broken imports in active codebase**

Run: `pytest tests/ -v`

- [ ] **Step 3: Commit**

```bash
git add -u
git commit -m "refactor: remove legacy postgres and controller logic"
```
