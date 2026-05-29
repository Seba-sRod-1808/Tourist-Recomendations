from neomodel import db


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

    # Elimina preferencias anteriores y recrea
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


def get_recommendations(django_user_id=None, limit=6):
    """
    Scoring Cypher:
      +20 por cada Category que el estudiante LIKES y el destino tiene (HAS_CATEGORY)
      +30 si la carrera del estudiante PREFERS el destino
      +10 * popularidad
    Excluye destinos ya VISITED por el estudiante.
    Sin django_user_id devuelve los más populares.
    """
    if django_user_id is None:
        results, _ = db.cypher_query(
            """
            MATCH (d:Destination)
            OPTIONAL MATCH (d)-[:HAS_CATEGORY]->(c:Category)
            WITH d, collect(c.name) AS categories
            ORDER BY coalesce(d.popularity, 0) DESC
            LIMIT $limit
            RETURN d.uid AS uid, d.name AS name,
                   toInteger(coalesce(d.cost, 0)) AS cost,
                   categories,
                   toInteger(coalesce(d.popularity, 0) * 10) AS score
            """,
            {"limit": limit},
        )
    else:
        results, _ = db.cypher_query(
            """
            MATCH (s:Student {django_user_id: $uid})
            MATCH (d:Destination)
            WHERE NOT (s)-[:VISITED]->(d)

            OPTIONAL MATCH (s)-[:LIKES]->(liked_cat:Category)<-[:HAS_CATEGORY]-(d)
            OPTIONAL MATCH (s)-[:STUDIES]->(career:Career)-[:PREFERS]->(d)
            OPTIONAL MATCH (d)-[:HAS_CATEGORY]->(any_cat:Category)

            WITH d,
                 count(DISTINCT liked_cat) AS cat_matches,
                 count(DISTINCT career)    AS career_score,
                 collect(DISTINCT any_cat.name) AS categories

            WITH d, categories,
                 toInteger(
                   cat_matches * 20 +
                   career_score  * 30 +
                   coalesce(d.popularity, 0) * 10
                 ) AS score

            ORDER BY score DESC
            LIMIT $limit

            RETURN d.uid AS uid, d.name AS name,
                   toInteger(coalesce(d.cost, 0)) AS cost,
                   categories, score
            """,
            {"uid": django_user_id, "limit": limit},
        )

    return [
        {
            "uid":         row[0],
            "name":        row[1],
            "cost":        row[2],
            "category":    " ".join(row[3]) if row[3] else "",
            "score":       min(row[4], 99),
            "tag":         row[3][0].capitalize() if row[3] else "Destino",
            "match_reason": "Basado en tus preferencias de carrera y categorías.",
            "image":       "",
        }
        for row in results
    ]
