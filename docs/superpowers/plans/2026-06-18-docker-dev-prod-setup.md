# Plan: Docker Dev and Prod Containers Setup

**Goal:** Create dev and prod container configurations in the docker compose stack so the app can be run locally in development mode (with code mounting and hot reloading) and deployed in a stable production mode.

---

### Task 1: Create docker-compose.dev.yml

**Files:**
- Create: [docker-compose.dev.yml](file:///home/thotsky/BrainVault/Projects/StashStats/docker-compose.dev.yml)

- [x] **Step 1: Define development overrides**
  Define a docker compose override file that runs the `web` container in development mode:
  - Mounts the local workspace directory `./:/app` so changes are instantly reflected.
  - Overrides the start command `command: python app.py` to run the Dash development server with hot-reload enabled.
  - Sets the environment variable `DEBUG=1` and `DEV_LOGGING=1`.

  ```yaml
  version: '3.8'

  services:
    web:
      volumes:
        - .:/app
      command: python app.py
      environment:
        - DEBUG=True
        - DEV_LOGGING=1
  ```

---

### Task 2: Configure docker-compose.yml for Production

**Files:**
- Modify: [docker-compose.yml](file:///home/thotsky/BrainVault/Projects/StashStats/docker-compose.yml)

- [x] **Step 1: Set production defaults**
  - Verify that the base `docker-compose.yml` does NOT mount the code directory as a volume (it should only mount the `./data:/app/data` volume for the SQLite database).
  - Verify that the default command is Gunicorn running in production mode (`gunicorn --workers 1 --threads 4 ...`).

---

### Task 3: Support Github Pull Trigger on Build/Start (Optional/Production Feature)

**Files:**
- Modify: [Dockerfile](file:///home/thotsky/BrainVault/Projects/StashStats/Dockerfile)
- Create: `entrypoint.sh`

- [-] **Step 1: Add git integration to startup**
  - Decided not to implement this feature at this time.

---

### Task 4: Verification

- [x] **Step 1: Test Dev Stack**
  Run: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`
  Verify that editing a file triggers hot reload.
- [x] **Step 2: Test Prod Stack**
  Run: `docker compose up --build -d`
  Verify that the app runs on Gunicorn, code mounts are disabled, and it starts successfully.
