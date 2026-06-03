import uuid
from django.core.management.base import BaseCommand
from neomodel import install_all_labels, db

PLACES = [
    {"name": "Antigua Guatemala", "cost": 550.0, "popularity": 0.94, "cats": ["Historia", "Cultura", "Gastronomía"], "lat": 14.5573, "lng": -90.7332, "description": "Hermosa ciudad colonial famosa por su arquitectura barroca, vibrantes calles empedradas y ruinas históricas, todo rodeado de imponentes volcanes."},
    {"name": "Lago Atitlan",      "cost": 400.0, "popularity": 0.91, "cats": ["Naturaleza", "Cultura", "Gastronomía"], "lat": 14.6907, "lng": -91.2025, "description": "Considerado uno de los lagos más hermosos del mundo, situado en un enorme cráter y rodeado de tres majestuosos volcanes y pintorescos pueblos mayas."},
    {"name": "Semuc Champey",     "cost": 350.0, "popularity": 0.87, "cats": ["Naturaleza", "Playas y Ríos", "Aventura"], "lat": 15.5539, "lng": -89.9572, "description": "Espectacular monumento natural oculto en la selva de Alta Verapaz, famoso por sus piscinas naturales de agua turquesa cristalina escalonadas sobre el río Cahabón."},
    {"name": "Tikal, Peten",      "cost": 600.0, "popularity": 0.82, "cats": ["Historia", "Arqueología", "Naturaleza"], "lat": 17.2223, "lng": -89.6237, "description": "Antigua metrópolis de la civilización maya. Sus gigantescas pirámides y templos se alzan por encima del denso dosel de la selva tropical."},
    {"name": "Rio Dulce",         "cost": 300.0, "popularity": 0.79, "cats": ["Naturaleza", "Playas y Ríos", "Historia"], "lat": 15.6558, "lng": -88.9416, "description": "Impresionante río que conecta el Lago de Izabal con el Mar Caribe, navegando a través de un cañón espectacular lleno de exuberante vegetación."},
    {"name": "Monterrico",        "cost": 650.0, "popularity": 0.75, "cats": ["Playas y Ríos", "Naturaleza", "Gastronomía"], "lat": 13.9189, "lng": -90.4811, "description": "Reserva natural en la costa del Pacífico, conocida por sus playas de arena negra volcánica, relajantes canales de manglares y conservación de tortugas."},
    {"name": "Chichicastenango",  "cost": 250.0, "popularity": 0.72, "cats": ["Cultura", "Historia"], "lat": 14.9427, "lng": -91.1114, "description": "Hogar del mercado tradicional indígena más vibrante de la región, un lugar perfecto para sumergirse en la cultura maya viva y adquirir artesanías únicas."},
    {"name": "Livingston",        "cost": 350.0, "popularity": 0.68, "cats": ["Playas y Ríos", "Cultura", "Gastronomía"], "lat": 15.8278, "lng": -88.7500, "description": "Pintoresco pueblo caribeño accesible solo por barco. Es el corazón de la cultura Garífuna en Guatemala, ofreciendo deliciosa gastronomía y ritmos únicos."},
    {"name": "Quetzaltenango",    "cost": 300.0, "popularity": 0.85, "cats": ["Cultura", "Historia", "Gastronomía"], "lat": 14.8347, "lng": -91.5181, "description": "Conocida como Xela, es una ciudad con un clima fresco y acogedor, rica en historia, hermosa arquitectura neoclásica y rodeada de aguas termales."},
    {"name": "Huehuetenango",     "cost": 450.0, "popularity": 0.80, "cats": ["Naturaleza", "Aventura"], "lat": 15.3195, "lng": -91.4702, "description": "Espectacular región montañosa en el occidente del país, puerta de entrada a la imponente cordillera de los Cuchumatanes y cenotes cristalinos."},
    {"name": "Castillo de San Felipe", "cost": 200.0, "popularity": 0.78, "cats": ["Historia", "Cultura"], "lat": 15.6377, "lng": -88.9942, "description": "Fortaleza histórica colonial ubicada estratégicamente en la entrada del Lago de Izabal, construida por los españoles para defender la zona de piratas."}, 
    {"name": "Irtra Retalhuleu",  "cost": 700.0, "popularity": 0.95, "cats": ["Aventura", "Gastronomía"], "lat": 14.6158, "lng": -91.6844, "description": "El complejo de parques de diversiones y acuáticos más grande de Centroamérica. Ideal para un fin de semana lleno de adrenalina, sol y mucha diversión."}, 
    {"name": "Volcan de Acatenango", "cost": 400.0, "popularity": 0.88, "cats": ["Aventura", "Naturaleza"], "lat": 14.5008, "lng": -90.8753, "description": "Un desafío épico de montañismo que recompensa con vistas espectaculares y la oportunidad única de dormir viendo las erupciones del vecino Volcán de Fuego."}, 
    {"name": "Fuentes Georginas", "cost": 150.0, "popularity": 0.82, "cats": ["Naturaleza", "Gastronomía"], "lat": 14.7497, "lng": -91.4806, "description": "Relajantes piscinas de aguas termales calentadas naturalmente por la actividad volcánica, inmersas en un espeso, frío y místico bosque nuboso."},
    {"name": "Crater Azul",       "cost": 500.0, "popularity": 0.84, "cats": ["Naturaleza", "Playas y Ríos", "Aventura"], "lat": 16.6347, "lng": -90.2332, "description": "Un oasis surrealista escondido en Petén. Sus aguas son tan transparentes y azules que los increíbles jardines subacuáticos parecen estar flotando en el aire."}, 
    {"name": "Hun Nal Ye",        "cost": 300.0, "popularity": 0.75, "cats": ["Naturaleza", "Aventura", "Playas y Ríos"], "lat": 15.6547, "lng": -90.3121, "description": "Un paraíso ecológico en Alta Verapaz que ofrece saltos a cenotes turquesas, senderismo, cabalgatas, canopy y exploración de cuevas místicas."}, 
    {"name": "Parque Naciones Unidas", "cost": 50.0, "popularity": 0.60, "cats": ["Naturaleza", "Cultura"], "lat": 14.4754, "lng": -90.6067, "description": "Un escape natural muy cercano a la ciudad, con senderos arbolados, churrasqueras, réplicas arqueológicas y miradores hacia el Lago de Amatitlán."}, 
    {"name": "Laguna del Pino",     "cost": 100.0, "popularity": 0.55, "cats": ["Naturaleza", "Aventura"], "lat": 14.3461, "lng": -90.3958, "description": "Parque nacional ideal para una escapada rápida. Perfecto para hacer un picnic, remar en kayak, nadar o simplemente relajarse bajo la sombra de los pinos."}, 
    {"name": "Mixco Viejo",         "cost": 150.0, "popularity": 0.50, "cats": ["Historia", "Arqueología"], "lat": 14.8725, "lng": -90.6625, "description": "Antigua capital del reino Poqomam, una impresionante fortaleza maya construida estratégicamente sobre colinas rodeadas de profundos barrancos."}, 
    {"name": "Iximché",             "cost": 150.0, "popularity": 0.70, "cats": ["Historia", "Arqueología"], "lat": 14.7350, "lng": -90.9944, "description": "Antigua capital del reino Kaqchikel y un sitio arqueológico fascinante e histórico donde aún hoy se practican ceremonias y rituales mayas vivos."}, 
    {"name": "Hobbitenango",        "cost": 250.0, "popularity": 0.85, "cats": ["Aventura", "Gastronomía", "Cultura"], "lat": 14.5947, "lng": -90.7103, "description": "Eco-parque temático mágico inspirado en la Comarca, en lo alto de las montañas. Disfruta de vistas increíbles, juegos de feria, miradores y buena comida."}, 
    {"name": "Volcan de Pacaya",    "cost": 200.0, "popularity": 0.88, "cats": ["Aventura", "Naturaleza"], "lat": 14.3822, "lng": -90.6014, "description": "Un volcán activo de ascenso amigable, famoso por sus paisajes de roca volcánica donde los visitantes pueden asar masmelos con el calor geotérmico."}, 
    {"name": "Finca El Amate",      "cost": 150.0, "popularity": 0.65, "cats": ["Naturaleza", "Aventura"], "lat": 14.3989, "lng": -90.5892, "description": "Reserva natural privada en las faldas del Volcán de Pacaya. Ofrece senderos de lava solidificada y praderas excepcionales para acampar bajo las estrellas."}, 
    {"name": "Cataratas Tatasirire","cost": 250.0, "popularity": 0.58, "cats": ["Aventura", "Naturaleza"], "lat": 14.5167, "lng": -89.9833, "description": "Parque ecológico en Jalapa que cuenta con impresionantes cascadas, densos bosques, rutas de canopy y áreas seguras equipadas para acampar."}, 
    {"name": "Laguna de Ayarza",    "cost": 300.0, "popularity": 0.62, "cats": ["Naturaleza", "Aventura"], "lat": 14.4167, "lng": -90.1167, "description": "Un imponente lago de aguas azules profundas formado en el fondo de un antiguo cráter colapsado, excelente para el buceo, la pesca y la desconexión total."}, 
    {"name": "Volcan de Ipala",     "cost": 200.0, "popularity": 0.65, "cats": ["Naturaleza", "Aventura"], "lat": 14.5500, "lng": -89.6333, "description": "Ubicado en el oriente de Guatemala, ofrece un ascenso relativamente fácil que culmina en un cráter que alberga una hermosa y apacible laguna esmeralda."}, 
    {"name": "Biotopo del Quetzal", "cost": 150.0, "popularity": 0.75, "cats": ["Naturaleza"], "lat": 15.2150, "lng": -90.2167, "description": "Santuario natural en Baja Verapaz dedicado a proteger al ave nacional. Sus senderos te sumergen en un denso y místico bosque nuboso lleno de vida."}, 
    {"name": "San Juan Comalapa",   "cost": 100.0, "popularity": 0.55, "cats": ["Cultura", "Historia"], "lat": 14.7333, "lng": -90.8833, "description": "Conocida como la 'Florencia de América', es cuna de talentosos pintores de arte naíf, músicos y herencia cultural, destacando sus enormes murales históricos."}, 
    {"name": "Cuevas de Candelaria","cost": 350.0, "popularity": 0.60, "cats": ["Aventura", "Naturaleza"], "lat": 15.8667, "lng": -89.9167, "description": "Una de las redes de cavernas más extensas de la región. Alberga un espectacular río subterráneo que los antiguos mayas consideraban la entrada al inframundo."}, 
    {"name": "El Paredon",          "cost": 450.0, "popularity": 0.82, "cats": ["Playas y Ríos", "Aventura", "Gastronomía"], "lat": 13.9167, "lng": -91.1333, "description": "El destino de surf de mayor crecimiento en el país. Un pintoresco pueblo con calles de arena, ambiente relajado, vibra bohemia y atardeceres dorados."}, 
    {"name": "Tak'alik Ab'aj",      "cost": 150.0, "popularity": 0.68, "cats": ["Arqueología", "Historia"], "lat": 14.6333, "lng": -91.7333, "description": "Un fascinante parque arqueológico en Retalhuleu que es testigo de la transición histórica entre la cultura Olmeca y el florecimiento de la civilización Maya."}, 
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
                ON CREATE SET pl.uid = $uid, pl.cost = $cost, pl.popularity = $popularity, pl.lat = $lat, pl.lng = $lng, pl.description = $description
                ON MATCH SET pl.cost = $cost, pl.popularity = $popularity, pl.lat = $lat, pl.lng = $lng, pl.description = $description
                """,
                {"name": p["name"], "uid": uid, "cost": p["cost"], "popularity": p["popularity"], "lat": p["lat"], "lng": p["lng"], "description": p["description"]},
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