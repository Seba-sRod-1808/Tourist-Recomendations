from recomendations.models import Student, Destination, Category

def get_recommendations(student_uid, limit=6):
    """
    Por ahora devuelve todos los destinos disponibles.
    """
    try:
        destinations = Destination.nodes.all()
        results = []
        for dest in destinations[:limit]:
            # Obtener categorías del destino
            cats = dest.categories.all()
            cat_names = [c.name.lower() for c in cats]

            results.append({
                'uid':          dest.uid,
                'name':         dest.name,
                'cost':         int(dest.cost) if dest.cost else 0,
                'popularity':   dest.popularity or 0,
                'score':        75,   # placeholder hasta implementar algoritmo
                'category':     ' '.join(cat_names),
                'match_reason': 'Destino popular entre estudiantes con perfil similar.',
            })

        # Ordenar por score descendente
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    except Exception as e:
        print(f"Error obteniendo recomendaciones: {e}")
        return []