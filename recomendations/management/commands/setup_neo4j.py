import uuid
from django.core.management.base import BaseCommand
from neomodel import install_all_labels, db


PLACES = [
    # Famosos
    {"name": "Antigua Guatemala", "cost": 550.0, "popularity": 0.94, "cats": ["Historia", "Cultura", "Gastronomía"], "lat": 14.5573, "lng": -90.7332},
    {"name": "Lago Atitlan",      "cost": 400.0, "popularity": 0.91, "cats": ["Naturaleza", "Cultura", "Gastronomía"], "lat": 14.6907, "lng": -91.2025},
    {"name": "Semuc Champey",     "cost": 350.0, "popularity": 0.87, "cats": ["Naturaleza", "Playas y Ríos", "Aventura"], "lat": 15.5539, "lng": -89.9572},
    {"name": "Tikal, Peten",      "cost": 600.0, "popularity": 0.82, "cats": ["Historia", "Arqueología", "Naturaleza"], "lat": 17.2223, "lng": -89.6237},
    {"name": "Rio Dulce",         "cost": 300.0, "popularity": 0.79, "cats": ["Naturaleza", "Playas y Ríos", "Historia"], "lat": 15.6558, "lng": -88.9416},
    {"name": "Monterrico",        "cost": 650.0, "popularity": 0.75, "cats": ["Playas y Ríos", "Naturaleza", "Gastronomía"], "lat": 13.9189, "lng": -90.4811},
    {"name": "Chichicastenango",  "cost": 250.0, "popularity": 0.72, "cats": ["Cultura", "Historia"], "lat": 14.9427, "lng": -91.1114},
    {"name": "Livingston",        "cost": 350.0, "popularity": 0.68, "cats": ["Playas y Ríos", "Cultura", "Gastronomía"], "lat": 15.8278, "lng": -88.7500},
    {"name": "Quetzaltenango",    "cost": 300.0, "popularity": 0.85, "cats": ["Cultura", "Historia", "Gastronomía"], "lat": 14.8347, "lng": -91.5181},
    {"name": "Huehuetenango",     "cost": 450.0, "popularity": 0.80, "cats": ["Naturaleza", "Aventura"], "lat": 15.3195, "lng": -91.4702},
    {"name": "Castillo de San Felipe", "cost": 200.0, "popularity": 0.78, "cats": ["Historia", "Cultura"], "lat": 15.6377, "lng": -88.9942},
    {"name": "Irtra Retalhuleu",  "cost": 700.0, "popularity": 0.95, "cats": ["Aventura", "Gastronomía"], "lat": 14.6158, "lng": -91.6844},
    {"name": "Volcan de Acatenango", "cost": 400.0, "popularity": 0.88, "cats": ["Aventura", "Naturaleza"], "lat": 14.5008, "lng": -90.8753},
    {"name": "Fuentes Georginas", "cost": 150.0, "popularity": 0.82, "cats": ["Naturaleza", "Gastronomía"], "lat": 14.7497, "lng": -91.4806},
    {"name": "Crater Azul",       "cost": 500.0, "popularity": 0.84, "cats": ["Naturaleza", "Playas y Ríos", "Aventura"], "lat": 16.6347, "lng": -90.2332},
    {"name": "Hun Nal Ye",        "cost": 300.0, "popularity": 0.75, "cats": ["Naturaleza", "Aventura", "Playas y Ríos"], "lat": 15.6547, "lng": -90.3121},
    {"name": "Parque Naciones Unidas", "cost": 50.0, "popularity": 0.60, "cats": ["Naturaleza", "Cultura"], "lat": 14.4754, "lng": -90.6067},
    {"name": "Laguna del Pino",     "cost": 100.0, "popularity": 0.55, "cats": ["Naturaleza", "Aventura"], "lat": 14.3461, "lng": -90.3958},
    {"name": "Mixco Viejo",         "cost": 150.0, "popularity": 0.50, "cats": ["Historia", "Arqueología"], "lat": 14.8725, "lng": -90.6625},
    {"name": "Iximché",             "cost": 150.0, "popularity": 0.70, "cats": ["Historia", "Arqueología"], "lat": 14.7350, "lng": -90.9944},
    {"name": "Hobbitenango",        "cost": 250.0, "popularity": 0.85, "cats": ["Aventura", "Gastronomía", "Cultura"], "lat": 14.5947, "lng": -90.7103},
    {"name": "Volcan de Pacaya",    "cost": 200.0, "popularity": 0.88, "cats": ["Aventura", "Naturaleza"], "lat": 14.3822, "lng": -90.6014},
    {"name": "Finca El Amate",      "cost": 150.0, "popularity": 0.65, "cats": ["Naturaleza", "Aventura"], "lat": 14.3989, "lng": -90.5892},
    {"name": "Cataratas Tatasirire","cost": 250.0, "popularity": 0.58, "cats": ["Aventura", "Naturaleza"], "lat": 14.5167, "lng": -89.9833},
    {"name": "Laguna de Ayarza",    "cost": 300.0, "popularity": 0.62, "cats": ["Naturaleza", "Aventura"], "lat": 14.4167, "lng": -90.1167},
    {"name": "Volcan de Ipala",     "cost": 200.0, "popularity": 0.65, "cats": ["Naturaleza", "Aventura"], "lat": 14.5500, "lng": -89.6333},
    {"name": "Biotopo del Quetzal", "cost": 150.0, "popularity": 0.75, "cats": ["Naturaleza"], "lat": 15.2150, "lng": -90.2167},
    {"name": "San Juan Comalapa",   "cost": 100.0, "popularity": 0.55, "cats": ["Cultura", "Historia"], "lat": 14.7333, "lng": -90.8833},
    {"name": "Cuevas de Candelaria","cost": 350.0, "popularity": 0.60, "cats": ["Aventura", "Naturaleza"], "lat": 15.8667, "lng": -89.9167},
    {"name": "El Paredon",          "cost": 450.0, "popularity": 0.82, "cats": ["Playas y Ríos", "Aventura", "Gastronomía"], "lat": 13.9167, "lng": -91.1333},
    {"name": "Tak'alik Ab'aj",      "cost": 150.0, "popularity": 0.68, "cats": ["Arqueología", "Historia"], "lat": 14.6333, "lng": -91.7333},
]

CAREER_PREFERENCES = {
    "Ingenieria": ["Tikal, Peten", "Semuc Champey", "Volcan de Pacaya"],
    "Ingeniería Mecánica": ["Volcan de Acatenango", "Semuc Champey", "Finca El Amate"],
    "Ingeniería Mecánica Industrial": ["Irtra Retalhuleu", "Antigua Guatemala", "Hobbitenango"],
    "Ingeniería En Sistemas": ["Crater Azul", "Tikal, Peten", "Mixco Viejo"],
    "Sistemas": ["Tikal, Peten", "Rio Dulce", "Mixco Viejo"],
    "Ingeniería En Informatica Y Sistemas": ["Tikal, Peten", "Lago Atitlan", "Iximché"],
    "Ingeniería En Ciencias De La Computación Y Tecnologías De La Información": ["Tikal, Peten", "Volcan de Pacaya", "Crater Azul"],
    "Medicina": ["Fuentes Georginas", "Lago Atitlan", "Monterrico"],
    "Nutrición": ["Lago Atitlan", "Biotopo del Quetzal", "Fuentes Georginas"],
    "Nutricion": ["Lago Atitlan", "Biotopo del Quetzal", "Fuentes Georginas"],
    "Bioquímica Y Microbiología": ["Hun Nal Ye", "Crater Azul", "Rio Dulce"],
    "Biotecnología Industrial": ["Semuc Champey", "Rio Dulce", "Biotopo del Quetzal"],
    "Psicología Clínica": ["Lago Atitlan", "Antigua Guatemala", "Laguna del Pino"],
    "Licenciatura En Física Aplicada": ["Volcan de Pacaya", "Lago Atitlan", "Cataratas Tatasirire"],
    "Derecho": ["Antigua Guatemala", "Quetzaltenango", "Iximché"],
    "Relaciones Internacionales": ["Castillo de San Felipe", "Antigua Guatemala", "Tikal, Peten"],
    "Ciencias Jurídicas Y Sociales": ["Antigua Guatemala", "Quetzaltenango", "San Juan Comalapa"],
    "Administracion": ["Irtra Retalhuleu", "Antigua Guatemala", "Monterrico"],
    "Licenciatura En Administración De Empresas": ["Tikal, Peten", "Antigua Guatemala", "Irtra Retalhuleu"],
    "Marketing": ["Hobbitenango", "El Paredon", "Antigua Guatemala"],
    "Arte": ["San Juan Comalapa", "Antigua Guatemala", "Quetzaltenango"],
    "Diseño Gráfico": ["Hobbitenango", "Lago Atitlan", "Antigua Guatemala"],
    "Diseño Grafico": ["Hobbitenango", "Lago Atitlan", "Antigua Guatemala"],
    "Arquitectura": ["Tikal, Peten", "Mixco Viejo", "Antigua Guatemala"],
    "Diseño Digital": ["Quetzaltenango", "Hobbitenango", "Antigua Guatemala"],
    "Diseño Industrial": ["Quetzaltenango", "Antigua Guatemala", "Irtra Retalhuleu"],
    "Diseño De Interiores": ["Antigua Guatemala", "Lago Atitlan", "Hobbitenango"],
    "Arquitectura Y Diseño De Interiores": ["Antigua Guatemala", "Iximché", "Tikal, Peten"],
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
            uid = str(uuid.uuid4())[:8]
            db.cypher_query(
                """
                MERGE (pl:Place {name: $name})
                ON CREATE SET pl.uid = $uid, pl.cost = $cost, pl.popularity = $popularity, pl.lat = $lat, pl.lng = $lng
                ON MATCH SET pl.cost = $cost, pl.popularity = $popularity, pl.lat = $lat, pl.lng = $lng
                """,
                {"name": p["name"], "uid": uid, "cost": p["cost"], "popularity": p["popularity"], "lat": p["lat"], "lng": p["lng"]},
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
            {"name": "Ana", "likes": ["Historia", "Cultura"], "visited": ["Antigua Guatemala", "Tikal, Peten"]},
            {"name": "Luis", "likes": ["Naturaleza", "Aventura"], "visited": ["Semuc Champey", "Lago Atitlan"]},
            {"name": "Marta", "likes": ["Playas y Ríos", "Naturaleza"], "visited": ["Monterrico", "Rio Dulce"]},
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
