"""Page layouts and tab containers for the StashStats Dash web interface."""

from stashstats.web.layouts.main import create_main_layout, create_navigation_tabs
from stashstats.web.layouts.search import create_search_layout, create_yarn_search_layout
from stashstats.web.layouts.stash import create_stash_layout

__all__ = [
    "create_main_layout",
    "create_navigation_tabs",
    "create_search_layout",
    "create_stash_layout",
    "create_yarn_search_layout",
]
