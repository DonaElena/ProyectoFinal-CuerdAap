from django.contrib import admin
from usuarios.models import Usuario, Perfil, Opinion

''' Registro de los modelos Usuario, Perfil y Opinion en el panel de administrador '''

admin.site.register(Usuario)
admin.site.register(Perfil)
admin.site.register(Opinion)