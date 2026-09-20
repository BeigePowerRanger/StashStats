---
title: StashStats Changelog
created: 2026-09-20
updated: 2026-09-20
type: project
tags:
  - project
  - stashstats
aliases:
  - StashStats Changelog
---

# StashStats Changelog

All notable changes to the StashStats application are documented here.

## [Unreleased] - 2026-09-02

### Added
- **Stash Form Custom Metrics**: Custom `grams` and `yards` per skein inputs on the yarn add/stash form (`a312590`).
- **Total Metrics API Dispatch**: Calculation and dispatch of `total_grams` and `total_yards` to the backend API (`d497e76`).
- **Item Deletion**: Implemented stash item deletion modal confirmation and callback (`60dd241`).
- **Test Infrastructure**: Multi-stage Dockerfile and `docker-compose.test.yml` for isolated containerized test execution (`50c5d30`).

### Changed
- **Type Annotations**: Cleaned up legacy typing references across docstrings (`ea39dd3`).

---

## [Projects Tab Accordion Refactor] - 2026-08-30

### Added
- **Accordion Components**: Collapsible accordion layout components for projects view (`55f55d8`).
- **Filtering & Pagination**: Project filtering, sorting, and pagination engine (`e5c41f2`).

---

## [Dev/Prod Account Toggle] - 2026-08-30

### Added
- **Runtime Auth Switcher**: `AccountManager` with dynamic switching between dev and prod accounts (`4d0a936`).
- **UI Indicators**: Header account switch badge, environment pill, and confirmation modal (`c196340`).
- **Data Reload Callbacks**: Callbacks triggering full data reload upon active account change (`8155eb5`).
- **Config Support**: Dual credential pairs exposed via `auth_tuple_for` (`eb5ba25`).

### Fixed
- **Store Scope**: Moved projects stores to global layout so auth callback reaches all tabs (`cf41406`).
- **Access Key Overrides**: Resolved auth_tuple handling so prod credentials can be overridden cleanly (`dd131ce`).

---

## [Project PDF Upload] - 2026-08-30

### Added
- **PDF Upload & Storage**: Endpoints and UI callbacks for uploading and attaching PDF project files (`af8ac42`).
- **File Management**: Delete callbacks and UI indicators for attached pattern PDFs (`338738a`).
