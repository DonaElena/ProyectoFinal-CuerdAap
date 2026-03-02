from django.shortcuts import redirect
from django.contrib import messages
from inscripcion_newsletter.forms import NewsletterForm
from inscripcion_newsletter.email import enviar_correo_bienvenida

''' Vista basada en una función. Cumple la funcionalidad de almacenar el correo del 
   suscriptor en la base de datos para poder enviarle información relativa a la 
   Newsletter '''

def inscripcion_newsletter(request):

    ''' Función que se encarga del manejo de la vista responsable de la inscripción a la Newsletter.
        -Procesa el email que introduce el usuario y lo almacena en la base de datos.
        -Muestra los errores si los hay, en caso de no haberlos muestra mensaje de éxito.
        -Redirige a la página desde la que se mandó la solicitud de inscripción:
             la vista del formulario está disponible en cualquier parte de la aplicación,
             por lo que es necesario redirigir a la vista desde la que fue mandada.
        -Envía correo de bienvenida. '''

    if request.method=='POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                email_usuario=form.cleaned_data['email']
                form.save()
                enviar_correo_bienvenida(email_usuario)
                messages.success(request,'Bienvenido/a a nuestro Newsletter!!',extra_tags='exito_newsletter')
            except Exception as e:
                print("Error newsletter:", e)
                messages.error(request, 'Ha ocurrido un error, inténtalo más tarde!', extra_tags='newsletter')
        else:
            for error in form.errors.values():
                messages.warning(request,error,extra_tags='newsletter')
    return redirect(request.META.get('HTTP_REFERER','/'))








# Create your views here.
