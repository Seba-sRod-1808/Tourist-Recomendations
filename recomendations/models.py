"""
PROCESO: Definición de Modelos de Datos (Nodos y Relaciones)
DESCRIPCIÓN: Define la estructura del grafo en Neo4j utilizando neomodel. 
Incluye nodos para Estudiantes, Lugares, Categorías, Carreras, Ciudades y Etiquetas, 
así como las relaciones y propiedades que los vinculan.
"""

from django.db import models
from neomodel import (
    StructuredNode, StructuredRel,
    StringProperty, FloatProperty,
    IntegerProperty, DateTimeProperty,
    RelationshipTo, RelationshipFrom
)

class LikesRel(StructuredRel):
    weight = FloatProperty(default=1.0)

class VisitedRel(StructuredRel):
    rating = FloatProperty()
    comment = StringProperty()
    timestamp = DateTimeProperty()
    budget_spent = FloatProperty()

class NearRel(StructuredRel):
    distance_km = FloatProperty(required=True)

class PreferenceRel(StructuredRel):
    weight = FloatProperty(required=True)

class Student(StructuredNode):
    uid = StringProperty(unique_index=True)
    django_user_id = IntegerProperty(unique_index=True)
    name = StringProperty()
    budget = FloatProperty()
    universidad = StringProperty()
    presupuesto = StringProperty()

    visited = RelationshipTo('Place', 'VISITED', model=VisitedRel)
    likes = RelationshipTo('Category', 'LIKES', model=LikesRel)
    studies = RelationshipTo('Career', 'STUDIES')

class City(StructuredNode):
    name = StringProperty(unique_index=True)
    country = StringProperty()

class Place(StructuredNode):
    uid = StringProperty(unique_index=True, required=True)
    name = StringProperty(unique_index=True)
    cost = FloatProperty()
    popularity = FloatProperty(default=0.0)
    lat = FloatProperty()
    lng = FloatProperty()

    city = RelationshipTo('City', 'LOCATED_IN')
    categories = RelationshipTo('Category', 'HAS_CATEGORY')
    tags = RelationshipTo('Tag', 'HAS_TAG')
    nearby = RelationshipTo('Place', 'NEAR', model=NearRel)

    preferred_by = RelationshipFrom('Career', 'PREFERS', model=PreferenceRel)
    visited_by = RelationshipFrom('Student', 'VISITED', model=VisitedRel)

class Category(StructuredNode):
    name = StringProperty(unique_index=True)
    liked_by = RelationshipFrom('Student', 'LIKES', model=LikesRel)
    places = RelationshipFrom('Place', 'HAS_CATEGORY')

class Career(StructuredNode):
    name = StringProperty(unique_index=True)
    prefers = RelationshipTo('Place', 'PREFERS', model=PreferenceRel)
    students = RelationshipFrom('Student', 'STUDIES')

class Tag(StructuredNode):
    name = StringProperty(unique_index=True)
    places = RelationshipFrom('Place', 'HAS_TAG')
