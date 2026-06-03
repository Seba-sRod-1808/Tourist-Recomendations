"""
PROCESO: Generación Masiva de Usuarios Simulados
DESCRIPCIÓN: Comando de Django para poblar las bases de datos (SQLite y Neo4j) 
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
    help = "Genera cientos de usuarios simulados basados en encuesta.csv con tendencias estandarizadas"

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

        # TENDENCIAS ESTANDARIZADAS POR CARRERA (User Mandate)
        # Sistemas: Playa, Historia
        # Mecánica: Playa, Aventura
        # Psicología: Aventura
        # Medicina: Naturaleza, Cultura
        # etc.
        TENDENCIAS = {
            "Ingeniería En Sistemas": ["playa", "historia"],
            "Sistemas": ["playa", "historia"],
            "Ingeniería Mecánica": ["playa", "aventura"],
            "Psicología Clínica": ["aventura"],
            "Medicina": ["naturaleza", "cultura"],
            "Administracion": ["cultura", "colonial"],
            "Marketing": ["playa", "gastronomia"],
            "Derecho": ["historia", "colonial"],
            "Arquitectura": ["historia", "cultura"],
            "Ingeniería Química": ["naturaleza", "gastronomia"],
            "Matemática Aplicada": ["historia", "aventura"],
            "Matemáticas": ["historia", "aventura"],
            "Ingeniería En Alimentos": ["gastronomia", "naturaleza"],
            "Ingeniería Civil": ["historia", "aventura"],
            "Ingeniería Electrónica": ["historia", "playa"],
            "Biología": ["naturaleza", "aventura"],
            "Antropología": ["historia", "cultura"],
            "Artes Liberales": ["cultura", "colonial"]
        }

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

        places_results, _ = db.cypher_query("MATCH (p:Place) RETURN p.uid, p.name")
        place_name_to_uid = {row[1]: row[0] for row in places_results}
        
        place_alias = {
            "Antigua Guatemala": "Antigua Guatemala",
            "Lago Atitlán": "Lago Atitlan",
            "Semuc Champey": "Semuc Champey",
            "Tikal": "Tikal, Peten",
            "Río Dulce": "Rio Dulce",
            "Monterrico": "Monterrico",
            "Chichicastenango": "Chichicastenango",
            "Livingston": "Livingston"
        }

        user_count = 0
        multiplier = 10 

        for i in range(multiplier):
            for row in rows:
                try:
                    raw_univ = row[1]
                    raw_career = row[2]
                    raw_budget = row[4]
                    raw_visited = row[10]

                    base_name = f"Estudiante_{user_count}"
                    username = f"user_{uuid.uuid4().hex[:8]}"
                    email = f"{username}@uvg.edu.gt"
                    
                    dj_user = User.objects.create_user(
                        username=username, 
                        email=email, 
                        password="password123",
                        first_name=base_name,
                        last_name=f"Simulado_{i}"
                    )

                    neo4j.create_student(dj_user.id, f"{base_name} {i}")

                    # APLICAR TENDENCIA ESTANDARIZADA
                    selected_cats = TENDENCIAS.get(raw_career, [])
                    if not selected_cats:
                        # Si no hay tendencia, usamos el CSV normalizado
                        raw_prefs = row[5]
                        for k, v in cat_map.items():
                            if k in raw_prefs:
                                selected_cats.append(v)
                    
                    if not selected_cats:
                        selected_cats = ["naturaleza"]

                    norm_budget = raw_budget.replace("Q200 - Q500", "Q200–Q500")

                    neo4j.set_student_preferences(
                        django_user_id=dj_user.id,
                        carrera=raw_career,
                        universidad=raw_univ,
                        categorias=selected_cats,
                        presupuesto=norm_budget
                    )

                    visited_names = [v.strip() for v in raw_visited.split(',')]
                    for v_name in visited_names:
                        system_name = place_alias.get(v_name)
                        if system_name and system_name in place_name_to_uid:
                            p_uid = place_name_to_uid[system_name]
                            rating = random.uniform(3.8, 5.0) # Tendencia positiva
                            neo4j.add_review(dj_user.id, p_uid, rating=rating, comment="Generado automáticamente")

                    user_count += 1
                    if user_count % 50 == 0:
                        self.stdout.write(f"Generados {user_count} usuarios...")

                except Exception as e:
                    continue

        self.stdout.write(self.style.SUCCESS(f"Población completada: {user_count} usuarios con tendencias lógicas."))
