"""
PROCESO: Generación Masiva de Usuarios Simulados
DESCRIPCIÓN: Comando de Django para poblar las bases de datos
con cientos de perfiles de estudiantes basados en datos reales de una encuesta CSV.
Normaliza preferencias, presupuestos y visitas para crear un entorno de datos rico
que permita probar el algoritmo de recomendación y el filtrado colaborativo.
"""

import csv
import random
import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from neomodel import db
from recomendations.queries import queries as neo4j

class Command(BaseCommand):
    help = "Genera cientos de usuarios simulados basados en encuesta.csv"

    def handle(self, *args, **options):
        csv_path = 'encuesta.csv'
        self.stdout.write(f"Leyendo datos desde {csv_path}...")

        try:
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                rows = list(reader)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("No se encontró encuesta.csv en la raíz."))
            return

        self.stdout.write(f"Procesando {len(rows)} registros base...")

        # Mapeo de categorías del CSV a las del sistema (Normalizadas en setup_neo4j.py)
        cat_map = {
            "Naturaleza": "Naturaleza",
            "Playas / Ríos": "Playas y Ríos",
            "Historia": "Historia",
            "Arqueología": "Arqueología",
            "Mercados / Cultura": "Cultura",
            "Gastronomía": "Gastronomía",
            "Aventura": "Aventura"
        }

        # Mapeo de nombres de lugares a los del sistema (Neo4j)
        places_results, _ = db.cypher_query("MATCH (p:Place) RETURN p.uid, p.name")
        place_name_to_uid = {row[1]: row[0] for row in places_results}
        
        # Alias para normalización de nombres del CSV a los nombres oficiales en PLACES (TODOS LOS 31 LUGARES)
        place_alias = {

            "Antigua Guatemala": "Antigua Guatemala",
            "La Antigua": "Antigua Guatemala",
            "Antigua": "Antigua Guatemala",
            "Lago Atitlán": "Lago Atitlan",
            "Lago De Atitlan": "Lago Atitlan",
            "Atitlan": "Lago Atitlan",
            "Semuc Champey": "Semuc Champey",
            "Semuc": "Semuc Champey",
            "Tikal": "Tikal, Peten",
            "Peten": "Tikal, Peten",
            "Río Dulce": "Rio Dulce",
            "Rio Dulce": "Rio Dulce",
            "Monterrico": "Monterrico",
            "Chichicastenango": "Chichicastenango",
            "Livingston": "Livingston",
            "Quetzaltenango": "Quetzaltenango",
            "Xela": "Quetzaltenango",
            "Huehuetenango": "Huehuetenango",
            "Castillo de San Felipe": "Castillo de San Felipe",
            "Irtra Retalhuleu": "Irtra Retalhuleu",
            "Irtra": "Irtra Retalhuleu",
            "Volcan de Acatenango": "Volcan de Acatenango",
            "Acatenango": "Volcan de Acatenango",
            "Fuentes Georginas": "Fuentes Georginas",
            "Crater Azul": "Crater Azul",
            "Hun Nal Ye": "Hun Nal Ye",
            "Parque Naciones Unidas": "Parque Naciones Unidas",
            "Laguna del Pino": "Laguna del Pino",
            "Mixco Viejo": "Mixco Viejo",
            "Iximché": "Iximché",
            "Hobbitenango": "Hobbitenango",
            "Volcan de Pacaya": "Volcan de Pacaya",
            "Pacaya": "Volcan de Pacaya",
            "Finca El Amate": "Finca El Amate",
            "Cataratas Tatasirire": "Cataratas Tatasirire",
            "Laguna de Ayarza": "Laguna de Ayarza",
            "Ayarza": "Laguna de Ayarza",
            "Volcan de Ipala": "Volcan de Ipala",
            "Ipala": "Volcan de Ipala",
            "Biotopo del Quetzal": "Biotopo del Quetzal",
            "San Juan Comalapa": "San Juan Comalapa",
            "Comalapa": "San Juan Comalapa",
            "Cuevas de Candelaria": "Cuevas de Candelaria",
            "El Paredon": "El Paredon",
            "Tak'alik Ab'aj": "Tak'alik Ab'aj"
        }

        user_count = 0
        multiplier = 5 

        for i in range(multiplier):
            for row in rows:
                try:
                    raw_univ = row[1]
                    raw_career = row[2]
                    raw_budget = row[4]
                    raw_prefs = row[5]
                    raw_visited = row[10]

                    username = f"user_{uuid.uuid4().hex[:8]}"
                    email = f"{username}@uvg.edu.gt"
                    
                    dj_user = User.objects.create_user(
                        username=username, 
                        email=email, 
                        password="password123",
                        first_name=f"Estudiante_{user_count}",
                        last_name=f"Simulado"
                    )

                    neo4j.create_student(dj_user.id, f"Estudiante_{user_count}")

                    selected_cats = []
                    for k, v in cat_map.items():
                        if k in raw_prefs:
                            selected_cats.append(v)
                    
                    if not selected_cats:
                        selected_cats = ["Naturaleza"]

                    norm_budget = raw_budget.replace(" - ", "–").replace(" - ", "–")

                    neo4j.set_student_preferences(
                        django_user_id=dj_user.id,
                        carrera=raw_career,
                        universidad=raw_univ,
                        categorias=selected_cats,
                        presupuesto=norm_budget
                    )

                    # Registrar visitas del CSV
                    visited_names = [v.strip() for v in raw_visited.split(',')]
                    user_visited_uids = set()
                    
                    for v_name in visited_names:
                        system_name = place_alias.get(v_name)
                        if system_name and system_name in place_name_to_uid:
                            p_uid = place_name_to_uid[system_name]
                            user_visited_uids.add(p_uid)
                            rating = random.uniform(3.5, 5.0)
                            neo4j.add_review(dj_user.id, p_uid, rating=rating, comment="Basado en encuesta")

                    # Inyectar visitas aleatorias a los 31 lugares para asegurar densidad en el grafo
                    # Especialmente a los lugares que no suelen aparecer en la encuesta
                    all_place_uids = list(place_name_to_uid.values())
                    num_extra = random.randint(1, 4)
                    extra_places = random.sample(all_place_uids, min(num_extra, len(all_place_uids)))
                    
                    for p_uid in extra_places:
                        if p_uid not in user_visited_uids:
                            rating = random.uniform(3.8, 5.0)
                            neo4j.add_review(dj_user.id, p_uid, rating=rating, comment="Visita simulada para densidad")

                    user_count += 1
                    if user_count % 50 == 0:
                        self.stdout.write(f"Generados {user_count} usuarios...")

                except Exception as e:
                    continue

        self.stdout.write(self.style.SUCCESS(f"Población completada: {user_count} usuarios generados con visitas a los 31 destinos."))
