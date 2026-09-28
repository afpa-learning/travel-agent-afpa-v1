"""Conversion des documents MongoDB en structures JSON-sérialisables."""

from bson import ObjectId


def serialize_document(doc: dict) -> dict:
    """Copie un document Mongo en convertissant _id (ObjectId) en chaîne flight_id."""
    if doc is None:
        return None
    clean = dict(doc)
    _id = clean.pop("_id", None)
    if _id is not None:
        clean["flight_id"] = str(_id)
    return clean


def serialize_documents(docs) -> list:
    return [serialize_document(d) for d in docs]


def to_object_id(value: str) -> ObjectId:
    return ObjectId(value)
