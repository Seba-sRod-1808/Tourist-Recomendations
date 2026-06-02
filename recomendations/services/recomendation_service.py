"""
PROCESO: Orquestación del Algoritmo de Recomendación
DESCRIPCIÓN: Clase principal que coordina el proceso de recomendación híbrida.
Realiza la obtención del perfil del estudiante, busca candidatos potenciales,
calcula las puntuaciones utilizando diversos componentes (contenido, colaborativo, demográfico)
y enriquece los resultados con metadatos para la interfaz.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from neomodel import db
from recomendations.utils.scoring import (
    score_place,
    calculate_jaccard_similarity,
    score_geographic_proximity,
)

@dataclass(frozen=True)
class RecommendationScore:
    destination_uid: str
    destination_name: str
    destination_cost: float
    categories: set[str]

    content_score: float
    collaborative_score: float
    demographic_score: float
    geographic_bonus: float
    popularity_norm: float

    final_score: float

    def to_dict(self) -> dict:
        return {
            "uid": self.destination_uid,
            "name": self.destination_name,
            "cost": int(self.destination_cost),
            "categories": list(self.categories),
            "score": round(self.final_score, 2),
            "components": {
                "content_based": round(self.content_score, 2),
                "collaborative": round(self.collaborative_score, 2),
                "demographic": round(self.demographic_score, 2),
                "geographic": round(self.geographic_bonus, 2),
                "popularity": round(self.popularity_norm, 2),
            },
        }

_W_CONTENT       = 0.40
_W_COLLABORATIVE = 0.35
_W_DEMOGRAPHIC   = 0.25
_W_GEO           = 0.05
_W_POPULARITY    = 0.05

_W_CONTENT_COLD       = 0.50
_W_COLLABORATIVE_COLD = 0.20
_W_DEMOGRAPHIC_COLD   = 0.25   
_W_GEO_COLD           = 0.05   
_W_POPULARITY_COLD    = 0.05   

_COLD_START_THRESHOLD = 3

class RecommendationService:

    def recommend(
        self,
        student_uid: int,
        limit: int = 10,
        budget_factor: float = 1.0,
    ) -> list[dict]:

        profile = self._fetch_student_profile(student_uid)
        if profile is None:
            return self._fallback_popular(limit)

        visited_count = len(profile["visited_uids"])
        cold_start = visited_count < _COLD_START_THRESHOLD

        effective_budget = profile["budget"] * budget_factor
        candidates = self._fetch_candidates(student_uid, effective_budget)

        if not candidates:
            return self._fallback_popular(limit)

        scored: list[RecommendationScore] = []
        for raw in candidates:
            rec_score = self._score_candidate(profile, raw, cold_start)
            scored.append(rec_score)

        scored.sort(key=lambda r: r.final_score, reverse=True)
        top = scored[:limit]

        return [self._enrich(r) for r in top]

    def _fetch_student_profile(self, student_uid: int) -> Optional[dict]:
        rows, _ = db.cypher_query(
            """
            MATCH (s:Student {django_user_id: $uid})
            OPTIONAL MATCH (s)-[:LIKES]->(lc:Category)
            OPTIONAL MATCH (s)-[:VISITED]->(vp:Place)-[:HAS_CATEGORY]->(vc:Category)
            OPTIONAL MATCH (s)-[:STUDIES]->(career:Career)
            RETURN
                s.budget                      AS budget,
                career.name                   AS career,
                collect(DISTINCT lc.name)     AS liked_cats,
                collect(DISTINCT vc.name)     AS visited_cats,
                collect(DISTINCT vp.uid)      AS visited_uids
            """,
            {"uid": student_uid},
        )

        if not rows:
            return None

        row = rows[0]
        budget, career, liked_cats, visited_cats, visited_uids = row

        if not liked_cats and not visited_cats:
            return None

        return {
            "budget": float(budget or 0.0),
            "career": career,
            "liked_categories": set(liked_cats),
            "visited_categories": set(visited_cats),
            "visited_uids": set(visited_uids),
        }

    def _fetch_candidates(self, student_uid: int, budget_limit: float) -> list[dict]:
        rows, _ = db.cypher_query(
            """
            MATCH (s:Student {django_user_id: $uid})
            MATCH (p:Place)
            WHERE NOT (s)-[:VISITED]->(p)
              AND (p.cost IS NULL OR p.cost <= $budget)
            OPTIONAL MATCH (s)-[:STUDIES]->(career:Career)-[:PREFERS]->(p)
            WITH s, p, career IS NOT NULL AS career_affinity
            OPTIONAL MATCH (s)-[:LIKES]->(shared_cat:Category)<-[:LIKES]-(peer:Student)
            WHERE s <> peer
            WITH s, p, career_affinity, collect(DISTINCT peer) AS similar_peers
            OPTIONAL MATCH (counted_peer:Student)-[:VISITED]->(p)
            WHERE counted_peer IN similar_peers
            WITH p, career_affinity, count(DISTINCT counted_peer) AS similar_visits
            OPTIONAL MATCH (p)-[:HAS_CATEGORY]->(cat:Category)
            RETURN
                p.uid                         AS uid,
                p.name                        AS name,
                coalesce(p.cost, 0.0)         AS cost,
                coalesce(p.popularity, 0.0)   AS popularity,
                p.lat                         AS lat,
                p.lng                         AS lng,
                collect(DISTINCT cat.name)    AS categories,
                career_affinity,
                similar_visits
            """,
            {"uid": student_uid, "budget": budget_limit},
        )

        return [
            {
                "uid": row[0],
                "name": row[1],
                "cost": float(row[2]),
                "popularity": float(row[3]),
                "lat": row[4],
                "lng": row[5],
                "categories": set(row[6]),
                "career_affinity": bool(row[7]),
                "similar_students_visits": int(row[8] or 0),
            }
            for row in rows
        ]

    def _score_candidate(
        self,
        profile: dict,
        place: dict,
        cold_start: bool,
    ) -> RecommendationScore:
        scoring_result = score_place(profile, place)
        comps = scoring_result["components"]

        content_score       = comps["content_based"]
        collaborative_score = comps["collaborative"]
        demographic_score   = comps["demographic"]
        geographic_bonus    = comps["geographic"]
        popularity_norm     = comps["popularity"]

        if cold_start:
            w_content       = _W_CONTENT_COLD
            w_collaborative = _W_COLLABORATIVE_COLD
        else:
            w_content       = _W_CONTENT
            w_collaborative = _W_COLLABORATIVE

        w_demographic = _W_DEMOGRAPHIC
        w_geo         = _W_GEO
        w_pop         = _W_POPULARITY

        final = (
            content_score       * w_content +
            collaborative_score * w_collaborative +
            demographic_score   * w_demographic +
            geographic_bonus    * w_geo +
            popularity_norm     * w_pop
        )
        final_scaled = min(final * 100, 100.0)

        return RecommendationScore(
            destination_uid=place["uid"],
            destination_name=place["name"],
            destination_cost=place["cost"],
            categories=place["categories"],
            content_score=content_score,
            collaborative_score=collaborative_score,
            demographic_score=demographic_score,
            geographic_bonus=geographic_bonus,
            popularity_norm=popularity_norm,
            final_score=round(final_scaled, 2),
        )

    def _enrich(self, rec: RecommendationScore) -> dict:
        result = rec.to_dict()
        result["image"] = self._get_image(rec.destination_name)
        result["match_reason"] = _generate_match_reason(rec)
        result["tag"] = _primary_tag(rec)
        return result

    def _fallback_popular(self, limit: int) -> list[dict]:
        rows, _ = db.cypher_query(
            """
            MATCH (p:Place)
            OPTIONAL MATCH (p)-[:HAS_CATEGORY]->(c:Category)
            WITH p, collect(DISTINCT c.name) AS categories
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
                "category": " ".join(row[3]),
                "score": int((row[4] or 0) * 100),
                "tag": row[3][0].capitalize() if row[3] else "Destino",
                "match_reason": "Basado en la popularidad actual del destino.",
                "image": self._get_image(row[1]),
            }
            for row in rows
        ]

    def _get_image(self, place_name: str) -> str:
        return _DEFAULT_IMAGES.get(
            place_name,
            "https://images.unsplash.com/photo-1506461883276-594a12b11cf3?q=80&w=600&auto=format&fit=crop",
        )

_DEFAULT_IMAGES = {
    "Antigua Guatemala": "https://images.unsplash.com/photo-1526487046039-335a122851ee?q=80&w=600&auto=format&fit=crop",
    "Lago Atitlan":      "https://images.unsplash.com/photo-1582424075549-b5cfccda7950?q=80&w=600&auto=format&fit=crop",
    "Semuc Champey":     "https://images.unsplash.com/photo-1598284687989-130ab63f73ce?q=80&w=600&auto=format&fit=crop",
    "Tikal, Peten":      "https://images.unsplash.com/photo-1512556798208-148886470870?q=80&w=600&auto=format&fit=crop",
    "Rio Dulce":         "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=600&auto=format&fit=crop",
    "Monterrico":        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=600&auto=format&fit=crop",
}

def _generate_match_reason(rec: RecommendationScore) -> str:
    if rec.collaborative_score > 0.6:
        return "Muchos estudiantes con tus mismos gustos han visitado este lugar."
    if rec.demographic_score > 0.8:
        return "Este destino es muy popular entre estudiantes de tu carrera."
    if rec.content_score > 0.7:
        return "Coincide perfectamente con las categorías que te gustan."
    return "Una opción equilibrada basada en tu perfil universitario."

def _primary_tag(rec: RecommendationScore) -> str:
    if rec.categories:
        return sorted(list(rec.categories))[0].capitalize()
    return "Destino"
