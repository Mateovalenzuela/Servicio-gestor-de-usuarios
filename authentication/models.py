import re
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.conf import settings
from django.utils import timezone
from django.db import models
from PIL import Image


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

    def validar_nombre(value):
        min_length = 2
        if len(value) < min_length:
            raise ValidationError(f"El nombre debe tener por lo menos {min_length} caracteres")

        # Utiliza una expresión regular para permitir solo letras
        if not re.match("^[a-zA-Z]*$", value):
            raise ValidationError(f"el apellido debe contener solo letras.")

    def validar_apellido(value):
        min_length = 2
        if len(value) < min_length:
            raise ValidationError(f"El apellido debe tener por lo menos {min_length} caracteres")

        # Utiliza una expresión regular para permitir solo letras
        if not re.match("^[a-zA-Z]*$", value):
            raise ValidationError(f"el apellido debe contener solo letras.")

    def validar_fecha(value):
        if value > timezone.now().date():
            raise ValidationError("La fecha no puede ser mayor que la fecha actual.")

    def validar_imagen(value):
        try:
            img = Image.open(value)
            img.verify()
        except Exception as e:
            raise ValidationError("Imagen no válida.")

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='perfil'
    )
    nombre = models.CharField(verbose_name='Nombre', max_length=100, blank=True, null=True,
                              validators=[validar_nombre])
    apellido = models.CharField(verbose_name='Apellido', max_length=100, blank=True, null=True,
                                validators=[validar_apellido])
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento', blank=True, null=True, editable=False,
                                        validators=[validar_fecha])
    imagen = models.ImageField(verbose_name='Imagen de Perfil', upload_to='perfil/', max_length=200, blank=True,
                               null=True, validators=[validar_imagen])


class Usuario(AbstractBaseUser, PermissionsMixin):

    def validar_username(value):
        min_length = 4
        if len(value) < min_length:
            raise ValidationError(f"El username debe tener por lo menos {min_length} caracteres")

        # Utiliza una expresión regular para permitir letras, números, puntos, guion bajo, arroba y corchete
        if not re.match("^[a-zA-Z0-9._]*$", value):
            raise ValidationError(
                f"El username puede contener letras, números, '._'")

    def validar_correo_electronico(value):
        email_validator = EmailValidator(message="Introduce una dirección de correo electrónico válida.")

        try:
            email_validator(value)
        except ValidationError as e:
            raise ValidationError(e)

    username = models.CharField(verbose_name='Nombre de Usuario', unique=True, max_length=30,
                                validators=[validar_username])
    email = models.EmailField(verbose_name='Correo Electrónico', unique=True, max_length=200,
                              validators=[validar_correo_electronico])

    email_confirmado = models.BooleanField(verbose_name='Email Confirmado', default=False, null=False, editable=False)
    is_active = models.BooleanField(default=True, null=False)
    is_staff = models.BooleanField(default=False, null=False)
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return f'{self.email} - {self.username}'
