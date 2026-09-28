import json
from pathlib import Path

import mongomock
import pytest

from serveur_mcp_local import db as db_module

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    """Remplace le client MongoDB réel par un client mongomock pré-chargé
    avec le jeu de données exemple (data/*.json), pour chaque test."""
    client = mongomock.MongoClient()
    database = client["travel_agent_db"]

    for name in ("flights", "airports", "airlines"):
        docs = json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))
        database[name].insert_many(docs)

    monkeypatch.setattr(db_module, "get_client", lambda: client)
    monkeypatch.setattr(db_module, "get_db", lambda: database)
    yield database
