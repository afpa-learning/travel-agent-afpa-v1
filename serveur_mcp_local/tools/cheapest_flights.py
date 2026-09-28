"""Outil cheapest_flights — les N vols les moins chers sur une route, dates flexibles."""

from typing import Optional

from db import get_db
from formatting import serialize_documents
from validation import validate_airport_code, validate_date, validate_limit
import config

DEFAULT_CHEAPEST_LIMIT = 5


def cheapest_flights_impl(
    origin: str,
    destination: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    origin = validate_airport_code(origin, "origin")
    destination = validate_airport_code(destination, "destination")
    limit = validate_limit(limit, default=DEFAULT_CHEAPEST_LIMIT, max_allowed=config.MAX_RESULTS)

    query: dict = {
        "departure.airport_code": origin,
        "arrival.airport_code": destination,
    }

    if date_from is not None or date_to is not None:
        date_range: dict = {}
        if date_from is not None:
            date_from = validate_date(date_from, "date_from")
            date_range["$gte"] = f"{date_from}T00:00:00Z"
        if date_to is not None:
            date_to = validate_date(date_to, "date_to")
            date_range["$lte"] = f"{date_to}T23:59:59Z"
        query["departure.datetime"] = date_range

    db = get_db()
    cursor = db.flights.find(query).sort("price.amount", 1).limit(limit)
    flights = serialize_documents(list(cursor))

    return {
        "origin": origin,
        "destination": destination,
        "date_from": date_from,
        "date_to": date_to,
        "count": len(flights),
        "flights": flights,
    }
