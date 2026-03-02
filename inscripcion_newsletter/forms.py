from django import forms

from inscripcion_newsletter.models import InscripcionNewsletter

''' Clase que define las características del formulario necesario para inscribirse
en la Newsletter '''


class NewsletterForm(forms.ModelForm):

    class Meta:

        model = InscripcionNewsletter
        fields = ['email']
        labels = {'email': ''}
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'newsletter-input',
                'placeholder': 'Introduce tu correo'
            })
        }
        error_messages = {
            'email': {
                'unique':'Tu solicitud no ha sido procesada porque ya estabas inscrito/a a la newsletter'
            }
        }


