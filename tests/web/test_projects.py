"""Tests for Projects tab layout, components, and callback business logic."""

import base64
from unittest.mock import MagicMock

import pytest

from stashstats.web.components.projects import (
    create_pdf_file_list,
    create_pdf_upload_zone,
    create_pdf_viewer,
)
from stashstats.web.layouts.projects import create_projects_layout

# ---------------------------------------------------------------------------
# Components: create_pdf_file_list
# ---------------------------------------------------------------------------


class TestCreatePdfFileList:
    def test_empty_returns_placeholder(self):
        result = create_pdf_file_list([], "proj1", "alice")
        assert len(result) == 1
        # Should be a paragraph element with muted text
        from dash import html

        assert isinstance(result[0], html.P)

    def test_one_file_renders_row(self):
        import dash_bootstrap_components as dbc

        result = create_pdf_file_list(["pattern.pdf"], "proj1", "alice")
        assert len(result) == 1
        assert isinstance(result[0], dbc.Row)

    def test_multiple_files_render_multiple_rows(self):
        import dash_bootstrap_components as dbc

        result = create_pdf_file_list(["a.pdf", "b.pdf", "c.pdf"], "proj1", "alice")
        assert len(result) == 3
        for row in result:
            assert isinstance(row, dbc.Row)

    def test_view_button_has_correct_id(self):
        import dash_bootstrap_components as dbc

        result = create_pdf_file_list(["my_file.pdf"], "proj42", "bob")
        # Find view button inside the row children
        row = result[0]
        # Flatten nested children to find buttons
        buttons = _find_components(row, dbc.Button)
        view_btns = [
            b
            for b in buttons
            if isinstance(b.id, dict) and b.id.get("type") == "project-pdf-view-btn"
        ]
        assert view_btns
        assert view_btns[0].id["index"] == "proj42"
        assert view_btns[0].id["filename"] == "my_file.pdf"

    def test_delete_button_has_correct_id(self):
        import dash_bootstrap_components as dbc

        result = create_pdf_file_list(["del.pdf"], "p99", "alice")
        buttons = _find_components(result[0], dbc.Button)
        del_btns = [
            b
            for b in buttons
            if isinstance(b.id, dict) and b.id.get("type") == "project-pdf-delete-btn"
        ]
        assert del_btns
        assert del_btns[0].id["filename"] == "del.pdf"


# ---------------------------------------------------------------------------
# Components: create_pdf_viewer
# ---------------------------------------------------------------------------


class TestCreatePdfViewer:
    def test_returns_iframe(self):
        from dash import html

        result = create_pdf_viewer("proj1")
        assert isinstance(result, html.Iframe)

    def test_default_src_is_empty(self):
        result = create_pdf_viewer("proj1")
        assert result.src == ""

    def test_custom_src_set(self):
        result = create_pdf_viewer("proj1", "/projects/pdf/alice/proj1/file.pdf")
        assert result.src == "/projects/pdf/alice/proj1/file.pdf"

    def test_has_width_100_percent(self):
        result = create_pdf_viewer("proj1")
        assert result.style.get("width") == "100%"


# ---------------------------------------------------------------------------
# Components: create_pdf_upload_zone
# ---------------------------------------------------------------------------


class TestCreatePdfUploadZone:
    def test_returns_upload_component(self):
        from dash import dcc

        result = create_pdf_upload_zone("proj1")
        assert isinstance(result, dcc.Upload)

    def test_id_contains_project_id(self):
        result = create_pdf_upload_zone("proj_abc")
        assert isinstance(result.id, dict)
        assert result.id["index"] == "proj_abc"

    def test_accepts_pdf(self):
        result = create_pdf_upload_zone("proj1")
        assert "pdf" in (result.accept or "").lower()


# ---------------------------------------------------------------------------
# Layout: create_projects_layout
# ---------------------------------------------------------------------------


class TestCreateProjectsLayout:
    def test_contains_controls(self):
        import dash_bootstrap_components as dbc

        result = create_projects_layout()

        # Check for inputs
        inputs = _find_components(result, dbc.Input)
        search_inputs = [i for i in inputs if getattr(i, "id", None) == "projects-search-input"]
        assert search_inputs, "Expected search input"

        selects = _find_components(result, dbc.Select)
        sort_dropdowns = [s for s in selects if getattr(s, "id", None) == "projects-sort-dropdown"]
        assert sort_dropdowns, "Expected sort dropdown"

        paginations = _find_components(result, dbc.Pagination)
        assert paginations, "Expected pagination component"

    def test_contains_accordion_container(self):
        from dash import html

        result = create_projects_layout()
        divs = _find_components(result, html.Div)
        containers = [d for d in divs if getattr(d, "id", None) == "projects-accordion-container"]
        assert containers, "Expected accordion container div"

    def test_contains_user_store(self):
        from dash import dcc

        result = create_projects_layout(user_id="testuser", include_stores=True)
        stores = _find_components(result, dcc.Store)
        user_stores = [s for s in stores if getattr(s, "id", None) == "projects-user-store"]
        assert user_stores, "Expected a dcc.Store with id='projects-user-store'"
        assert user_stores[0].data["user_id"] == "testuser"


# ---------------------------------------------------------------------------
# Layout: create_project_card
# ---------------------------------------------------------------------------


# Callback unit tests: _decode_upload and upload validation
# ---------------------------------------------------------------------------


class TestDecodeUpload:
    def test_valid_pdf_decoded(self):
        from stashstats.web.callbacks.projects import _decode_upload

        raw = b"%PDF-1.4 hello"
        b64 = base64.b64encode(raw).decode()
        contents = f"data:application/pdf;base64,{b64}"
        mime, data = _decode_upload(contents)
        assert mime == "application/pdf"
        assert data == raw

    def test_invalid_returns_none_tuple(self):
        from stashstats.web.callbacks.projects import _decode_upload

        mime, data = _decode_upload("not-a-valid-upload-string")
        assert mime is None
        assert data is None


class TestProjectsSyncLogic:
    def test_sync_no_clicks_prevents_update(self):
        import dash

        from stashstats.web.callbacks.projects import handle_projects_sync_logic

        with pytest.raises(dash.exceptions.PreventUpdate):
            handle_projects_sync_logic(None, [])

    def test_sync_with_client_success(self):
        from stashstats.models.project import ProjectListResponse, ProjectListResult
        from stashstats.web.callbacks.projects import handle_projects_sync_logic

        mock_client = MagicMock()
        mock_client.get_my_projects.return_value = ProjectListResponse(
            projects=[
                ProjectListResult(id=1, name="Test Scarf", status_name="In progress", progress=40)
            ],
            paginator={"page_count": 1, "page": 1, "page_size": 50, "results": 1, "last_page": 1},
        )

        status, color, last_synced, items = handle_projects_sync_logic(1, [], client=mock_client)
        assert status == "Synced"
        assert color == "success"
        assert "Last synced:" in last_synced
        assert len(items) == 1
        assert items[0]["name"] == "Test Scarf"

    def test_sync_with_client_failure(self):
        from stashstats.web.callbacks.projects import handle_projects_sync_logic

        mock_client = MagicMock()
        mock_client.get_my_projects.side_effect = RuntimeError("API error")

        status, color, last_synced, items = handle_projects_sync_logic(
            1, [{"id": 1}], client=mock_client
        )
        assert status == "Sync Failed"
        assert color == "danger"
        assert "offline/error" in last_synced
        assert items == [{"id": 1}]


# Helper: recursive component finder
# ---------------------------------------------------------------------------


def _find_components(root, component_type):
    """Recursively find all instances of component_type within a Dash component tree."""
    found = []
    if isinstance(root, component_type):
        found.append(root)
    children = getattr(root, "children", None)
    if children is None:
        return found
    if not isinstance(children, (list, tuple)):
        children = [children]
    for child in children:
        if hasattr(child, "children") or isinstance(child, component_type):
            found.extend(_find_components(child, component_type))
    return found


# ---------------------------------------------------------------------------
# Logic: filter_projects, sort_projects, paginate_projects
# ---------------------------------------------------------------------------


class TestFilterProjects:
    @pytest.fixture
    def sample_projects(self):
        return [
            {
                "id": 1,
                "name": "Blue Sweater",
                "pattern_name": "Basic Raglan",
                "craft_name": "Knitting",
                "status_name": "In progress",
                "tag_names": ["winter", "blue"],
            },
            {
                "id": 2,
                "name": "Red Scarf",
                "pattern_name": "Lace Scarf",
                "craft_name": "Crochet",
                "status_name": "Finished",
                "tag_names": ["gift"],
            },
            {
                "id": 3,
                "name": "Green Socks",
                "pattern_name": "Vanilla Socks",
                "craft_name": "Knitting",
                "status_name": "Hibernating",
                "tag_names": [],
            },
        ]

    def test_filter_empty_query(self, sample_projects):
        from stashstats.web.components.projects import filter_projects

        res = filter_projects(sample_projects, "")
        assert len(res) == 3

    def test_filter_by_name(self, sample_projects):
        from stashstats.web.components.projects import filter_projects

        res = filter_projects(sample_projects, "blue")
        assert len(res) == 1
        assert res[0]["id"] == 1

    def test_filter_by_pattern_name(self, sample_projects):
        from stashstats.web.components.projects import filter_projects

        res = filter_projects(sample_projects, "lace")
        assert len(res) == 1
        assert res[0]["id"] == 2

    def test_filter_by_craft_name(self, sample_projects):
        from stashstats.web.components.projects import filter_projects

        res = filter_projects(sample_projects, "crochet")
        assert len(res) == 1
        assert res[0]["id"] == 2

    def test_filter_by_status_name(self, sample_projects):
        from stashstats.web.components.projects import filter_projects

        res = filter_projects(sample_projects, "hibernating")
        assert len(res) == 1
        assert res[0]["id"] == 3

    def test_filter_by_tags(self, sample_projects):
        from stashstats.web.components.projects import filter_projects

        res = filter_projects(sample_projects, "gift")
        assert len(res) == 1
        assert res[0]["id"] == 2

    def test_filter_no_matches(self, sample_projects):
        from stashstats.web.components.projects import filter_projects

        res = filter_projects(sample_projects, "xyz")
        assert len(res) == 0


class TestSortProjects:
    @pytest.fixture
    def sample_projects(self):
        return [
            {
                "id": 1,
                "name": "C",
                "started": "2023-01-01",
                "created_at": "2023-01-01",
                "progress": 50,
                "status_name": "In progress",
            },
            {
                "id": 2,
                "name": "A",
                "started": "2023-02-01",
                "created_at": "2023-02-01",
                "progress": 100,
                "status_name": "Finished",
            },
            {
                "id": 3,
                "name": "B",
                "started": None,
                "created_at": "2023-01-15",
                "progress": 0,
                "status_name": "Hibernating",
            },
        ]

    def test_sort_date_desc_uses_started_or_created(self, sample_projects):
        from stashstats.web.components.projects import sort_projects

        res = sort_projects(sample_projects, "date_desc")
        assert [p["id"] for p in res] == [2, 3, 1]

    def test_sort_name_asc(self, sample_projects):
        from stashstats.web.components.projects import sort_projects

        res = sort_projects(sample_projects, "name_asc")
        assert [p["id"] for p in res] == [2, 3, 1]

    def test_sort_progress_desc(self, sample_projects):
        from stashstats.web.components.projects import sort_projects

        res = sort_projects(sample_projects, "progress_desc")
        assert [p["id"] for p in res] == [2, 1, 3]

    def test_sort_status_asc(self, sample_projects):
        from stashstats.web.components.projects import sort_projects

        res = sort_projects(sample_projects, "status_asc")
        assert [p["id"] for p in res] == [2, 3, 1]


class TestPaginateProjects:
    def test_paginate_valid_page(self):
        from stashstats.web.components.projects import paginate_projects

        items = list(range(25))
        page, paginated = paginate_projects(items, page=2, page_size=10)
        assert page == 2
        assert len(paginated) == 10
        assert paginated[0] == 10

    def test_paginate_page_too_high_clamps(self):
        from stashstats.web.components.projects import paginate_projects

        items = list(range(25))
        page, paginated = paginate_projects(items, page=5, page_size=10)
        assert page == 3
        assert len(paginated) == 5

    def test_paginate_page_too_low_clamps(self):
        from stashstats.web.components.projects import paginate_projects

        items = list(range(25))
        page, paginated = paginate_projects(items, page=0, page_size=10)
        assert page == 1
        assert len(paginated) == 10

    def test_paginate_empty(self):
        from stashstats.web.components.projects import paginate_projects

        page, paginated = paginate_projects([], page=1, page_size=10)
        assert page == 1
        assert paginated == []


# ---------------------------------------------------------------------------
# Components: create_project_accordion_item
# ---------------------------------------------------------------------------


class TestCreateProjectAccordionItem:
    def test_shows_project_name_and_pattern(self):
        import dash_bootstrap_components as dbc

        from stashstats.web.components.projects import create_project_accordion_item

        item = create_project_accordion_item(
            {"id": 1, "name": "My Mittens", "pattern_name": "Cozy Mittens"}
        )
        assert isinstance(item, dbc.AccordionItem)
        title_text = str(item.title)
        assert "My Mittens" in title_text

    def test_shows_status_badge_when_present(self):
        import dash_bootstrap_components as dbc

        from stashstats.web.components.projects import create_project_accordion_item

        item = create_project_accordion_item({"id": 1, "name": "X", "status_name": "Frogged"})
        title_components = _find_components(item.title, dbc.Badge)
        assert any("Frogged" in str(b.children) for b in title_components)

    def test_has_upload_zone_in_body(self):
        from dash import dcc

        from stashstats.web.components.projects import create_project_accordion_item

        item = create_project_accordion_item({"id": 77, "name": "Y"})
        uploads = _find_components(item, dcc.Upload)
        assert uploads

    def test_has_pdf_viewer_iframe(self):
        from dash import html

        from stashstats.web.components.projects import create_project_accordion_item

        item = create_project_accordion_item({"id": 77, "name": "Y"})
        iframes = _find_components(item, html.Iframe)
        assert iframes

    def test_existing_pdfs_rendered_in_file_list(self):
        import dash_bootstrap_components as dbc

        from stashstats.web.components.projects import create_project_accordion_item

        item = create_project_accordion_item({"id": 7, "name": "Z", "existing_pdfs": ["file.pdf"]})
        buttons = _find_components(item, dbc.Button)
        view_btns = [
            b
            for b in buttons
            if isinstance(b.id, dict) and b.id.get("type") == "project-pdf-view-btn"
        ]
        assert view_btns


# ---------------------------------------------------------------------------
# Components: create_grouped_projects_accordion
# ---------------------------------------------------------------------------


class TestCreateGroupedProjectsAccordion:
    def test_populated_projects_returns_accordion(self):
        import dash_bootstrap_components as dbc

        from stashstats.web.components.projects import create_grouped_projects_accordion

        projects = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
        accordion = create_grouped_projects_accordion(projects)
        assert isinstance(accordion, dbc.Accordion)
        assert len(accordion.children) == 2

    def test_empty_projects_returns_alert(self):
        import dash_bootstrap_components as dbc

        from stashstats.web.components.projects import create_grouped_projects_accordion

        result = create_grouped_projects_accordion([])
        # It should return an empty state component (like a Div containing text or alert)
        assert not isinstance(result, dbc.Accordion)


# ---------------------------------------------------------------------------
# Logic: update_projects_view_logic
# ---------------------------------------------------------------------------


class TestUpdateProjectsViewLogic:
    @pytest.fixture
    def sample_projects(self):
        return [
            {
                "id": 1,
                "name": "Blue Scarf",
                "started": "2023-01-01",
                "created_at": "2023-01-01",
                "progress": 10,
                "status_name": "In progress",
            },
            {
                "id": 2,
                "name": "Red Hat",
                "started": "2023-03-01",
                "created_at": "2023-03-01",
                "progress": 100,
                "status_name": "Finished",
            },
            {
                "id": 3,
                "name": "Blue Socks",
                "started": "2023-02-01",
                "created_at": "2023-02-01",
                "progress": 50,
                "status_name": "In progress",
            },
            {
                "id": 4,
                "name": "Green Mittens",
                "started": "2023-04-01",
                "created_at": "2023-04-01",
                "progress": 0,
                "status_name": "Hibernating",
            },
            {
                "id": 5,
                "name": "Yellow Shawl",
                "started": "2023-05-01",
                "created_at": "2023-05-01",
                "progress": 80,
                "status_name": "In progress",
            },
        ]

    def test_empty_projects(self):
        from stashstats.web.callbacks.projects import update_projects_view_logic

        accordion, total_pages, page = update_projects_view_logic(None)
        assert total_pages == 1
        assert page == 1
        assert accordion is not None

    def test_filter_and_sort(self, sample_projects):
        from stashstats.web.callbacks.projects import update_projects_view_logic

        accordion, total_pages, page = update_projects_view_logic(
            raw_projects=sample_projects,
            search_query="blue",
            sort_by="name_asc",
            active_page=1,
            page_size=10,
        )
        assert total_pages == 1
        assert page == 1
        assert len(accordion.children) == 2
        assert "Blue Scarf" in str(accordion.children[0].title)
        assert "Blue Socks" in str(accordion.children[1].title)

    def test_pagination_and_clamping(self, sample_projects):
        from stashstats.web.callbacks.projects import update_projects_view_logic

        accordion, total_pages, page = update_projects_view_logic(
            raw_projects=sample_projects,
            search_query="",
            sort_by="date_desc",
            active_page=10,
            page_size=2,
        )
        assert total_pages == 3
        assert page == 3
        assert len(accordion.children) == 1

    def test_page_clamped_to_minimum(self, sample_projects):
        from stashstats.web.callbacks.projects import update_projects_view_logic

        accordion, total_pages, page = update_projects_view_logic(
            raw_projects=sample_projects,
            active_page=0,
            page_size=2,
        )
        assert total_pages == 3
        assert page == 1
        assert len(accordion.children) == 2
