#!/usr/bin/env python3
"""
load_data.py — Charge la base de données exemple "travel_agent_db" décrite
dans le cahier des charges "Agent de Voyage IA" (Flask + MCP + MongoDB).

Importe les collections destinations/flights/airlines/airports depuis
data/*.json et crée les index recommandés (section 3.4 du cahier des charges).

Usage :
    pip install "pymongo[srv]"
    python scripts/load_data.py
    python scripts/load_data.py --reset    # peuple la base (vide chaque collection avant)
    python scripts/load_data.py --uri "mongodb://localhost:27017" --db travel_agent_db
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from pymongo import MongoClient, ASCENDING
except ImportError:
    print("pymongo n'est pas installé. Lancez : pip install \"pymongo[srv]\"")
    sys.exit(1)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

COLLECTIONS = {
    "flights": "flights.json",
    "airports": "airports.json",
    "airlines": "airlines.json",
}


def load_json(filename):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"  ! Fichier introuvable, ignoré : {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Charge la base de données exemple de l'agent de voyage")
    parser.add_argument(
        "--uri",
        default=os.environ.get("MONGODB_URI", "mongodb://localhost:27017"),
        help="Chaîne de connexion MongoDB/DocumentDB (défaut : variable MONGODB_URI ou mongodb://localhost:27017)",
    )
    parser.add_argument(
        "--db",
        default=os.environ.get("MONGODB_DB", "travel_agent_db"),
        help="Nom de la base de données (défaut : travel_agent_db)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Vide les collections avant de les recharger",
    )
    args = parser.parse_args()

    print(f"Connexion à {args.uri} ...")
    client = MongoClient(args.uri, serverSelectionTimeoutMS=8000)
    try:
        client.admin.command("ping")
    except Exception as exc:
        print(f"Impossible de joindre le serveur MongoDB/DocumentDB : {exc}")
        sys.exit(1)

    db = client[args.db]
    print(f"Base cible : {args.db}\n")

    for coll_name, filename in COLLECTIONS.items():
        docs = load_json(filename)
        collection = db[coll_name]

        if args.reset:
            deleted = collection.delete_many({}).deleted_count
            if deleted:
                print(f"  - {coll_name}: {deleted} document(s) supprimé(s) avant rechargement")

        if not docs:
            continue

        result = collection.insert_many(docs)
        print(f"  - {coll_name}: {len(result.inserted_ids)} document(s) inséré(s)")

    print("\nCréation des index recommandés (section 3.4 du cahier des charges) ...")

    flights = db["flights"]
    flights.create_index(
        [
            ("departure.airport_code", ASCENDING),
            ("arrival.airport_code", ASCENDING),
            ("departure.datetime", ASCENDING),
        ],
        name="idx_route_date",
    )
    flights.create_index([("price.amount", ASCENDING)], name="idx_price")
    flights.create_index([("airline.code", ASCENDING)], name="idx_airline")
    print("  - flights: idx_route_date, idx_price, idx_airline")

    db["airports"].create_index([("airport_code", ASCENDING)], unique=True, name="idx_airport_code")
    db["airlines"].create_index([("code", ASCENDING)], unique=True, name="idx_airline_code")
    print("  - airports: idx_airport_code (unique)")
    print("  - airlines: idx_airline_code (unique)")

    print("\nDécompte final des documents :")
    for coll_name in COLLECTIONS:
        count = db[coll_name].count_documents({})
        print(f"  {coll_name}: {count}")

    print("\nTerminé.")


if __name__ == "__main__":
    main()
