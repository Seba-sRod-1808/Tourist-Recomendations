from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from recomendations.queries import queries as neo4j

MOCK_DESTINATIONS = [
    {
        'uid': '1',
        'name': 'Antigua Guatemala',
        'cost': 550,
        'score': 94,
        'category': 'cultura historia',
        'tag': 'Colonial',
        'match_reason': '8 estudiantes de Ingeniería con presupuesto similar lo visitaron este mes.',
        'image': 'https://images.unsplash.com/photo-1526487046039-335a122851ee?q=80&w=600&auto=format&fit=crop',
    },
    {
        'uid': '2',
        'name': 'Lago Atitlán',
        'cost': 400,
        'score': 91,
        'category': 'naturaleza aventura',
        'tag': 'Naturaleza',
        'match_reason': 'Encaja con tu preferencia por naturaleza. Ideal para fin de semana.',
        'image': 'https://images.unsplash.com/photo-1582424075549-b5cfccda7950?q=80&w=600&auto=format&fit=crop',
    },
    {
        'uid': '3',
        'name': 'Semuc Champey',
        'cost': 350,
        'score': 87,
        'category': 'naturaleza aventura',
        'tag': 'Aventura',
        'match_reason': 'Destino popular entre estudiantes universitarios en vacaciones.',
        'image': 'https://images.unsplash.com/photo-1598284687989-130ab63f73ce?q=80&w=600&auto=format&fit=crop',
    },
    {
        'uid': '4',
        'name': 'Tikal, Petén',
        'cost': 600,
        'score': 82,
        'category': 'historia cultura naturaleza',
        'tag': 'Historia',
        'match_reason': 'Coincide con intereses en historia maya.',
        'image': 'https://images.unsplash.com/photo-1512556798208-148886470870?q=80&w=600&auto=format&fit=crop',
    },
    {
        'uid': '5',
        'name': 'Río Dulce',
        'cost': 300,
        'score': 79,
        'category': 'aventura naturaleza playa',
        'tag': 'Aventura',
        'match_reason': 'El más económico. Popular entre estudiantes con tiempo limitado.',
        'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=600&auto=format&fit=crop',
    },
    {
        'uid': '6',
        'name': 'Monterrico',
        'cost': 650,
        'score': 75,
        'category': 'playa naturaleza',
        'tag': 'Playa',
        'match_reason': 'Estudiantes que visitaron Atitlán también lo califican altamente.',
        'image': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=600&auto=format&fit=crop',
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
        return redirect('recuperar_contrasena')
    return render(request, 'recomendations/password_reset_confirm.html')


def logout_view(request):
    logout(request)
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
        request.session['preferences'] = prefs
        try:
            neo4j.set_student_preferences(
                django_user_id=request.user.id,
                carrera=prefs['carrera'],
                universidad=prefs['universidad'],
                categorias=prefs['categorias'],
                presupuesto=prefs['presupuesto'],
            )
        except Exception as e:
            print(f"Neo4j set_student_preferences error: {e}")
        return redirect('recommendations')
    return render(request, 'recomendations/onboarding.html')


@login_required(login_url='login')
def mostrar_recomendaciones(request):
    prefs = request.session.get('preferences', {})
    categorias = prefs.get('categorias', [])

    try:
        neo4j_results = neo4j.get_recommendations(django_user_id=request.user.id, limit=6)
        recommendations = neo4j_results if neo4j_results else None
    except Exception as e:
        print(f"Neo4j get_recommendations error: {e}")
        recommendations = None

    if recommendations is None:
        if categorias:
            scored = []
            for dest in MOCK_DESTINATIONS:
                dest_cats = dest['category'].split()
                bonus = sum(3 for c in categorias if c in dest_cats)
                scored.append({**dest, 'score': min(dest['score'] + bonus, 99)})
            recommendations = sorted(scored, key=lambda x: x['score'], reverse=True)
        else:
            recommendations = sorted(MOCK_DESTINATIONS, key=lambda x: x['score'], reverse=True)

    context = {
        'user_name': request.user.first_name or request.user.email,
        'recommendations': recommendations,
        'total': len(recommendations),
        'prefs': prefs,
    }
    return render(request, 'recomendations/recomendaciones.html', context)

@login_required(login_url='login')
def perfil_view(request):
    prefs = request.session.get('preferences', {})
    context = {
        'user_name': request.user.first_name or request.user.email,
        'email': request.user.email,
        'prefs': prefs
    }
    return render(request, 'recomendations/perfil.html', context)

@login_required(login_url='login')
def destino_detalle_view(request, uid):
    destino = next((d for d in MOCK_DESTINATIONS if d['uid'] == uid), None)
    
    if not destino:
        return redirect('recommendations') 
        
    return render(request, 'recomendations/destino_detalle.html', {'destino': destino})


@login_required(login_url='login')
def explorar_view(request):
    query = request.GET.get('q', '').lower()
    
    try:
        destinations = None
        if not destinations:
            destinations = MOCK_DESTINATIONS
    except Exception as e:
        print(f"Neo4j get_all_places error: {e}")
        destinations = MOCK_DESTINATIONS

    if query:
        destinations = [d for d in destinations if query in d['name'].lower()]

    context = {
        'user_name': request.user.first_name or request.user.email,
        'destinations': destinations
    }
    return render(request, 'recomendations/explorar.html', context)

@login_required(login_url='login')
def mis_viajes_view(request):
    return render(request, 'recomendations/mis_viajes.html', {
        'user_name': request.user.first_name or request.user.username
    })