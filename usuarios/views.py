from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.edit import FormMixin, DeleteView

from usuarios.forms import CrearPerfilForm, OpinionForm
from usuarios.models import Perfil, Opinion, Usuario
from utils.mixins import EsPropietarioMixin, RevisarPermisosMixin
from viajes.models import Reserva

"""
Vistas de la aplicación Usuarios.

Este archivo define las vistas relativas a la creación, visualización, edición y eliminación
de perfiles de usuario.

Las vistas relacionadas con registro, login, login mediante Google OAuth 2.0 y logout
se encuentran en la librería 'django-allauth'
"""

def acceder_comentarios(perfil):

    """ Función auxiliar función que extrae los comentarios asociados a un perfil.
      Devuelve una tupla '(comentarios, hay_comentarios)', donde 'comentarios' es un QuerySet
      de objetos 'Opinion' ordenados por fecha de publicación descendente, y 'hay_comentarios'
      es un booleano que indica si existen comentarios para el perfil.
      """
    hay_comentarios = False

    comentarios = Opinion.objects.filter(perfil=perfil).order_by('-fecha_publicacion')
    if comentarios:
        hay_comentarios = True

    return comentarios,hay_comentarios

class CrearPerfil(LoginRequiredMixin,CreateView):

    """
        Vista para que un usuario autenticado cree su perfil.
        - model: Perfil
        - form_class: CrearPerfilForm
        - form_valid(): asigna automáticamente el usuario logueado al perfil antes de guardarlo.
    """

    model = Perfil
    form_class = CrearPerfilForm

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class MostrarPerfil(EsPropietarioMixin,FormMixin,DetailView):

    """
     Vista para mostrar un perfil y sus opiniones.
        - model: Perfil
        - form_class: OpinionForm
        - get_context_data(): agrega al contexto:
            * el formulario de opinión
            * los comentarios y si existen
            * si el usuario logueado comparte una reserva con el propietario del perfil
        - post(): maneja el envío del formulario de opinión
        - form_valid(): asigna automáticamente el usuario y el perfil antes de guardar la opinión
        - get_success_url(): redirige a la URL del perfil mostrado
    """

    model =  Perfil
    form_class = OpinionForm

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        comentarios,hay_comentarios = acceder_comentarios(self.object)

        context['form'] = self.get_form()
        context['comentarios'] = comentarios
        context['hay_comentarios'] = hay_comentarios


        # Se comprueba que el perfil del usuario logeado tiene una reserva con la persona
        # Se muestran los datos necesarios para que contacten
        context['van_a_compartir_viaje'] = Reserva.objects.filter(viaje__propietario_vehiculo = self.object,
                               quien_reserva = self.request.user.perfil).exists()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.perfil = self.object
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return Perfil.get_absolute_url(self.object)


class EditarPerfil(EsPropietarioMixin,RevisarPermisosMixin,UpdateView):

    """
     Vista para que un usuario edite su propio perfil.
        - model: Perfil
        - form_class: CrearPerfilForm
        - template_name_suffix: '_editar'
        - form_valid(): asegura que el usuario logueado sea asignado correctamente
        Nota: el ModelForm excluye el campo 'usuario' para mayor seguridad.
    """
    model = Perfil
    template_name_suffix = '_editar'
    form_class = CrearPerfilForm

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

class EliminarPerfil(LoginRequiredMixin,RevisarPermisosMixin,DeleteView):

    """
    Vista para que un usuario elimine su propia cuenta.
        - model: Usuario
        - template_name_suffix: '_eliminar'
        - success_url: redirige a la página principal ('home') tras la eliminación

    """
    model = Usuario
    template_name_suffix = '_eliminar'
    success_url = reverse_lazy('home')









