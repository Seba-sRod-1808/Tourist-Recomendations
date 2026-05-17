from django.urls import path
from . import views  

urlpatterns = [
    # Ruta principal (Landing / Login)
    path('', views.login_view, name='login'),
    
    # Ruta para crear cuenta y llenar la encuesta
    path('registro/', views.registro_view, name='registro'),
    
    # La ruta de recomendaciones
    path('mis-recomendaciones/', views.mostrar_recomendaciones, name='recommendations'),
    
    # Ruta para el panel de administración
    path('admin-destinos/', views.admin_view, name='panel_admin'),

    # Ruta de recuperación de contraseña
    path('recuperar-contrasena/', views.recuperar_view, name='recuperar_contrasena'),

]