"""Connexion MongoDB/DocumentDB partagée par tous les outils du serveur MCP."""

from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

import config


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    """Retourne un client MongoDB singleton, créé au premier appel."""
    return MongoClient(
        config.MONGODB_URI,
        serverSelectionTimeoutMS=config.SERVER_SELECTION_TIMEOUT_MS,
    )


def get_db() -> Database:
    """Retourne la base de données cible (travel_agent_db par défaut)."""
    return get_client()[config.MONGODB_DB]


def reset_client_cache() -> None:
    """Utilitaire de test : force la recréation du client au prochain appel."""
    get_client.cache_clear()
