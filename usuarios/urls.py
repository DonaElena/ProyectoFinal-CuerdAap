from django.urls import path
from usuarios import views
from usuarios.views import CrearPerfil, EditarPerfil, EliminarPerfil
from usuarios.views import MostrarPerfil

urlpatterns = [
    path('perfil/<int:usuario_id>/',MostrarPerfil.as_view(), name='perfil-detail'),
    path('perfil_form/', CrearPerfil.as_view(), name='perfil-form'),
    path('perfil_editar/<int:usuario_id>/', EditarPerfil.as_view(), name='perfil-editar'),
    path('perfil_eliminar/<int:pk>/', EliminarPerfil.as_view(), name='perfil-eliminar')
]

