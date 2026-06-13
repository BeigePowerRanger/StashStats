# Stash Items Grouping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Group stash items on the Personal Stash page by unique yarn brand and name using a clean, interactive accordion interface.

**Architecture:** UI-level grouping in `app_controller.py` to keep the data model layer (`model.py`) flat. The rendering logic delegates to `stash_card.py` which will build `dbc.AccordionItem` objects containing nested colorway rows with their own edit stores and buttons.

**Tech Stack:** Python, Dash, Dash Bootstrap Components (DBC).

---

### Task 1: Add Accordion Rendering Methods to StashCard

**Files:**
- Modify: `stashies/components/stash_card.py`
- Test: `tests/test_stash_grouping.py`

- [ ] **Step 1: Define create_colorway_row and create_grouped_accordion_item methods**

Replace the end of the `StashCard` class with `create_colorway_row` and `create_grouped_accordion_item`.

Modify `stashies/components/stash_card.py` (add these methods after `create_card`):
```python
    def create_colorway_row(self, s: Dict[str, Any], totals: Dict[str, float]) -> html.Div:
        """
        Build a single row layout for a specific colorway of a yarn.
        - Input:
            - s (dict): Raw stash entry from Ravelry API.
            - totals (dict): Calculated totals dictionary.
        - output: html.Div containing the colorway row layout.
        """
        status = s.get("stash_status") or {}
        status_name = status.get("name") or "Unknown"
        status_id = status.get("id") or 1
        badge_color = self.STASH_STATUS_COLORS.get(status_id, "success")

        y = totals.get("yards", 0.0)
        m = totals.get("meters", 0.0)
        sk = totals.get("skeins", 0.0)
        g = totals.get("grams", 0.0)

        is_fiber = s.get("type") == "fiber"
        if is_fiber:
            qty_text = f"{g:,.0f} g"
            if y > 0:
                qty_text += f" ({y:,.0f} yds / {m:,.0f} m)"
            quantity_element = html.Span([html.Strong("Weight: "), qty_text])
        else:
            quantity_element = html.Span([html.Strong("Qty: "), f"{sk:.1f} sk ({y:,.0f} yds / {m:,.0f} m / {g:,.0f} g)"])

        stash_id_str = str(s.get("id", ""))
        edit_btn = dbc.Button(
            [html.I(className="bi bi-pencil-fill me-1"), "Edit"],
            id={"type": "stash-edit-btn", "index": stash_id_str},
            color="outline-success",
            size="sm",
            className="ms-2",
            style={"padding": "2px 8px", "fontSize": "0.8rem"}
        )

        item_store = dcc.Store(
            id={"type": "stash-data-store", "index": stash_id_str},
            data={
                "id": s.get("id"),
                "name": s.get("name") or s.get("yarn", {}).get("name") or "Unnamed Yarn",
                "colorway": s.get("colorway_name") or "",
                "dye_lot": s.get("dye_lot") or "",
                "location": s.get("location") or "",
                "notes": s.get("notes") or "",
                "skeins": sk,
                "status_id": status_id,
            }
        )

        row_content = dbc.Row(
            [
                dbc.Col(
                    [
                        html.Span(s.get("colorway_name") or "Not specified", className="fw-bold text-success me-2"),
                        html.Span(f"Dye Lot: {s.get('dye_lot')}", className="text-muted small me-2") if s.get("dye_lot") else None,
                        html.Span(f"Loc: {s.get('location')}", className="text-muted small") if s.get("location") else None,
                    ],
                    xs=12, md=6,
                    className="d-flex align-items-center flex-wrap"
                ),
                dbc.Col(
                    [
                        quantity_element,
                        html.Span(status_name, className=f"badge bg-{badge_color} ms-2 text-white"),
                        edit_btn
                    ],
                    xs=12, md=6,
                    className="d-flex align-items-center justify-content-md-end mt-2 mt-md-0"
                )
            ],
            className="py-2 align-items-center"
        )

        notes_content = None
        if s.get("notes"):
            notes_content = dbc.Row(
                dbc.Col(
                    html.P(s.get("notes"), className="text-muted small mb-0 ps-3 border-start border-secondary"),
                    width=12
                ),
                className="pb-2"
            )

        return html.Div(
            [
                item_store,
                row_content,
                notes_content,
                html.Hr(className="my-1 border-secondary")
            ],
            className="colorway-row px-2"
        )

    def create_grouped_accordion_item(
        self,
        brand: str,
        name: str,
        items_with_totals: List[tuple],
        combined_totals: Dict[str, float]
    ) -> dbc.AccordionItem:
        """
        Build a single AccordionItem grouping all colorways/items of a specific yarn product.
        - Input:
            - brand (str): Yarn manufacturer/brand.
            - name (str): Yarn product name.
            - items_with_totals (list[tuple]): List of (raw_stash_dict, totals_dict) pairs.
            - combined_totals (dict): Summed totals for yards, meters, skeins, grams.
        - output: dbc.AccordionItem containing the grouped list.
        """
        # Find first available photo in any colorway/yarn
        photo_url = None
        for s, _ in items_with_totals:
            yarn_info = s.get("yarn") or {}
            photos = s.get("photos") or yarn_info.get("photos") or []
            if not photos and yarn_info.get("first_photo"):
                photos = [yarn_info.get("first_photo")]
            for p in photos:
                url = p.get("medium_url") or p.get("square_url") or p.get("small_url") or p.get("thumbnail_url")
                if url:
                    photo_url = url
                    break
            if photo_url:
                break

        thumbnail = html.Img(
            src=photo_url,
            style={
                "height": "35px",
                "width": "35px",
                "borderRadius": "4px",
                "objectFit": "cover",
                "marginRight": "12px",
                "border": "1px solid #444"
            }
        ) if photo_url else html.Div(
            style={
                "height": "35px",
                "width": "35px",
                "borderRadius": "4px",
                "backgroundColor": "#333",
                "marginRight": "12px",
                "border": "1px solid #444"
            }
        )

        badge_text = f"{len(items_with_totals)} items | {combined_totals['skeins']:.1f} sk"
        if combined_totals["yards"] > 0:
            badge_text += f" | {combined_totals['yards']:,.0f} yds"
        elif combined_totals["grams"] > 0:
            badge_text += f" | {combined_totals['grams']:,.0f} g"

        summary_badge = dbc.Badge(
            badge_text,
            color="success",
            className="ms-auto me-3 text-white small"
        )

        header_layout = html.Div(
            [
                thumbnail,
                html.Span(f"{brand} — {name}", className="fw-bold text-white me-auto"),
                summary_badge
            ],
            className="d-flex align-items-center w-100"
        )

        rows = []
        for s, totals in items_with_totals:
            rows.append(self.create_colorway_row(s, totals))

        # Remove the final trailing <hr> from the last row
        if rows:
            rows[-1].children.pop()

        return dbc.AccordionItem(
            html.Div(rows, className="bg-dark text-white rounded p-1"),
            title=header_layout,
            item_id=f"group-{brand}-{name}".replace(" ", "_")
        )
```

- [ ] **Step 2: Verify code syntax by running a quick syntax check**

Run: `python -m py_compile stashies/components/stash_card.py`
Expected: Successful compile with exit code 0.

- [ ] **Step 3: Commit additions**

Run:
```bash
git add stashies/components/stash_card.py
git commit -m "feat: add grouped accordion card rendering methods to StashCard"
```

---

### Task 2: Modify AppController to Group Stash List and Render Accordion

**Files:**
- Modify: `stashies/app_controller.py:226-259`
- Test: `tests/test_stash_grouping.py`

- [ ] **Step 1: Implement grouping in render_stash_cards**

Replace `render_stash_cards` in `stashies/app_controller.py` to group stashes by Brand and Name, compute totals, and build the accordion layout.

Modify `stashies/app_controller.py` from line 226 to 259:
```python
    def render_stash_cards(self, query: Optional[str]) -> List[dbc.Col]:
        """
        Filter, group by yarn, and render stash accordion list.
        - Input:
            - query (str | None): Search query for stash filtration.
        - output: List of dbc.Col containing the single accordion container.
        """
        stash_list = self.MODEL.get_stash_list()
        if not stash_list:
            return [html.Div("No stashed yarns found or API request failed.", className="text-warning mt-3")]

        filtered = stash_list
        if query:
            q = query.lower()
            filtered = []
            for s in stash_list:
                name = (s.get("name") or "").lower()
                yarn_info = s.get("yarn") or {}
                brand = (yarn_info.get("yarn_company_name") or "").lower()
                colorway = (s.get("colorway_name") or "").lower()
                if q in name or q in brand or q in colorway:
                    filtered.append(s)

        if not filtered:
            return [html.Div("No matching stash entries found.", className="text-info mt-3 ms-2")]

        # Group by (brand, name)
        grouped_data = {}
        from .model import get_primary_totals
        for s in filtered:
            yarn_info = s.get("yarn") or {}
            brand = yarn_info.get("yarn_company_name") or "Unknown Brand"
            name = yarn_info.get("name") or s.get("name") or "Unnamed Yarn"
            key = (brand, name)
            
            packs = s.get("packs") or []
            totals = get_primary_totals(packs, yarn_info)
            
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((s, totals))

        accordion_items = []
        for (brand, name), items in grouped_data.items():
            # Calculate combined totals
            comb_t = {"yards": 0.0, "meters": 0.0, "skeins": 0.0, "grams": 0.0}
            for _, totals in items:
                comb_t["yards"] += totals.get("yards") or 0.0
                comb_t["meters"] += totals.get("meters") or 0.0
                comb_t["skeins"] += totals.get("skeins") or 0.0
                comb_t["grams"] += totals.get("grams") or 0.0

            accordion_item = self.STASH_CARD.create_grouped_accordion_item(
                brand=brand,
                name=name,
                items_with_totals=items,
                combined_totals=comb_t
            )
            accordion_items.append(accordion_item)

        # Wrap in a single accordion container
        accordion = dbc.Accordion(
            accordion_items,
            flush=True,
            always_open=True,
            className="border border-secondary rounded overflow-hidden"
        )
        return [dbc.Col(accordion, width=12)]
```

- [ ] **Step 2: Verify syntax compile**

Run: `python -m py_compile stashies/app_controller.py`
Expected: Successful compile with exit code 0.

- [ ] **Step 3: Commit modifications**

Run:
```bash
git add stashies/app_controller.py
git commit -m "feat: group stash items and render as accordion in AppController"
```

---

### Task 3: Write and Run Unit Tests for Grouping

**Files:**
- Create: `tests/test_stash_grouping.py`

- [ ] **Step 1: Write tests verifying grouping logic**

Create `tests/test_stash_grouping.py` with mock stashes sharing the same yarn to ensure they group correctly under a single AccordionItem.

Write to `tests/test_stash_grouping.py`:
```python
from unittest.mock import MagicMock
import dash_bootstrap_components as dbc
from dash import html
from stashies.app_controller import AppController

def test_render_stash_cards_grouping():
    # Setup controller with mocked model
    controller = AppController(header_id="h", search_id="s", result_id="r")
    controller.MODEL = MagicMock()
    
    # Mock two stash items sharing the same yarn brand and name
    mock_stash = [
        {
            "id": 1,
            "name": "Yarn A",
            "colorway_name": "Colorway 1",
            "stash_status": {"id": 1, "name": "Active"},
            "yarn": {
                "name": "Yarn A",
                "yarn_company_name": "Brand X",
            },
            "packs": [{"skeins": 2.0, "total_yards": 400.0, "total_grams": 100.0}]
        },
        {
            "id": 2,
            "name": "Yarn A",
            "colorway_name": "Colorway 2",
            "stash_status": {"id": 1, "name": "Active"},
            "yarn": {
                "name": "Yarn A",
                "yarn_company_name": "Brand X",
            },
            "packs": [{"skeins": 1.0, "total_yards": 200.0, "total_grams": 50.0}]
        }
    ]
    
    controller.MODEL.get_stash_list.return_value = mock_stash

    # Render stash cards list
    cols = controller.render_stash_cards(query=None)
    
    assert len(cols) == 1
    col = cols[0]
    accordion = col.children
    
    # Verify we got a dbc.Accordion containing a single AccordionItem
    assert isinstance(accordion, dbc.Accordion)
    assert len(accordion.children) == 1
    
    item = accordion.children[0]
    assert isinstance(item, dbc.AccordionItem)
    
    # Verify the body has two colorway rows + stores
    body = item.children
    assert isinstance(body, html.Div)
    # Each row is a html.Div containing Store, Row, Notes, Hr (4 elements in row)
    assert len(body.children) == 2
```

- [ ] **Step 2: Run pytest to verify grouping unit test passes**

Run: `docker exec stashstats-web-1 pytest tests/test_stash_grouping.py -v` (since we are using Docker containers, or run locally via `.venv/bin/pytest tests/test_stash_grouping.py -v`)
Expected: `test_render_stash_cards_grouping` PASS.

- [ ] **Step 3: Run full test suite to ensure no regressions**

Run: `docker exec stashstats-web-1 pytest -v` (or run locally: `.venv/bin/pytest -v`)
Expected: All tests pass.

- [ ] **Step 4: Commit tests**

Run:
```bash
git add tests/test_stash_grouping.py
git commit -m "test: add unit test for stash grouping logic"
```
