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

        # Mapeo de categorías del CSV a las del sistema
        cat_map = {
            "Naturaleza": "naturaleza",
            "Playas / Ríos": "playa",
            "Historia": "historia",
            "Arqueología": "historia",
            "Mercados / Cultura": "cultura",
            "Gastronomía": "gastronomia",
            "Colonial": "colonial",
            "Aventura": "aventura"
        }

        # Mapeo de nombres de lugares a los del sistema (Neo4j)
        # Necesitamos los UIDs reales de los lugares existentes
        places_results, _ = db.cypher_query("MATCH (p:Place) RETURN p.uid, p.name")
        place_name_to_uid = {row[1]: row[0] for row in places_results}
        
        # Alias para normalización de nombres
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
            "Livingston": "Livingston"
        }

        user_count = 0
        multiplier = 10 # Generar 10 usuarios por cada fila de la encuesta para llegar a cientos

        for i in range(multiplier):
            for row in rows:
                try:
                    # Datos básicos
                    raw_univ = row[1]
                    raw_career = row[2]
                    raw_budget = row[4]
                    raw_prefs = row[5]
                    raw_visited = row[10]

                    # Generar nombre único
                    base_name = f"Estudiante_{user_count}"
                    username = f"user_{uuid.uuid4().hex[:8]}"
                    email = f"{username}@uvg.edu.gt"
                    
                    # 1. Crear en Django
                    dj_user = User.objects.create_user(
                        username=username, 
                        email=email, 
                        password="password123",
                        first_name=base_name,
                        last_name=f"Simulado_{i}"
                    )

                    # 2. Crear en Neo4j
                    neo4j.create_student(dj_user.id, f"{base_name} {i}")

                    # 3. Normalizar Preferencias
                    selected_cats = []
                    for k, v in cat_map.items():
                        if k in raw_prefs:
                            selected_cats.append(v)
                    
                    if not selected_cats:
                        selected_cats = ["naturaleza"] # Fallback

                    # Normalizar presupuesto para que coincida con budget_map
                    norm_budget = raw_budget.replace("Q200 - Q500", "Q200–Q500") # Normalizar guión

                    neo4j.set_student_preferences(
                        django_user_id=dj_user.id,
                        carrera=raw_career,
                        universidad=raw_univ,
                        categorias=selected_cats,
                        presupuesto=norm_budget
                    )

                    # 4. Registrar Visitas (para Collaborative Filtering)
                    visited_names = [v.strip() for v in raw_visited.split(',')]
                    for v_name in visited_names:
                        system_name = place_alias.get(v_name)
                        if system_name and system_name in place_name_to_uid:
                            p_uid = place_name_to_uid[system_name]
                            rating = random.uniform(3.5, 5.0)
                            neo4j.add_review(dj_user.id, p_uid, rating=rating, comment="Generado automáticamente")

                    user_count += 1
                    if user_count % 50 == 0:
                        self.stdout.write(f"Generados {user_count} usuarios...")

                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error procesando fila: {e}"))
                    continue

        self.stdout.write(self.style.SUCCESS(f"Población completada: {user_count} usuarios generados."))
