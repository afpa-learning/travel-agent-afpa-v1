"""Outil list_airports — recherche d'aéroports par ville, pays ou code IATA."""

import re
from typing import Optional

from db import get_db
from validation import ValidationError, validate_limit
import config


def list_airports_impl(query: str, limit: Optional[int] = None) -> dict:
    if not query or not query.strip():
        raise ValidationError("`query` ne peut pas être vide.")

    limit = validate_limit(limit, default=config.MAX_RESULTS, max_allowed=config.MAX_RESULTS)
    needle = re.escape(query.strip())

    db = get_db()
    mongo_query = {
        "$or": [
            {"airport_code": query.strip().upper()},
            {"city": {"$regex": needle, "$options": "i"}},
            {"country": {"$regex": needle, "$options": "i"}},
            {"name": {"$regex": needle, "$options": "i"}},
        ]
    }

    results = list(db.airports.find(mongo_query, {"_id": 0}).limit(limit))
    return {"query": query, "count": len(results), "airports": results}
