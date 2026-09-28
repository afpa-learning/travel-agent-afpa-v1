"""
Serveur MCP de l'agent de voyage — expose en lecture seule la base
travel_agent_db (collections flights, airports) décrite dans le cahier des
charges "Agent de Voyage IA — Application Flask + Serveur MCP + MongoDB".

Lancement :
    python -m serveur-mcp-local.server

Configuration : voir serveur-mcp-local/config.py et .env.example
(MONGODB_URI, MONGODB_DB, MCP_MAX_RESULTS).

Dépendance SDK : mcp>=2,<3 (API MCPServer ; voir requirements.txt).
Le décorateur @mcp.tool() a la même signature qu'avec l'ancien FastMCP (v1).
"""

from typing import List, Optional

from mcp.server.mcpserver import MCPServer

from tools.search_flights import search_flights_impl
from tools.flight_details import get_flight_details_impl
from tools.compare_flights import compare_flights_impl
from tools.list_airports import list_airports_impl
from tools.cheapest_flights import cheapest_flights_impl

mcp = MCPServer(
    "travel-agent-mcp",
    instructions=(
        "Serveur MCP en lecture seule pour un agent de voyage. Donne accès à "
        "une base de vols (travel_agent_db) et à un référentiel d'aéroports. "
        "Utilise toujours ces outils pour toute donnée de vol (prix, horaires, "
        "disponibilités) : ne jamais inventer ces informations."
    ),
)


@mcp.tool()
def search_flights(
    origin: str,
    destination: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_price: Optional[float] = None,
    max_stops: Optional[int] = None,
    limit: Optional[int] = None,
) -> dict:
    """Recherche des vols entre deux aéroports (codes IATA à 3 lettres, ex. CDG, HND).

    Filtres optionnels : date_from/date_to (AAAA-MM-JJ), max_price (budget
    maximum), max_stops (nombre d'escales maximum). Résultats triés par prix
    croissant, limités à MAX_RESULTS (20 par défaut).
    """
    return search_flights_impl(origin, destination, date_from, date_to, max_price, max_stops, limit)


@mcp.tool()
def get_flight_details(
    flight_id: Optional[str] = None,
    flight_number: Optional[str] = None,
    date: Optional[str] = None,
) -> dict:
    """Retourne le détail complet d'un vol, par flight_id (identifiant interne)
    ou par flight_number. Un même flight_number pouvant exister à plusieurs
    dates, précise `date` (AAAA-MM-JJ) en cas d'ambiguïté.
    """
    return get_flight_details_impl(flight_id, flight_number, date)


@mcp.tool()
def compare_flights(flights: List[str]) -> dict:
    """Compare 2 à 6 vols (prix, durée, escales, sièges disponibles) à partir
    d'une liste de flight_id et/ou de flight_number. Indique le vol le moins
    cher et le vol le plus rapide parmi ceux comparés.
    """
    return compare_flights_impl(flights)


@mcp.tool()
def list_airports(query: str, limit: Optional[int] = None) -> dict:
    """Recherche des aéroports par ville, pays ou code IATA (ex. 'Tokyo',
    'Japon', 'HND'). Utile pour résoudre un nom de ville en code aéroport
    avant d'appeler search_flights.
    """
    return list_airports_impl(query, limit)


@mcp.tool()
def cheapest_flights(
    origin: str,
    destination: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """Retourne les vols les moins chers entre deux aéroports, éventuellement
    sur une plage de dates flexible (date_from/date_to au format AAAA-MM-JJ).
    """
    return cheapest_flights_impl(origin, destination, date_from, date_to, limit)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
