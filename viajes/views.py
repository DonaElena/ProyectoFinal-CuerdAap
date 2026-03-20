from datetime import datetime, timedelta


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import OuterRef, Exists
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView, FormView, DeleteView

from usuarios.models import Perfil
from usuarios.views import EsPropietarioMixin
from utils.clase_base import DetallesViajeBase
from utils.mixins import RevisarSiTieneReservasMixin, EsPropietarioViajeMixin, TieneReservasContextMixin, \
    RevisarPermisosMixin
from viajes.forms import ViajeOfertaForm, BuscarViajeForm, SolicitarPlazaForm
from viajes.models import ViajeOferta, Reserva, Solicitud


class PublicarViaje(LoginRequiredMixin,CreateView):
    """
      Vista basada en clases para que un usuario autenticado pueda publicar un nuevo viaje.

      Hereda de `LoginRequiredMixin` para asegurar que solo usuarios logueados
      puedan acceder, y de `CreateView` para gestionar la creación de instancias
      del modelo `ViajeOferta`.

      Atributos:
          model (Model): Modelo asociado a la vista, `ViajeOferta`.
          form_class (Form): Formulario utilizado para crear la instancia de viaje.

      Métodos:
          form_valid(form):
              Se ejecuta cuando el formulario es válido. Asigna automáticamente
              el perfil del usuario autenticado como propietario del vehículo
              antes de guardar la instancia.

          get_success_url():
              Devuelve la URL a la que redirigir después de crear el viaje,
              en este caso, la vista de detalle del viaje recién creado.
      """

    model = ViajeOferta
    form_class = ViajeOfertaForm

    def form_valid(self, form):
        form.instance.propietario_vehiculo = self.request.user.perfil
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('viaje-detail', kwargs={'pk': self.object.pk})

class MostrarViajesPropios(LoginRequiredMixin,ListView):
    """
        Vista basada en clases para mostrar los viajes propios de un usuario autenticado.

        Hereda de `LoginRequiredMixin` para asegurar que solo usuarios logueados puedan acceder,
        y de `ListView` para listar las instancias del modelo `ViajeOferta` asociadas al usuario.

        Atributos:
            model (Model): Modelo asociado a la vista, `ViajeOferta`.
            context_object_name (str): Nombre de la variable de contexto que contendrá
                                       la lista de viajes en la plantilla.

        Métodos:
            get_queryset():
                Devuelve el queryset de viajes del usuario autenticado que no han caducado,
                anotando si cada viaje tiene reservas existentes.

            get_context_data(**kwargs):
                Añade al contexto una variable booleana 'tiene_viajes' que indica
                si el usuario tiene algún viaje publicado.
        """

    model = ViajeOferta
    context_object_name = 'viajes'

    def get_queryset(self):
        self.qs =ViajeOferta.objects.filter(propietario_vehiculo = self.request.user.perfil).no_caducados()

        self.qs = self.qs.annotate(tiene_reserva=Exists(Reserva.objects.filter(viaje=OuterRef('pk'))))
        return self.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tiene_viajes'] = self.qs.exists()
        return context

class DetallesViajePropietario(EsPropietarioViajeMixin,TieneReservasContextMixin,DetallesViajeBase):
    """
        Vista de detalle de un viaje para su propietario.

        Extiende `DetallesViajeBase` añadiendo mixins que proporcionan funcionalidades
        adicionales:

            - EsPropietarioViajeMixin: Verifica que el usuario autenticado es el
              propietario del viaje, restringiendo el acceso si no lo es.

            - TieneReservasContextMixin: Añade al contexto información sobre si
              el viaje tiene reservas asociadas, útil para mostrar indicadores en la plantilla.

        No añade métodos adicionales propios; hereda todo el comportamiento de
        la clase base y los mixins.
        """
    pass

class EditarViaje(EsPropietarioViajeMixin,RevisarSiTieneReservasMixin,UpdateView):
    """
        Vista basada en clases para editar un viaje existente por su propietario.

        Hereda de:
            - `EsPropietarioViajeMixin`: asegura que solo el propietario del viaje
              pueda acceder a la edición.
            - `RevisarSiTieneReservasMixin`: permite revisar restricciones si el viaje ya tiene reservas asociadas.
            - `UpdateView`: proporciona la funcionalidad de actualización de instancias
              de modelos.

        Atributos:
            model (Model): Modelo asociado a la vista, `ViajeOferta`.
            form_class (Form): Formulario utilizado para editar la instancia de viaje.
            template_name_suffix (str): Sufijo para buscar el template correspondiente,
                                        por defecto '_form'.

        Métodos:
            form_valid(form):
                Se ejecuta cuando el formulario es válido. Asegura que el propietario
                del viaje sea el usuario autenticado antes de guardar los cambios.

            get_context_data(**kwargs):
                Añade al contexto la variable booleana 'modo_edicion' para indicar
                que la vista se encuentra en modo edición.

            get_success_url():
                Devuelve la URL a la que redirigir después de editar el viaje,
                en este caso, la vista de detalle del viaje editado.
        """

    model = ViajeOferta
    form_class = ViajeOfertaForm
    template_name_suffix = '_form'

    def form_valid(self, form):
        form.instance.propietario_vehiculo = self.request.user.perfil
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modo_edicion'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('viaje-detail', kwargs={'pk': self.object.pk})

class BuscarViaje(FormView):
    """
        Vista basada en formulario para buscar viajes compartidos según criterios del usuario.

        Hereda de `FormView` y permite a los usuarios ingresar datos de búsqueda
        como ciudad de salida, ciudad de llegada y fecha del viaje.

        Atributos:
            template_name (str): Plantilla utilizada para mostrar el formulario de búsqueda.
            form_class (Form): Formulario `BuscarViajeForm` que captura los criterios de búsqueda.

        Métodos:
            get_context_data(**kwargs):
                Añade al contexto una variable booleana 'busca_viaje' para indicar
                que la vista se encuentra en modo búsqueda.

            form_valid(form):
                Se ejecuta cuando el formulario es válido. Extrae los datos de
                ciudad de salida, ciudad de llegada y fecha del formulario, y
                redirige a la vista de resultados de búsqueda pasando estos datos
                como `kwargs` en la URL. Los `kwargs` actúan como filtros de
                búsqueda entre fechas y ubicaciones.
        """

    template_name = 'viajes/buscar_viaje_form.html'
    form_class = BuscarViajeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busca_viaje'] = True
        return context

    def form_valid(self, form):
        datos = form.cleaned_data
        ciudad_salida = datos['ciudad_salida']
        ciudad_llegada = datos['ciudad_llegada']
        fecha = datos['fecha'].strftime('%Y-%m-%d')

        url = reverse('resultados-busqueda',
                      kwargs={'ciudad_salida':ciudad_salida,
                              'ciudad_llegada': ciudad_llegada,
                              'fecha' : fecha
                               })
        return redirect(url)

class ResultadosBusqueda(ListView):
    """
        Vista basada en listas que muestra los resultados de búsqueda de viajes compartidos.

        Hereda de `ListView` y filtra las ofertas de viaje según los criterios
        proporcionados en los `kwargs` de la URL: ciudad de salida, ciudad de llegada
        y fecha. Solo se muestran viajes no caducados y con plazas disponibles.

        Atributos:
            model (Model): Modelo asociado a la vista, `ViajeOferta`.
            context_object_name (str): Nombre de la variable de contexto que contendrá
                                       la lista de viajes en la plantilla.

        Métodos:
            get_queryset():
                Filtra los viajes según ciudad de salida, ciudad de llegada y fecha,
                y aplica métodos personalizados `no_caducados()` y `tiene_plazas_libres()`.

            get_context_data(**kwargs):
                Añade información adicional al contexto:
                    - 'en_resultados_busqueda': indica que la vista corresponde a una búsqueda.
                    - 'tiene_viajes': booleano que indica si hay resultados.
                    - 'ciudad_salida', 'ciudad_llegada': ciudades de búsqueda.
                    - 'siguiente_dia', 'dia_anterior': fechas adyacentes a la búsqueda,
                      útiles para navegación entre días.
        """

    model=ViajeOferta
    context_object_name = 'viajes'


    def get_queryset(self):
        return ViajeOferta.objects.filter(
            ciudad_salida=self.kwargs['ciudad_salida'],
            ciudad_llegada=self.kwargs['ciudad_llegada'],
            fecha_salida=self.kwargs['fecha']
        ).no_caducados().tiene_plazas_libres()

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['en_resultados_busqueda'] = True
        context['tiene_viajes'] = self.get_queryset().exists()

        fecha_str = self.kwargs['fecha']
        fecha_obj_date = datetime.strptime(fecha_str,'%Y-%m-%d').date()
        siguiente_dia = (fecha_obj_date + timedelta(days=1)).strftime('%Y-%m-%d')
        dia_anterior = (fecha_obj_date - timedelta(days=1)).strftime('%Y-%m-%d')



        context['ciudad_salida'] = self.kwargs['ciudad_salida']
        context['ciudad_llegada'] = self.kwargs['ciudad_llegada']
        context['siguiente_dia'] = siguiente_dia
        context['dia_anterior'] = dia_anterior

        return context

class DetallesViaje(TieneReservasContextMixin,DetallesViajeBase):
    """
        Vista de detalle de un viaje accesible para cualquier usuario, incluso
        sin estar autenticado o sin ser el propietario del viaje.

        Hereda de:
            - `DetallesViajeBase`: proporciona la funcionalidad básica de detalle
              de un viaje.
            - `TieneReservasContextMixin`: añade al contexto información sobre
              si el viaje tiene reservas asociadas.

        No añade métodos adicionales propios; hereda todo el comportamiento de
        la clase base y el mixin, permitiendo mostrar detalles de un viaje de manera
        segura a cualquier visitante.
        """
    pass

class CancelarViaje(EsPropietarioViajeMixin,RevisarSiTieneReservasMixin,DeleteView):
    """
        Vista basada en clases para cancelar (eliminar) un viaje por su propietario.

        Hereda de:
            - `EsPropietarioViajeMixin`: asegura que solo el propietario del viaje
              pueda acceder a la cancelación.
            - `RevisarSiTieneReservasMixin`: permite revisar advertencias o restricciones
              si el viaje tiene reservas asociadas.
            - `DeleteView`: proporciona la funcionalidad de eliminación de instancias
              de modelos.

        Atributos:
            model (Model): Modelo asociado a la vista, `ViajeOferta`.
            template_name_suffix (str): Sufijo para buscar la plantilla de confirmación
                                        de cancelación ('_cancelar').

        Métodos:
            get_success_url():
                Devuelve la URL a la que redirigir después de cancelar el viaje,
                en este caso, la vista que lista los viajes publicados por el usuario.
        """

    model = ViajeOferta
    template_name_suffix = '_cancelar'

    def get_success_url(self):
        return reverse_lazy('viajes-publicados')

class SolicitarPlazas(LoginRequiredMixin,CreateView):
    """
       Vista basada en formulario para que un usuario autenticado solicite plazas en un viaje.

       Hereda de `LoginRequiredMixin` para asegurar que solo usuarios logueados
       puedan acceder, y de `CreateView` para gestionar la creación de instancias
       de `Solicitud`.

       Atributos:
           model (Model): Modelo asociado a la vista, `Solicitud`.
           form_class (Form): Formulario `SolicitarPlazaForm` utilizado para crear la solicitud.
           template_name (str): Plantilla utilizada para mostrar el formulario de solicitud.

       Métodos:
           form_valid(form):
               Se ejecuta cuando el formulario es válido. Realiza varias validaciones:
                   - Impide que un usuario solicite plazas en su propio viaje.
                   - Evita solicitudes duplicadas pendientes para el mismo viaje.
                   - Comprueba que el número de plazas solicitadas no exceda las plazas disponibles.

               Si todas las condiciones se cumplen, asigna automáticamente el perfil
               del usuario y el viaje a la instancia de `Solicitud`, la guarda y
               devuelve la plantilla con un indicador de que la solicitud fue enviada.
       """
    model = Solicitud
    form_class = SolicitarPlazaForm
    template_name = 'viajes/solicitud_form.html'

    def form_valid(self, form):
        viaje = get_object_or_404(ViajeOferta, pk=self.kwargs['pk'])
        perfil = self.request.user.perfil

        if perfil == viaje.propietario_vehiculo:
            form.add_error(None, "No puedes solicitar plazas en tu propio viaje.")
            return self.form_invalid(form)

        if Solicitud.objects.filter(
                quien_solicita=perfil,
                viaje=viaje,
                estado='Pendiente'
        ).exists():
            form.add_error(None, "Ya tienes una solicitud pendiente para este viaje.")
            return self.form_invalid(form)

        if form.cleaned_data['numero_plazas'] > viaje.plazas_restantes:
            form.add_error(
                'numero_plazas',
                f"Solo quedan {viaje.plazas_disponibles} plazas disponibles."
            )
            return self.form_invalid(form)

        form.instance.quien_solicita = perfil
        form.instance.viaje = viaje
        form.save()
        return render(self.request,self.template_name,{'form' : self.get_form(),'solicitud_enviada':True})

class MostrarSolicitudes(EsPropietarioMixin,RevisarPermisosMixin,DetailView):
    """
        Vista de detalle para mostrar las solicitudes de plazas de un perfil.

        Hereda de:
            - `EsPropietarioMixin`: asegura que solo el propietario del perfil pueda acceder.
            - `RevisarPermisosMixin`: permite verificar permisos adicionales si es necesario.
            - `DetailView`: proporciona la funcionalidad de vista detallada de un objeto.

        Atributos:
            model (Model): Modelo asociado a la vista, `Perfil`.
            template_name (str): Plantilla utilizada para mostrar la lista de solicitudes.

        Métodos:
            get_context_data(**kwargs):
                Añade al contexto dos listas de solicitudes:
                    - 'solicitudes_recibidas': solicitudes pendientes recibidas por el perfil.
                    - 'solicitudes_enviadas': solicitudes pendientes enviadas por el perfil.
                Estas listas se obtienen utilizando los métodos personalizados del
                `SolicitudQuerySet` (`pendientes_recibidas` y `pendientes_enviadas`).
        """

    model = Perfil
    template_name = 'viajes/solicitud_list.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['solicitudes_recibidas'] = Solicitud.objects.pendientes_recibidas(self.object)
        context['solicitudes_enviadas'] = Solicitud.objects.pendientes_enviadas(self.object)

        return context

class SolicitudAccion(LoginRequiredMixin,View):
    """
        Vista para procesar acciones sobre solicitudes de plazas en viajes.

        Hereda de `LoginRequiredMixin` para asegurar que solo usuarios autenticados
        puedan ejecutar acciones, y de `View` para manejar peticiones HTTP genéricas.

        Métodos:
            post(request, *args, **kwargs):
                Procesa la acción sobre una solicitud específica. Realiza las siguientes
                operaciones:
                    - Obtiene la solicitud por su `pk` y verifica que el usuario
                      autenticado sea el propietario del viaje asociado.
                    - Extrae la acción/estado a aplicar (`Aceptada` o `Rechazada`) desde los kwargs.
                    - Llama al método `procesar_solicitud` de la instancia para actualizar su estado.
                    - Si la solicitud es aceptada, redirige a la lista de reservas del usuario.
                    - Si la solicitud es rechazada, redirige a la lista de solicitudes pendientes.
        """
    def post(self, request, *args, **kwargs):

        solicitud = get_object_or_404(
            Solicitud,
            pk=kwargs['pk'],
            viaje__propietario_vehiculo=request.user.perfil
        )

        respuesta_solicitud = self.kwargs['estado']

        solicitud.procesar_solicitud(respuesta_solicitud)

        if respuesta_solicitud == 'Aceptada':
            return redirect(reverse('reservas-list', kwargs={'usuario_id': request.user.id})
)

        return redirect('solicitudes-pendientes', kwargs={'usuario_id': request.user.id})

class MostrarReservas(EsPropietarioMixin,RevisarPermisosMixin, DetailView):
    """
        Vista de detalle para mostrar las reservas relacionadas con un perfil.

        Hereda de:
            - `EsPropietarioMixin`: asegura que solo el propietario del perfil pueda acceder.
            - `RevisarPermisosMixin`: permite verificar permisos adicionales si es necesario.
            - `DetailView`: proporciona la funcionalidad de vista detallada de un objeto.

        Atributos:
            model (Model): Modelo asociado a la vista, `Perfil`.
            template_name (str): Plantilla utilizada para mostrar la lista de reservas.

        Métodos:
            get_context_data(**kwargs):
                Añade al contexto varias listas de reservas:
                    - 'reservas_en_mi_viaje': reservas en los viajes cuyo propietario es el perfil.
                    - 'yo_reserve': reservas realizadas por el perfil.
                También añade la variable booleana 'tiene_reservas' que indica si
                existen reservas en cualquiera de las dos listas.
                Los datos se obtienen utilizando los métodos personalizados del
                `ReservaQuerySet` (`en_mis_viajes` y `yo_reserve`).
        """

    model = Perfil
    template_name = 'viajes/reservas_list.html'

    def get_context_data(self, **kwargs):

       context = super().get_context_data(**kwargs)

       context['reservas_en_mi_viaje'] = Reserva.objects.en_mis_viajes(self.object)

       context['yo_reserve'] = Reserva.objects.yo_reserve(self.object)

       if context['reservas_en_mi_viaje'].exists() or context['yo_reserve'].exists():
           context['tiene_reservas'] = True
       else:
           context['tiene_reservas'] = False

       return context



















