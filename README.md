# StashStats

StashStats is a personal yarn stash tracker that wraps the Ravelry API and provides an interactive dashboard built with Plotly Dash. It allows you to search for yarn, manage your stash, track your projects, and view analytics on your yarn usage and acquisition.

## Features

- **Yarn Search**: Search the Ravelry API for yarns by name, brand, or colorway.
- **Stash Management**: Add yarns to your stash, log usage, and update quantities.
- **Analytics Dashboard**: View your stash statistics, including total yardage, meters, skeins, and weight.
- **Animated Growth Plot**: An interactive, animated scatter plot showing yarn category growth over time (yards vs. weight) with playback controls.
- **Projects & Queue**: View your current projects and queued projects.
- **Needles & Hooks**: Keep track of your knitting needles and crochet hooks.

## Directory Layout

```
.
├── app.py                     # Main Dash application entrypoint and callbacks
├── dev.py                     # Development script
├── docker-compose.yml         # Docker Compose configuration for the stack
├── Dockerfile                 # Multi-stage Dockerfile for the web application
├── requirements.txt           # Python dependencies
├── stashies/                  # Main application package
│   ├── app_controller.py      # Controller logic connecting model to UI
│   ├── base_req.py            # Base HTTP requests module
│   ├── base.py                # Base classes
│   ├── components/            # UI components (search, stash cards, analytics, etc.)
│   ├── dataclasses/           # Pydantic data models for validation
│   ├── db.py                  # SQLite database interactions
│   ├── model.py               # Ravelry API interactions and business logic
│   └── utils/                 # Utilities and logging configurations
├── static/                    # Static assets (images, CSS, etc.)
└── tests/                     # Automated test suite (Playwright E2E and unit tests)
```

## Installation Steps

You can run StashStats either locally using a Python virtual environment or using Docker Compose.

### Environment Variables

Before starting, create a `.env` file in the root directory and configure your Ravelry API credentials. Use the `.env.example` file as a template:

```env
# Ravelry API Credentials (use Personal Access credentials for write operations)
API_USERNAME=your_personal_access_username
API_KEY=your_personal_access_password
RAVELRY_USERNAME=YourRavelryUsername

# Local dev/docker environment variables
SQLITE_DB_PATH=/app/data/stash.db
REDIS_URL=redis://cache:6379/0
```

### Option 1: Docker Compose (Recommended)

To run the application using Docker Compose (includes Redis cache):

```bash
docker compose up --build -d
```

The application will be available at `http://localhost:8050`. The SQLite database will be stored in the local `./data` folder.

### Option 2: Local Virtual Environment

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
PYTHONPATH=. python3 app.py
```

The application will be available at `http://127.0.0.1:8050`.

## Testing

StashStats includes an automated test suite with End-to-End (E2E) tests using Playwright.

1. Install testing dependencies (already included in `requirements.txt` if using dev environment, but specifically you need pytest and playwright):

```bash
pip install pytest pytest-playwright
```

2. Install Playwright browsers (one-time setup):

```bash
playwright install chromium
```

3. Run the tests:

```bash
PYTHONPATH=. python3 -m pytest tests/test_e2e.py -v
```

## Usage Guide

- **Personal Stash**: View your current yarn inventory. You can search within your stash, click "Log Usage" to update quantities, or "Edit" to modify details.
- **Add to Stash**: Use the search bar at the top to find new yarns on Ravelry and add them directly to your stash.
- **Stash Analytics**: Navigate to the analytics tab to view metrics. You can switch between Yards, Meters, Skeins, and Grams, and toggle a 30-day moving average.
- **Animated Growth Scatter Plot**: The analytics tab includes an animated scatter plot showing your yarn category growth (cumulative weight vs. cumulative yards) over time. Press play to see how your stash composition has evolved!
