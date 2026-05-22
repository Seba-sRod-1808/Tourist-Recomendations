from django.urls import path
from . import views  

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('mis-recomendaciones/', views.mostrar_recomendaciones, name='recommendations'),
    path('admin-destinos/', views.admin_view, name='panel_admin'),
    path('recuperar-contrasena/', views.recuperar_view, name='recuperar_contrasena'),
]