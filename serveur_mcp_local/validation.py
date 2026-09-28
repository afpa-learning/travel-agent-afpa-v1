"""Validation stricte des paramètres d'entrée (section 4.4 du cahier des charges)."""

import re
from datetime import datetime

_IATA_RE = re.compile(r"^[A-Za-z]{3}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_OBJECT_ID_RE = re.compile(r"^[0-9a-fA-F]{24}$")


class ValidationError(ValueError):
    """Erreur de validation d'un paramètre d'outil MCP."""


def validate_airport_code(value: str, field_name: str) -> str:
    if not value or not _IATA_RE.match(value.strip()):
        raise ValidationError(
            f"{field_name} doit être un code aéroport IATA à 3 lettres (ex. 'CDG'), reçu : {value!r}"
        )
    return value.strip().upper()


def validate_date(value: str, field_name: str) -> str:
    if not value or not _DATE_RE.match(value.strip()):
        raise ValidationError(
            f"{field_name} doit être une date au format AAAA-MM-JJ (ex. '2026-11-28'), reçu : {value!r}"
        )
    try:
        datetime.strptime(value.strip(), "%Y-%m-%d")
    except ValueError as exc:
        raise ValidationError(f"{field_name} n'est pas une date calendaire valide : {value!r}") from exc
    return value.strip()


def validate_positive_number(value, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} doit être un nombre, reçu : {value!r}") from exc
    if number < 0:
        raise ValidationError(f"{field_name} doit être positif ou nul, reçu : {value!r}")
    return number


def validate_non_negative_int(value, field_name: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} doit être un entier, reçu : {value!r}") from exc
    if number < 0:
        raise ValidationError(f"{field_name} doit être positif ou nul, reçu : {value!r}")
    return number


def validate_limit(value, default: int, max_allowed: int) -> int:
    if value is None:
        return default
    number = validate_non_negative_int(value, "limit")
    if number == 0:
        raise ValidationError("limit doit être supérieur à 0")
    return min(number, max_allowed)


def is_object_id(value: str) -> bool:
    return bool(value) and bool(_OBJECT_ID_RE.match(value.strip()))
