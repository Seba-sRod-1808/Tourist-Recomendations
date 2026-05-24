from django.shortcuts import render, redirect
from recomendations.services.recomendation_service import get_recommendations

def login_view(request):
    if request.method == 'POST':
        # Al presionar el botón de inicio de sesión, redirige al registro de intereses
        return redirect('registro')
    return render(request, 'recomendations/login.html')

def recuperar_view(request):
    if request.method == 'POST':
        # Aquí procesarías el envío del correo de recuperación en el futuro
        return redirect('login')
    return render(request, 'recomendations/recuperar.html')

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

def landing_view(request):
    return render(request, 'recomendations/landing.html')

def registro_view(request):
    if request.method == 'POST':
        return redirect('onboarding')
    return render(request, 'recomendations/registro.html')

def onboarding_view(request):
    if request.method == 'POST':
        return redirect('recommendations')
    return render(request, 'recomendations/onboarding.html')

def mostrar_recomendaciones(request):
    # Simulación de datos para la interfaz (luego vendrán de Neo4j)
    recommendations = [
        {
            'name': 'Antigua Guatemala', 
            'cost': 'Q550', 
            'tag': 'Colonial', 
            'image': 'https://images.unsplash.com/photo-1526487046039-335a122851ee?q=80&w=600&auto=format&fit=crop'
        },
        {
            'name': 'Lago Atitlán', 
            'cost': 'Q400', 
            'tag': 'Naturaleza', 
            'image': 'https://images.unsplash.com/photo-1582424075549-b5cfccda7950?q=80&w=600&auto=format&fit=crop'
        },
        {
            'name': 'Semuc Champey', 
            'cost': 'Q350', 
            'tag': 'Aventura', 
            'image': 'https://images.unsplash.com/photo-1598284687989-130ab63f73ce?q=80&w=600&auto=format&fit=crop'
        },
        {
            'name': 'Tikal, Petén', 
            'cost': 'Q600', 
            'tag': 'Historia', 
            'image': 'https://images.unsplash.com/photo-1512556798208-148886470870?q=80&w=600&auto=format&fit=crop'
        }
    ]

    context = {
        'user_name': 'USUARIO1', # aqui va a ir el nombre del usuario que se logueo, por ahora es un placeholder
        'recommendations': recommendations
    }
    return render(request, 'recomendations/recomendaciones.html', context)