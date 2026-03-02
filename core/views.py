from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from core.textos import cargar_texto
from core.forms import ContactForm
from django.contrib import messages

'''"""
Vistas de la app 'core'.

Estas vistas están basadas en funciones y permiten a usuarios no autenticados:
- Acceder a la página principal ('home')
- Consultar información sobre nosotros ('sobre_nosotros')
- Enviar mensajes de contacto ('formulario_contacto')
""" '''

def home (request):

    ''' Vista para la página principal de la aplicación '''

    return render(request,'home.html')

def sobre_nosotros (request):

    ''' Vista que se encarga de cargar el texto necesario para la sección 'sobre nosotros' '''

    contexto = {'filosofia': cargar_texto('filosofía.txt'),
                'quienes_somos': cargar_texto('quienes_somos.txt'),
                'propositos': cargar_texto('propositos.txt'),
                'valores_ambientales': cargar_texto('valores_ambientales.txt'),
                'valores_tecnicos': cargar_texto('valores_tecnicos.txt')}

    return render(request,'sobre_nosotros.html',contexto)

def formulario_contacto(request):

    ''' Vista que se encarga de renderizar el formulario de contacto,
        validar los datos que se introducen,
        enviar un correo electrónico al sistema de soporte
        y emitir mensajes de éxito o error para los usuarios '''

    if request.method =='POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            datos_formulario=form.cleaned_data
            try:
                mensaje= f"{datos_formulario['nombre']} con e-mail {datos_formulario['email']} ha escrito el siguiente mensaje:\n {datos_formulario['mensaje']}"

                send_mail(datos_formulario['asunto'],
                          mensaje,
                          settings.DEFAULT_FROM_EMAIL,
               [settings.EMAIL_HOST_USER],
                          fail_silently=False)
                messages.success(request,'Tu mensaje nos ha llegado!',extra_tags='formulario contacto enviado')
                return redirect('/formulario_contacto')

            except Exception:
                messages.error(request,'Ha ocurrido un error, intente más tarde o escriba directamente a soporte@cuerdapp.com', extra_tags='error envio contacto')
    else:
        form=ContactForm()

    return render(request, 'formulario_contacto.html',{'form':form,
                                                                            })

