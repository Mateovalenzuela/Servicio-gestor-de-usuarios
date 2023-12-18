from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UsuarioSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        min_length=4,
        max_length=50,
        required=True,
        validators=User._meta.get_field('username').validators
    )
    password = serializers.CharField(
        min_length=8,
        max_length=50,
        required=True,
        validators=User._meta.get_field('password').validators
    )
    email = serializers.EmailField(max_length=50, required=True)
    first_name = serializers.CharField(min_length=2, max_length=50, required=True)
    last_name = serializers.CharField(min_length=2, max_length=50, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'id': {'read_only': True},
            'email': {'read_only': True},
            'password': {'write_only': True}
        }

    def to_representation(self, instance):
        return {
            'username': instance.username,
            'email': instance.email,
            'first_name': instance.first_name,
            'last_name': instance.last_name
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class UpdateUsuarioSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        min_length=4,
        max_length=50,
        required=True,
        validators=User._meta.get_field('username').validators
    )
    first_name = serializers.CharField(min_length=2, max_length=50, required=True)
    last_name = serializers.CharField(min_length=2, max_length=50, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

    def validate_username(self, value):
        # Verifica si ya existe un usuario con el mismo nombre de usuario
        existing_user = User.objects.filter(username=value).exclude(pk=self.instance.pk).first()
        if existing_user:
            raise serializers.ValidationError('Este nombre de usuario ya está en uso.')
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)

        instance.save()
        return instance


class PasswordOfUserSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=8,
        max_length=50,
        required=True,
        validators=User._meta.get_field('password').validators
    )
    password2 = serializers.CharField(
        min_length=8,
        max_length=50,
        required=True,
        validators=User._meta.get_field('password').validators
    )

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Debe ingresar ambas contraseñas iguales'})
        return data





class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass
