"""Tests for the Dash application factory in stashstats.web.app."""

import dash
import dash_bootstrap_components as dbc
from flask import Flask

from stashstats.client import RavelryClient
from stashstats.web.app import create_app


def test_create_app_returns_dash_instance() -> None:
    """Verify create_app returns a Dash instance."""
    app = create_app()
    assert isinstance(app, dash.Dash)
    assert app.title == "StashStats"


def test_create_app_darkly_theme() -> None:
    """Verify create_app configures Darkly theme by default."""
    app = create_app()
    assert dbc.themes.DARKLY in app.config.external_stylesheets


def test_create_app_custom_stylesheets() -> None:
    """Verify custom external stylesheets can be provided."""
    custom_sheets = [dbc.themes.DARKLY, "https://example.com/custom.css"]
    app = create_app(external_stylesheets=custom_sheets)
    assert "https://example.com/custom.css" in app.config.external_stylesheets


def test_create_app_server_exposed() -> None:
    """Verify the underlying WSGI/Flask server is exposed."""
    app = create_app()
    assert hasattr(app, "server")
    assert isinstance(app.server, Flask)


def test_create_app_custom_title() -> None:
    """Verify custom application title."""
    app = create_app(title="Custom StashStats")
    assert app.title == "Custom StashStats"


def test_create_app_with_client() -> None:
    """Verify optional RavelryClient instance can be attached."""
    from stashstats.config import Settings

    client = RavelryClient(
        settings=Settings(access_key="test_key", personal_key="test_secret")
    )
    app = create_app(client=client)
    assert app.client is client


def test_create_app_layout_initialized() -> None:
    """Verify default layout root container is initialized."""
    app = create_app()
    assert app.layout is not None
    assert getattr(app.layout, "id", None) == "app-root"
