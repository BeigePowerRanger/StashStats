# Specification: Web App Frontend — Core Shell & Personal Stash

## 1. Overview
Build the foundation of the modern StashStats web dashboard using **Dash + FastAPI** and **Dash Bootstrap Components (DBC)** with the **DARKLY** theme. This track implements the application shell, 4-tab navigation layout, the **Personal Stash** grouped accordion view, and the **Stash Edit & Usage Modal** based on `wiki/concepts/web-app-specification.md`.

## 2. Technical Stack & Architecture
- **Framework**: Dash 2.x with Dash Bootstrap Components (`dbc.themes.DARKLY`) served via FastAPI / ASGI.
- **Styling**: DBC Darkly theme matching `#222222` dark background, `#00bc8c` teal accents, and responsive layout containers.
- **Client Integration**: Direct integration with existing Pydantic client models (`stashstats.client.RavelryClient`, `StashItem`, `Pack`, `StashHistoryEntry`).
- **Caching Layer**: Modular cache interface (in-memory / local fallback), structured to connect to Redis when the Docker Compose stack is deployed in a subsequent track.
- **Code Layout**:
  - `src/stashstats/web/app.py` — Application factory and server configuration.
  - `src/stashstats/web/layouts/` — Page templates and tab containers.
  - `src/stashstats/web/components/` — Grouped stash accordion cards, edit/usage modal, metric badges.
  - `src/stashstats/web/callbacks/` — Reactive callbacks for search filtering, pagination, and modal mutations.

## 3. Functional Requirements

### 3.1 Global Header & Navigation Shell
- **Header**: StashStats branding, authenticated user badge (`@username` from `client.get_current_user()`), and last sync timestamp.
- **Tabs**: 4 navigation tabs (`Personal Stash` [Active], `Stash Analytics` [Placeholder/Stub], `Projects` [Placeholder/Stub], `Yarn Search` [Placeholder/Stub]).

### 3.2 View 1: Personal Stash (Grouped Accordion)
- **Top Controls**: "Sync Now" button with pending sync badge, live debounced search filter (yarn name, brand, colorway), and sort dropdown (Brand A-Z, Name A-Z, Quantity, Date Added).
- **Grouped Accordion Cards**: Group stash records by parent yarn (`[Brand] — [Yarn Product Name]`):
  - **Header**: Product thumbnail, aggregate badge (`X items | Y sk | Z yds`), and collapse/expand trigger.
  - **Expanded Rows**: Colorway name, dye lot, location (`Loc: ...`), formatted quantities (skeins, yards, meters, grams), status badge (`In stash`, `Used up`, `Gifted`, `Gone / Sold`), notes snippet, and an **[Edit]** action button.
- **Pagination**: 10 grouped parent yarns per page with Previous/Next and page number buttons.

### 3.3 View 2: Stash Edit & Usage Modal
- **Tab 1 (Edit Details)**: Modify colorway, dye lot, storage location, skein count, status dropdown, and notes.
- **Tab 2 (Log Usage & History Ledger)**:
  - Baseline display (`Originally stashed: YYYY-MM-DD (X sk / Y yds / Z g)`).
  - Skeins used input + date picker with real-time remaining preview (proportional length/weight math).
  - **Usage History Table**: Past deductions list with a **Delete** action that automatically restores deducted yarn quantities.
- **Modal Actions**: Delete Entry (confirmation dialog), Save Changes (persist + queue API update), and Cancel.

## 4. Non-Functional & Testing Requirements
- Unit and component tests for layout builders, group aggregators, sorting/filtering helpers, and callback logic in `tests/web/`.
- Clean linting (`ruff check .`) and formatting.

## 5. Out of Scope for Phase 1
- Full Stash Analytics timeseries/scatter charts (subsequent track).
- Projects showcase & Yarn Catalog Search ingestion (subsequent phases).
- Docker Compose and Redis container infrastructure setup (handled in dedicated Docker track).
