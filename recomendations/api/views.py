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
from django.core.files.storage import FileSystemStorage

from recomendations.queries import queries as neo4j
from recomendations.services.recomendation_service import RecommendationService
from recomendations.services.recommendation_debugger import RecommendationDebugger

# DICCIONARIO DE DESCRIPCIONES EXACTAS PARA CADA LUGAR
DESCRIPCIONES_LUGARES = {
    "Antigua Guatemala": "Hermosa ciudad colonial famosa por su arquitectura barroca, vibrantes calles empedradas y ruinas históricas, todo rodeado de imponentes volcanes.",
    "Lago Atitlan": "Considerado uno de los lagos más hermosos del mundo, situado en un enorme cráter y rodeado de tres majestuosos volcanes y pintorescos pueblos mayas.",
    "Semuc Champey": "Espectacular monumento natural oculto en la selva de Alta Verapaz, famoso por sus piscinas naturales de agua turquesa cristalina escalonadas sobre el río Cahabón.",
    "Tikal, Peten": "Antigua metrópolis de la civilización maya. Sus gigantescas pirámides y templos se alzan por encima del denso dosel de la selva tropical.",
    "Rio Dulce": "Impresionante río que conecta el Lago de Izabal con el Mar Caribe, navegando a través de un cañón espectacular lleno de exuberante vegetación.",
    "Monterrico": "Reserva natural en la costa del Pacífico, conocida por sus playas de arena negra volcánica, relajantes canales de manglares y conservación de tortugas.",
    "Chichicastenango": "Hogar del mercado tradicional indígena más vibrante de la región, un lugar perfecto para sumergirse en la cultura maya viva y adquirir artesanías únicas.",
    "Livingston": "Pintoresco pueblo caribeño accesible solo por barco. Es el corazón de la cultura Garífuna en Guatemala, ofreciendo deliciosa gastronomía y ritmos únicos.",
    "Quetzaltenango": "Conocida como Xela, es una ciudad con un clima fresco y acogedor, rica en historia, hermosa arquitectura neoclásica y rodeada de aguas termales.",
    "Huehuetenango": "Espectacular región montañosa en el occidente del país, puerta de entrada a la imponente cordillera de los Cuchumatanes y cenotes cristalinos.",
    "Castillo de San Felipe": "Fortaleza histórica colonial ubicada estratégicamente en la entrada del Lago de Izabal, construida por los españoles para defender la zona de piratas.",
    "Irtra Retalhuleu": "El complejo de parques de diversiones y acuáticos más grande de Centroamérica. Ideal para un fin de semana lleno de adrenalina, sol y mucha diversión.",
    "Volcan de Acatenango": "Un desafío épico de montañismo que recompensa con vistas espectaculares y la oportunidad única de dormir viendo las erupciones del vecino Volcán de Fuego.",
    "Fuentes Georginas": "Relajantes piscinas de aguas termales calentadas naturalmente por la actividad volcánica, inmersas en un espeso, frío y místico bosque nuboso.",
    "Crater Azul": "Un oasis surrealista escondido en Petén. Sus aguas son tan transparentes y azules que los increíbles jardines subacuáticos parecen estar flotando en el aire.",
    "Hun Nal Ye": "Un paraíso ecológico en Alta Verapaz que ofrece saltos a cenotes turquesas, senderismo, cabalgatas, canopy y exploración de cuevas místicas.",
    "Parque Naciones Unidas": "Un escape natural muy cercano a la ciudad, con senderos arbolados, churrasqueras, réplicas arqueológicas y miradores hacia el Lago de Amatitlán.",
    "Laguna del Pino": "Parque nacional ideal para una escapada rápida. Perfecto para hacer un picnic, remar en kayak, nadar o simplemente relajarse bajo la sombra de los pinos.",
    "Mixco Viejo": "Antigua capital del reino Poqomam, una impresionante fortaleza maya construida estratégicamente sobre colinas rodeadas de profundos barrancos.",
    "Iximché": "Antigua capital del reino Kaqchikel y un sitio arqueológico fascinante e histórico donde aún hoy se practican ceremonias y rituales mayas vivos.",
    "Hobbitenango": "Eco-parque temático mágico inspirado en la Comarca, en lo alto de las montañas. Disfruta de vistas increíbles, juegos de feria, miradores y buena comida.",
    "Volcan de Pacaya": "Un volcán activo de ascenso amigable, famoso por sus paisajes de roca volcánica donde los visitantes pueden asar masmelos con el calor geotérmico.",
    "Finca El Amate": "Reserva natural privada en las faldas del Volcán de Pacaya. Ofrece senderos de lava solidificada y praderas excepcionales para acampar bajo las estrellas.",
    "Cataratas Tatasirire": "Parque ecológico en Jalapa que cuenta con impresionantes cascadas, densos bosques, rutas de canopy y áreas seguras equipadas para acampar.",
    "Laguna de Ayarza": "Un imponente lago de aguas azules profundas formado en el fondo de un antiguo cráter colapsado, excelente para el buceo, la pesca y la desconexión total.",
    "Volcan de Ipala": "Ubicado en el oriente de Guatemala, ofrece un ascenso relativamente fácil que culmina en un cráter que alberga una hermosa y apacible laguna esmeralda.",
    "Biotopo del Quetzal": "Santuario natural en Baja Verapaz dedicado a proteger al ave nacional. Sus senderos te sumergen en un denso y místico bosque nuboso lleno de vida.",
    "San Juan Comalapa": "Conocida como la 'Florencia de América', es cuna de talentosos pintores de arte naíf, músicos y herencia cultural, destacando sus enormes murales históricos.",
    "Cuevas de Candelaria": "Una de las redes de cavernas más extensas de la región. Alberga un espectacular río subterráneo que los antiguos mayas consideraban la entrada al inframundo.",
    "El Paredon": "El destino de surf de mayor crecimiento en el país. Un pintoresco pueblo con calles de arena, ambiente relajado, vibra bohemia y atardeceres dorados.",
    "Tak'alik Ab'aj": "Un fascinante parque arqueológico en Retalhuleu que es testigo de la transición histórica entre la cultura Olmeca y el florecimiento de la civilización Maya."
}

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
        'name': 'Lago Atitlan',
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
    request.session.flush() 
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
            request.session.modified = True
        except Exception as e:
            print(f"Neo4j set_student_preferences error: {e}")
        return redirect('recommendations')
    return render(request, 'recomendations/onboarding.html')

@login_required(login_url='login')
def mostrar_recomendaciones(request):
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
        
    # INYECTAMOS LA DESCRIPCIÓN CORRECTA A CADA RECOMENDACIÓN
    for dest in recommendations:
        if not dest.get('description'):
            dest['description'] = DESCRIPCIONES_LUGARES.get(dest['name'], dest.get('match_reason', 'Un destino increíble esperando ser explorado.'))

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
            
            favoritos = neo4j.get_favorites(request.user.id)
            es_favorito = any(str(row[0]) == str(uid) for row in favoritos)

    except Exception as e:
        print(f"Error al buscar detalle en Neo4j: {e}")
        
    if not destino:
        destino = next((d for d in MOCK_DESTINATIONS if str(d['uid']) == str(uid)), None)
    
    if not destino:
        return redirect('recommendations') 
        
    # INYECTAMOS LA DESCRIPCIÓN CORRECTA AL DETALLE DEL DESTINO
    if not destino.get('description'):
        destino['description'] = DESCRIPCIONES_LUGARES.get(destino['name'], 'Un destino increíble esperando ser explorado.')
        
    return render(request, 'recomendations/destino_detalle.html', {
        'destino': destino,
        'es_favorito': es_favorito
    })

@login_required(login_url='login')
def registrar_visita_view(request, uid):
    if request.method == 'POST':
        try:
            rating = float(request.POST.get('rating', 5))
            comment = request.POST.get('comment', 'Visitado desde la web')
            neo4j.add_review(request.user.id, uid, rating, comment)
            messages.success(request, '¡Felicidades por tu viaje! Tu historial se ha actualizado.')
        except Exception as e:
            print(f"Error al registrar visita: {e}")
            messages.error(request, 'No se pudo registrar la visita.')
    
    return redirect('destino_detalle', uid=uid)

@login_required(login_url='login')
def eliminar_favorito_view(request, uid):
    if request.method == 'POST':
        try:
            neo4j.remove_favorite(request.user.id, uid)
            messages.success(request, '¡Destino eliminado de tus favoritos!')
        except Exception as e:
            print(f"Error al eliminar favorito: {e}")
            messages.error(request, 'No se pudo eliminar el favorito.')
    
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
        cat_lower = categoria.lower()
        if cat_lower in ['gastronomia', 'gastronomía']:
            destinations = [d for d in destinations if 'gastronom' in d.get('category', '').lower() or 'gastronom' in d.get('tag', '').lower()]
        else:
            destinations = [d for d in destinations if cat_lower in d.get('category', '').lower() or cat_lower in d.get('tag', '').lower()]
    
    for dest in destinations:
        if not dest.get('description'):
            dest['description'] = DESCRIPCIONES_LUGARES.get(dest['name'], 'Descubre lo que este lugar tiene para ofrecerte.')
            
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

@login_required(login_url='login')
def subir_foto_view(request):
    if request.method == 'POST' and request.FILES.get('foto_perfil'):
        foto = request.FILES['foto_perfil']
        fs = FileSystemStorage()
        filename = fs.save(f'perfil_{request.user.id}.jpg', foto)
        uploaded_file_url = fs.url(filename)
        
        request.session['foto_perfil_url'] = uploaded_file_url
        messages.success(request, '¡Foto de perfil actualizada correctamente!')
        
    return redirect('perfil')