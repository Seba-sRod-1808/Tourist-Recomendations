"""
PROCESO: Capa de Consultas y Mutaciones
DESCRIPCIÓN: Implementa las consultas Cypher para interactuar con la base de datos de grafos.
Incluye funciones para gestionar el perfil del estudiante, registrar visitas,
y recuperar información detallada de destinos y recomendaciones.
"""

from neomodel import db
from recomendations.services.recomendation_service import RecommendationService

_service = RecommendationService()

def get_recommendations(django_user_id=None, limit=6):
    if django_user_id is None:
        return _service._fallback_popular(limit)
    return _service.recommend(student_uid=django_user_id, limit=limit)

def create_student(django_user_id: int, name: str) -> None:
    db.cypher_query(
        """
        MERGE (s:Student {django_user_id: $uid})
        SET s.name = $name
        """,
        {"uid": django_user_id, "name": name},
    )

def set_student_preferences(
    django_user_id: int,
    carrera: str,
    universidad: str,
    categorias: list,
    presupuesto: str,
) -> None:
    budget_map = {
        "Menos de Q200": 200.0,
        "Q200–Q500": 500.0,
        "Q500–Q1000": 1000.0,
        "Más de Q1000": 2000.0
    }
    budget_val = budget_map.get(presupuesto, 500.0)

    db.cypher_query(
        """
        MATCH (s:Student {django_user_id: $uid})
        MERGE (c:Career {name: $carrera})
        MERGE (s)-[:STUDIES]->(c)
        SET s.universidad = $universidad, s.presupuesto = $presupuesto, s.budget = $budget
        """,
        {"uid": django_user_id, "carrera": carrera, "universidad": universidad, "presupuesto": presupuesto, "budget": budget_val},
    )

    db.cypher_query(
        "MATCH (s:Student {django_user_id: $uid})-[r:LIKES]->(:Category) DELETE r",
        {"uid": django_user_id},
    )
    for cat in categorias:
        db.cypher_query(
            """
            MATCH (s:Student {django_user_id: $uid})
            MERGE (c:Category {name: $cat})
            MERGE (s)-[:LIKES {weight: 1.0}]->(c)
            """,
            {"uid": django_user_id, "cat": cat},
        )

def add_review(django_user_id: int, place_uid: str, rating: float, comment: str = ""):
    db.cypher_query(
        """
        MATCH (s:Student {django_user_id: $uid})
        MATCH (p:Place {uid: $p_uid})
        MERGE (s)-[r:VISITED]->(p)
        SET r.rating    = $rating,
            r.comment   = $comment,
            r.timestamp = datetime()
        WITH p
        MATCH (:Student)-[all_r:VISITED]->(p)
        WITH p, avg(all_r.rating) AS avg_rating
        SET p.popularity = avg_rating / 5.0
        """,
        {"uid": django_user_id, "p_uid": place_uid, "rating": rating, "comment": comment},
    )

def get_place_details_by_uid(place_uid: str):
    query = """
    MATCH (p:Place {uid: $uid})
    OPTIONAL MATCH (p)-[:HAS_CATEGORY]->(c:Category)
    RETURN p.uid, p.name, p.cost, p.popularity, p.lat, p.lng, collect(c.name)
    """
    results, meta = db.cypher_query(query, {'uid': place_uid})
    if not results or not results[0][0]:
        return None
    
    row = results[0]
    categorias_lista = row[6] if row[6] else []
    
    return {
        'uid': row[0],
        'name': row[1],
        'cost': row[2],
        'popularity': row[3],
        'lat': row[4],
        'lng': row[5],
        'categories': categorias_lista,
        'category': ' '.join(categorias_lista) if categorias_lista else 'General',
        'tag': categorias_lista[0].capitalize() if categorias_lista else 'Destino',
        'match_reason': 'Sugerido por nuestro algoritmo basado en tus preferencias.',
        'image': RecommendationService()._get_image(row[1]) 
    }

def get_all_places():
    query = """
    MATCH (p:Place)
    OPTIONAL MATCH (p)-[:HAS_CATEGORY]->(c:Category)
    RETURN p.uid, p.name, p.cost, p.popularity, p.lat, p.lng, collect(c.name)
    """
    results, meta = db.cypher_query(query)
    
    places = []
    for row in results:
        categorias_lista = row[6] if row[6] else []
        places.append({
            'uid': row[0],
            'name': row[1],
            'cost': row[2],
            'score': int((row[3] or 0) * 100),
            'lat': row[4],
            'lng': row[5],
            'categories': categorias_lista,
            'category': ' '.join(categorias_lista),
            'tag': categorias_lista[0].capitalize() if categorias_lista else "Destino",
            'image': RecommendationService()._get_image(row[1])
        })
    return places

def get_visited_places(django_user_id):
    query = """
    MATCH (s:Student {django_user_id: $user_id})-[r:VISITED]->(p:Place)
    RETURN p.uid AS uid, 
           p.name AS name, 
           r.rating AS rating, 
           r.timestamp AS date
    """
    results, meta = db.cypher_query(query, {'user_id': django_user_id})
    
    visited = []
    for row in results:
        visited.append({
            'uid': row[0],
            'name': row[1],
            'image': RecommendationService()._get_image(row[1]),
            'rating': row[2], 
            'date': row[3]
        })
    return visited

def add_favorite(django_user_id: int, place_uid: str):
    # Aseguramos que el estudiante exista y vinculamos al lugar si existe
    query = """
    MERGE (s:Student {django_user_id: $uid})
    WITH s
    MATCH (p:Place {uid: $p_uid})
    MERGE (s)-[:FAVORITED]->(p)
    RETURN p.name
    """
    results, _ = db.cypher_query(query, {"uid": django_user_id, "p_uid": place_uid})
    
    if not results:
        # Si no hubo resultados, es porque el lugar no existe en Neo4j (posiblemente un MOCK)
        # Intentamos buscarlo por nombre si el UID es de un solo dígito (MOCK)
        mock_map = {
            '1': 'Antigua Guatemala',
            '2': 'Lago Atitlan',
            '3': 'Semuc Champey',
            '4': 'Tikal, Peten',
            '5': 'Rio Dulce',
            '6': 'Monterrico'
        }
        name = mock_map.get(place_uid)
        if name:
            db.cypher_query(
                """
                MERGE (s:Student {django_user_id: $uid})
                WITH s
                MATCH (p:Place {name: $name})
                MERGE (s)-[:FAVORITED]->(p)
                """,
                {"uid": django_user_id, "name": name}
            )

def remove_favorite(django_user_id: int, place_uid: str):
    db.cypher_query(
        """
        MATCH (s:Student {django_user_id: $uid})-[r:FAVORITED]->(p:Place {uid: $p_uid})
        DELETE r
        """,
        {"uid": django_user_id, "p_uid": place_uid}
    )

def get_favorites(django_user_id: int):
    rows, _ = db.cypher_query(
        """
        MATCH (s:Student {django_user_id: $uid})-[:FAVORITED]->(p:Place)
        OPTIONAL MATCH (p)-[:HAS_CATEGORY]->(c:Category)
        RETURN p.uid, p.name, coalesce(p.cost, 0), collect(DISTINCT c.name), coalesce(p.popularity, 0)
        """,
        {"uid": django_user_id}
    )
    return rows

def get_student_profile(django_user_id: int):
    rows, _ = db.cypher_query(
        """
        MATCH (s:Student {django_user_id: $uid})
        OPTIONAL MATCH (s)-[:STUDIES]->(career:Career)
        OPTIONAL MATCH (s)-[:LIKES]->(lc:Category)
        RETURN s.name, s.universidad, s.presupuesto, career.name, collect(DISTINCT lc.name)
        """,
        {"uid": django_user_id}
    )
    if not rows:
        return None
    
    row = rows[0]
    return {
        "nombre": row[0],
        "universidad": row[1],
        "presupuesto": row[2],
        "carrera": row[3],
        "categorias": row[4]
    }
