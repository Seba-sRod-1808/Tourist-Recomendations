"""
PROCESO: Depuración Visual del Algoritmo (Debugger)
DESCRIPCIÓN: Versión extendida del servicio de recomendaciones diseñada para
exponer el paso a paso del cálculo en la consola. Proporciona visibilidad
sobre pesos, puntuaciones crudas y decisiones de filtrado.
"""

from __future__ import annotations
from typing import Optional
from recomendations.services.recomendation_service import RecommendationService, RecommendationScore
from recomendations.utils.scoring import score_place

class RecommendationDebugger(RecommendationService):

    def recommend_with_debug(self, student_uid: int, limit: int = 10) -> list[dict]:
        print(f"\n{'='*60}")
        print(f" DEBUGGER: Iniciando proceso para Usuario ID: {student_uid}")
        print(f"{'='*60}")

        profile = self._fetch_student_profile(student_uid)
        if profile is None:
            print(" [!] Perfil no encontrado o sin preferencias. Usando Fallback Popular.")
            return self._fallback_popular(limit)

        print(f" [+] Perfil cargado: {profile['career']} | Presupuesto: Q{profile['budget']}")
        print(f" [+] Categorías gustadas: {profile['liked_categories']}")
        print(f" [+] Lugares visitados: {len(profile['visited_uids'])}")
        
        visited_count = len(profile["visited_uids"])
        is_cold = visited_count < 3
        print(f" [+] ESTADO: {'COLD START' if is_cold else 'RECOMENDACIÓN MADURA'} (Umbral: 3 visitas)")

        candidates = self._fetch_candidates(student_uid, profile["budget"])
        print(f" [+] Candidatos encontrados en Neo4j: {len(candidates)}")

        scored: list[RecommendationScore] = []
        for raw in candidates:
            print(f"\n ---> Evaluando: {raw['name']}")
            
            # Cálculo de componentes individuales
            scoring_result = score_place(profile, raw)
            comps = scoring_result["components"]
            
            print(f"      - Contenido: {comps['content_based']:.2f}")
            print(f"      - Colaborativo:   {comps['collaborative']:.2f}")
            print(f"      - Demográfico:  {comps['demographic']:.2f}")
            print(f"      - Geográfico): {comps['geographic']:.2f}")
            print(f"      - Popularidad:   {comps['popularity']:.2f}")

            rec_score = self._score_candidate(profile, raw, len(profile["visited_uids"]) < 3)
            print(f"      => SCORE FINAL CALCULADO: {rec_score.final_score}%")
            scored.append(rec_score)

        scored.sort(key=lambda r: r.final_score, reverse=True)
        top = scored[:limit]

        print(f"\n{'='*60}")
        print(f" RESULTADO TOP {len(top)} FINALIZADO")
        print(f"{'='*60}\n")

        return [self._enrich(r) for r in top]
