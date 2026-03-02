import os
from CuerdApp import settings

''' Función auxiliar necesaria para cargar los textos que aparecen en la sección sobre nosotros. '''


def cargar_texto(nombre_texto):

    ruta_txt = os.path.join(settings.BASE_DIR, f'core/texto/{nombre_texto}')
    with open(ruta_txt, encoding='utf-8') as f:
        texto = f.read()
    return texto