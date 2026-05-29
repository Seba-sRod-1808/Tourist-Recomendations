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
    Scoring:
      +20 por cada Category que el Student LIKES y el Place tiene (HAS_CATEGORY)
      +30 si la Career del Student PREFERS el Place
      +10 * popularity del Place
    Excluye Places ya VISITED por el Student.
    Sin django_user_id devuelve los más populares.
    """
    if django_user_id is None:
        results, _ = db.cypher_query(
            """
            MATCH (p:Place)
            OPTIONAL MATCH (p)-[:HAS_CATEGORY]->(c:Category)
            WITH p, collect(c.name) AS categories
            ORDER BY coalesce(p.popularity, 0) DESC
            LIMIT $limit
            RETURN p.uid AS uid, p.name AS name,
                   toInteger(coalesce(p.cost, 0)) AS cost,
                   categories,
                   toInteger(coalesce(p.popularity, 0) * 10) AS score
            """,
            {"limit": limit},
        )
    else:
        results, _ = db.cypher_query(
            """
            MATCH (s:Student {django_user_id: $uid})
            MATCH (p:Place)
            WHERE NOT (s)-[:VISITED]->(p)

            OPTIONAL MATCH (s)-[:LIKES]->(liked_cat:Category)<-[:HAS_CATEGORY]-(p)
            OPTIONAL MATCH (s)-[:STUDIES]->(career:Career)-[:PREFERS]->(p)
            OPTIONAL MATCH (p)-[:HAS_CATEGORY]->(any_cat:Category)

            WITH p,
                 count(DISTINCT liked_cat) AS cat_matches,
                 count(DISTINCT career)    AS career_score,
                 collect(DISTINCT any_cat.name) AS categories

            WITH p, categories,
                 toInteger(
                   cat_matches * 20 +
                   career_score  * 30 +
                   coalesce(p.popularity, 0) * 10
                 ) AS score

            ORDER BY score DESC
            LIMIT $limit

            RETURN p.uid AS uid, p.name AS name,
                   toInteger(coalesce(p.cost, 0)) AS cost,
                   categories, score
            """,
            {"uid": django_user_id, "limit": limit},
        )

    return [
        {
            "uid":          row[0],
            "name":         row[1],
            "cost":         row[2],
            "category":     " ".join(row[3]) if row[3] else "",
            "score":        min(row[4], 99),
            "tag":          row[3][0].capitalize() if row[3] else "Destino",
            "match_reason": "Basado en tus preferencias de carrera y categorías.",
            "image":        "",
        }
        for row in results
    ]
