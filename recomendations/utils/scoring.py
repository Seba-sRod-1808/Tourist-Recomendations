"""
Interfaz de scoring para el algoritmo de recomendación.
"""


def score_place(student_profile: dict, place: dict) -> dict:

    direct_matches = len(place['categories'].intersection(student_profile['liked_categories']))
    visited_matches = len(place['categories'].intersection(student_profile['visited_categories']))

    content_score = 0.0
    if place['categories']:
        content_score = (direct_matches * 1.0 + visited_matches * 0.7) / len(place['categories'])
    content_score = min(content_score, 1.0)

    collaborative_score = min(place['similar_students_visits'] / 5.0, 1.0)

    demographic_score = 1.0 if place['career_affinity'] else 0.0


    popularity_bonus = place['popularity']

    geo_bonus = score_geographic_proximity(place)

    WEIGHT_CONTENT = 0.40
    WEIGHT_COLLABORATIVE = 0.35
    WEIGHT_DEMOGRAPHIC = 0.25
    WEIGHT_POPULARITY = 0.05
    WEIGHT_GEO = 0.05

    final_score = (
        (content_score * WEIGHT_CONTENT) +
        (collaborative_score * WEIGHT_COLLABORATIVE) +
        (demographic_score * WEIGHT_DEMOGRAPHIC) +
        (popularity_bonus * WEIGHT_POPULARITY) +
        (geo_bonus * WEIGHT_GEO)
    )

    final_score_scaled = min(final_score * 100, 100.0)

    return {
        "final_score": round(final_score_scaled, 2),
        "components": {
            "content_based": round(content_score, 2),
            "collaborative": round(collaborative_score, 2),
            "demographic": round(demographic_score, 2),
            "popularity": round(popularity_bonus, 2),
            "geographic": round(geo_bonus, 2)
        }
    }


def score_geographic_proximity(place: dict) -> float:
    return 0.5


def calculate_jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union
