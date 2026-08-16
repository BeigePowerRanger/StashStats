"""Package entry point for `python -m stashstats`."""

import sys

from stashstats.cli import main

if __name__ == "__main__":
    sys.exit(main())
