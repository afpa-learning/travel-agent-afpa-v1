"""Outil compare_flights — comparaison de plusieurs vols (prix, durée, escales)."""

from typing import List

from db import get_db
from formatting import serialize_document, to_object_id
from validation import ValidationError, is_object_id

MAX_COMPARISON_ITEMS = 6


def compare_flights_impl(flights: List[str]) -> dict:
    if not flights or not isinstance(flights, list):
        raise ValidationError("`flights` doit être une liste non vide de flight_id ou flight_number.")
    if len(flights) < 2:
        raise ValidationError("Fournir au moins deux vols à comparer.")
    if len(flights) > MAX_COMPARISON_ITEMS:
        raise ValidationError(f"Un maximum de {MAX_COMPARISON_ITEMS} vols peut être comparé à la fois.")

    db = get_db()
    resolved = []
    not_found = []
    ambiguous = []

    for identifier in flights:
        identifier = str(identifier).strip()
        doc = None
        if is_object_id(identifier):
            doc = db.flights.find_one({"_id": to_object_id(identifier)})
            if doc is not None:
                resolved.append(serialize_document(doc))
            else:
                not_found.append(identifier)
        else:
            matches = list(db.flights.find({"flight_number": identifier.upper()}))
            if len(matches) == 0:
                not_found.append(identifier)
            elif len(matches) == 1:
                resolved.append(serialize_document(matches[0]))
            else:
                ambiguous.append(identifier)

    comparison = [
        {
            "flight_id": f["flight_id"],
            "flight_number": f["flight_number"],
            "airline": f["airline"]["name"],
            "departure_datetime": f["departure"]["datetime"],
            "route": f"{f['departure']['airport_code']} -> {f['arrival']['airport_code']}",
            "duration_minutes": f["duration_minutes"],
            "stops": len(f.get("stops", [])),
            "price_amount": f["price"]["amount"],
            "price_currency": f["price"]["currency"],
            "fare_class": f["price"]["fare_class"],
            "seats_available": f["seats_available"],
        }
        for f in resolved
    ]

    cheapest = min(comparison, key=lambda x: x["price_amount"]) if comparison else None
    fastest = min(comparison, key=lambda x: x["duration_minutes"]) if comparison else None

    return {
        "compared_count": len(comparison),
        "comparison": comparison,
        "cheapest_flight_number": cheapest["flight_number"] if cheapest else None,
        "fastest_flight_number": fastest["flight_number"] if fastest else None,
        "not_found": not_found,
        "ambiguous": ambiguous,
    }
