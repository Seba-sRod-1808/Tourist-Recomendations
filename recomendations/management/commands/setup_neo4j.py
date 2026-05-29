import uuid
from django.core.management.base import BaseCommand
from neomodel import install_all_labels, db


PLACES = [
    {"name": "Antigua Guatemala", "cost": 550.0, "popularity": 0.94, "cats": ["historia", "cultura", "colonial"]},
    {"name": "Lago Atitlan",      "cost": 400.0, "popularity": 0.91, "cats": ["naturaleza", "aventura"]},
    {"name": "Semuc Champey",     "cost": 350.0, "popularity": 0.87, "cats": ["naturaleza", "aventura"]},
    {"name": "Tikal, Peten",      "cost": 600.0, "popularity": 0.82, "cats": ["historia", "cultura", "naturaleza"]},
    {"name": "Rio Dulce",         "cost": 300.0, "popularity": 0.79, "cats": ["aventura", "naturaleza", "playa"]},
    {"name": "Monterrico",        "cost": 650.0, "popularity": 0.75, "cats": ["playa", "naturaleza"]},
    {"name": "Chichicastenango",  "cost": 250.0, "popularity": 0.72, "cats": ["cultura", "historia"]},
    {"name": "Livingston",        "cost": 350.0, "popularity": 0.68, "cats": ["playa", "cultura", "aventura"]},
]

CAREER_PREFERENCES = {
    "Ingenieria":     ["Tikal, Peten", "Semuc Champey", "Rio Dulce"],
    "Medicina":       ["Lago Atitlan", "Monterrico", "Livingston"],
    "Derecho":        ["Antigua Guatemala", "Chichicastenango"],
    "Administracion": ["Antigua Guatemala", "Lago Atitlan", "Monterrico"],
    "Arte":           ["Antigua Guatemala", "Chichicastenango", "Lago Atitlan"],
}


class Command(BaseCommand):
    help = "Instala constraints en Neo4j y opcionalmente carga datos de prueba"

    def add_arguments(self, parser):
        parser.add_argument(
            "--seed",
            action="store_true",
            help="Carga lugares, categorias y carreras de prueba en Neo4j",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Elimina TODOS los nodos antes de hacer seed",
        )

    def handle(self, *args, **options):
        self.stdout.write("Instalando constraints e indices...")
        install_all_labels()
        self.stdout.write(self.style.SUCCESS("Constraints e indices instalados"))

        if options["clear"]:
            db.cypher_query("MATCH (n) DETACH DELETE n")
            self.stdout.write(self.style.WARNING("Grafo limpiado"))

        if options["seed"]:
            self._seed()

    def _seed(self):
        self.stdout.write("Cargando datos de prueba...")

        # Categorias
        all_cats = {cat for p in PLACES for cat in p["cats"]}
        for cat in all_cats:
            db.cypher_query("MERGE (:Category {name: $name})", {"name": cat})

        # Lugares + relaciones HAS_CATEGORY
        for p in PLACES:
            # Generamos un UID si no existe para mantener consistencia con neomodel
            uid = str(uuid.uuid4())[:8]
            db.cypher_query(
                """
                MERGE (pl:Place {name: $name})
                ON CREATE SET pl.uid = $uid, pl.cost = $cost, pl.popularity = $popularity
                ON MATCH SET pl.cost = $cost, pl.popularity = $popularity
                """,
                {"name": p["name"], "uid": uid, "cost": p["cost"], "popularity": p["popularity"]},
            )
            for cat in p["cats"]:
                db.cypher_query(
                    """
                    MATCH (pl:Place {name: $place}), (c:Category {name: $cat})
                    MERGE (pl)-[:HAS_CATEGORY]->(c)
                    """,
                    {"place": p["name"], "cat": cat},
                )

        # Carreras y Preferencias
        for career, place_names in CAREER_PREFERENCES.items():
            db.cypher_query("MERGE (:Career {name: $name})", {"name": career})
            for place_name in place_names:
                db.cypher_query(
                    """
                    MATCH (cr:Career {name: $career}), (pl:Place {name: $place})
                    MERGE (cr)-[:PREFERS {weight: 1.0}]->(pl)
                    """,
                    {"career": career, "place": place_name},
                )

        # Estudiantes de prueba para Collaborative Filtering
        self.stdout.write("Creando estudiantes de prueba para simulacion...")
        test_students = [
            {"name": "Ana", "likes": ["historia", "cultura"], "visited": ["Antigua Guatemala", "Tikal, Peten"]},
            {"name": "Luis", "likes": ["naturaleza", "aventura"], "visited": ["Semuc Champey", "Lago Atitlan"]},
            {"name": "Marta", "likes": ["playa", "naturaleza"], "visited": ["Monterrico", "Rio Dulce"]},
        ]

        for s in test_students:
            uid = str(uuid.uuid4())[:8]
            db.cypher_query(
                "MERGE (st:Student {name: $name}) ON CREATE SET st.uid = $uid, st.django_user_id = $did",
                {"name": s["name"], "uid": uid, "did": hash(s["name"]) % 10000}
            )
            for cat in s["likes"]:
                db.cypher_query(
                    "MATCH (st:Student {name: $name}), (c:Category {name: $cat}) MERGE (st)-[:LIKES]->(c)",
                    {"name": s["name"], "cat": cat}
                )
            for place in s["visited"]:
                db.cypher_query(
                    "MATCH (st:Student {name: $name}), (p:Place {name: $place}) MERGE (st)-[:VISITED {rating: 5.0}]->(p)",
                    {"name": s["name"], "place": place}
                )

        places_count = db.cypher_query("MATCH (p:Place) RETURN count(p)")[0][0][0]
        cats_count   = db.cypher_query("MATCH (c:Category) RETURN count(c)")[0][0][0]
        careers_count = db.cypher_query("MATCH (c:Career) RETURN count(c)")[0][0][0]

        self.stdout.write(self.style.SUCCESS(
            f"Seed completo — {places_count} places, {cats_count} categorias, {careers_count} carreras"
        ))
