from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario, Perfil


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('username', 'password', 'email')

    def to_representation(self, instance):
        representation = {
            'username': instance.username,
            'email': instance.email,
        }

        if hasattr(instance, 'perfil'):
            representation['perfil'] = {
                'nombre': instance.perfil.nombre,
                'apellido': instance.perfil.apellido
            }

        return representation

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


class UpdateUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('username',)

    def validate_username(self, value):
        # Verifica si ya existe un usuario con el mismo nombre de usuario
        existing_user = Usuario.objects.filter(username=value).exclude(pk=self.instance.pk).first()
        if existing_user:
            raise serializers.ValidationError('Este nombre de usuario ya está en uso.')
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
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


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ('nombre', 'apellido', 'fecha_nacimiento')


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
