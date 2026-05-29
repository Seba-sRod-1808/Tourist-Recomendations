from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('home/', views.mostrar_recomendaciones, name='recommendations'),
    path('recuperar-contrasena/', views.recuperar_view, name='recuperar_contrasena'),
]
