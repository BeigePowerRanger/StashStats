import json
import logging
from pathlib import Path
import sqlite3
from typing import Any

logger = logging.getLogger("stashstats.reference_db")

DB_PATH = Path("data/reference.db")

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS reference_data (key TEXT PRIMARY KEY, value TEXT)")
    logger.debug(f"[SQLITE INIT] Reference database initialized at {DB_PATH}")

def get_reference_data(key: str) -> Any | None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT value FROM reference_data WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            logger.debug(f"[SQLITE HIT] key={key}")
            return json.loads(row[0])
    logger.debug(f"[SQLITE MISS] key={key}")
    return None

def set_reference_data(key: str, data: Any):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO reference_data (key, value) VALUES (?, ?)",
            (key, json.dumps(data))
        )
    logger.debug(f"[SQLITE SET] key={key}")
