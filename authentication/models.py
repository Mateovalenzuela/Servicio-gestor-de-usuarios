from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.db import models


# Create your models here.

class UsuarioManager(BaseUserManager):

    def _create_user(self, email, username, password, is_staff, is_superuser, **extra_fields):
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        return self._create_user(email, username, password, is_staff=False, is_superuser=False,
                                 **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        return self._create_user(email, username, password, is_staff=True, is_superuser=True,
                                 **extra_fields)


class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='perfil'
    )
    nombre = models.CharField(verbose_name='Nombre', max_length=100, blank=True, null=True)
    apellido = models.CharField(verbose_name='Apellido', max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento', blank=True, null=True)
    imagen = models.ImageField(verbose_name='Imagen de Perfil', upload_to='perfil/', max_length=200, blank=True,
                               null=True)


class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(verbose_name='Nombre de Usuario', unique=True, max_length=30, )

    email = models.EmailField(verbose_name='Correo Electrónico', unique=True, max_length=200)

    email_confirmado = models.BooleanField(verbose_name='Email Confirmado', default=False, null=False, editable=False)
    is_active = models.BooleanField(default=True, null=False)
    is_staff = models.BooleanField(default=False, null=False)
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return f'{self.email} - {self.username}'
