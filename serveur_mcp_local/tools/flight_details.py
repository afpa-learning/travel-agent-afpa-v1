"""Outil get_flight_details — détail d'un ou plusieurs vols par identifiant ou numéro."""

from typing import Optional

from bson.errors import InvalidId

from db import get_db
from formatting import serialize_document, serialize_documents, to_object_id
from validation import ValidationError, is_object_id, validate_date


def get_flight_details_impl(
    flight_id: Optional[str] = None,
    flight_number: Optional[str] = None,
    date: Optional[str] = None,
) -> dict:
    if not flight_id and not flight_number:
        raise ValidationError("Fournir flight_id ou flight_number.")

    db = get_db()

    if flight_id:
        if not is_object_id(flight_id):
            raise ValidationError(f"flight_id invalide (attendu : identifiant Mongo à 24 caractères hexadécimaux) : {flight_id!r}")
        try:
            doc = db.flights.find_one({"_id": to_object_id(flight_id)})
        except InvalidId as exc:
            raise ValidationError(f"flight_id invalide : {flight_id!r}") from exc
        if doc is None:
            return {"found": False, "message": f"Aucun vol trouvé pour flight_id={flight_id}"}
        return {"found": True, "flight": serialize_document(doc)}

    # Recherche par numéro de vol : un même numéro peut exister sur plusieurs
    # dates (cas réel des compagnies aériennes) -> désambiguïsation possible
    # via le paramètre `date`, sinon toutes les occurrences sont renvoyées.
    query: dict = {"flight_number": flight_number.strip().upper()}
    if date is not None:
        date = validate_date(date, "date")
        query["departure.datetime"] = {"$regex": f"^{date}"}

    matches = serialize_documents(list(db.flights.find(query)))

    if len(matches) == 0:
        return {"found": False, "message": f"Aucun vol trouvé pour flight_number={flight_number}"}
    if len(matches) == 1:
        return {"found": True, "flight": matches[0]}

    return {
        "found": True,
        "ambiguous": True,
        "message": (
            f"{len(matches)} vols correspondent au numéro {flight_number}. "
            "Précisez `date` (AAAA-MM-JJ) ou utilisez flight_id pour désambiguïser."
        ),
        "flights": matches,
    }
