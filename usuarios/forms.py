from datetime import date

from django.forms import ModelForm
from django import forms

from usuarios.models import Perfil,Opinion

"""
Clases que definen los formularios utilizados en la aplicación.

Se emplean ModelForm para los formularios que requieren los mismos
campos que los modelos que representan.

La forma de modificar el formulario por defecto de django-allauth es a través 
de Form
"""

class CustomSignupForm(forms.Form):
    """
    Formulario personalizado de django-allauth que amplía el formulario
    de registro por defecto.

    El formulario predefinido únicamente incluye email y contraseña.
    Esta clase añade los campos "first_name" y "last_name" y, mediante
    el método signup, guarda dichos valores en el modelo User al
    completarse el registro.
    """

    first_name = forms.CharField(max_length=30,
                                 label="Nombre")
    last_name = forms.CharField(max_length=30,
                                label="Apellidos"
                                      )

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()


class CrearPerfilForm(ModelForm):
    """
    Formulario basado en ModelForm que define los campos que los usuarios
    utilizan para crear su perfil.

    Se excluye el campo 'usuario' para mayor seguridad, siguiendo las
    recomendaciones de la documentación de Django.
    """
    class Meta:

        model=Perfil
        exclude = ['usuario']
        widgets={
            'fecha_nacimiento':forms.DateInput(attrs={'type':'date',
                                                      'min':'1900-01-01',
                                                      'max': date.today().strftime('%Y-%m-%d'),
                                                      'class': 'form-control',
                                                      },
                                               format='%Y-%m-%d'),
            'inicio_escalada':forms.DateInput(attrs={'type':'date',
                                                     'min':'1900-01-01',
                                                     'max': date.today().strftime('%Y-%m-%d'),
                                                     'class': 'form-control'
                                                     },
                                              format='%Y-%m-%d'),
            'descripcion': forms.Textarea(attrs={'rows': 3,
                                                 'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+340000000 (Obligatorio)',
                                               'class': 'form-control'}),
            'sexo': forms.Select(attrs={'placeholder': '(Obligatorio)',
                                        'class': 'form-control'}),
            'material_propio': forms.Select(attrs={'placeholder': '(Obligatorio)',
                                                   'class': 'form-control'}),
            'recibir_gente': forms.Select(attrs={'placeholder': '+340000000(Obligatorio)',
                                                 'class': 'form-control'}),

        }

class OpinionForm(ModelForm):
    class Meta:
        model=Opinion
        fields=['comentario']
        widgets={
            'comentario':forms.TextInput(attrs={
                                                'placeholder':'Comparte tu experiencia con este/a escalador/a',
                                                'class': 'form-control',
                                                'rows': 5})

        }







