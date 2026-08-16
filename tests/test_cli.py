"""Tests for StashStats CLI launcher in stashstats.cli."""

from unittest.mock import MagicMock, patch

from stashstats.cli import build_parser, main, run_server


def test_cli_parser_defaults() -> None:
    """Verify CLI parser default argument values."""
    parser = build_parser()
    args = parser.parse_args([])
    assert args.host == "127.0.0.1"
    assert args.port == 8050
    assert args.debug is False
    assert args.dev is False
    assert args.open_browser is False


def test_cli_parser_custom_args() -> None:
    """Verify custom flags and values parsed correctly."""
    parser = build_parser()
    args = parser.parse_args(
        ["--host", "0.0.0.0", "--port", "9090", "--debug", "--dev", "--open-browser"]
    )
    assert args.host == "0.0.0.0"
    assert args.port == 9090
    assert args.debug is True
    assert args.dev is True
    assert args.open_browser is True


def test_cli_parser_short_flags() -> None:
    """Verify short flags for host and port."""
    parser = build_parser()
    args = parser.parse_args(["-H", "192.168.1.50", "-p", "8888"])
    assert args.host == "192.168.1.50"
    assert args.port == 8888


def test_cli_parser_serve_subcommand() -> None:
    """Verify `serve` subcommand parses properly."""
    parser = build_parser()
    args = parser.parse_args(["serve", "--host", "127.0.0.1", "--port", "8080"])
    assert args.command == "serve"
    assert args.host == "127.0.0.1"
    assert args.port == 8080


@patch("stashstats.cli.run_server")
def test_cli_main_entrypoint(mock_run_server: MagicMock) -> None:
    """Verify main() function parses arguments and triggers run_server."""
    exit_code = main(["--host", "127.0.0.1", "--port", "8055", "--debug"])
    assert exit_code == 0
    mock_run_server.assert_called_once_with(
        host="127.0.0.1",
        port=8055,
        debug=True,
        dev=False,
        open_browser=False,
    )


@patch("stashstats.cli.create_app")
def test_cli_run_server(mock_create_app: MagicMock) -> None:
    """Verify run_server creates Dash app and starts it with specified parameters."""
    mock_app = MagicMock()
    mock_create_app.return_value = mock_app

    run_server(host="127.0.0.1", port=8050, debug=False, dev=False, open_browser=False)

    mock_create_app.assert_called_once()
    mock_app.run.assert_called_once_with(
        host="127.0.0.1",
        port=8050,
        debug=False,
        dev_tools_ui=False,
    )
