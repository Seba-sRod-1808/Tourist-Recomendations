from recomendations.queries.queries import get_recommendations as neo4j_query


def get_recommendations(django_user_id=None, limit=6):
    return neo4j_query(django_user_id=django_user_id, limit=limit)
