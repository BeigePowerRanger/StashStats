"""UI components for the StashStats Dash web interface."""

from stashstats.web.components.analytics import (
    create_kpi_summary_cards,
    create_unit_selector_bar,
)
from stashstats.web.components.analytics_charts import (
    create_fiber_donut_chart,
    create_monthly_flow_chart,
    create_projects_pie_chart,
    create_stash_by_time_chart,
    create_velocity_pace_chart,
    create_weight_distribution_chart,
)
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
    "create_fiber_donut_chart",
    "create_grouped_stash_accordion",
    "create_header",
    "create_kpi_summary_cards",
    "create_monthly_flow_chart",
    "create_parent_yarn_accordion_item",
    "create_projects_pie_chart",
    "create_stash_by_time_chart",
    "create_stash_item_row",
    "create_unit_selector_bar",
    "create_velocity_pace_chart",
    "create_weight_distribution_chart",
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
