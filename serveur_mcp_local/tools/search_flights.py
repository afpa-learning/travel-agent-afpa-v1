"""Outil search_flights — recherche de vols filtrée (section 4.2 du cahier des charges)."""

from typing import Optional

from db import get_db
from formatting import serialize_documents
from validation import (
    validate_airport_code,
    validate_date,
    validate_positive_number,
    validate_non_negative_int,
    validate_limit,
)
import config


def search_flights_impl(
    origin: str,
    destination: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_price: Optional[float] = None,
    max_stops: Optional[int] = None,
    limit: Optional[int] = None,
) -> dict:
    origin = validate_airport_code(origin, "origin")
    destination = validate_airport_code(destination, "destination")
    
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

    if max_price is not None:
        max_price = validate_positive_number(max_price, "max_price")
        query["price.amount"] = {"$lte": max_price}

    max_stops_filter = None
    if max_stops is not None:
        max_stops = validate_non_negative_int(max_stops, "max_stops")
        max_stops_filter = {"$expr": {"$lte": [{"$size": "$stops"}, max_stops]}}

    limit = validate_limit(limit, default=config.MAX_RESULTS, max_allowed=config.MAX_RESULTS)

    db = get_db()
    if max_stops_filter:
        pipeline = [
            {"$match": query},
            {"$match": max_stops_filter},
            {"$sort": {"price.amount": 1}},
            {"$limit": limit},
        ]
        cursor = db.flights.aggregate(pipeline)
    else:
        cursor = db.flights.find(query).sort("price.amount", 1).limit(limit)

    flights = serialize_documents(list(cursor))
    return {
        "origin": origin,
        "destination": destination,
        "filters": {
            "date_from": date_from,
            "date_to": date_to,
            "max_price": max_price,
            "max_stops": max_stops,
        },
        "count": len(flights),
        "flights": flights,
    }
