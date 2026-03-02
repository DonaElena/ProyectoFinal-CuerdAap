from django.core.exceptions import ObjectDoesNotExist

from viajes.models import ViajeOferta, Solicitud

def revisar_solicitudes(request):
    """
       Context processor para indicar si el usuario tiene solicitudes pendientes.

       Este contexto se utiliza en la plantilla del menú de navegación para mostrar
       notificaciones o alertas si el usuario tiene solicitudes de viaje pendientes.

       Parámetros:
       -----------
       request : HttpRequest
           Objeto de la petición actual de Django.

       Flujo:
       ------
       1. Comprueba si el usuario está autenticado:
           - Si no lo está, devuelve {'tiene_solicitudes_pendientes': False}.
       2. Intenta obtener el perfil del usuario (`request.user.perfil`):
           - Si el perfil no existe, captura `ObjectDoesNotExist` y marca como False.
       3. Comprueba si existen solicitudes pendientes:
           - `Solicitud.objects.pendientes_recibidas(perfil)` → solicitudes recibidas sin responder.
           - `Solicitud.objects.pendientes_enviadas(perfil)` → solicitudes enviadas aún sin aceptar/rechazar.
           - `exists()` devuelve True si hay al menos una solicitud pendiente.
       4. Devuelve un diccionario con la clave `'tiene_solicitudes_pendientes'` y el valor True/False.

       Retorno:
       --------
       dict
           {'tiene_solicitudes_pendientes': bool}

       Ejemplo de uso en plantilla:
       ----------------------------
       {% if tiene_solicitudes_pendientes %}
           <span class="alerta">¡Tienes solicitudes pendientes!</span>
       {% endif %}

       Notas:
       ------
       - Este context processor se registra en `settings.TEMPLATES['OPTIONS']['context_processors']`
         para que la variable esté disponible en **todas las páginas de la aplicación**.
       - Permite actualizar dinámicamente el menú de navegación según las solicitudes del usuario.
       """

    if not request.user.is_authenticated:
        return {'tiene_solicitudes_pendientes': False}

    try:
        perfil = request.user.perfil
        tiene = Solicitud.objects.pendientes_recibidas(perfil).exists() or Solicitud.objects.pendientes_enviadas(perfil).exists()
    except ObjectDoesNotExist:
        tiene = False

    return {'tiene_solicitudes_pendientes': tiene}

