"""Tests for Projects tab layout, components, and callback business logic."""

import base64
from unittest.mock import MagicMock, patch

import pytest

from stashstats.web.components.projects import (
    create_pdf_file_list,
    create_pdf_upload_zone,
    create_pdf_viewer,
)
from stashstats.web.layouts.projects import create_project_card, create_projects_layout


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
        from dash import html
        import dash_bootstrap_components as dbc
        result = create_pdf_file_list(["my_file.pdf"], "proj42", "bob")
        # Find view button inside the row children
        row = result[0]
        # Flatten nested children to find buttons
        buttons = _find_components(row, dbc.Button)
        view_btns = [b for b in buttons if isinstance(b.id, dict) and b.id.get("type") == "project-pdf-view-btn"]
        assert view_btns
        assert view_btns[0].id["index"] == "proj42"
        assert view_btns[0].id["filename"] == "my_file.pdf"

    def test_delete_button_has_correct_id(self):
        import dash_bootstrap_components as dbc
        result = create_pdf_file_list(["del.pdf"], "p99", "alice")
        buttons = _find_components(result[0], dbc.Button)
        del_btns = [b for b in buttons if isinstance(b.id, dict) and b.id.get("type") == "project-pdf-delete-btn"]
        assert del_btns
        assert del_btns[0].id["filename"] == "del.pdf"


# ---------------------------------------------------------------------------
# Components: create_pdf_viewer
# ---------------------------------------------------------------------------


class TestCreatePdfViewer:
    def test_returns_iframe(self):
        from dash import html
        result = create_pdf_viewer()
        assert isinstance(result, html.Iframe)

    def test_default_src_is_empty(self):
        from dash import html
        result = create_pdf_viewer()
        assert result.src == ""

    def test_custom_src_set(self):
        from dash import html
        result = create_pdf_viewer("/projects/pdf/alice/proj1/file.pdf")
        assert result.src == "/projects/pdf/alice/proj1/file.pdf"

    def test_has_width_100_percent(self):
        from dash import html
        result = create_pdf_viewer()
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
        from dash import dcc
        result = create_pdf_upload_zone("proj_abc")
        assert isinstance(result.id, dict)
        assert result.id["index"] == "proj_abc"

    def test_accepts_pdf(self):
        from dash import dcc
        result = create_pdf_upload_zone("proj1")
        assert "pdf" in (result.accept or "").lower()


# ---------------------------------------------------------------------------
# Layout: create_projects_layout
# ---------------------------------------------------------------------------


class TestCreateProjectsLayout:
    def test_no_projects_shows_empty_state(self):
        import dash_bootstrap_components as dbc
        result = create_projects_layout()
        # Should contain an Alert for empty state
        alerts = _find_components(result, dbc.Alert)
        assert alerts, "Expected an Alert for empty projects state"

    def test_with_projects_renders_cards(self):
        import dash_bootstrap_components as dbc
        projects = [
            {"id": 1, "name": "Sweater", "status_name": "In progress", "progress": 50},
            {"id": 2, "name": "Scarf", "status_name": "Finished", "progress": 100},
        ]
        result = create_projects_layout(projects=projects, user_id="alice")
        cards = _find_components(result, dbc.Card)
        assert len(cards) >= 2

    def test_contains_user_store(self):
        from dash import dcc
        result = create_projects_layout(user_id="testuser")
        stores = _find_components(result, dcc.Store)
        user_stores = [s for s in stores if getattr(s, "id", None) == "projects-user-store"]
        assert user_stores, "Expected a dcc.Store with id='projects-user-store'"
        assert user_stores[0].data["user_id"] == "testuser"

    def test_project_card_contains_upload_zone(self):
        from dash import dcc
        projects = [{"id": 42, "name": "Hat"}]
        result = create_projects_layout(projects=projects)
        uploads = _find_components(result, dcc.Upload)
        assert uploads, "Expected at least one dcc.Upload per project"

    def test_project_card_has_pdf_viewer_iframe(self):
        from dash import html
        projects = [{"id": 42, "name": "Hat"}]
        result = create_projects_layout(projects=projects)
        iframes = _find_components(result, html.Iframe)
        assert iframes, "Expected at least one iframe for PDF viewer"


# ---------------------------------------------------------------------------
# Layout: create_project_card
# ---------------------------------------------------------------------------


class TestCreateProjectCard:
    def test_shows_project_name(self):
        import dash_bootstrap_components as dbc
        card = create_project_card({"id": "1", "name": "My Mittens"})
        assert isinstance(card, dbc.Card)

    def test_shows_status_badge_when_present(self):
        import dash_bootstrap_components as dbc
        card = create_project_card({"id": "1", "name": "X", "status_name": "Frogged"})
        badges = _find_components(card, dbc.Badge)
        assert any("Frogged" in str(b.children) for b in badges)

    def test_no_badge_when_no_status(self):
        import dash_bootstrap_components as dbc
        card = create_project_card({"id": "1", "name": "X"})
        badges = _find_components(card, dbc.Badge)
        assert not badges

    def test_has_upload_zone(self):
        from dash import dcc
        card = create_project_card({"id": "77", "name": "Y"})
        uploads = _find_components(card, dcc.Upload)
        assert uploads

    def test_has_pdf_viewer_iframe(self):
        from dash import html
        card = create_project_card({"id": "77", "name": "Y"})
        iframes = _find_components(card, html.Iframe)
        assert iframes

    def test_existing_pdfs_rendered_in_file_list(self):
        import dash_bootstrap_components as dbc
        card = create_project_card({"id": "7", "name": "Z"}, existing_pdfs=["file.pdf"])
        buttons = _find_components(card, dbc.Button)
        view_btns = [b for b in buttons if isinstance(b.id, dict) and b.id.get("type") == "project-pdf-view-btn"]
        assert view_btns


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


# ---------------------------------------------------------------------------
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
