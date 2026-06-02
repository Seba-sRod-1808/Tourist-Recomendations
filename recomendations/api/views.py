"""
PROCESO: Capa de Vistas
DESCRIPCIÓN: Gestiona las peticiones HTTP y la lógica de presentación.
Incluye el manejo de autenticación de usuarios, registro de preferencias,
visualización de recomendaciones personalizadas, detalles de destinos y perfiles.
Actúa como puente entre la lógica de negocio y los templates de Django.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from recomendations.queries import queries as neo4j
from recomendations.services.recomendation_service import RecommendationService
from recomendations.services.recommendation_debugger import RecommendationDebugger

MOCK_DESTINATIONS = [
    {
        'uid': '1',
        'name': 'Antigua Guatemala',
        'cost': 550,
        'score': 94,
        'category': 'cultura historia',
        'tag': 'Colonial',
        'match_reason': '8 estudiantes de Ingeniería con presupuesto similar lo visitaron este mes.',
        'image': 'https://images.unsplash.com/photo-1518105779142-d975f22f1b0a?q=80&w=1000',
    },
    {
        'uid': '2',
        'name': 'Lago Atitlán',
        'cost': 400,
        'score': 91,
        'category': 'naturaleza aventura',
        'tag': 'Naturaleza',
        'match_reason': 'Encaja con tu preferencia por naturaleza. Ideal para fin de semana.',
        'image': 'https://images.unsplash.com/photo-4uhaeralB_M?q=80&w=1000',
    },
]

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('recommendations')
    return render(request, 'recomendations/landing.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('recommendations')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
        if user is not None:
            login(request, user)
            return redirect('recommendations')
        messages.error(request, 'Correo o contraseña incorrectos.')
    return render(request, 'recomendations/login.html')

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('recommendations')
    
    # Limpiamos mensajes previos acumulados para que no salgan al crear cuenta
    storage = messages.get_messages(request)
    for _ in storage:
        pass
        
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Ya existe una cuenta con ese correo.')
            return render(request, 'recomendations/registro.html')
        user = User.objects.create_user(username=email, email=email, password=password)
        parts = nombre.split(' ', 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''
        user.save()
        login(request, user)
        try:
            neo4j.create_student(user.id, nombre)
        except Exception as e:
            print(f"Neo4j create_student error: {e}")
        return redirect('onboarding')
    return render(request, 'recomendations/registro.html')

def recuperar_view(request):
    if request.method == 'POST':
        messages.success(request, 'Si ese correo está registrado, recibirás las instrucciones pronto.')
        return redirect('password_reset')
    return render(request, 'recomendations/recuperar.html')

def logout_view(request):
    logout(request)
    request.session.flush() # Borra todo rastro de la sesión anterior
    return redirect('landing')

@login_required(login_url='login')
def onboarding_view(request):
    if request.method == 'POST':
        prefs = {
            'universidad': request.POST.get('universidad', ''),
            'carrera': request.POST.get('carrera', ''),
            'categorias': request.POST.getlist('categorias'),
            'presupuesto': request.POST.get('presupuesto', ''),
            'compania': request.POST.getlist('compania'),
        }
        # Guardamos en sesión para acceso rápido, pero Neo4j es la fuente de verdad
        request.session['preferences'] = prefs
        try:
            neo4j.set_student_preferences(
                django_user_id=request.user.id,
                carrera=prefs['carrera'],
                universidad=prefs['universidad'],
                categorias=prefs['categorias'],
                presupuesto=prefs['presupuesto'],
            )
            # Forzamos que la sesión se guarde
            request.session.modified = True
        except Exception as e:
            print(f"Neo4j set_student_preferences error: {e}")
        return redirect('recommendations')
    return render(request, 'recomendations/onboarding.html')

@login_required(login_url='login')
def mostrar_recomendaciones(request):
    # Sincronizamos preferencias desde Neo4j para asegurar que el algoritmo y la UI estén alineados
    profile = neo4j.get_student_profile(request.user.id)
    if profile:
        prefs = {
            'carrera': profile['carrera'],
            'universidad': profile['universidad'],
            'categorias': profile['categorias'],
            'presupuesto': profile['presupuesto']
        }
        request.session['preferences'] = prefs
    else:
        prefs = request.session.get('preferences', {})
    
    try:
        debugger = RecommendationDebugger()
        neo4j_results = debugger.recommend_with_debug(request.user.id, limit=6)
        recommendations = neo4j_results if neo4j_results else None
    except Exception as e:
        print(f"Neo4j get_recommendations error: {e}")
        recommendations = None

    if recommendations is None:
        recommendations = sorted(MOCK_DESTINATIONS, key=lambda x: x.get('score', 0), reverse=True)

    context = {
        'user_name': request.user.first_name or request.user.email,
        'recommendations': recommendations,
        'total': len(recommendations) if recommendations else 0,
        'prefs': prefs,
    }
    return render(request, 'recomendations/recomendaciones.html', context)

@login_required(login_url='login')
def perfil_view(request):
    profile = neo4j.get_student_profile(request.user.id)
    if profile:
        prefs = {
            'carrera': profile['carrera'],
            'universidad': profile['universidad'],
            'categorias': profile['categorias'],
            'presupuesto': profile['presupuesto']
        }
    else:
        prefs = request.session.get('preferences', {})

    context = {
        'user_name': request.user.first_name or request.user.email,
        'email': request.user.email,
        'prefs': prefs
    }
    return render(request, 'recomendations/perfil.html', context)

@login_required(login_url='login')
def destino_detalle_view(request, uid):
    destino = None
    es_favorito = False
    try:
        destino = neo4j.get_place_details_by_uid(str(uid))
        if destino:
            if 'popularity' in destino:
                destino['score'] = int((destino['popularity'] or 0.5) * 100)
            
            # Verificar si ya es favorito
            favoritos = neo4j.get_favorites(request.user.id)
            es_favorito = any(str(row[0]) == str(uid) for row in favoritos)

    except Exception as e:
        print(f"Error al buscar detalle en Neo4j: {e}")
        
    if not destino:
        destino = next((d for d in MOCK_DESTINATIONS if str(d['uid']) == str(uid)), None)
    
    if not destino:
        return redirect('recommendations') 
        
    return render(request, 'recomendations/destino_detalle.html', {
        'destino': destino,
        'es_favorito': es_favorito
    })

@login_required(login_url='login')
def eliminar_favorito_view(request, uid):
    if request.method == 'POST':
        try:
            neo4j.remove_favorite(request.user.id, uid)
            messages.success(request, '¡Destino eliminado de tus favoritos!')
        except Exception as e:
            print(f"Error al eliminar favorito: {e}")
            messages.error(request, 'No se pudo eliminar el favorito.')
    
    # Redirigir según de donde venga
    next_url = request.GET.get('next', 'favoritos')
    if next_url == 'detalle':
        return redirect('destino_detalle', uid=uid)
    return redirect('favoritos')

@login_required(login_url='login')
def explorar_view(request):
    query = request.GET.get('q', '').lower()
    categoria = request.GET.get('categoria', '')
    try:
        destinations = neo4j.get_all_places()
    except Exception as e:
        print(f"Neo4j get_all_places error: {e}")
        destinations = MOCK_DESTINATIONS

    if query:
        destinations = [d for d in destinations if query in d['name'].lower()]
    if categoria:
        destinations = [d for d in destinations if categoria.lower() in d.get('category', '').lower() or categoria.lower() in d.get('tag', '').lower()]
    
    context = {
        'user_name': request.user.first_name or request.user.email,
        'destinations': destinations,
        'categoria_actual': categoria 
    }
    return render(request, 'recomendations/explorar.html', context)

@login_required(login_url='login')
def mis_viajes_view(request):
    visited = neo4j.get_visited_places(request.user.id)
    return render(request, 'recomendations/mis_destinos.html', {
        'user_name': request.user.first_name or request.user.username,
        'visited': visited
    })

@login_required(login_url='login')
def guardar_favorito_view(request, uid):
    if request.method == 'POST':
        try:
            neo4j.add_favorite(request.user.id, uid)
            messages.success(request, '¡Destino guardado en tus favoritos!')
        except Exception as e:
            print(f"Error al guardar favorito: {e}")
            messages.error(request, 'Hubo un error al guardar el destino.')
    
    return redirect('destino_detalle', uid=uid)

@login_required(login_url='login')
def favoritos_view(request):
    try:
        raw_favs = neo4j.get_favorites(request.user.id)
        favoritos = []
        
        service = RecommendationService()
        for row in raw_favs:
            categorias_lista = row[3] if row[3] else []
            favoritos.append({
                'uid': row[0],
                'name': row[1],
                'cost': int(row[2]),
                'tag': categorias_lista[0].capitalize() if categorias_lista else "Destino",
                'score': int((row[4] or 0) * 100),
                'image': service._get_image(row[1])
            })
            
        sort_by = request.GET.get('sort', 'match')
        if sort_by == 'price':
            favoritos = sorted(favoritos, key=lambda x: x['cost'])
        elif sort_by == 'recent':
            favoritos.reverse()
        else:
            favoritos = sorted(favoritos, key=lambda x: x['score'], reverse=True)
            
    except Exception as e:
        print(f"Error cargando favoritos: {e}")
        favoritos = []
        sort_by = 'match'

    context = {
        'user_name': request.user.first_name or request.user.email,
        'favoritos': favoritos,
        'current_sort': sort_by
    }
    return render(request, 'recomendations/favoritos.html', context)
