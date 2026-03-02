# middleware/perfil_required.py
from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

class TienePerfilMiddleware:
    """
    Middleware que verifica que el usuario autenticado tenga perfil.
    Si no tiene, lo redirige a la URL de creación de perfil.
    No afecta a admin, usuarios anónimos, logout o rutas de login de Google.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            excluded_paths = [
                reverse('perfil-form'),
                reverse('account_logout'),
                '/admin/',
                '/accounts/google/login/callback/',
            ]

            if not any(request.path.startswith(path) for path in excluded_paths):
                try:
                    _ = request.user.perfil
                except ObjectDoesNotExist:
                    return redirect('perfil-form')

        response = self.get_response(request)
        return response