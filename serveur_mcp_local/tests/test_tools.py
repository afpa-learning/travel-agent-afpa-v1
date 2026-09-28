import pytest

from serveur_mcp_local.tools.search_flights import search_flights_impl
from serveur_mcp_local.tools.flight_details import get_flight_details_impl
from serveur_mcp_local.tools.compare_flights import compare_flights_impl
from serveur_mcp_local.tools.list_airports import list_airports_impl
from serveur_mcp_local.tools.cheapest_flights import cheapest_flights_impl
from serveur_mcp_local.validation import ValidationError


# ---------- search_flights ----------

def test_search_flights_basic_route():
    result = search_flights_impl("CDG", "HND")
    assert result["count"] >= 3
    assert all(f["departure"]["airport_code"] == "CDG" for f in result["flights"])
    assert all(f["arrival"]["airport_code"] == "HND" for f in result["flights"])
    # tri par prix croissant
    prices = [f["price"]["amount"] for f in result["flights"]]
    assert prices == sorted(prices)


def test_search_flights_max_price_filter():
    result = search_flights_impl("CDG", "HND", max_price=700)
    assert result["count"] >= 1
    assert all(f["price"]["amount"] <= 700 for f in result["flights"])


def test_search_flights_max_stops_filter():
    result = search_flights_impl("CDG", "HND", max_stops=0)
    assert result["count"] >= 1
    assert all(len(f["stops"]) == 0 for f in result["flights"])


def test_search_flights_date_range():
    result = search_flights_impl("CDG", "LIS", date_from="2026-10-01", date_to="2026-10-15")
    assert result["count"] >= 1
    for f in result["flights"]:
        assert f["departure"]["datetime"].startswith("2026-10-1") or f["departure"]["datetime"].startswith("2026-10-0")


def test_search_flights_invalid_airport_code():
    with pytest.raises(ValidationError):
        search_flights_impl("Paris", "HND")


def test_search_flights_no_results():
    result = search_flights_impl("CDG", "XXX")
    assert result["count"] == 0
    assert result["flights"] == []


# ---------- get_flight_details ----------

def test_get_flight_details_single_match():
    result = get_flight_details_impl(flight_number="TP453")
    assert result["found"] is True
    assert result["flight"]["flight_number"] == "TP453"


def test_get_flight_details_ambiguous_without_date():
    # AF1180 existe à deux dates différentes dans le jeu de données exemple
    result = get_flight_details_impl(flight_number="AF1180")
    assert result["found"] is True
    assert result.get("ambiguous") is True
    assert len(result["flights"]) == 2


def test_get_flight_details_disambiguated_by_date():
    result = get_flight_details_impl(flight_number="AF1180", date="2026-12-10")
    assert result["found"] is True
    assert "ambiguous" not in result
    assert result["flight"]["departure"]["datetime"].startswith("2026-12-10")


def test_get_flight_details_by_flight_id():
    first = search_flights_impl("CDG", "LIS")["flights"][0]
    result = get_flight_details_impl(flight_id=first["flight_id"])
    assert result["found"] is True
    assert result["flight"]["flight_id"] == first["flight_id"]


def test_get_flight_details_not_found():
    result = get_flight_details_impl(flight_number="ZZ9999")
    assert result["found"] is False


def test_get_flight_details_missing_params():
    with pytest.raises(ValidationError):
        get_flight_details_impl()


# ---------- compare_flights ----------

def test_compare_flights_two_flights():
    result = compare_flights_impl(["TP453", "AF1704"])
    assert result["compared_count"] == 2
    assert result["cheapest_flight_number"] in ("TP453", "AF1704")
    assert result["fastest_flight_number"] in ("TP453", "AF1704")


def test_compare_flights_needs_at_least_two():
    with pytest.raises(ValidationError):
        compare_flights_impl(["TP453"])


def test_compare_flights_reports_not_found():
    result = compare_flights_impl(["TP453", "ZZ0000"])
    assert result["compared_count"] == 1
    assert "ZZ0000" in result["not_found"]


# ---------- list_airports ----------

def test_list_airports_by_city():
    result = list_airports_impl("Tokyo")
    assert result["count"] == 1
    assert result["airports"][0]["airport_code"] == "HND"


def test_list_airports_by_country():
    result = list_airports_impl("France")
    assert result["count"] == 1
    assert result["airports"][0]["airport_code"] == "CDG"


def test_list_airports_by_code():
    result = list_airports_impl("BKK")
    assert result["count"] == 1


def test_list_airports_empty_query():
    with pytest.raises(ValidationError):
        list_airports_impl("")


# ---------- cheapest_flights ----------

def test_cheapest_flights_sorted_and_limited():
    result = cheapest_flights_impl("CDG", "HND", limit=2)
    assert result["count"] == 2
    prices = [f["price"]["amount"] for f in result["flights"]]
    assert prices == sorted(prices)


def test_cheapest_flights_default_limit_is_five():
    result = cheapest_flights_impl("CDG", "HND", limit=None)
    assert result["count"] <= 5
