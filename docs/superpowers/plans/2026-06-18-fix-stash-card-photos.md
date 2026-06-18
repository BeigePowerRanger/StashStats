# Plan: Fix Card Accordion Photos

**Goal:** Ensure that yarn stash photos (stored in `first_photo` at the stash item root level) load correctly in the Personal Stash accordion header and card content.

---

### Task 1: Update Card Photo Extraction

**Files:**
- Modify: [stash_card.py](file:///home/thotsky/BrainVault/Projects/StashStats/stashies/components/stash_card.py)

- [x] **Step 1: Update create_card photo extraction**
  Modify lines 50-56 in `create_card` to check for `s.get("first_photo")` directly on the stash dictionary `s` before falling back to `yarn_info.get("photos")` or `yarn_info.get("first_photo")`.
  ```python
  photos = s.get("photos")
  if not photos:
      first_photo = s.get("first_photo")
      if first_photo:
          photos = [first_photo]
      else:
          photos = yarn_info.get("photos") or []
          if not photos and yarn_info.get("first_photo"):
              photos = [yarn_info.get("first_photo")]
  ```

- [x] **Step 2: Update create_grouped_accordion_item photo extraction**
  Modify lines 287-300 in `create_grouped_accordion_item` to also check for `s.get("first_photo")` directly on the stash dictionary `s`.
  ```python
  photo_url = None
  for s, _ in items_with_totals:
      yarn_info = s.get("yarn") or {}
      photos = s.get("photos")
      if not photos:
          first_photo = s.get("first_photo")
          if first_photo:
              photos = [first_photo]
          else:
              photos = yarn_info.get("photos") or []
              if not photos and yarn_info.get("first_photo"):
                  photos = [yarn_info.get("first_photo")]
      for p in photos:
          url = p.get("medium_url") or p.get("square_url") or p.get("small_url") or p.get("thumbnail_url")
          if url:
              photo_url = url
              break
      if photo_url:
          break
  ```

---

### Task 2: Verification

- [x] **Step 1: Run E2E tests**
  Command: `.venv/bin/pytest`
  Expected: PASS
- [x] **Step 2: Manual Check**
  Load the Personal Stash tab. Accordion items and card thumbnails should display their respective stash/yarn photos instead of falling back to default grey placeholders.
