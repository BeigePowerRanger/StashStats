# Mock Analytics Data Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide a drop-in replacement module to generate rich and varied time-series datasets using probability distributions and Faker for development of StashStats.

**Architecture:** A new module `stashies/mock_analytics.py` generates daily and monthly mock dataframes, intercepted in `stashies/model.py` if `DEV_MOCK_ANALYTICS=True`.

**Tech Stack:** Python, Pandas, Numpy, Faker, Pytest

---

### Task 1: Add Faker Dependency

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Edit requirements.txt**

Add `faker` to requirements.txt:
```diff
 plotly==5.15.0
 redis==4.6.0
 gunicorn==20.1.0
+faker>=19.0.0
```

- [ ] **Step 2: Run pip install**

Run: `.venv/bin/pip install -r requirements.txt`
Expected: Installation completes successfully.

- [ ] **Step 3: Commit**

Run:
```bash
git add requirements.txt
git commit -m "deps: add faker to requirements"
```

---

### Task 2: Implement Mock Analytics Generator Module

**Files:**
- Create: `stashies/mock_analytics.py`

- [ ] **Step 1: Write stashies/mock_analytics.py**

Create `stashies/mock_analytics.py` with the following implementation:
```python
import datetime
import numpy as np
import pandas as pd
from faker import Faker

def get_mock_analytics_dataframe(days: int = 730) -> pd.DataFrame:
    fake = Faker()
    Faker.seed(42)
    np.random.seed(42)

    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days)
    dates = [start_date + datetime.timedelta(days=i) for i in range(days)]
    
    # Modeled with daily Poisson process for stash additions (lambda = 0.15 events/day)
    stash_events = np.random.poisson(0.15, days)
    # Modeled with daily Poisson process for projects consuming stash (lambda = 0.08 events/day)
    project_events = np.random.poisson(0.08, days)
    
    data = []
    
    for i, date in enumerate(dates):
        # Stash additions
        for _ in range(stash_events[i]):
            # Log-normal distribution of skeins added
            skeins = float(np.random.lognormal(mean=0.8, sigma=0.5))
            skeins = max(1.0, round(skeins))
            
            # Yardage per skein depends on random weights
            weight_type = np.random.choice(["fingering", "dk", "worsted", "bulky"], p=[0.4, 0.2, 0.3, 0.1])
            yd_map = {"fingering": 400.0, "dk": 220.0, "worsted": 200.0, "bulky": 110.0}
            yardage = skeins * yd_map[weight_type]
            grams = skeins * 100.0
            
            data.append({
                "date": pd.to_datetime(date),
                "yards": yardage,
                "meters": yardage * 0.9144,
                "skeins": float(skeins),
                "grams": grams
            })
            
        # Stash consumption
        for _ in range(project_events[i]):
            # Log-normal distribution of skeins consumed
            skeins = float(np.random.lognormal(mean=0.5, sigma=0.4))
            skeins = max(1.0, round(skeins))
            
            weight_type = np.random.choice(["fingering", "dk", "worsted", "bulky"], p=[0.4, 0.2, 0.3, 0.1])
            yd_map = {"fingering": 400.0, "dk": 220.0, "worsted": 200.0, "bulky": 110.0}
            yardage = skeins * yd_map[weight_type]
            grams = skeins * 100.0
            
            data.append({
                "date": pd.to_datetime(date),
                "yards": -yardage,
                "meters": -yardage * 0.9144,
                "skeins": -float(skeins),
                "grams": -grams
            })

    if not data:
        # Fallback empty dataframe structure
        return pd.DataFrame(columns=["date", "yards", "meters", "skeins", "grams",
                                     "cumulative_yards", "cumulative_meters",
                                     "cumulative_skeins", "cumulative_grams"])

    df = pd.DataFrame(data)
    df = df.groupby("date")[["yards", "meters", "skeins", "grams"]].sum().reset_index()
    df = df.sort_values("date")
    
    df["cumulative_yards"] = df["yards"].cumsum()
    df["cumulative_meters"] = df["meters"].cumsum()
    df["cumulative_skeins"] = df["skeins"].cumsum()
    df["cumulative_grams"] = df["grams"].cumsum()
    
    return df

def get_mock_animated_analytics_dataframe(days: int = 730) -> pd.DataFrame:
    np.random.seed(42)
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days)
    dates = [start_date + datetime.timedelta(days=i) for i in range(days)]
    
    categories = ["Lace", "Fingering", "DK", "Worsted", "Bulky"]
    probs = [0.15, 0.35, 0.20, 0.20, 0.10]
    
    data = []
    
    for i, date in enumerate(dates):
        month_start = pd.to_datetime(date).to_period("M").to_timestamp("M")
        
        # Arrivals (Poisson lambda = 0.2)
        events = np.random.poisson(0.2)
        for _ in range(events):
            cat = np.random.choice(categories, p=probs)
            skeins = float(np.random.lognormal(mean=0.8, sigma=0.5))
            skeins = max(1.0, round(skeins))
            yd_map = {"Lace": 600.0, "Fingering": 400.0, "DK": 220.0, "Worsted": 200.0, "Bulky": 110.0}
            yardage = skeins * yd_map[cat]
            
            data.append({
                "date": month_start,
                "category": cat,
                "yards": yardage,
                "meters": yardage * 0.9144,
                "skeins": float(skeins),
                "grams": skeins * 100.0
            })
            
        # Consumption (Poisson lambda = 0.1)
        events_cons = np.random.poisson(0.1)
        for _ in range(events_cons):
            cat = np.random.choice(categories, p=probs)
            skeins = float(np.random.lognormal(mean=0.5, sigma=0.4))
            skeins = max(1.0, round(skeins))
            yd_map = {"Lace": 600.0, "Fingering": 400.0, "DK": 220.0, "Worsted": 200.0, "Bulky": 110.0}
            yardage = skeins * yd_map[cat]
            
            data.append({
                "date": month_start,
                "category": cat,
                "yards": -yardage,
                "meters": -yardage * 0.9144,
                "skeins": -float(skeins),
                "grams": -skeins * 100.0
            })

    if not data:
        return pd.DataFrame(columns=["date", "category", "yards", "meters", "skeins", "grams",
                                     "cumulative_yards", "cumulative_meters",
                                     "cumulative_skeins", "cumulative_grams", "size_skeins", "frame_date"])

    df = pd.DataFrame(data)
    df = df.groupby(["date", "category"])[["yards", "meters", "skeins", "grams"]].sum().reset_index()
    
    all_dates = df["date"].unique()
    all_categories = df["category"].unique()
    idx = pd.MultiIndex.from_product([all_dates, all_categories], names=["date", "category"])
    df = df.set_index(["date", "category"]).reindex(idx, fill_value=0.0).reset_index()
    
    df = df.sort_values(["category", "date"])
    df["cumulative_yards"] = df.groupby("category")["yards"].cumsum()
    df["cumulative_meters"] = df.groupby("category")["meters"].cumsum()
    df["cumulative_skeins"] = df.groupby("category")["skeins"].cumsum()
    df["cumulative_grams"] = df.groupby("category")["grams"].cumsum()
    
    df = df.sort_values(["date", "category"])
    df["frame_date"] = df["date"].dt.strftime("%Y-%m")
    df["size_skeins"] = df["cumulative_skeins"].apply(lambda x: max(x, 0.1))
    
    return df
```

- [ ] **Step 2: Commit**

Run:
```bash
git add stashies/mock_analytics.py
git commit -m "feat: implement mock analytics time-series generators"
```

---

### Task 3: Integrate Mock Generator into Model

**Files:**
- Modify: `stashies/model.py`

- [ ] **Step 1: Modify model.py methods**

Update `get_analytics_dataframe` and `get_animated_analytics_dataframe` in `stashies/model.py`:

```python
    def get_analytics_dataframe(self, stash_list: List[Dict[str, Any]], proj_map: Dict[int, Any]) -> Any:
        """
        Extract history and build cumulative data over time for analytics.
        """
        import os
        if os.getenv("DEV_MOCK_ANALYTICS") == "True":
            from .mock_analytics import get_mock_analytics_dataframe
            return get_mock_analytics_dataframe()

        # ... (original method implementation) ...
```

And:

```python
    def get_animated_analytics_dataframe(self, stash_list: List[Dict[str, Any]], proj_map: Dict[int, Any]) -> Any:
        """
        Extract history and build cumulative data grouped by month and yarn weight category.
        """
        import os
        if os.getenv("DEV_MOCK_ANALYTICS") == "True":
            from .mock_analytics import get_mock_animated_analytics_dataframe
            return get_mock_animated_analytics_dataframe()

        # ... (original method implementation) ...
```

- [ ] **Step 2: Commit**

Run:
```bash
git add stashies/model.py
git commit -m "feat: route analytics requests to mock generators when DEV_MOCK_ANALYTICS is True"
```

---

### Task 4: Add Unit Tests

**Files:**
- Create: `tests/test_mock_analytics.py`

- [ ] **Step 1: Write tests/test_mock_analytics.py**

Create `tests/test_mock_analytics.py` containing:
```python
import pandas as pd
from stashies.mock_analytics import get_mock_analytics_dataframe, get_mock_animated_analytics_dataframe

def test_mock_analytics_dataframe():
    df = get_mock_analytics_dataframe(days=100)
    assert not df.empty
    expected_cols = [
        "date", "yards", "meters", "skeins", "grams",
        "cumulative_yards", "cumulative_meters", "cumulative_skeins", "cumulative_grams"
    ]
    for col in expected_cols:
        assert col in df.columns
    assert isinstance(df["date"].iloc[0], pd.Timestamp)

def test_mock_animated_analytics_dataframe():
    df = get_mock_animated_analytics_dataframe(days=100)
    assert not df.empty
    expected_cols = [
        "date", "category", "yards", "meters", "skeins", "grams",
        "cumulative_yards", "cumulative_meters", "cumulative_skeins",
        "cumulative_grams", "size_skeins", "frame_date"
    ]
    for col in expected_cols:
        assert col in df.columns
    assert set(df["category"].unique()) == {"Lace", "Fingering", "DK", "Worsted", "Bulky"}
```

- [ ] **Step 2: Run pytest**

Run: `.venv/bin/pytest tests/test_mock_analytics.py -v`
Expected: 2 passed.

- [ ] **Step 3: Commit**

Run:
```bash
git add tests/test_mock_analytics.py
git commit -m "test: add tests for mock analytics generator"
```

---

### Task 5: Enable Mock Data in Environment

**Files:**
- Modify: `.env.example`
- Modify: `.env`

- [ ] **Step 1: Edit .env.example**

Add `DEV_MOCK_ANALYTICS` to `.env.example`:
```diff
 RAVELRY_PASSWORD=your_password
 RAVELRY_USERNAME=your_username
 REDIS_URL=redis://localhost:6379/0
+DEV_MOCK_ANALYTICS=False
```

- [ ] **Step 2: Edit .env**

Add `DEV_MOCK_ANALYTICS=True` to `.env` to enable it in dev environment.

- [ ] **Step 3: Commit**

Run:
```bash
git add .env.example
git commit -m "config: add DEV_MOCK_ANALYTICS config option"
```
