import re
from datetime import timezone, datetime
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario, Perfil
from PIL import Image


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('username', 'password', 'email')

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
        }

        if hasattr(instance, 'perfil'):
            representation['perfil'] = {
                'nombre': instance.perfil.nombre,
                'apellido': instance.perfil.apellido,
                'fecha_nacimiento': instance.perfil.fecha_nacimiento
            }

        return representation

    def validate_username(self, value):
        min_length = 4
        if len(value) < min_length:
            raise serializers.ValidationError(f"El username debe tener por lo menos {min_length} caracteres")

        if not re.match("^[a-zA-Z0-9._]*$", value):
            raise serializers.ValidationError(f"El username puede contener letras, números, '._'")

        # # Verifica si ya existe un usuario con el mismo nombre de usuario
        # existing_user = Usuario.objects.filter(username=value).exclude(pk=self.instance.pk).first()
        # if existing_user:
        #     raise serializers.ValidationError('Este nombre de usuario ya está en uso.')

        return value

    def validate_password(self, value):
        min_length = 8
        if len(value) < min_length:
            raise serializers.ValidationError(f"La contraseña debe tener al menos {min_length} caracteres.")

        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("La contraseña debe contener al menos un número.")

        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra.")

        # Puedes agregar más reglas según tus requisitos, como caracteres especiales, mayúsculas, etc.

        return value

    def create(self, validated_data):
        # Extraer la contraseña del diccionario de datos validados
        password = validated_data.pop('password', None)

        # Crear el usuario sin guardar
        user = Usuario(**validated_data)

        # Establecer la contraseña y guardar el usuario
        if password:
            user.set_password(password)
        user.save()
        return user


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=8,
        max_length=50,
        required=True,
        validators=Usuario._meta.get_field('password').validators
    )
    password2 = serializers.CharField(
        min_length=8,
        max_length=50,
        required=True,
        validators=Usuario._meta.get_field('password').validators
    )

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Debe ingresar ambas contraseñas iguales'})
        return data


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ('nombre', 'apellido', 'fecha_nacimiento')

    def validate_nombre(self, value):
        min_length = 2
        if len(value) < min_length:
            raise serializers.ValidationError(f"El nombre debe tener por lo menos {min_length} caracteres")

        # Utiliza una expresión regular para permitir solo letras
        if not re.match("^[a-zA-Z]*$", value):
            raise serializers.ValidationError(f"El nombre debe contener solo letras.")

        return value

    def validate_apellido(self, value):
        min_length = 2
        if len(value) < min_length:
            raise serializers.ValidationError(f"El apellido debe tener por lo menos {min_length} caracteres")

        # Utiliza una expresión regular para permitir solo letras
        if not re.match("^[a-zA-Z]*$", value):
            raise serializers.ValidationError(f"El apellido debe contener solo letras.")

        return value

    def validate_fecha_nacimiento(self, value):

        # value type is <class 'datetime.date'>
        if value is None:
            raise serializers.ValidationError("El campo de fecha de nacimiento es obligatorio.")

        # Verificar si la fecha de nacimiento es mayor que la fecha actual
        if value > datetime.now().date():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser mayor que la fecha actual.")

        return value

    def validate_imagen(self, value):
        try:
            img = Image.open(value)
            img.verify()
        except Exception as e:
            raise serializers.ValidationError("Imagen no válida.")

        return value


class ConfirmarEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('password', 'email')

    def validate(self, data):
        if not data['email']:
            raise serializers.ValidationError({'email': 'El email es requerido'})
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass
