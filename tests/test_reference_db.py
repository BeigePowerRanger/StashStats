import sqlite3
import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from stashstats.client import RavelryClient
from stashstats.config import Settings
from stashstats.models import YarnWeightReference
from stashstats.reference_db import init_db, get_reference_data, set_reference_data, DB_PATH

@pytest.fixture(autouse=True)
def mock_db_path(tmp_path):
    with patch("stashstats.reference_db.DB_PATH", tmp_path / "test_reference.db"):
        yield tmp_path / "test_reference.db"

def test_sqlite_reference_population():
    init_db()
    
    settings = Settings(access_key="dummy", personal_key="dummy")
    client = RavelryClient(settings=settings)
    
    dummy_api_response = {
        "yarn_weights": [
            {"id": 1, "name": "Lace", "crochet_gauge": "", "knit_gauge": "", "wpi": "", "min_gauge": None, "max_gauge": None}
        ]
    }
    
    with patch.object(RavelryClient, 'get', return_value=dummy_api_response) as mock_get:
        # First call hits API
        res = client.get_yarn_weights()
        assert len(res) == 1
        assert res[0].name == "Lace"
        assert mock_get.called
        
        mock_get.reset_mock()
        
        # Second call hits DB
        res2 = client.get_yarn_weights()
        assert len(res2) == 1
        assert res2[0].name == "Lace"
        mock_get.assert_not_called()
