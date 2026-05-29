"""
Interfaz de scoring para el algoritmo de recomendación.

El compañero encargado del algoritmo debe implementar `score_place`.
El servicio en queries/queries.py llama a get_recommendations() que actualmente
usa Cypher puro. Para integrar lógica Python más compleja, reemplaza la función
get_recommendations en queries.py para que use score_place aquí.

Esquema del grafo relevante:
  (Student)-[:LIKES {weight}]->(Category)<-[:HAS_CATEGORY]-(Place)
  (Student)-[:STUDIES]->(Career)-[:PREFERS {weight}]->(Place)
  (Student)-[:VISITED {rating, budget_spent}]->(Place)
  (Place)-[:NEAR {distance_km}]->(Place)
  (Place)-[:LOCATED_IN]->(City)
"""


def score_place(student_profile: dict, place: dict) -> float:
    """
    Calcula el score de afinidad entre un estudiante y un lugar.

    Parámetros
    ----------
    student_profile : dict
        categorias     : list[str]   -- categorias que el estudiante LIKES (de Neo4j)
        carrera        : str         -- nombre de la carrera que estudia
        presupuesto    : str         -- rango seleccionado en onboarding (ej. 'Q200-Q500')
        budget         : float       -- presupuesto numerico si esta disponible
        visited_uids   : list[str]   -- UIDs de places ya visitados (excluir)

    place : dict
        uid            : str
        name           : str
        cost           : float
        popularity     : float       -- valor 0-10
        categories     : list[str]   -- categorias del lugar (de Neo4j)
        career_affinity: float       -- peso de Career-[:PREFERS]->Place (0 si no existe)

    Returns
    -------
    float
        Score entre 0.0 y 100.0. Mayor = mejor recomendacion.

    Notas para el algoritmo
    -----------------------
    - Filtrar places en visited_uids antes de llamar esta funcion.
    - El Cypher base en queries/queries.py ya hace +20/cat, +30/career, +10*pop.
      Este metodo permite logica hibrida (Python + datos del grafo).
    - Para collaborative filtering: buscar Students similares en Neo4j
      y usar sus ratings (VisitedRel.rating) como senal adicional.
    """
    raise NotImplementedError(
        "Implementar algoritmo de scoring. "
        "Ver docstring para contrato de parametros y esquema de grafo."
    )
