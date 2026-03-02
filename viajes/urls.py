from django.urls import path

from viajes.autocompletado_view import CiudadAutocomplete
from viajes.views import PublicarViaje, MostrarViajesPropios
from viajes import views, autocompletado_view


urlpatterns = [
    path('ciudad-autocomplete/', CiudadAutocomplete.as_view(), name='ciudad-autocomplete'),
    path('publicar_viaje/',PublicarViaje.as_view(), name='viaje-form'),
    path('detalles_viaje/<int:pk>/',views.DetallesViajePropietario.as_view(), name='viaje-detail'),
    path('viajes_publicados/', MostrarViajesPropios.as_view(), name='viajes-publicados'),
    path('editar_viaje/<int:pk>/', views.EditarViaje.as_view(), name='viaje-editar'),
    path('buscar_viaje/', views.BuscarViaje.as_view(), name='buscar-viaje'),
    path('resultados_busqueda/<str:ciudad_salida>/<str:ciudad_llegada>/<str:fecha>', views.ResultadosBusqueda.as_view(), name='resultados-busqueda'),
    path('detalles_viaje_busqueda/<int:pk>/', views.DetallesViaje.as_view(), name='viaje-detail-no-propietario'),
    path('cancelar_viaje/<int:pk>/', views.CancelarViaje.as_view(), name='viaje-delete'),
    path('solicitar_plazas/<int:pk>', views.SolicitarPlazas.as_view(), name='solicitar-plazas'),
    path('solicitudes_pendientes/<int:usuario_id>', views.MostrarSolicitudes.as_view(), name='solicitudes-pendientes'),
    path('gestion_solicitud/<int:pk>/<str:estado>', views.SolicitudAccion.as_view(), name='solicitud-accion'),
    path('reservas_viajes/<int:usuario_id>', views.MostrarReservas.as_view(), name='reservas-list')

]


