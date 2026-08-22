---
aliases: []
tags: []
---

# StashStats

Dash-based web app. Search, track, manage personal [[Yarn Stash|yarn stash]] via [[ravelRy|Ravelry]] [[api|API]].

---

# Current Issues

- Sync doesn't work
- Edit stash modal -> no actual change in stash
	- makes change but immediately reverts back to previous state
	-above `delete entry` it says "usage entry deleted"

## TODOs

- [ ] #TODO the comments in the code are terrible i'm having to interpret everything myself at least in app.py
- [ ] #TODO this working directory (where the code is ) is a clusterfuck. we need to clean it up a lot.
- [ ] #TODO the typing library is deprecated now :( we're supposed to use dict and list mostly normal built in objects instead of special objects
- [ ] #TODO need to get main branch set up to use Katies account and then the dev branch which can use my account
	- [ ] time to use 0 auth if its that easy

# User Code Review

 - [ ] #TODO create work tree before beginning refactor/ rework of code [priority:: highest]

## App.py

### App Initiation

- prevent initial callbacks
- suppress callback exceptions
- darkly theme
- metatags
- Initializes `AppController` Object

### Dash Callbacks

- Handle Search callback
  - calls `CONTROLLER.search_yarn` passing in the user query, sorting mechanism, and category to search

- `toggle_search_collapse`: logically this handles collapsing search results once they've been expanded but not really sure why

- `handle_add_to_stash`: add yarn to stash from search interface

  - skeins, colorway, dyelot, location (?), notes, and date added are all potential inputs
    - I believe the `MATCH` thing is for updating the values of thiings dynamically so objects can have different ids without having to have a million `STATE` objects in the callback definition

- `render_analytics_layout` `render_stash_tab`, `update_remaining_preview` `render_projects_tab`, `load_projects_list` : just passthroughs to the `CONTROLLER` object.

- `save_stash_edit` is kind of a cluster fuck

## Stashies

### base.py

creates a base class that assigns a `Logger` object to all child classes

I feel like this `Base` class either needs to do more or just go away


### ravelry_client.py

okay what the hell is this 