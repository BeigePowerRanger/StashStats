# Design Spec: Mock Analytics Data Generator

## 1. Goal
Provide a drop-in mock data generator for development/testing of the Stash Stats analytics dashboard.
It must generate a rich, realistic, and highly varied time-series dataset using faker, numpy, and probability distributions to simulate stash addition and consumption events.

## 2. Approach
- Create a new module `stashies/mock_analytics.py`.
- Expose `get_mock_analytics_dataframe()` and `get_mock_animated_analytics_dataframe()`.
- Add environment variable `DEV_MOCK_ANALYTICS=True` to enable the mock dataset.
- Intercept calls in `stashies/model.py` methods `get_analytics_dataframe()` and `get_animated_analytics_dataframe()`.

## 3. Data Generation Model
- Time range: Configurable (default 2 years/730 days).
- Stash additions (Arrivals): Modeled as a Poisson process (e.g., lambda = 0.15 stash events/day).
- Stash consumption (Knitting projects): Modeled as a Poisson process (e.g., lambda = 0.08 project completion events/day).
- Yarn weights (Categories): Finger, Sport, DK, Worsted, Bulky. Distribution probabilities: [0.35, 0.15, 0.20, 0.20, 0.10].
- Yarn quantities (Skeins/Yards): Log-normal distribution to reflect that knitters tend to buy small-to-medium packs, with rare large acquisitions (sweater quantities).
  - Fingering/Lace: Mean = 3 skeins, Sigma = 1.5. Yardage per skein: 400 yds.
  - DK/Worsted: Mean = 4 skeins, Sigma = 2.0. Yardage per skein: 220 yds.
  - Bulky: Mean = 2 skeins, Sigma = 1.0. Yardage per skein: 110 yds.
- Event times: Random timestamps generated using Faker to distribute events throughout the day/week.

## 4. Dependencies
- `faker` (add to requirements.txt)
- `numpy`
- `pandas`
