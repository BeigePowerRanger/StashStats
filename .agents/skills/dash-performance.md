---
name: dash-performance
description: Guideline for optimizing Dash web application performance, client-side callbacks, pattern-matching callback efficiency, caching, and layout design.
risk: safe
source: community
date_added: "2026-06-12"
---

# Dash Performance & Optimization Guidelines

Use when developing, refactoring, or optimizing Dash applications here.

## Use this skill when

- Callback execution is slow or blocking main thread
- Layout contains nested components causing rendering lags
- Client-side callbacks can replace server-side roundtrips
- Pattern-matching callbacks (MATCH/ALL) need performance improvements

## Optimization Checklist

### 1. Client-Side Callbacks
- Use client-side callbacks for UI-only updates (e.g., toggling modal visibility, updating simple preview calculations, tab transitions).
- Avoid server roundtrips for operations not querying databases or external APIs.

Example:
```javascript
// assets/clientside.js or inline clientside callback
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        toggle_modal: function(n_clicks, is_open) {
            if (n_clicks) {
                return !is_open;
            }
            return is_open;
        }
    }
});
```

### 2. Pattern-Matching Callbacks (MATCH / ALL)
- Restrict search space in pattern-matching callbacks.
- Use `MATCH` over `ALL` when only triggered item's state required.
- Store static component IDs in config/constants to avoid dynamic ID creation overhead.

### 3. Layout Complexity & Component Hierarchies
- Flatten layout structures. Deeply nested HTML/Bootstrap structures increase DOM tree depth, slowing React rendering.
- Keep layout generation functions simple and fast. Return simple structures; construct complex parts dynamically only on user interaction.
- Use `dash.no_update` to prevent unnecessary component updates and re-renders.

### 4. Caching & State Management
- Do not store state in global Python variables. Not thread-safe; fails in multi-user environments.
- Use `dcc.Store` for light client-side state.
- Use server-side caching (e.g., Redis, Flask-Caching memoize/cache decorators) for heavy database or API queries.
- Keep data in `dcc.Store` serialized as JSON strings only if small (<100KB) to prevent network transfer overhead.
