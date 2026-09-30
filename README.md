# Base de données exemple — Agent de Voyage IA

Jeu de données de démonstration correspondant au **modèle de données MongoDB**
décrit dans le cahier des charges *« Agent de Voyage IA — Application Flask +
Serveur MCP + MongoDB »* (section 3).

## Contenu

| Fichier                 | Collection MongoDB | Documents | Description                                   |
| ------------------------ | ------------------- | --------- | ---------------------------------------------- |
| `data/flights.json`      | `flights`           | 20        | Vols (schéma complet : compagnie, horaires, escales, prix, sièges, bagages) |
| `data/airports.json`     | `airports`          | 15        | Référentiel des aéroports utilisés par les vols |
| `data/airlines.json`     | `airlines`          | 13        | Référentiel des compagnies aériennes            |

Base cible par défaut : **`travel_agent_db`**.

Les vols couvrent plusieurs profils volontairement variés pour tester l'agent :
vols directs et vols avec escale, tarifs bas et longs courriers premium,
disponibilités faibles (`seats_available` bas, ex. 3 places) pour tester les
alertes de rareté, et deux dates différentes sur la route Paris → Tokyo pour
tester le tri par date/prix.

## Prérequis

```bash
pip install "pymongo[srv]"
```

Une instance MongoDB (locale via Docker, ou un cluster Azure DocumentDB /
MongoDB Atlas).

## Démarrage rapide (MongoDB local via Docker)

```bash
cp .env.example .env
docker compose up -d
python scripts/load_data.py --uri "mongodb://admin:Test1234@localhost:27017/?authSource=admin"
```

Sortie attendue :

```
  - flights: 20 document(s) inséré(s)
  - airports: 15 document(s) inséré(s)
  - airlines: 13 document(s) inséré(s)

Création des index recommandés (section 3.4 du cahier des charges) ...
  - flights: idx_route_date, idx_price, idx_airline
  - airports: idx_airport_code (unique)
  - airlines: idx_airline_code (unique)

Décompte final des documents :
  flights: 20
  airports: 15
  airlines: 13
```

## Utilisation avec Azure DocumentDB / MongoDB Atlas

```bash
python scripts/load_data.py --uri "mongodb+srv://<user>:<password>@<cluster>.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256" --db travel_agent_db
```

Ou en définissant les variables d'environnement `MONGODB_URI` / `MONGODB_DB`
puis en lançant simplement `python scripts/load_data.py`.

## Recharger les données depuis zéro

```bash
python scripts/load_data.py --reset
```

Vide les trois collections avant de les réinsérer (utile après une modification
des fichiers JSON).

## Index créés

| Collection | Index               | Champs                                                              | Usage                                  |
| ---------- | -------------------- | --------------------------------------------------------------------- | --------------------------------------- |
| `flights`  | `idx_route_date`      | `departure.airport_code`, `arrival.airport_code`, `departure.datetime` | Recherche principale (trajet + date)    |
| `flights`  | `idx_price`           | `price.amount`                                                        | Tri/filtrage par budget                 |
| `flights`  | `idx_airline`         | `airline.code`                                                        | Filtrage par compagnie                  |
| `airports` | `idx_airport_code`    | `airport_code` (unique)                                               | Résolution rapide code IATA → aéroport  |
| `airlines` | `idx_airline_code`    | `code` (unique)                                                       | Résolution rapide code → compagnie      |

## Exemples de requêtes à tester avec l'agent

- « Trouves-moi un vol Paris → Tokyo fin novembre, budget max 700 € »
- « Quels sont les vols directs vers Lisbonne en octobre ? »
- « Compare les vols AF1180 et EK071 »
- « Quel est le vol le moins cher pour Bangkok en décembre ? »
- « Combien de places restent sur le vol AF1180 du 10 décembre ? »

> Les données sont **synthétiques**, générées à des fins de démonstration
> uniquement, et ne reflètent pas de disponibilités ou tarifs réels.

## Licence

Projet pédagogique AFPA.