from django.urls import path
from . import views, api_views

urlpatterns = [
    # UI Views
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('home/', views.mostrar_recomendaciones, name='recommendations'),
    path('recuperar-contrasena/', views.recuperar_view, name='recuperar_contrasena'),

    # REST API Endpoints
    path('api/recommendations/', api_views.get_recommendations_api, name='api_recommendations'),
    path('api/recommendations/review/', api_views.submit_review_api, name='api_submit_review'),
    path('api/recommendations/explain/', api_views.explain_recommendation_api, name='api_explain_recommendation'),
]

