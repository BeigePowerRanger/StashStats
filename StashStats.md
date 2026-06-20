---
aliases: []
tags: []
---

# StashStats

StashStats is a Dash-based web application for searching, tracking, and managing personal yarn stash data via the Ravelry API.

---

## TODOs

## Unprocessed


### UX / Features
- [ ] #TODO personal stash → edit entry modal → log usage: needs to show table of history of changes [priority:: medium]
- [x] #TODO #stashstats log usage modal in personal stash should have table of past changes underneath the save changes/ cancel boxes [priority:: low]
- [ ] #TODO Personal Stash → add delete button on accordion items[^1] and on colorways within the accordions [priority:: low]
	- [ ] also add ability to select multiple accordion items or colorways inside the modal
- [ ] #TODO Personal Stash → Edit Modal: editing text about entry may not be working correctly [priority:: medium]
- [ ] #TODO Sync notes from edit stash entry/ add stash entry (?) with notes thing on API [priority:: low]
- [ ] #TODO Yarn Search: when adding to stash from web app, the colorway is showing up as undefined when going to Personal Stash tab
	- [ ] info not showing up on ravelry correctly: skeins not showing up, various other 

### Analytics
- [ ] #TODO Stash Analytics Broken: probably just needs to be reworked [priority:: highest]
	- [ ] need use `dcc.Interval` object for live plot/stat update
	- [ ] plot needs better compatability with mobile browsers.

### Data / Cleanup
- [ ] #TODO Remove wool works wool city parenvale 8 ply with like 91 entries [priority:: low]
- [ ] #TODO don't need Needles/hooks [priority:: low]

### Ops / Tooling
- [ ] #TODO/agy setup notebooklm mcp server – two options: [notebooklm-mcp](https://github.com/PleasePrompto/notebooklm-mcp) or [ntoebooklm-mcp-server](https://github.com/moodRobotics/notebooklm-mcp-server). pick whichever one is "better" i.e. better/ more complete feature implementation, etc. [priority:: low]
- [ ] #TODO have jules review code and make suggestions on optimizations and improvements [priority:: low]

## Known Bugs / Active TODOs

### 🔴 Critical

- [x] #TODO **`Optional`/`List` not imported in `search_results.py:21`** — used in function signature but never imported. `NameError` at runtime on every search result render. Fix: `from typing import Optional, List`. [priority:: highest]
- [x] #TODO **`data['yarns']` no key guard in `model.py:75`** — if API returns `{}` or omits `yarns` key, raises `KeyError` before function can return `None`. Fix: use `data.get('yarns')` with guard. [priority:: highest]
- [x] #TODO **`os.getenv("USERNAME")` collides with Linux shell variable** — on Linux, `USERNAME` is set by the shell to the OS user (e.g. `thotsky`). If `.env` doesn't explicitly override it, Ravelry API calls silently hit wrong user's stash. Same issue in `app.py:341`, `model.py:84`, `model.py:210`. Fix: rename env var to `RAVELRY_USERNAME`. [priority:: highest]
- [x] #TODO **`MagicMock` imported after use in `tests/test_e2e.py:57`** — `MagicMock` used inside `mock_get` defined at line 57 but not imported until line 99 → `NameError` when mock is called. Fix: move import to top of test function. [priority:: highest]

### 🟡 Warnings

- [x] #TODO **Edit modal doesn't show yarn name** — modal title says "Edit Stash Entry" with no yarn identification. Fix: pass yarn name into `dcc.Store` data; display in modal header. [priority:: medium]
- [x] #TODO **First stash card may auto-open edit modal on tab load** — pattern-matched `n_clicks=None` check may fire on initial layout render. Fix: add `if not any(c for c in edit_clicks if c): raise PreventUpdate`. [priority:: medium]
- [x] #TODO **Stash list doesn't auto-refresh after edit** — must manually switch tabs and return. Fix: output to `stash-list-container` from save callback, or add `dcc.Interval`. [priority:: medium]
- [x] #TODO **Subtraction loop doesn't skip child packs** (`app.py:433-462` actually in `model.py`) — positive acquisition loop correctly skips `primary_pack_id is not None` packs, but the subtraction loop does not, double-counting yardage removed for multi-pack entries. [priority:: high]
- [x] #TODO **`search-category` State wired but ignored** (`app.py:239`) — category filter silently dropped in `handle_search`. Fix: pass to `CONTROLLER.search_yarn` or remove from callback inputs. [priority:: medium]
- [x] #TODO **`search-sort` value mismatch** — UI sends `"best_match"` but Ravelry API expects `"best"`. Fix: map UI value to API value before calling search. [priority:: medium]
- [x] #TODO **Project fetch not paginated** (`app.py:344`) — `projects/list.json` fetched with `page_size=100` only. Users with >100 projects miss older project dates. Fix: paginate like stash list. [priority:: high]
- [x] #TODO **Cache `updated_at` removed but `original_values`/`history` kept on invalidation** (`model.py:update_stash`) — after a write, `updated_at` sentinel removed so next fetch re-fetches details, but the _new_ pack totals are then compared against the existing cached packs (stale), generating a spurious zero-or-wrong delta. Fix: also zero out `packs` in cache on invalidation. [priority:: high]
- [x] #TODO **`time.sleep(0.2)` in ThreadPoolExecutor doesn't serialize requests** (`model.py:129`) — 3 workers all sleep then burst simultaneously. Fix: use a threading `Semaphore` + sleep, or reduce `max_workers=1`. [priority:: medium]
- [x] #TODO ~**`stash_cache.json` not atomic write**~ (Obsolete: moving to Redis) [priority:: medium]
- [x] #TODO ~**`stash_cache.json` relative path**~ (Obsolete: moving to Redis) [priority:: medium]
- [x] #TODO ~**`stash_cache.json` grows unboundedly**~ (Obsolete: moving to Redis) [priority:: medium]
- [x] #TODO **`stash_post.py` schema unused** — `StashPost`/`PackPost` defined but `create_stash` builds raw dicts. Fix: validate payload against schema before POST. [priority:: medium]
- [x] #TODO **`memory-output` Store dead code** — `dcc.Store(id='memory-output')` in layout, no callbacks use it. Remove. [priority:: medium]
- [x] #TODO **`btn_ids` / `store_data_list` ordering assumption** (`app.py:943`) — assumes 1:1 DOM order between `ALL` pattern outputs. Not guaranteed on dynamic add/remove. Low risk currently but could silently populate wrong entry's modal data. [priority:: medium]
- [x] #TODO **`payload = {"pack": {"skeins": remaining}}` partial pack update** (`app.py:1051`) — sends only skeins; verified valid for primary pack via `POST stash`. Need to build `PUT /packs/{pack_id}.json` endpoint if supporting secondary pack updates. [priority:: high]
- [x] #TODO **History event bare key access** (`app.py:474` actually in `model.py`) — `event["date"]`, `event["yards"]` etc. crash on malformed history entries. `except Exception: pass` silently swallows — data lost without trace. Fix: use `.get()` with explicit skip + log. [priority:: high]
- [x] #TODO **`yarn.py:71` `v['name']` no guard** — `KeyError` if API returns company dict without `name` key. Fix: `v.get('name', '')`. [priority:: high]
- [x] #TODO **`dash_server` test fixture strips environment** (`tests/test_e2e.py:12`) — `env` dict fully replaces env; PATH missing; subprocess may fail to find shared libs. Fix: `{**os.environ, "API_USERNAME": …, …}`. [priority:: medium]
- [x] #TODO **`test_stash_yarn_flow` is a no-op** (`tests/test_e2e.py:29`) — body is `pass`, silently passes with no assertions. Fix: implement or `pytest.mark.skip`. [priority:: medium]

### 🔵 Minor

- [ ] #TODO **`sorted(set(…))` order in `yarn.py:53`** — `list(set(sorted(…)))` destroys sort order (`set` is unordered). Fix: `sorted(set([c['name'] for c in v]))`. [priority:: low]
- [ ] #TODO **`random.choice(v)` for photo selection** (`yarn.py:65`) — non-deterministic; different photo shown each render. Fix: `v[0]` for consistency. [priority:: low]
- [ ] #TODO **`dev_changes.log` always-on** — should be gated by `DEV_LOGGING=1` env var for production. [priority:: low]
- [ ] #TODO **`0.9144` yards-to-meters constant duplicated** — appears in 5+ places across `app.py` and `model.py`. Extract to module-level constant. [priority:: low]
- [ ] #TODO **`if photos and len(photos) > 0`** (`app.py:792`) — `len > 0` redundant. Use `if photos`. [priority:: low]
- [ ] #TODO **Test `time.sleep(3)` flaky on slow CI** — use retry poll loop instead. [priority:: low]
- [x] #TODO ~**E2E tests lack cache cleanup between runs**~ (Obsolete: moving to Redis) [priority:: low]
- [x] #TODO **No tests for edit modal, Log Usage, or `update_stash`** — entire write path untested. (Edit modal tested, Log Usage pending) [priority:: low]

---

## Implementation Plans

### Optimization & Tech Debt Plan

## 1. Class-Based OOP & Architecture Refactoring
**Problem:** `app_controller.py` (29KB) and `model.py` (47KB) too big. Logic tangled. Pydantic schemas defined but ignored. Code format inconsistent.
**Plan:**
*   **Formatter:** Run code through Black to enforce standard Python format.
*   **Service Layer:** Extract API logic from `model.py` into focused services (`YarnService`, `StashService`, `AnalyticsService`).
*   **Repository Pattern:** Wrap Ravelry API and storage in `StashRepository`. Replace `stash_cache.json` file storage with Redis (already in docker compose stack) for fast, safe caching.
*   **Component Classes:** Break `app_controller.py` into discrete Dash component classes (e.g. `StashTab`, `SearchTab`).
*   **Strict Pydantic Enforcement:** Use existing schemas (like `stash_post.py`) to validate all API payloads before sending. Reject raw dicts.

## 2. Technical Debt & Code Quality
**Problem:** Hardcoded logic, missing guards, duplicated code, dead code.
**Plan:**
*   **Fix Critical Bugs:** Add guards for `KeyError`s (`data['yarns']`, `v['name']`), fix Linux `USERNAME` env var collision (`RAVELRY_USERNAME`).
*   **DRY Code:** Extract duplicated constants (like `0.9144` yards-to-meters) to a `config/constants.py` file.
*   **Clean Up:** Remove dead code (e.g., `memory-output` Store). Fix unused imports (`Optional/List` in `search_results.py`).
*   **Safe Access:** Replace bare key access on history events with `.get()` to prevent silent crashes.

## 3. Performance & Optimizations
**Problem:** Unbounded cache growth, bad thread sleeping, pagination missing.
**Plan:**
*   **Concurrency Fix:** Replace `time.sleep(0.2)` in `ThreadPoolExecutor` with a rate-limiting `Semaphore` or token bucket.
*   **Cache Management:** Connect to Redis container. Migrate cache logic from JSON file to Redis. Clean up orphaned stash entries to prevent unbounded growth.
*   **Pagination:** Add pagination to Project fetch (currently max 100). Implement virtual scrolling or pagination for the main Stash List UI.

## 4. Testing Quality
**Problem:** Write paths untested. Mocking issues.
**Plan:**
*   **Fix Mocking:** Move `MagicMock` import to top of `test_e2e.py` to fix `NameError`.
*   **Test Coverage:** Add unit tests for write paths (`update_stash`, Log Usage math).
*   **Test Environment:** Fix `dash_server` fixture to keep `os.environ` so PATH is preserved. Clean up `stash_cache.json` between E2E test runs to ensure determinism.


---

### Warnings Fix Plan

Plan broken into 4 phases. High risk data stuff first. UI stuff second.

## Phase 1: API & Data Integrity (High Risk)
1. **Fix KeyError Risks:** Update `yarn.py:71` to use `v.get('name', '')`.
	- [x] Fixed: Swapped `v['name']` to `v.get('name', '')` in `yarn.py` to prevent crash on missing names.
2. **Safe History Parsing:** Update `app.py:474` to use `.get()` on history events. Skip + log bad entries. Don't let bare keys crash the app.
	- [x] Fixed: Swapped bare keys `event['date']` and `event['yards']` to `.get()` with safe defaults in `model.py`.
3. **Fix Subtraction Loop:** Update `app.py:433-462`. Add `if pack.get('primary_pack_id') is not None: continue` to the subtraction loop so we don't double-count yards.
	- [x] Fixed: Added `if pack.get('primary_pack_id') is not None: continue` in `model.py` subtraction loop to stop double-counting yardage.
4. **Fix Partial Pack PUT:** Verify Ravelry API allows just `{"pack": {"skeins": X}}` without pack ID. If it needs ID, add it to payload.
	- [x] Verified: `{"pack": {"skeins": X}}` via POST is valid for primary packs. Secondary packs require new PUT endpoint (deferred).
5. **Thread Concurrency:** Replace `time.sleep(0.2)` in `model.py` ThreadPoolExecutor with a `threading.Semaphore(1)` to serialize hits and avoid Ravelry rate limits.
	- [x] Fixed: Replaced `time.sleep(0.2)` with `threading.Semaphore(1)` lock inside worker thread in `model.py`.

## Phase 2: Dash UI & Search Flow
1. [x] **Modal Auto-Open:** Add `if not any(c for c in edit_clicks if c): raise PreventUpdate` to `toggle_edit_modal` so it ignores layout load.
	- Added `any(c for c in edit_clicks if c)` check in `app.py` wrapper callback.
2. [x] **Modal Yarn Name:** Pass yarn name into the modal's `dcc.Store` data payload. Show it in the header.
	- Stored `name` in `edit-stash-id-store` payload and rendered in header.
3. [x] **Search Filters:** Pass `search-category` value to API request. Map UI `"best_match"` sort value to `"best"` for API.
	- Passed category parameter to model and mapped `best_match` to `best`.
4. [x] **Auto-Refresh:** After save callback completes, fire a `dcc.Interval` or push data to `stash-list-container` to force re-render.
	- Save callback outputs directly to `stash-list-container`.
5. [x] **Dead Code:** Delete `memory-output` `dcc.Store` and remove from layout.
	- Removed `memory-output` `dcc.Store` from layout.

## Phase 3: Pagination & Cache Logic
1. [x] **Project Pagination:** Wrap `projects/list.json` fetch in a loop. Paginate until `page_results` is 0.
	- Projects are already paginated using loop logic in `get_projects_list` and `get_project_map`.
2. [x] **Cache Spurious Delta:** In `model.py:update_stash`, when nuking `updated_at`, also `pop('packs', None)` from cache. Prevents stale packs causing fake deltas.
	- `update_stash` deletes the entire `stash_detail:{stash_id}` cache key in Redis, zeroing out cached packs on invalidation.
3. [x] **Schema Enforcement:** Use `StashPost` / `PackPost` Pydantic models to construct payload instead of raw dicts.
	- Enforced `StashPost` validation in `create_stash` and `update_stash`.

## Phase 4: Test Infra
1. [x] **Fix Environment Drop:** Update `dash_server` fixture to pass `{**os.environ, ...}` instead of wiping PATH.
	- Obsolete; replaced by `dash_thread_server` fixture which runs Dash in-process, retaining full environment variables naturally.
2. [x] **Write E2E Test:** Implement `test_stash_yarn_flow` (currently `pass`).
	- Replaced by `test_stash_yarn_flow_thread` which is fully implemented with Playwright.




# Ravelry Notes

![[NotebookLM Mind Map.png]]

- [[Platform Features]] 
	- [[Pattern Data]]
		- [[Search and Metadata]]
		- [[Categories and Attributes]]
		- [[Designer Information]]
		- [[Pattern Sources]]
	- [[Yarn Database]]
		- [[Weight and Thickness]]
		- [[Fiber Composition]]
		- [[Color Families]]
		- [[Brands and Shops]]
	- [[User Content]]
		- [[Personal Notebook]]
		- [[Project Tracking]]
		- [[Yarn Stash]]
		- [[Queue and Favorites]]
	- [[Authentication]]
		- [[Ravelry Basic HTTP Auth|Basic HTTP Auth]]
		- [[Ravelry OAuth 2.0|OAuth 2.0]]
		- [[Ravelry Security and Setup|Security & Setup]]
	- [[SDKs and Libraries]]
		- [[ravelRy]]
			- [[Ravelry search_patterns Function|search_patterns()]]
			- [[Ravelry get_yarns Function|get_yarns()]]
			- [[Ravelry ravelry_auth Function|ravelry_auth()]]
		- [[Ravelry Python Ecosystem|Python Ecosystem]]
			- [[Ravelry Knotion Library|Knotion library]]
			- [[Ravelry Flask-FastAPI Integration|Flask/FastAPI Integration]]
			- [[Ravelry Reticulate Bridge|Reticulate Bridge]]
		- [[Ravelry PHP and Go|PHP & Go]]
		- [[Ravelry Kotlin and Android|Kotlin & Android]]
	- [[Ravelry Mobile Ecosystem|Mobile Ecosystem]]
	- [[Ravelry Technical Architecture|Technical Architecture]]
		- [[Ravelry Endpoint Design|Endpoint Design]]
		- [[Ravelry Operational Safety|Operational Safety]]
		- [[Ravelry Troubleshooting|Troubleshooting]]
