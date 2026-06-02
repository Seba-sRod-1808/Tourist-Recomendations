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
    RETURN p.uid, p.name, p.cost, p.popularity, p.lat, p.lng, collect(c.name), p.image_url
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
        'image': row[7] or 'https://images.unsplash.com/photo-1526487046039-335a122851ee' 
    }

def get_all_places():
    query = """
    MATCH (p:Place)
    OPTIONAL MATCH (p)-[:HAS_CATEGORY]->(c:Category)
    RETURN p.uid, p.name, p.cost, p.popularity, p.lat, p.lng, collect(c.name), p.image_url
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
            'image': row[7] or 'https://images.unsplash.com/photo-1526487046039-335a122851ee'
        })
    return places

def get_visited_places(django_user_id):
    query = """
    MATCH (s:Student {django_user_id: $user_id})-[r:VISITED]->(p:Place)
    RETURN p.uid AS uid, 
           p.name AS name, 
           p.image AS image, 
           r.rating AS rating, 
           r.timestamp AS date
    """
    results, meta = db.cypher_query(query, {'user_id': django_user_id})
    
    visited = []
    for row in results:
        visited.append({
            'uid': row[0],
            'name': row[1],
            'image': row[2] or 'https://images.unsplash.com/photo-1526487046039-335a122851ee',
            'rating': row[3], 
            'date': row[4]
        })
    return visited

def add_favorite(django_user_id: int, place_uid: str):
    db.cypher_query(
        """
        MATCH (s:Student {django_user_id: $uid})
        MATCH (p:Place {uid: $p_uid})
        MERGE (s)-[:FAVORITED]->(p)
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
