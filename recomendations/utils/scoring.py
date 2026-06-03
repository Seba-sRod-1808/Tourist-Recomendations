"""
PROCESO: Funciones de Puntuación (Scoring)
DESCRIPCIÓN: Implementa la lógica matemática para evaluar cada destino candidato.
Calcula puntuaciones individuales basadas en contenido (categorías),
colaboración (comportamiento de pares), demografía (carrera universitaria)
y proximidad geográfica, combinándolas en una puntuación final normalizada.
Incluye un factor de serendipia para evitar recomendaciones monótonas.
"""

import math
import random

def score_place(student_profile: dict, place: dict) -> dict:
    # 1. Content-based: Coincidencia de categorías (Normalizado a minúsculas)
    liked_set = {c.lower() for c in student_profile['liked_categories']}
    visited_set = {c.lower() for c in student_profile['visited_categories']}
    place_cats = {c.lower() for c in place['categories']}
    
    direct_matches = len(place_cats.intersection(liked_set))
    visited_matches = len(place_cats.intersection(visited_set))

    content_score = 0.0
    if place_cats:
        # Penalizamos si no hay ninguna coincidencia de interés explícito
        content_score = (direct_matches * 1.0 + visited_matches * 0.5) / len(place_cats)
    
    # 2. Collaborative: Visitas de estudiantes similares
    collaborative_score = min(place['similar_students_visits'] / 5.0, 1.0)

    # 3. Demographic: Afinidad por carrera
    demographic_score = 1.0 if place['career_affinity'] else 0.0

    # 4. Popularidad y Geografía
    popularity_bonus = place['popularity']
    geo_bonus = score_geographic_proximity(place)

    # 5. Serendipity: Pequeña variación aleatoria para evitar monotonía (0-0.10)
    serendipity_factor = random.uniform(0, 0.10)

    # RECALIBRACIÓN DE PESOS: Prioridad a Carrera e Intereses
    WEIGHT_CONTENT       = 0.45
    WEIGHT_DEMOGRAPHIC   = 0.30
    WEIGHT_COLLABORATIVE = 0.15
    WEIGHT_POPULARITY    = 0.05
    WEIGHT_GEO           = 0.05

    final_score = (
        (content_score * WEIGHT_CONTENT) +
        (demographic_score * WEIGHT_DEMOGRAPHIC) +
        (collaborative_score * WEIGHT_COLLABORATIVE) +
        (popularity_bonus * WEIGHT_POPULARITY) +
        (geo_bonus * WEIGHT_GEO) +
        serendipity_factor
    )

    final_score_scaled = min(final_score * 100, 100.0)

    return {
        "final_score": round(final_score_scaled, 2),
        "components": {
            "content_based": round(content_score, 2),
            "collaborative": round(collaborative_score, 2),
            "demographic": round(demographic_score, 2),
            "popularity": round(popularity_bonus, 2),
            "geographic": round(geo_bonus, 2),
            "serendipity": round(serendipity_factor, 2)
        }
    }

def score_geographic_proximity(place: dict) -> float:
    BASE_LAT = 14.6349
    BASE_LNG = -90.5069
    
    place_lat = place.get('lat')
    place_lng = place.get('lng')
    
    if place_lat is None or place_lng is None:
        return 0.5

    distance = math.sqrt((place_lat - BASE_LAT)**2 + (place_lng - BASE_LNG)**2)
    score = max(0, 1.0 - (distance / 5.0))
    return round(score, 2)

def calculate_jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a or not set_b:
        return 0.0
    # Normalizamos para la comparación
    s_a = {str(x).lower() for x in set_a}
    s_b = {str(x).lower() for x in set_b}
    intersection = len(s_a.intersection(s_b))
    union = len(s_a.union(s_b))
    return intersection / union
