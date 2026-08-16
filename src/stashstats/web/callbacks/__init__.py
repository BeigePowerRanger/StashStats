"""Reactive Dash callbacks for StashStats."""

from stashstats.web.callbacks.modal import (
    handle_history_rollback,
    handle_save_modal,
    handle_usage_preview_update,
    register_modal_callbacks,
)
from stashstats.web.callbacks.search import (
    build_search_query,
    handle_yarn_search_callback,
    register_search_callbacks,
    update_yarn_search_logic,
)
from stashstats.web.callbacks.stash import (
    handle_stash_sync_logic,
    register_stash_callbacks,
    update_stash_view_logic,
)

__all__ = [
    "build_search_query",
    "handle_history_rollback",
    "handle_save_modal",
    "handle_stash_sync_logic",
    "handle_usage_preview_update",
    "handle_yarn_search_callback",
    "register_modal_callbacks",
    "register_search_callbacks",
    "register_stash_callbacks",
    "update_stash_view_logic",
    "update_yarn_search_logic",
]

