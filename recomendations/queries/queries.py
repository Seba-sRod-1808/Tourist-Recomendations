from neomodel import db
from recomendations.utils.scoring import score_place


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


DEFAULT_IMAGES = {
    "Antigua Guatemala": "https://images.unsplash.com/photo-1526487046039-335a122851ee?q=80&w=600&auto=format&fit=crop",
    "Lago Atitlan":      "https://images.unsplash.com/photo-1582424075549-b5cfccda7950?q=80&w=600&auto=format&fit=crop",
    "Semuc Champey":     "https://images.unsplash.com/photo-1598284687989-130ab63f73ce?q=80&w=600&auto=format&fit=crop",
    "Tikal, Peten":      "https://images.unsplash.com/photo-1512556798208-148886470870?q=80&w=600&auto=format&fit=crop",
    "Rio Dulce":         "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=600&auto=format&fit=crop",
    "Monterrico":        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=600&auto=format&fit=crop",
}


def _get_image(place_name):
    return DEFAULT_IMAGES.get(place_name, "https://images.unsplash.com/photo-1506461883276-594a12b11cf3?q=80&w=600&auto=format&fit=crop")


def get_recommendations(django_user_id=None, limit=6):
    """
    Motor de recomendaciones híbrido.
    1. Si no hay usuario, devuelve los lugares más populares.
    2. Si hay usuario, recupera perfil y candidatos, y aplica score_place.
    """
    if django_user_id is None:
        return _get_popular_recommendations(limit)

    # 1. Obtener Perfil del Estudiante
    student_data_results, _ = db.cypher_query(
        """
        MATCH (s:Student {django_user_id: $uid})
        OPTIONAL MATCH (s)-[:LIKES]->(lc:Category)
        OPTIONAL MATCH (s)-[:VISITED]->(p:Place)-[:HAS_CATEGORY]->(vc:Category)
        OPTIONAL MATCH (s)-[:STUDIES]->(career:Career)
        RETURN
            collect(DISTINCT lc.name) AS liked_cats,
            collect(DISTINCT vc.name) AS visited_cats,
            career.name AS career_name,
            s.budget AS budget,
            collect(DISTINCT p.uid) AS visited_uids
        """,
        {"uid": django_user_id}
    )

    if not student_data_results or (not student_data_results[0][0] and not student_data_results[0][1]):
        # Estudiante nuevo o sin preferencias, volver a populares
        return _get_popular_recommendations(limit)

    s_row = student_data_results[0]
    student_profile = {
        "liked_categories": set(s_row[0]),
        "visited_categories": set(s_row[1]),
        "career": s_row[2],
        "budget": s_row[3] or 0.0,
        "visited_uids": set(s_row[4])
    }

    # 2. Obtener Candidatos y Metadata para Scoring
    candidates_results, _ = db.cypher_query(
        """
        MATCH (s:Student {django_user_id: $uid})
        MATCH (p:Place)
        WHERE NOT (s)-[:VISITED]->(p)

        # Career Affinity
        OPTIONAL MATCH (s)-[:STUDIES]->(career:Career)-[:PREFERS]->(p)
        WITH s, p, career IS NOT NULL AS career_affinity

        # Collaborative: Estudiantes que LIKES las mismas categorías que S
        OPTIONAL MATCH (s)-[:LIKES]->(c:Category)<-[:LIKES]-(other:Student)
        WHERE s <> other
        WITH s, p, career_affinity, collect(DISTINCT other) AS similar_students

        # Conteo de visitas de esos estudiantes similares al lugar P
        OPTIONAL MATCH (other_sim:Student)-[:VISITED]->(p)
        WHERE other_sim IN similar_students
        WITH p, career_affinity, count(DISTINCT other_sim) AS similar_visits

        # Categorías del lugar
        MATCH (p)-[:HAS_CATEGORY]->(cat:Category)
        RETURN
            p.uid AS uid,
            p.name AS name,
            p.cost AS cost,
            p.popularity AS popularity,
            collect(cat.name) AS categories,
            career_affinity,
            similar_visits
        """,
        {"uid": django_user_id}
    )

    scored_list = []
    for row in candidates_results:
        place_data = {
            "uid": row[0],
            "name": row[1],
            "cost": row[2] or 0.0,
            "popularity": row[3] or 0.0,
            "categories": set(row[4]),
            "career_affinity": row[5],
            "similar_students_visits": row[6]
        }

        scoring_result = score_place(student_profile, place_data)

        scored_list.append({
            "uid": row[0],
            "name": row[1],
            "cost": int(row[2] or 0),
            "category": " ".join(row[4]),
            "score": int(scoring_result["final_score"]),
            "tag": row[4][0].capitalize() if row[4] else "Destino",
            "match_reason": _generate_match_reason(scoring_result),
            "image": _get_image(row[1]),
            "details": scoring_result["components"]
        })

    scored_list.sort(key=lambda x: x["score"], reverse=True)
    return scored_list[:limit]


def _get_popular_recommendations(limit):
    results, _ = db.cypher_query(
        """
        MATCH (p:Place)
        OPTIONAL MATCH (p)-[:HAS_CATEGORY]->(c:Category)
        WITH p, collect(c.name) AS categories
        ORDER BY coalesce(p.popularity, 0) DESC
        LIMIT $limit
        RETURN p.uid, p.name, p.cost, categories, p.popularity
        """,
        {"limit": limit},
    )
    return [
        {
            "uid": row[0],
            "name": row[1],
            "cost": int(row[2] or 0),
            "category": " ".join(row[3]) if row[3] else "",
            "score": int((row[4] or 0) * 100) if row[4] else 50,
            "tag": row[3][0].capitalize() if row[3] else "Destino",
            "match_reason": "Basado en la popularidad actual del destino.",
            "image": _get_image(row[1]),
        }
        for row in results
    ]


def _generate_match_reason(scoring_result):
    comps = scoring_result["components"]
    if comps["collaborative"] > 0.6:
        return "Muchos estudiantes con tus mismos gustos han visitado este lugar."
    if comps["demographic"] > 0.8:
        return "Este destino es muy popular entre estudiantes de tu carrera."
    if comps["content_based"] > 0.7:
        return "Coincide perfectamente con las categorías que te gustan."
    return "Una opción equilibrada basada en tu perfil universitario."


def add_review(django_user_id: int, place_uid: str, rating: float, comment: str = ""):
    """
    Registra una visita y calificación de un estudiante a un lugar.
    """
    db.cypher_query(
        """
        MATCH (s:Student {django_user_id: $uid})
        MATCH (p:Place {uid: $p_uid})
        MERGE (s)-[r:VISITED]->(p)
        SET r.rating = $rating,
            r.comment = $comment,
            r.timestamp = datetime()
        WITH p
        # Actualizar popularidad del lugar basada en promedio de ratings
        MATCH (:Student)-[all_r:VISITED]->(p)
        WITH p, avg(all_r.rating) AS avg_rating
        SET p.popularity = avg_rating / 5.0
        """,
        {"uid": django_user_id, "p_uid": place_uid, "rating": rating, "comment": comment}
    )
