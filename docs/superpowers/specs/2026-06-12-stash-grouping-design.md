# Design Spec: Stash Items Grouping by Yarn

Group Ravelry stash entries by yarn product (brand + name) in Personal Stash view, using an accordion interface to show colorways inside.

## 1. Context & Goals
Currently, Personal Stash tab renders each Ravelry stash item (representing one colorway/dye lot) as a standalone card. Users with multiple colorways of the same yarn see many separate cards, making browsing difficult.
Goal: Group stash items by unique yarn brand and name using a clean accordion interface.

## 2. Technical Approach
- **UI-level Grouping**: Maintain flat structure in data layer (`Model.get_stash_list()`) to avoid breaking database delta tracking and analytics. Group items during rendering in `app_controller.py`.
- **Grouping Key**: `(yarn_company_name, yarn_name)`.
  - Brand: `s.get("yarn", {}).get("yarn_company_name") or "Unknown Brand"`
  - Name: `s.get("yarn", {}).get("name") or s.get("name") or "Unnamed Yarn"`
- **Accordion Integration**: Use `dbc.Accordion` and `dbc.AccordionItem`.
- **Edit Modal Compatibility**: Render the same pattern-matching input components (`dcc.Store` and `dbc.Button` for editing) inside each colorway row to keep the edit modal callbacks functional.

## 3. UI Design Specifications
- **Accordion Header**:
  - Thumbnail: Tiny rounded image (40x40px, `object-fit: cover`) using the first available photo from any colorway in the group.
  - Title: `Brand - Yarn Name` (e.g. `Malabrigo - Rios`).
  - Summary badge: E.g., `3 colorways | 12.0 skeins | 2,400 yds` (summed totals for yards/meters/skeins/grams).
- **Accordion Body**:
  - Render list of rows, one per colorway/stash item.
  - Each row contains:
    - Left: Colorway name, dye lot, location.
    - Center: Quantity details (skeins, yards, meters, grams) + Status badge.
    - Right: Edit button.
    - Bottom (optional): Notes in italicized text.

## 4. Verification Plan
1. Open stash tab, verify yarns are grouped under accordions.
2. Search/filter, verify match on name, brand, or colorway displays correct grouped accordions.
3. Click edit on a colorway row, verify edit modal opens with correct pre-filled values.
4. Save edit, verify update propagates and stash lists refresh.
