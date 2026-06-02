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
        img = _DEFAULT_IMAGES.get(place_name)
        if not img:
            return "https://images.unsplash.com/photo-1506461883276-594a12b11cf3?q=80&w=800&auto=format&fit=crop"
        return img

_DEFAULT_IMAGES = {
    "Antigua Guatemala": "https://images.unsplash.com/photo-1637966201771-b0b251baa2ef?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Lago Atitlan":      "https://images.unsplash.com/photo-1650734837526-3036e11e0e25?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bGFnbyUyMGF0aXRsYW58ZW58MHx8MHx8fDA%3D",
    "Semuc Champey":     "https://images.unsplash.com/photo-1675185457371-aae4e3ea0270?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Tikal, Peten":      "https://images.unsplash.com/photo-1669025467363-ace9bad030dc?q=80&w=1471&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Rio Dulce":         "https://images.unsplash.com/photo-1641581006900-97f4f6e14819?q=80&w=1633&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Monterrico":        "https://images.unsplash.com/photo-1641581006914-0a37ef759189?q=80&w=1484&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Chichicastenango":  "https://images.unsplash.com/photo-1669578718614-0dec2071ce83?q=80&w=1655&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Livingston":        "https://images.unsplash.com/photo-1641581006723-cbb37e20bd6e?q=80&w=1476&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Quetzaltenango":    "https://images.unsplash.com/photo-1696511149389-a137de3d0737?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Huehuetenango":     "https://images.unsplash.com/photo-1647650585586-c119557a50f7?q=80&w=1374&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Castillo de San Felipe": "https://plus.unsplash.com/premium_photo-1733342463294-946b7bec4b1f?q=80&w=1535&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Irtra Retalhuleu":  "https://epinvestiga.com/wp-content/uploads/2022/02/DSC_0020.jpg",
    "Volcan de Acatenango": "https://images.unsplash.com/photo-1669025466409-450f22c7561a?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YWNhdGVuYW5nb3xlbnwwfHwwfHx8MA%3D%3D",
    "Fuentes Georginas": "https://www.guatemala.com/wp-content/uploads/2017/12/Fuentes-Georginas-de-Quetzaltenango.jpg",
    "Crater Azul":       "https://upload.wikimedia.org/wikipedia/commons/7/78/Crater_azul.png",
    "Hun Nal Ye":        "https://www.guatemala.com/fotos/2024/07/hun-nal-ye.jpg",
    "Parque Naciones Unidas": "https://defensores.org.gt/wp-content/uploads/PNNU-2.jpg",
    "Laguna del Pino":   "https://revistayuam.com/wp-content/uploads/2021/07/Foto-laguna-El-pino-6.jpg",
    "Mixco Viejo":       "https://www.soy502.com/sites/default/files/styles/escalar_image_inline/public/2025/Ago/07/mixco_viejo_tesoro_ancestral_que_habla_desde_las_alturas_imperio_chapin_4037792.jpg",
    "Iximché":           "https://tropicanahostel.com/wp-content/uploads/2025/04/Iximche-Ruins-Guatemala-e1745022124527.jpg",
    "Hobbitenango":      "https://www.thoroughlytravel.com/wp-content/uploads/2025/10/lucy-hobbit-house-hobbitenango-antigua-guatemala-1024x768.jpg",
    "Volcan de Pacaya":  "https://images.unsplash.com/photo-1565365906073-6d5bd6b9013c?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8cGFjYXlhfGVufDB8fDB8fHww",
    "Finca El Amate":    "https://www.guatemala.com/fotos/2024/12/Finca-El-Amate.jpg",
    "Cataratas Tatasirire": "https://www.prensalibre.com/wp-content/uploads/2018/12/c9b7f2fe-f5e2-4673-b112-7217704fe8e3.jpg?quality=52",
    "Laguna de Ayarza":  "https://www.sicultura.gob.gt/wp-content/uploads/2021/03/Fotografia-Fly-GT-.jpg",
    "Volcan de Ipala":   "https://www.volcanesdeguatemala.com/imagenes/volcanes/volcan-ipala-guatemala.jpg",
    "Biotopo del Quetzal": "https://www.guatemala.com/fotos/2025/09/biotopo-del-quetzal.webp",
    "San Juan Comalapa": "https://www.guatemala.com/wp-content/uploads/2019/12/Municipio-San-Juan-Comalapa-Chimaltenango.jpg",
    "Cuevas de Candelaria": "https://www.guatevalley.com/photo/photo_a1/1352/EW3BkNUhBV3gEhLxhTAZ.jpg",
    "El Paredon":        "https://elparedongt.com/cdn/shop/files/el-paredon-sunset-2-845x550.jpg",
    "Tak'alik Ab'aj":    "https://upload.wikimedia.org/wikipedia/commons/0/0d/ESTRUCTURA_12_MUSEO_AL_AIRE_LIBRE_FACHADA_OESTE_-_TAKALIK_ABAJ.png?utm_source=es.wikipedia.org&utm_campaign=index&utm_content=original",
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
