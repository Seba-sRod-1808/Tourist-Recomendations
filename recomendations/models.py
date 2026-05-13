from django.db import models

from neomodel import (
    StructuredNode, StructuredRel,
    UniqueIdProperty, StringProperty, FloatProperty,
    IntegerProperty, DateTimeProperty,
    RelationshipTo, RelationshipFrom
)

# =========================
# RELACIONES
# =========================

class LikesRel(StructuredRel):
    weight = FloatProperty(default=1.0) 


class VisitedRel(StructuredRel):
    rating = FloatProperty() 
    timestamp = DateTimeProperty()
    budget_spent = FloatProperty()


class NearRel(StructuredRel):
    distance_km = FloatProperty(required=True)


class PreferenceRel(StructuredRel):
    weight = FloatProperty(required=True)


# =========================
# NODOS
# =========================

class Student(StructuredNode):
    uid = UniqueIdProperty()
    django_user_id = IntegerProperty(unique_index=True)

    name = StringProperty()
    budget = FloatProperty()

    visited = RelationshipTo('Destination', 'VISITED', model=VisitedRel)
    likes = RelationshipTo('Category', 'LIKES', model=LikesRel)
    studies = RelationshipTo('Career', 'STUDIES')


class City(StructuredNode):
    name = StringProperty(unique_index=True)
    country = StringProperty()


class Destination(StructuredNode):
    uid = UniqueIdProperty()

    name = StringProperty()
    cost = FloatProperty()
    popularity = FloatProperty(default=0.0)

    city = RelationshipTo('City', 'LOCATED_IN')
    categories = RelationshipTo('Category', 'HAS_CATEGORY')
    tags = RelationshipTo('Tag', 'HAS_TAG')

    nearby = RelationshipTo('Destination', 'NEAR', model=NearRel)

    preferred_by = RelationshipFrom('Career', 'PREFERS', model=PreferenceRel)
    visited_by = RelationshipFrom('Student', 'VISITED', model=VisitedRel)


class Category(StructuredNode):
    name = StringProperty(unique_index=True)

    liked_by = RelationshipFrom('Student', 'LIKES', model=LikesRel)
    destinations = RelationshipFrom('Destination', 'HAS_CATEGORY')


class Career(StructuredNode):
    name = StringProperty(unique_index=True)

    prefers = RelationshipTo('Destination', 'PREFERS', model=PreferenceRel)

    students = RelationshipFrom('Student', 'STUDIES')


class Tag(StructuredNode):
    name = StringProperty(unique_index=True)

    destinations = RelationshipFrom('Destination', 'HAS_TAG')