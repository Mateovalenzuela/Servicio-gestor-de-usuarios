from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('username', 'password', 'email', 'nombre', 'apellido')

    def to_representation(self, instance):
        return {
            'username': instance.username,
            'email': instance.email,
            'nombre': instance.nombre,
            'apellido': instance.apellido
        }

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


class UpdateUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('username', 'nombre', 'apellido')

    def validate_username(self, value):
        # Verifica si ya existe un usuario con el mismo nombre de usuario
        existing_user = Usuario.objects.filter(username=value).exclude(pk=self.instance.pk).first()
        if existing_user:
            raise serializers.ValidationError('Este nombre de usuario ya está en uso.')
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.apellido = validated_data.get('apellido', instance.apellido)

        instance.save()
        return instance


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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass
