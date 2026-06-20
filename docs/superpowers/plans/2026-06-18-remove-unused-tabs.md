# Plan: Remove Needles & Hooks and Queue Tabs

**Goal:** Remove the "Needles & Hooks" and "Queue" tabs from the main dashboard interface and clean up all related backend controllers, components, models, and callbacks.

---

### Task 1: Update App Layout & Controller

**Files:**
- Modify: [app_controller.py](file:///home/thotsky/BrainVault/Projects/StashStats/stashies/app_controller.py)

- [x] **Step 1: Remove tab layouts**
  Remove the `dcc.Tab` blocks for `Queue` (value="tab-queue") and `Needles & Hooks` (value="tab-needles") in the main layout creation.
- [x] **Step 2: Remove controller imports and instances**
  Remove references to `NeedlesComponent` and `QueueComponent` imports.
  Delete properties `self.NEEDLES` and `self.QUEUE` from class initialization.
- [x] **Step 3: Remove rendering helper methods**
  Delete the following methods from `app_controller.py`:
  - `render_needles_tab_layout`
  - `render_needles_list`
  - `render_queue_tab_layout`
  - `render_queue_list`
  - `handle_reposition_queue`
  - `handle_remove_queue`

---

### Task 2: Clean Up Component Files

**Files:**
- Delete: `stashies/components/needles.py`
- Delete: `stashies/components/queue.py`
- Modify: `stashies/components/__init__.py`

- [x] **Step 1: Delete Python component files**
  Delete the files `needles.py` and `queue.py` under the components directory.
- [x] **Step 2: Update components init imports**
  Remove `from .needles import NeedlesComponent` and `from .queue import QueueComponent` from the `__init__.py` module.

---

### Task 3: Clean Up App Callbacks

**Files:**
- Modify: [app.py](file:///home/thotsky/BrainVault/Projects/StashStats/app.py)

- [x] **Step 1: Remove needles & queue tab switch callbacks**
  Delete the following Dash callbacks:
  - `render_queue_tab`
  - `load_queue_list`
  - `render_needles_tab`
  - `load_needles_list`
  - `handle_queue_actions`

---

### Task 4: Clean Up API Model Methods

**Files:**
- Modify: [model.py](file:///home/thotsky/BrainVault/Projects/StashStats/stashies/model.py)

- [x] **Step 1: Remove Ravelry API wrappers**
  Delete the unused methods:
  - `get_queue_list`
  - `get_needles_list`
  - `reposition_queue_item`
  - `remove_queue_item`

---

### Task 5: Verification

- [x] **Step 1: Run E2E tests**
  Command: `.venv/bin/pytest`
  Expected: PASS (if tests have references to queue/needles, update them or check mock fixtures)
- [x] **Step 2: Manual browser test**
  Start server, check that only Personal Stash, Stash Analytics, Projects, and Yarn Search tabs are visible.
