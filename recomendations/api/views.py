from django.shortcuts import render, redirect
from recomendations.services.recomendation_service import get_recommendations

def login_view(request):
    if request.method == 'POST':
        # Al presionar el botón de inicio de sesión, redirige al registro de intereses
        return redirect('registro')
    return render(request, 'recomendations/login.html')

def registro_view(request):
    if request.method == 'POST':
        # Al guardar los intereses, redirige a las recomendaciones finales
        return redirect('recommendations')
    return render(request, 'recomendations/registro.html')

def mostrar_recomendaciones(request):
    # Intentamos jalar los destinos reales guardados en Neo4j mediante tu servicio
    recommendations = get_recommendations(student_uid=None, limit=6)

    # Si Neo4j no tiene datos cargados aún, usamos el plan de respaldo con datos reales ficticios
    if not recommendations:
        recommendations = [
            {
                'uid': '1',
                'name': 'Antigua Guatemala',
                'cost': 550,
                'score': 94,
                'category': 'cultura historia',
                'match_reason': '8 estudiantes de Ingeniería con presupuesto similar lo visitaron este mes.',
            },
            {
                'uid': '2',
                'name': 'Lago Atitlán',
                'cost': 400,
                'score': 91,
                'category': 'naturaleza aventura',
                'match_reason': 'Encaja con tu preferencia por naturaleza. Ideal para fin de semana.',
            },
            {
                'uid': '3',
                'name': 'Semuc Champey',
                'cost': 350,
                'score': 87,
                'category': 'naturaleza aventura',
                'match_reason': 'Destino popular entre estudiantes universitarios en vacaciones.',
            },
            {
                'uid': '4',
                'name': 'Tikal, Petén',
                'cost': 400,
                'score': 82,
                'category': 'historia cultura naturaleza',
                'match_reason': 'Coincide con intereses en historia maya.',
            },
            {
                'uid': '5',
                'name': 'Río Dulce',
                'cost': 300,
                'score': 79,
                'category': 'aventura naturaleza playa',
                'match_reason': 'El más económico. Popular entre estudiantes con tiempo limitado.',
            },
            {
                'uid': '6',
                'name': 'Monterrico',
                'cost': 650,
                'score': 75,
                'category': 'playa naturaleza',
                'match_reason': 'Estudiantes que visitaron Atitlán también lo califican altamente.',
            },
        ]

    context = {
        'recommendations': recommendations,
        'total': len(recommendations),
    }
    return render(request, 'recomendations/recomendaciones.html', context)

def admin_view(request):
    return render(request, 'recomendations/admin_panel.html')