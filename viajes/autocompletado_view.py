import requests
from dal import autocomplete

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

        if not query:
            return []

        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "format": "json",
            "addressdetails": 1,
            "limit": 5,
            "q": query
        }

        headers = {
            'User-Agent': 'ProyectoFinal',
            'Accept-Language': 'es-ES, es'
        }

        response = requests.get(url, params=params, headers=headers)
        datos = response.json()

        if not datos:
            return ["Búsqueda sin resultados"]

        resultados = []
        for lugar in datos:

            ciudad = lugar.get('display_name')

            if ciudad:
                resultados.append(ciudad)

        if not resultados:
            resultados.append("Búsqueda sin resultados")

        return resultados
