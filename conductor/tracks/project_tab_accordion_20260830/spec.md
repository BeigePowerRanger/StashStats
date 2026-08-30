# Specification: Projects Tab Accordion Layout Refactor

## Overview
Refactor the Projects tab in StashStats to replace the flat card list with a grouped/collapsible accordion interface patterned after the Personal Stash tab. Add project filtering, sorting, pagination, and enriched project header metadata (photos, pattern names, status badges, progress badges).

## Functional Requirements
1. **Accordion Layout**:
   - Wrap project cards/items in a `dbc.Accordion` with `always_open=True` and `start_collapsed=True`.
   - Each project item has a clean header displaying:
     - Project thumbnail photo (from `first_photo.thumbnail_url` or `square_url`) or a fallback icon (`bi-folder2-open` or `bi-card-checklist`).
     - Project name and pattern name (e.g. `[Project Name] — [Pattern Name]` or styled together).
     - Status badge (e.g., "In progress", "Finished", "Hibernating", "Frogged") with contextual color coding.
     - Progress badge indicating percentage (`X%`).
   - Accordion item body displays:
     - Progress bar.
     - Project metadata chips (Craft type, Started date, Completed date, Tags).
     - PDF attachment dropzone, list of attached PDFs with view/delete actions, and inline PDF iframe viewer.

2. **Search & Filter**:
   - Search input (`projects-search-input`) with debounce and search button (`projects-search-btn`).
   - Case-insensitive filtering matching project title, pattern name, craft type, status name, or tags.

3. **Sort Options**:
   - Dropdown selector (`projects-sort-dropdown`) supporting:
     - Date Started / Added (Newest first) - `date_desc` (Default)
     - Project Name (A-Z) - `name_asc`
     - Progress (High-Low) - `progress_desc`
     - Status (A-Z) - `status_asc`

4. **Pagination**:
   - `dbc.Pagination` component (`projects-pagination`) with 10 projects per page.
   - Status text (`projects-pagination-info`) showing "Showing page X of Y (Z projects)".
   - Preserves active page clamped within valid range when filtering/sorting.

5. **State Management & Callbacks**:
   - Unified reactive callback updating the project list view on search, sort, page change, or data store sync.
   - Maintain full compatibility with PDF upload, deletion, viewing, and Ravelry manual sync callbacks.

## Acceptance Criteria
- [ ] Projects tab renders projects in a collapsible `dbc.Accordion` container.
- [ ] Project headers show thumbnail, title, pattern name, status badge, and progress badge.
- [ ] Expanding an accordion shows progress bar, metadata, and attached PDF controls.
- [ ] Search filter dynamically narrows down project items by keyword in name, pattern, craft, status, or tag.
- [ ] Sort dropdown reorders projects by date, name, progress, or status.
- [ ] Pagination controls paginate projects in sets of 10 and display accurate page counts.
- [ ] PDF upload, view, and delete capabilities remain fully functional inside accordion items.
- [ ] All unit and integration tests pass with >80% code coverage.
