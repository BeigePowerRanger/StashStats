"""UI components for the StashStats Dash web interface."""

from stashstats.web.components.header import create_header
from stashstats.web.components.search import (
    create_yarn_search_accordion,
    create_yarn_search_accordion_item,
    create_yarn_search_details,
    create_yarn_search_form,
    create_yarn_search_pagination,
)
from stashstats.web.components.stash import (
    ParentYarnGroup,
    create_grouped_stash_accordion,
    create_parent_yarn_accordion_item,
    create_stash_item_row,
    filter_stash_groups,
    group_stash_items,
    paginate_stash_groups,
    sort_stash_groups,
)

__all__ = [
    "ParentYarnGroup",
    "create_grouped_stash_accordion",
    "create_header",
    "create_parent_yarn_accordion_item",
    "create_stash_item_row",
    "create_yarn_search_accordion",
    "create_yarn_search_accordion_item",
    "create_yarn_search_details",
    "create_yarn_search_form",
    "create_yarn_search_pagination",
    "filter_stash_groups",
    "group_stash_items",
    "paginate_stash_groups",
    "sort_stash_groups",
]
