from datetime import date

from django.forms import ModelForm
from django import forms
from dal import autocomplete

from viajes.models import ViajeOferta, Solicitud


class ViajeOfertaForm(ModelForm):
    """
        Formulario para crear o editar ofertas de viaje.

        Basado en el modelo `ViajeOferta`, permite que los usuarios completen
        los detalles de un viaje que desean ofrecer. Este formulario excluye
        el campo `propietario_vehiculo`, ya que se asigna automáticamente al usuario logueado.

        Widgets personalizados:
        ----------------------
        - fecha_salida: DateInput tipo calendario HTML, con fecha mínima de hoy.
        - ciudad_salida: Autocompletado de ciudades usando Select2.
        - ciudad_llegada: Autocompletado de ciudades usando Select2.
        - codigo_postal: TextInput con placeholder 'Ej. 210334'.
        - plazas_disponibles: NumberInput con placeholder 'Ej. 1, 2, 3', mínimo 1 y máximo 7.
        - hora: TimeInput tipo reloj HTML.
        - acepto_mascotas: Select desplegable para indicar si acepta mascotas.
        - regreso_hoy: Select desplegable para indicar si el viaje tiene regreso el mismo día.
        - nombre_sector: TextInput para indicar el nombre del sector.
        - nivel_escalada: TextInput con placeholder para el nivel de escalada (Ej. 6a, 7b+, 5.9, 5.13a, V+).
        - descripcion_viaje: Textarea de 3 filas para descripción del viaje.

        Notas:
        ------
        - Utiliza `django-autocomplete-light` para los campos de ciudad.
        - Los atributos `class: 'form-control'` aseguran consistencia con Bootstrap.
        - Las restricciones de `min` y `max` para plazas y la fecha mínima ayudan a la validación en el frontend.
        - Formato de fecha: '%Y-%m-%d', formato de hora: '%H:%M'.
        """
    class Meta:
        model=ViajeOferta
        exclude = ['propietario_vehiculo']
        widgets={
           'fecha_salida': forms.DateInput(attrs={'type': 'date',
                                           'class': 'form-control',
                                            'min' : date.today().strftime('%Y-%m-%d'),
                                           },
                                            format='%Y-%m-%d'),
            'ciudad_salida':autocomplete.Select2(url = 'ciudad-autocomplete',

        ),


            'ciudad_llegada': autocomplete.Select2(url='ciudad-autocomplete'),


            'codigo_postal': forms.TextInput(attrs={'placeholder': 'Ej. 210334',
                                           'class': 'form-control'
                                           }),
            'plazas_disponibles': forms.NumberInput(attrs={'placeholder': 'Ej. 1, 2, 3',
                                                            'class': 'form-control',
                                                            'min': 1,
                                                            'max': 7}),
            'hora': forms.TimeInput(attrs={'type' : 'time',
                                           'class': 'form-control'},
                                    format='%H:%M'),
            'acepto_mascotas' : forms.Select(attrs={'class': 'form-control'}),
            'regreso_hoy': forms.Select(attrs={'class' :'form-control'}),
            'nombre_sector': forms.TextInput(attrs={'class' :'form-control'}),
            'nivel_escalada': forms.TextInput(attrs={'placeholder': 'Ej. 6a, 7b+, 5.9, 5.13a, V+',
                                                     'class': 'form-control'}),
            'descripcion_viaje': forms.Textarea(attrs={'rows': 3,
                                                 'class': 'form-control'}),
        }

class BuscarViajeForm(forms.Form):
    """
       Formulario para buscar viajes según ciudad de salida, ciudad de llegada y fecha.

       Este formulario permite que los usuarios filtren ofertas de viaje en la aplicación,
       utilizando autocompletado para las ciudades y un selector de fecha.

       Campos:
       -------
       - ciudad_salida: CharField con autocompletado Select2.
           - URL del autocompletado: 'ciudad-autocomplete'.
           - Atributo `data-width='100%'` para que ocupe todo el ancho del contenedor.
       - ciudad_llegada: CharField con autocompletado Select2.
           - URL del autocompletado: 'ciudad-autocomplete'.
           - Atributo `data-width='100%'`.
       - fecha: DateField con widget DateInput HTML5.
           - Tipo 'date' para mostrar calendario en navegadores compatibles.
           - Clase CSS 'form-control' para estilo Bootstrap.
           - Fecha mínima (`min`) = hoy, evitando búsquedas en fechas pasadas.

       Notas:
       ------
       - Utiliza `django-autocomplete-light` para los campos de ciudad.
       - Preparado para integrarse con Bootstrap y Select2.
       - Garantiza que los usuarios solo puedan seleccionar fechas válidas en el futuro.
       """
    ciudad_salida=forms.CharField(widget=autocomplete.Select2(url='ciudad-autocomplete',
                                                              attrs={
                                                                  'data-width' : '100%'                                                              }
                                                              ))

    ciudad_llegada=forms.CharField(widget=autocomplete.Select2(url='ciudad-autocomplete',
                                                               attrs={
                                                                   'data-width': '100%',

                                                               }
                                                               ))

    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date',
                                           'class': 'form-control',
                                            'min' : date.today().strftime('%Y-%m-%d'),
                                           }))

class SolicitarPlazaForm(ModelForm):
    """
        Formulario para solicitar plazas en un viaje.

        Basado en el modelo `Solicitud`, este formulario permite a un usuario
        indicar cuántas plazas desea reservar en un viaje específico.

        Meta:
        -----
        - model: Solicitud
        - fields: ['numero_plazas'] → solo se expone el número de plazas a solicitar

        Notas:
        ------
        - Otros campos del modelo (como usuario o viaje) se asignan automáticamente
          en la vista correspondiente, para garantizar seguridad y consistencia.
        - Ideal para integrarse en vistas donde un usuario puede solicitar plazas
          de manera controlada y segura.
        """

    class Meta:
        model = Solicitud
        fields = ['numero_plazas']




