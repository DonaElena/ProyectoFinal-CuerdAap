from django.urls import path
from .views import inscripcion_newsletter

urlpatterns = [
    path('newsletter/', inscripcion_newsletter, name='inscripcion_newsletter'),
]
