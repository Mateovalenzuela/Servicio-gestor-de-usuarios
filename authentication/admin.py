from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import Usuario, Perfil

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Permission)
admin.site.register(Perfil)
