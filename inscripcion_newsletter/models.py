from django.db import models

class InscripcionNewsletter(models.Model):

    email = models.EmailField(unique=True,blank=False,
                              error_messages={'unique':'Este correo ya está dado de alta'})
