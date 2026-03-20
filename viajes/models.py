from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import ForeignKey, F, Sum, Q
from django.db.models.functions import Coalesce
from django.urls import reverse
from usuarios.models import Perfil
from utils.mixins import NoCaducadoMixin


class Ciudad(models.Model):
    """
        Modelo que representa una ciudad con información geográfica básica.

        Atributos:
            nombre_ciudad (CharField): Nombre de la ciudad. Índice para búsquedas rápidas.
            latitud (CharField): Latitud de la ciudad en formato de cadena.
            longitud (CharField): Longitud de la ciudad en formato de cadena.
        """

    nombre_ciudad = models.CharField(max_length=150, db_index=True)
    latitud = models.CharField(max_length=20)
    longitud = models.CharField(max_length=20)

class ViajeOfertaQuerySet(models.QuerySet, NoCaducadoMixin):
    """
        QuerySet personalizado para el modelo de ofertas de viaje.

        Proporciona métodos de utilidad para filtrar viajes según su disponibilidad
        y estado de caducidad.

        Métodos:
            no_caducados():
                Retorna las instancias del QuerySet que no han caducado utilizando
                el mixin NoCaducadoMixin.

            tiene_plazas_libres():
                Retorna las instancias del QuerySet que todavía tienen plazas disponibles,
                calculando las plazas libres restando las reservas realizadas a las
                plazas disponibles.
        """

    def no_caducados(self):
        return self.filter_no_caducados(self)

    def tiene_plazas_libres(self):
        qs = self.annotate(
            plazas_libres= F('plazas_disponibles') - Coalesce(Sum('reservas__numero_plazas'),0)
        )
        qs_filtrado = qs.filter(plazas_libres__gt = 0)

        return qs_filtrado


class ViajeOferta (models.Model):
    """
        Modelo que representa una oferta de viaje compartido.

        Contiene información sobre el propietario, las ciudades de salida y llegada,
        las plazas disponibles, horarios, aceptación de mascotas, sector y nivel de
        escalada, y descripción opcional.

        Atributos:
            propietario_vehiculo (ForeignKey): Perfil del propietario del vehículo.
            fecha_salida (DateField): Fecha de salida del viaje.
            ciudad_salida (CharField): Ciudad de origen del viaje.
            ciudad_llegada (CharField): Ciudad de destino del viaje.
            plazas_disponibles (IntegerField): Número total de plazas disponibles.
            hora (TimeField): Hora de salida.
            acepto_mascotas (CharField): Indica si se aceptan mascotas ('S' o 'N').
            regreso_hoy (CharField): Indica si hay regreso el mismo día ('S' o 'N').
            nombre_sector (CharField): Nombre del sector de escalada asociado al viaje.
            nivel_escalada (CharField): Nivel de dificultad de escalada.
            descripcion_viaje (CharField): Descripción opcional del viaje.

        Propiedades:
            plazas_restantes: Calcula las plazas libres restando reservas a las disponibles.
            ciudad_salida_corto: Devuelve versión abreviada de la ciudad de salida.
            ciudad_llegada_corto: Devuelve versión abreviada de la ciudad de llegada.

        Manager:
            objects: QuerySet personalizado `ViajeOfertaQuerySet` que permite
                     utilizar métodos como `no_caducados()` y `tiene_plazas_libres()`.
        """

    RESPUESTA = (
        ('S', 'Sí'),
        ('N', 'No')
    )

    propietario_vehiculo = ForeignKey(Perfil,on_delete=models.CASCADE)
    fecha_salida = models.DateField()
    ciudad_salida = models.CharField(max_length=150)
    ciudad_llegada = models.CharField(max_length=150)
    plazas_disponibles = models.IntegerField()
    hora = models.TimeField()
    acepto_mascotas = models.CharField(max_length= 2 , choices=RESPUESTA,default='N')
    regreso_hoy = models.CharField(max_length= 2 , choices=RESPUESTA,default='N')
    nombre_sector = models.CharField(max_length= 30)
    nivel_escalada = models.CharField(max_length=5)
    descripcion_viaje = models.CharField(max_length=350, blank=True, null=True)

    objects = ViajeOfertaQuerySet.as_manager()

    @property
    def plazas_restantes(self):
        plazas_ocupadas = Reserva.objects.filter(
        solicitud__viaje=self).aggregate(
            total=Coalesce(Sum('numero_plazas'), 0)
        )['total']
        return self.plazas_disponibles - plazas_ocupadas


    @property
    def ciudad_salida_corto(self):

        partes = []

        for p in self.ciudad_salida.split(","):
            partes.append(p.strip())

        if len(partes) >= 2:
            return f"{partes[0]}, {partes[-1]}"

        return self.ciudad_salida

    @property
    def ciudad_llegada_corto(self):

        partes = []

        for p in self.ciudad_llegada.split(","):
            partes.append(p.strip())

        if len(partes) >= 2:
            return f"{partes[0]}, {partes[-1]}"

        return self.ciudad_llegada

class SolicitudQuerySet(models.QuerySet, NoCaducadoMixin):
    """
        QuerySet personalizado para solicitudes de viaje.

        Permite filtrar solicitudes según su estado, caducidad y relación con un perfil.

        Métodos:
            no_caducadas():
                Retorna las solicitudes que aún no han caducado, utilizando el mixin
                NoCaducadoMixin. Considera los campos `viaje__fecha_salida` y `viaje__hora`
                para determinar la caducidad.

            pendientes_recibidas(perfil):
                Retorna las solicitudes pendientes recibidas por un perfil específico,
                es decir, aquellas cuyo viaje pertenece al perfil como propietario y
                cuyo estado es 'Pendiente'. Solo devuelve las que no han caducado.

            pendientes_enviadas(perfil):
                Retorna las solicitudes pendientes enviadas por un perfil específico,
                es decir, aquellas que el perfil ha solicitado y cuyo estado es
                'Pendiente'. Solo devuelve las que no han caducado.
        """

    def no_caducadas(self):
        return self.filter_no_caducados(self, fecha_field='viaje__fecha_salida', hora_field='viaje__hora')

    def pendientes_recibidas(self, perfil):
        return self.filter(viaje__propietario_vehiculo=perfil, estado='Pendiente').no_caducadas()

    def pendientes_enviadas(self, perfil):
        return self.filter(quien_solicita=perfil, estado='Pendiente').no_caducadas()


class Solicitud(models.Model):
    """
      Modelo que representa una solicitud de reserva para un viaje compartido.

      Contiene información sobre quién realiza la solicitud, el viaje asociado,
      el número de plazas solicitadas, el estado de la solicitud y la fecha/hora
      de creación.

      Atributos:
          quien_solicita (ForeignKey): Perfil que realiza la solicitud.
          viaje (ForeignKey): Oferta de viaje a la que se asocia la solicitud.
          numero_plazas (IntegerField): Número de plazas solicitadas.
          estado (CharField): Estado de la solicitud ('Aceptada', 'Pendiente', 'Rechazada').
          fecha_hora_solicitud (DateTimeField): Fecha y hora de creación automática.

      Manager:
          objects: QuerySet personalizado `SolicitudQuerySet` que permite
                   filtrar solicitudes no caducadas, pendientes recibidas o enviadas.

      Métodos:
          crear_reserva():
              Crea una instancia de `Reserva` correspondiente a esta solicitud,
              asignando las plazas solicitadas al perfil solicitante.

          procesar_solicitud(estado):
              Actualiza el estado de la solicitud. Si el estado se cambia a
              'Aceptada', automáticamente crea la reserva correspondiente.
      """

    ESTADO = (
        ('Aceptada', 'Aceptada'),
        ('Pendiente', 'Pendiente'),
        ('Rechazada', 'Rechazada')
    )

    quien_solicita = models.ForeignKey(Perfil, on_delete=models.CASCADE,
                                       related_name='reserva_solicitada')
    viaje = models.ForeignKey(ViajeOferta, on_delete=models.CASCADE)
    numero_plazas = models.PositiveIntegerField()
    estado = models.CharField(max_length=10, choices=ESTADO, default='Pendiente')
    fecha_hora_solicitud = models.DateTimeField(auto_now_add=True)

    objects = SolicitudQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['quien_solicita', 'viaje'],
                condition=Q(estado = 'Pendiente'),
                name= 'unica_solicitud_por_usuario_edo_pendiente'
            )
        ]

    def crear_reserva(self):

        if self.numero_plazas > self.viaje.plazas_restantes:
            raise ValidationError('No hay plazas suficientes')

        Reserva.objects.create(
            viaje = self.viaje,
            quien_reserva = self.quien_solicita,
            numero_plazas = self.numero_plazas)

    def procesar_solicitud(self,estado):

        with transaction.atomic():

            self.estado = estado
            self.save()

            if estado == 'Aceptada' and not hasattr(self, 'reserva'):

                viaje = ViajeOferta.objects.select_for_update().get(id=self.viaje.id)

                if self.numero_plazas > viaje.plazas_restantes:
                    raise ValidationError('No hay plazas suficientes')

                self.crear_reserva()

class ReservaQuerySet(models.QuerySet, NoCaducadoMixin):
    """
        QuerySet personalizado para reservas de viajes.

        Proporciona métodos para filtrar reservas según su caducidad y su relación
        con un perfil específico, ya sea como propietario del viaje o como quien realizó la reserva.

        Métodos:
            no_caducadas():
                Retorna las reservas que aún no han caducado, utilizando el mixin
                NoCaducadoMixin. Se consideran los campos `viaje__fecha_salida` y `viaje__hora`
                para determinar la caducidad.

            en_mis_viajes(perfil):
                Retorna las reservas de viajes cuyo propietario es el perfil dado y
                que no han caducado.

            yo_reserve(perfil):
                Retorna las reservas realizadas por el perfil dado y que no han caducado.
        """

    def no_caducadas(self):
        return self.filter_no_caducados(self,fecha_field='viaje__fecha_salida',hora_field='viaje__hora')


    def en_mis_viajes(self, perfil):
        return self.filter(viaje__propietario_vehiculo=perfil).no_caducadas()

    def yo_reserve(self, perfil):
       return self.filter(quien_reserva=perfil).no_caducadas()

class Reserva(models.Model):
    """
        Modelo que representa una reserva de plazas en un viaje compartido.

        Contiene información sobre el viaje reservado, el perfil que realiza la reserva
        y el número de plazas reservadas.

        Atributos:
            viaje (ForeignKey): Oferta de viaje asociada a la reserva.
            quien_reserva (ForeignKey): Perfil que realiza la reserva.
            numero_plazas (IntegerField): Número de plazas reservadas.

        Manager:
            objects: QuerySet personalizado `ReservaQuerySet` que permite filtrar
                     reservas no caducadas, reservas hechas por un perfil y reservas
                     de viajes cuyo perfil es propietario.
        """

    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE, related_name='reserva')
    numero_plazas = models.PositiveIntegerField()

    @property
    def quien_reserva(self):
        return self.solicitud.quien_solicita

    @property
    def viaje(self):
        return self.solicitud.viaje

    objects = ReservaQuerySet.as_manager()















