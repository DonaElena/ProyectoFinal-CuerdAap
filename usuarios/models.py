from datetime import date

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import OneToOneField
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from CuerdApp import settings
from django.contrib.auth.models import BaseUserManager

"""
Este archivo contiene las clases que definen los modelos de la aplicación
de registro de usuarios y gestión de autenticación y perfiles.

"""


class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para el modelo User, que permite crear
    usuarios normales y superusuarios.
    Se implementa este Manager para que pueda crear usuarios y superusuarios
    sin username, utilizando el correo electrónico como identificador único
    para iniciar sesión.

    Incluye métodos:
    - create_user: crea un usuario estándar con email y contraseña.
    - create_superuser: crea un superusuario con permisos administrativos.
    """


    def create_user(self,email,password=None):
        if not email:
            raise ValueError('Es obligatorio introducir un email. Será tu identificador')
        usuario=self.model(
            email=self.normalize_email(email),
        )
        usuario.set_password(password)
        usuario.save()
        return usuario

    def create_superuser(self,email,password=None):
        if password is None:
            raise ValueError('Crea una contraseña')

        usuario = self.create_user(email,password)
        usuario.is_staff=True
        usuario.is_superuser=True
        usuario.is_active=True

        usuario.save()
        return usuario


class Usuario(AbstractUser):

    """
    Clase que hereda AbstracUser, clase necesaria para crear usuarios personalizados.
    En este caso, no se requiere un username (predefinido de Django) y se utiliza
    el correo electrónico como identificador para el inicio de sesión.
    """
    username = None
    email = models.EmailField(
                              blank=False,
                              unique=True,
                              null=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UsuarioManager()

class Perfil(models.Model):
    """
    Modelo que define los datos asociados al perfil de un usuario.

    Este modelo está relacionado uno a uno (OneToOneField) con el modelo de Usuario
    personalizado (`settings.AUTH_USER_MODEL`), de manera que cada usuario tiene exactamente
    un perfil.

    Campos del perfil:
        - usuario: enlace al usuario (OneToOneField)
        - telefono: número de teléfono del usuario (PhoneNumberField)
        - fecha_nacimiento: fecha de nacimiento
        - sexo: género del usuario (opciones: Femenino, Masculino)
        - inicio_escalada: fecha en la que comenzó a escalar
        - perfil_8anu: enlace a perfil en 8a.nu (opcional)
        - descripcion: breve descripción del usuario (opcional)
        - material_propio: indica si tiene material propio (Sí/No)
        - recibir_gente: indica si acepta recibir a otras personas para escalar (Sí/No)

    Métodos y propiedades:
        - tiempo_transcurrido(fecha): método estático que calcula años transcurridos desde
          una fecha dada hasta hoy.
        - edad: propiedad que devuelve la edad del usuario calculada desde `fecha_nacimiento`.
        - tiempo_escalando: propiedad que devuelve los años que lleva escalando desde
          `inicio_escalada`.
        - get_absolute_url(): devuelve la URL absoluta del detalle del perfil.
        - __str__(): devuelve el nombre completo del usuario asociado (first_name + last_name).
    """

    SEXO =(
        ('F', 'Femenino'),
        ('M', 'Masculino')
    )

    RESPUESTA= (
        ('S', 'Sí'),
        ('N', 'No')
    )
    usuario =OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    telefono = PhoneNumberField()
    fecha_nacimiento = models.DateField()
    sexo=models.CharField(max_length=1,choices=SEXO,default='M')
    inicio_escalada = models.DateField()
    perfil_8anu = models.URLField(blank=True,null=True)
    descripcion= models.CharField(blank=True,null=True)
    material_propio =models.CharField(max_length= 2 , choices=RESPUESTA,default='N')
    recibir_gente= models.CharField(max_length= 2, choices=RESPUESTA,default='N')


    @staticmethod
    def tiempo_transcurrido(fecha):
        hoy = date.today()
        anyos = hoy.year - fecha.year
        if (hoy.month, hoy.day) < (fecha.month, fecha.day):
            anyos -= 1
        return anyos

    @property
    def edad(self):
        return self.tiempo_transcurrido(self.fecha_nacimiento)

    @property
    def tiempo_escalando(self):
        return self.tiempo_transcurrido(self.inicio_escalada)

    def get_absolute_url(self):
        return reverse('perfil-detail', kwargs={'usuario_id': self.usuario_id})

    def __str__(self):
        return f'{self.usuario.first_name} {self.usuario.last_name}'

class Opinion(models.Model):
    """
    Modelo que representa una opinión o comentario que un usuario deja sobre el perfil de otro usuario.

    Campos del modelo:
        - usuario: referencia al usuario que publica la opinión (ForeignKey a Usuario)
        - perfil: referencia al perfil del usuario al que va dirigida la opinión (ForeignKey a Perfil)
        - comentario: contenido de la opinión, máximo 200 caracteres (TextField)
        - fecha_publicacion: fecha y hora en que se publicó la opinión, asignada automáticamente (DateTimeField)

    Propiedades:
        - tiempo_transcurrido: propiedad que devuelve un string legible indicando cuánto tiempo ha pasado
          desde la publicación de la opinión, usando `django.utils.timesince.timesince`.
          Por ejemplo: "Hace 2 horas".
    """

    usuario=models.ForeignKey(Usuario,on_delete=models.CASCADE)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    comentario=models.TextField(max_length=200)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    @property
    def tiempo_transcurrido(self):
        from django.utils.timesince import timesince
        return f"Hace {timesince(self.fecha_publicacion)}"





















