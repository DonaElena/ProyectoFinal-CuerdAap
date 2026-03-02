import folium
import requests

from viajes.models import Ciudad




def buscar_coordenadas_api(ciudad):
    """
       Obtiene las coordenadas geográficas (latitud y longitud) de una ciudad
       utilizando la API de Nominatim (OpenStreetMap).

       Parámetros:
       -----------
       ciudad : str
           Nombre de la ciudad a buscar.

       Retorno:
       --------
       tuple[float, float] o (None, None)
           - latitud y longitud de la ciudad si se encuentra.
           - (None, None) si no se encuentran resultados.

       Notas:
       ------
       - Se realiza una petición HTTP GET a Nominatim con límite de 1 resultado.
       - Se incluyen cabeceras obligatorias (`User-Agent`) y preferencia de idioma (`Accept-Language`).
       """

    query = ciudad

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "format": "json",
        "addressdetails": 1,
        "limit": 1,
        "q": query
    }

    headers = {
        'User-Agent': 'ProyectoFinal',
        'Accept-Language': 'es-ES, es'
    }

    response = requests.get(url, params=params, headers=headers)
    datos = response.json()

    if not datos:
        return None,None

    latitud = float(datos[0]['lat'])
    longitud = float(datos[0]['lon'])

    return latitud, longitud

class MapaViaje:
    """
        Clase para generar un mapa interactivo de un viaje con folium.

        Esta clase permite visualizar gráficamente la ruta de un viaje, desde
        la ciudad de salida hasta la ciudad de llegada, utilizando coordenadas
        almacenadas en la base de datos o consultando la API de OpenStreetMap
        en caso de que no existan.

        Atributos:
        ----------
        viaje : Viaje
            Instancia del modelo Viaje con información del viaje.
        ciudad_salida : str
            Nombre de la ciudad de salida del viaje.
        ciudad_llegada : str
            Nombre de la ciudad de llegada del viaje.
        mapa : folium.Map o None
            Mapa generado con folium que contiene la ruta; None si no se pueden obtener coordenadas.

        Métodos:
        --------
        obtener_coordenadas(self) -> list[tuple[float, float]]
            - Obtiene las coordenadas de las ciudades de salida y llegada.
            - Primero intenta buscar la ciudad en la base de datos (`Ciudad`).
            - Si no existe, consulta la API de Nominatim y guarda la ciudad en la base de datos.
            - Devuelve una lista de tuplas (latitud, longitud).

        obtener_mapa(self) -> folium.Map o None
            - Genera un mapa de folium centrado en la ciudad de salida.
            - Dibuja una línea entre la ciudad de salida y llegada usando PolyLine.
            - Devuelve None si no se pueden obtener las coordenadas de ambas ciudades.

        html (property)
            - Retorna la representación HTML del mapa (`_repr_html_`) lista para insertar
              en plantillas Django.
            - Retorna None si no hay mapa disponible.

        Notas:
        ------
        - Se utiliza la clase `Ciudad` para almacenar coordenadas y evitar consultas repetidas a la API.
        - `folium` se encarga de la visualización y el trazado de la ruta.
        - El mapa generado ocupa el 100% del ancho y alto de su contenedor.
        """

    def __init__(self,viaje):

        self.viaje = viaje
        self.ciudad_salida = viaje.ciudad_salida
        self.ciudad_llegada = viaje.ciudad_llegada
        self.mapa = self.obtener_mapa()


    def obtener_coordenadas(self):

        coordenadas = []
        ciudades = [self.ciudad_salida,self.ciudad_llegada]

        for ciudad in ciudades:

            try:
                ciudad_query = Ciudad.objects.get(nombre_ciudad = ciudad)
                latitud = float(ciudad_query.latitud)
                longitud = float(ciudad_query.longitud)
                coordenadas.append((latitud, longitud))
            except Ciudad.DoesNotExist:
                latitud, longitud = buscar_coordenadas_api(ciudad)
                if latitud is not None and longitud is not None:
                    Ciudad.objects.create(
                        nombre_ciudad=ciudad,
                        latitud=latitud,
                        longitud=longitud
                    )
                    coordenadas.append((latitud, longitud))
        return coordenadas


    def obtener_mapa(self):

        coordenadas = self.obtener_coordenadas()

        if len(coordenadas) != 2:
            return None

        coordenadas_mapa_general =list(coordenadas[0])

        m = folium.Map(location = coordenadas_mapa_general,
                       zoom_start= 6,
                       width='100%',
                       height='100%'
                       )
        folium.PolyLine(coordenadas,
                        color='#6f0f3e',
                        weight = 5,
                        ).add_to(m)
        return m

    @property
    def html(self):
        if not self.mapa is None:
            return self.mapa._repr_html_()
        else:
            return None











