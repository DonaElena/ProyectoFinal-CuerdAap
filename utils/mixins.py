from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from usuarios.models import Perfil


class EsPropietarioMixin(LoginRequiredMixin):

    """
    Permite obtener el perfil específico de cada usuario a través de del id de usuario.
    Necesario en las vistas que trabajan con el perfil.

    Métodos sobrescritos:
    get_object(queryset=None)
        - Se sobreescribe para buscar el perfil a través del id de usuario que obtiene
          de los kwargs de la URL.
    get_context_data(**kwargs)
       - Añade al contexto el tag de 'es_propietario'. A través de este tag se pueden
         controlar funcionalidades de la vista y facilitar su reutilización.

    """
    def get_object(self,queryset=None):
        usuario_id = self.kwargs.get('usuario_id')
        return get_object_or_404(Perfil,usuario_id=usuario_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_propietario'] = (self.object.usuario_id == self.request.user.id)
        return context

class RevisarPermisosMixin(UserPassesTestMixin):

    """
    Permite controlar las acciones que pueden hacer los usuarios en vistas que utilizan
    el objeto Perfil.
    Pasa el test si el perfil sobre el que se intenta hacer una acción es el perfil
    del usuario autenticado

    Métodos:
    - test_func():
       compara si el id del perfil sobre el que se intenta hacer una acción es el mismo
       del usuario que está logeado

    - handle_no_permission():
      Devuelve un HttpResponseForbidden en caso de que no pase el test
    """

    def test_func(self):
        return self.get_object().usuario_id == self.request.user.id

    def handle_no_permission(self):
        return HttpResponseForbidden('No tienes permiso para esta acción')

class RevisarSiTieneReservasMixin:

    """
    Mixin utilizado en las vistas que editan o eliminan viajes. Dentro de dispatch se llama
    a self.get_object() para buscar reservas en el viaje antes de que se intente
    eliminar o editar un viaje.

    Métodos sobreescritos:
     - dispatch(request,*args,**kwargs):
        Obtiene la instancia del objeto ViajeOferta y bloquea el flujo si tiene reservas
        o permite que continúe.
    """

    def dispatch(self,request, *args, **kwargs):

        self.viaje = self.get_object()

        if self.viaje.reservas.exists():
            return HttpResponseForbidden('No puedes editar ni cancelar el viaje porque tiene reservas. Para cualquier cancelación o modificación, contacta a los/as pasajeros/as')
        else:
            return super().dispatch(request,*args,**kwargs)


class TieneReservasContextMixin:

    """
    Mixin utilizado para las vistas que trabajan con información de las reservas.
    Nos permite saber si un viaje tiene reservas y si las tiene, qué perfiles son los
    que han reservado en el viaje.

    Método sobreescrito:
      - get_context_data(**kwargs):
        Si tiene reservas el viaje devuelve el tag True y una lista con los perfiles
        que han reservado. En caso contrario devuelve el tag False y una lista vacía
    """

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        perfiles = []

        if self.object.reservas.exists():
            tiene_reserva = True
            reservas = self.object.reservas.all().distinct()

            for reserva in reservas:
                perfiles.append(reserva.quien_reserva)
        else:
            tiene_reserva = False

        context['tiene_reserva'] = tiene_reserva
        context['perfiles'] = perfiles
        return context



class EsPropietarioViajeMixin(LoginRequiredMixin):

    """
    Mixin que utilizan las vistas que trabajan con el objeto ViajeOferta para determinar
    si el usuario es propietario del viaje con el que trabaja la vista.
    Especialmente útil para acciones de edición y cancelación del viaje.

    Métodos que sobreescrite:

     - dispatch(request, *args, **kwargs):
       crea el tag de es_propietario: booleano que afirma o niega si es propietario.
       en caso de no ser propietario del viaje, redirige al login.
    - get_context_data(**kwargs):
      le pasa al contexto de la vista el tag de es_propietario
    """

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.es_propietario = False

        if self.request.user.perfil != self.object.propietario_vehiculo:
            return redirect('account_login')
        else:
            self.es_propietario = True
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['es_propietario'] = self.es_propietario

        return context

class NoCaducadoMixin:

    """
    Mixin útil para las vistas que devuelven la búsqueda de viajes. Permite filtrar
    los viajes por su fecha y hora de forma que devuelve los viajes que no han caducado
    aún.
    Utilizamos Q objects de módulo models para construir consultar OR complejas
    """

    @staticmethod
    def filter_no_caducados(qs, fecha_field='fecha_salida', hora_field='hora'):
        """
        Recibe un QuerySet y filtra los objetos cuyo viaje no ha caducado.
        - fecha_field: nombre del campo fecha
        - hora_field: nombre del campo hora

        Se utiliza para filtrar objetos ViajeOferta, Solicitud y Reserva.
        Al utilizar el desempaquetamiento de un diccionario podemos utilizar de forma dinámica el filtro.

        """
        ahora = timezone.now()
        return qs.filter(
            Q(**{f"{fecha_field}__gt": ahora.date()}) |
            Q(**{f"{fecha_field}__exact": ahora.date(), f"{hora_field}__gt": ahora.time()})
        )



