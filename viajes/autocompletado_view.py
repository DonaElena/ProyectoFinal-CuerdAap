import requests
from django.core.cache import cache
from dal import autocomplete
from viajes.models import Ciudad

def busqueda_en_cache(query):

    """ Función auxiliar que verifica si la búsqueda introducida por el usuario está en cache.

        Utiliza el objeto cache del módulo cache de Django.
    """
    cache_key = f'autocomplete_{query}'
    en_cache = cache.get(cache_key)

    if en_cache:
        return en_cache

def busqueda_en_bbdd(query):

    """
       Función auxiliar que busca en la BBDD poblada con ciudades si existe la ciudad
    """

    ciudades_db = Ciudad.objects.filter(
        nombre_ciudad__icontains=query)[:5]

    if ciudades_db.exists():
        return [ciudad.nombre_ciudad for ciudad in ciudades_db]

def guardar_en_cache(resultados_api,query):

    """
       Función auxiliar para cachear búsquedas en de ciudades para las que aún
       no se ha publicado ningún viaje.
       Optimiza búsquedas de viajes cuyas ciudades aún no han sido origen ni destino
    """
    cache.set(f'autocomplete_{query}',resultados_api,timeout=7200)

class CiudadAutocomplete(autocomplete.Select2ListView):
    """
     Autocompletado de ciudades usando la API de Nominatim (OpenStreetMap).

     Esta clase permite que un campo de formulario genere sugerencias
     de ciudades mientras el usuario escribe. Se integra con `django-autocomplete-light`.

     Métodos sobrescritos:
     ---------------------

     get_list(self) -> list:
         - Obtiene la lista de sugerencias basada en la consulta del usuario (`self.q`).
         - Flujo:
             1. Comprueba si `self.q` contiene texto; si no, devuelve lista vacía.
             2. Realiza una solicitud HTTP GET a la API de Nominatim:
                 - URL: https://nominatim.openstreetmap.org/search
                 - Parámetros:
                     - format=json : para obtener respuesta en formato JSON
                     - addressdetails=1 : incluye detalles de la dirección
                     - limit=5 : máximo 5 resultados
                     - q=query : texto de búsqueda
                 - Headers:
                     - User-Agent='ProyectoFinal' : obligatorio para Nominatim
                     - Accept-Language='es-ES, es' : devuelve resultados en español
             3. Convierte la respuesta JSON en lista de diccionarios (`datos`).
             4. Extrae el campo `display_name` de cada resultado y lo agrega a `resultados`.
             5. Si no hay resultados, agrega "Búsqueda sin resultados".
             6. Devuelve la lista final de sugerencias.

     Ejemplo de retorno:
         ["Madrid, Comunidad de Madrid, España",
          "Barcelona, Cataluña, España",
          "Búsqueda sin resultados"]

     Notas:
     ------
     - Este autocompletado se utiliza típicamente en formularios con `Select2`.
     - Limita la carga en la API a 5 resultados para mejorar el rendimiento.
     - Se asegura de que siempre haya al menos un elemento en la lista para mostrar al usuario.
     """

    def get_list(self):

        query = self.q

        # Comenzar petición a la API a partir de 3 letras.

        if not query or len(query) < 3:
            return []

        query_normalizada = query.lower().strip()

        resultados_cache = busqueda_en_cache(query_normalizada)
        if resultados_cache:
            return resultados_cache

        resultados_bbdd = busqueda_en_bbdd(query_normalizada)
        if resultados_bbdd:
            return resultados_bbdd

        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "format": "json",
            "addressdetails": 1,
            "limit": 5,
            "q": query_normalizada
                }

        headers = {
            'User-Agent': 'ProyectoFinal',
            'Accept-Language': 'es-ES, es'
                 }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            datos = response.json()

        except requests.RequestException:

            return ['Intenta buscar tu viaje más tarde']

        resultados = [lugar.get('display_name') for lugar in datos if lugar.get('display_name')]

        if not resultados:
            resultados.append('Búsqueda sin resultado')
        else:
            guardar_en_cache(resultados,query_normalizada)

        return resultados
