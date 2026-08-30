import os
from dotenv import load_dotenv

from stashstats.client import RavelryClient
from stashstats.config import Settings
from stashstats.logging import setup_logging
from stashstats.web.app import create_app

load_dotenv(override=False)

# Configure structured file and console logging
logger = setup_logging()

settings = Settings()
client = RavelryClient(settings=settings)

app = create_app(client=client, title="StashStats")
server = app.server

if __name__ == "__main__":
    debug_mode = os.getenv("APP_DEBUG", "true").lower() in ("true", "1", "t", "yes")
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8050")),
        debug=debug_mode,
        dev_tools_hot_reload=debug_mode,
        dev_tools_ui=debug_mode,
    )
