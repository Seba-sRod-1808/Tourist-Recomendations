
from neomodel import db
from recomendations.services.recomendation_service import RecommendationService

_service = RecommendationService()


# ---------------------------------------------------------------------------
# Recomendaciones
# ---------------------------------------------------------------------------

def get_recommendations(django_user_id=None, limit=6):

    if django_user_id is None:
        return _service._fallback_popular(limit)
    return _service.recommend(student_uid=django_user_id, limit=limit)


# ---------------------------------------------------------------------------
# Mutaciones de perfil
# ---------------------------------------------------------------------------

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
    db.cypher_query(
        """
        MATCH (s:Student {django_user_id: $uid})
        MERGE (c:Career {name: $carrera})
        MERGE (s)-[:STUDIES]->(c)
        SET s.universidad = $universidad, s.presupuesto = $presupuesto
        """,
        {"uid": django_user_id, "carrera": carrera, "universidad": universidad, "presupuesto": presupuesto},
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


# ---------------------------------------------------------------------------
# Reseñas
# ---------------------------------------------------------------------------

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