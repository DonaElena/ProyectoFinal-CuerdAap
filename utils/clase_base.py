from django.views.generic import DetailView

from viajes.generar_mapa import MapaViaje
from viajes.models import ViajeOferta


class DetallesViajeBase(DetailView):

    """
    Clase base para vistas de detalle de un viaje ('DetailView').

    Esta clase se utiliza como base para implementar vistas de detalle de un viaje
    desde diferentes perspectivas de usuario:
        - Propietario del viaje
        - Usuario autenticado
        - Usuario no autenticado

    Características:
        - Modelo utilizado: `ViajeOferta`
        - Contexto: agrega al contexto la representación cartográfica del viaje ('mapa')
          generada por la clase 'MapaViaje'.

    Métodos sobrescritos:
        - get_context_data(**kwargs):
            Añade al contexto la variable 'mapa', que contiene el HTML del mapa
            correspondiente al viaje actual.
    """

    model = ViajeOferta
    context_object_name = 'viaje'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        mapa = MapaViaje(self.object)

        context['mapa'] = mapa.html
        return context