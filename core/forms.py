from django import forms

''' Se implementan las clases necesarias para la aplicación
    --ContactForm : Formulario de contacto de la aplicación '''

class ContactForm(forms.Form):
    nombre = forms.CharField(max_length=30,
                             widget=forms.TextInput(attrs={'placeholder':'Introduce tu nombre','class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Introduce tu e-mail','class': 'form-control'}))
    mensaje = forms.CharField(max_length=350,
                             widget=forms.TextInput(attrs={'placeholder':'Longitud máxima de 350 caracteres', 'class':'form-control'}))
    asunto = forms.CharField(max_length=100,
                              widget=forms.TextInput(
                                  attrs={'placeholder': 'Introduce un asunto', 'class': 'form-control'}))