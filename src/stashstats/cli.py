"""CLI entry point and web application launcher for StashStats."""

import argparse
import os
import sys
import threading
import time
import webbrowser
from collections.abc import Sequence

from stashstats.client import RavelryClient
from stashstats.config import settings
from stashstats.exceptions import RavelryAPIError, RavelryAuthError
from stashstats.web.app import create_app

# NOTE: is this cli stuff doing anything right now? if its not being used for the web app I think it should be moved to a new subdirectory. 

def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser for StashStats CLI.

    Returns:
        Configured argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="stashstats",
        description="StashStats — Personal analytics and inventory management for Ravelry stashes.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Serve subcommand (and top-level fallback)
    serve_parser = subparsers.add_parser("serve", help="Launch the Dash web dashboard")
    _add_server_arguments(serve_parser)
    _add_server_arguments(parser)

    return parser


def _add_server_arguments(parser: argparse.ArgumentParser) -> None:
    """Add web server options to parser."""
    parser.add_argument(
        "--host",
        "-H",
        type=str,
        default=os.getenv("STASHSTATS_HOST", "127.0.0.1"),
        help="Host interface to bind the web server to (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=int(os.getenv("STASHSTATS_PORT", "8050")),
        help="Port to bind the web server to (default: 8050).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.getenv("STASHSTATS_DEBUG", "").lower() in ("1", "true", "yes"),
        help="Enable Dash debug mode and hot reloading.",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        default=False,
        help="Enable Dash dev tools UI overlay.",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        default=False,
        help="Automatically open web browser at launch.",
    )


def run_server(
    host: str = "127.0.0.1",
    port: int = 8050,
    debug: bool = False,
    dev: bool = False,
    open_browser: bool = False,
    client: RavelryClient | None = None,
) -> None:
    """Launch the StashStats Dash web server.

    Args:
        host: Host IP or hostname to bind.
        port: Port number to bind.
        debug: Whether to run Dash with debug mode.
        dev: Whether to enable Dash dev tools UI.
        open_browser: Whether to open default browser automatically.
        client: Optional pre-configured RavelryClient instance.
    """
    # Attempt to initialize client if not provided
    if client is None:
        try:
            if settings.access_key and settings.personal_key:
                client = RavelryClient(settings=settings)
        except (RavelryAuthError, RavelryAPIError, ValueError, OSError):
            client = None

    app = create_app(client=client)

    url = f"http://{host}:{port}"
    print(f"Starting StashStats web dashboard at {url}")

    if open_browser:
        def _launch_browser() -> None:
            time.sleep(1.0)
            webbrowser.open_new_tab(url)

        threading.Thread(target=_launch_browser, daemon=True).start()

    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            dev_tools_ui=dev,
        )
    except KeyboardInterrupt:
        print("\nShutting down StashStats server...")


def main(args: Sequence[str] | None = None) -> int:
    """Main CLI entry point.

    Args:
        args: Command-line arguments sequence (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success).
    """
    parser = build_parser()
    parsed_args = parser.parse_args(args=args if args is not None else sys.argv[1:])

    run_server(
        host=parsed_args.host,
        port=parsed_args.port,
        debug=parsed_args.debug,
        dev=parsed_args.dev,
        open_browser=parsed_args.open_browser,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
