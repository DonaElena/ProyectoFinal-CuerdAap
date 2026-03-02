from django.contrib.messages import get_messages
from .forms import NewsletterForm


''' Context processor necesario para renderizar el formulario de la inscripción a la newsletter
desde cualquier vista. Este context processor permite que el formulario esté disponible
 en todos los templates de la aplicación.
 Es necesaria esta arquitectura porque el formulario forma parte del template base, 
 y el template base se utiliza en casi todas las vistas '''

def newsletter_form(request):

    mensajes = get_messages(request)
    mensajes_filtrados = []

    for mensaje in mensajes:
        if 'newsletter' in mensaje.tags:
            mensajes_filtrados.append(mensaje)

    return {
        'newsletter_form': NewsletterForm(),
        'mensajes_filtrados': mensajes_filtrados
    }
