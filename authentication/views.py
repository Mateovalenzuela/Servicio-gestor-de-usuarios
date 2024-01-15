from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UsuarioSerializer, CustomTokenObtainPairSerializer, \
    PasswordSerializer, PerfilSerializer, ConfirmarEmailSerializer
from .mixins import LoginAndIsOwnerMixin, AllowAny, IsAuthenticated


# Create your views here.


class UsuarioViewSet(GenericViewSet, LoginAndIsOwnerMixin):
    model = get_user_model()
    serializer_class = UsuarioSerializer
    queryset = None

    def get_object(self, pk):
        return get_object_or_404(self.model, pk=pk, is_active=True, is_superuser=False)

    def get_queryset(self):
        if self.queryset is None:
            return self.model.objects.filter(is_active=True, is_superuser=False)
        return self.queryset

    def get_permissions(self):
        # Aplicar el mixin a todas las vistas excepto las de la lista
        if self.action in ['list', 'create']:
            return [AllowAny()]

        return [LoginAndIsOwnerMixin()]

    def list(self, request):
        """
        Retorna un listado de todos los usuarios


        :param request:
        :return: Lista vacía o Lista con todos los usuarios
        """
        try:
            serializer = self.serializer_class(self.get_queryset(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Servicio no disponible'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """
        Retorna un usuario


        :param request:
        :param pk: int
        :return: El usuario (id, username, password, email, first_name, last_name) o error: usuario no encontrado
        """
        try:
            usuario = self.get_object(pk)
            if usuario:
                serializer = self.serializer_class(usuario)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Servicio no disponible: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """
        Crea un usuario


        :param request: username, password, email, first_name, last_name.
        :return: message: usuario creado. o error en el/los campos.
        """
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Usuario creado'}, status=status.HTTP_201_CREATED)
            return Response({
                'message': 'Error al registrarse',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Servicio no disponible: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='add_perfil')
    def add_perfil_to_user(self, request, pk=None):
        """
                Agrega un perfil a un usuario


                :param request: nombre, apellido, fecha_nacimiento(opcional)
                :param pk: int
                :return: message: Perfil Agregado a usuario o {message: Error al agregar el perfil de usuario, errors: [los campos incorrectos]}
                """
        try:
            usuario = self.get_object(pk)
            # Verificar si ya existe un perfil para el usuario
            if hasattr(usuario, 'perfil'):
                return Response({'message': 'Ya existe un perfil para este usuario.'},
                                status=status.HTTP_400_BAD_REQUEST)

            # serializa los datos del perfil
            serializer = PerfilSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(usuario=usuario)
                return Response({'message': 'Perfil Agregado a usuario'}, status=status.HTTP_201_CREATED)

            return Response({
                'message': 'Error al agregar el perfil de usuario',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Servicio no disponible'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'], url_path='update_username')
    def update_username(self, request, pk=None):
        """
        Actualiza un usuario


        :param request: username
        :param pk: int
        :return: message: Username Actualizado o {message: error al actualizar el username, errors: [los campos incorrectos]}
        """
        try:
            usuario = self.get_object(pk)
            serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Username Actualizado'}, status=status.HTTP_200_OK)
            return Response({
                'message': 'Error al actualizar el username',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Servicio no disponible: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['put'], url_path='update_perfil')
    def update_perfil(self, request, pk=None):
        """
        Actualiza el perfil del usuario


        :param request: nombre, apellido, fecha_de_nacimeinto(opcional)
        :param pk: int
        :return: message: Perfil Actualizado o {message: error al actualizar el perfil, errors: [los campos incorrectos]}
        """
        try:
            usuario = self.get_object(pk)
            # Verificar si el usuario no tiene datos de perfil
            if not hasattr(usuario, 'perfil'):
                return Response({'error': 'El usuario que desea actualizar no tiene datos de perfil'},
                                status=status.HTTP_400_BAD_REQUEST)

            # serializa los datos del perfil
            serializer = PerfilSerializer(usuario.perfil, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Perfil actualizado'}, status=status.HTTP_200_OK)

            return Response({
                'message': 'Error al actualizar el perfil de usuario',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Servicio no disponible: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='set_password')
    def set_password(self, request, pk=None):
        """
        Actualiza la contraseña de un usuario


        :param request: password y password2
        :param pk: int
        :return: message: Contraseña Actualizada o {message: Error al actualizar la contraseña, errors: [los campos incorrectos]}
        """
        try:
            user = self.get_object(pk)
            password_serializer = PasswordSerializer(data=request.data)
            if password_serializer.is_valid():
                user.set_password(password_serializer.validated_data['password'])
                user.save()
                return Response({'message': 'Contraseña Actualizada'}, status=status.HTTP_200_OK)

            return Response({
                'message': 'Error al actualizar la contraseña',
                'errors': password_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Servicio no disponible'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='update_email')
    def update_email(self, request, pk=None):
        """
            Actualiza el email de un usuario


            :param request: email, password
            :param pk: int
            :return: message: Email Actualizado o {message: Error al actualizar el email, errors: [los campos incorrectos]}
        """
        try:
            user = self.get_object(pk)
            email_serializer = ConfirmarEmailSerializer(data=request.data)

            if email_serializer.is_valid():
                # valída que la contraseña ingresada sea la del usuario a actualizar
                valid_password = user.check_password(email_serializer.validated_data['password'])

                if not valid_password:
                    # La contraseña no ingresada no coincide con la del usuario
                    return Response(
                        {'error': 'La contraseña es invalida'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # la contraseña es correcta
                user.email = email_serializer.validated_data['email']
                user.save()
                return Response({'message': 'Email Actualizado'}, status=status.HTTP_200_OK)

            return Response({
                'message': 'Error al actualizar el email',
                'errors': email_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({'error': 'Servicio no disponible'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        """
        Elimina un usuario


        :param request:
        :param pk: int
        :return: message, Usuario eliminado. O error: Usuario no encontrado.
        """
        try:
            updated_rows = self.model.objects.filter(id=pk, is_active=True, is_superuser=False).update(is_active=False)
            if updated_rows == 1:
                return Response({'message': 'Usuario eliminado'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'error': 'Servicio no disponible'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Login(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('email', '')
            password = request.data.get('password', '')

            user = authenticate(
                username=username,
                password=password
            )  # devuelve un bool si existe o no un usuario para esas credenciales
            if user:
                login_serializer = self.serializer_class(data=request.data)
                if login_serializer.is_valid():
                    return Response({
                        'token': login_serializer.validated_data.get('access'),
                        'refresh-token': login_serializer.validated_data.get('refresh'),
                        'username': username,
                        'message': 'Inicio de Sesion Exitoso'
                    }, status=status.HTTP_200_OK, content_type='application/json')

            return Response({'error': 'Contraseña o nombre de usuario incorrectos'}, status=status.HTTP_400_BAD_REQUEST,
                            content_type='application/json')
        except Exception as e:
            return Response({'error': f'Servicio no disponible: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Logout(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # obtiene el usuario que inicio sesion
            id = request.user.id or 0
            user = UsuarioSerializer.Meta.model.objects.filter(id=id, is_active=True)

            if user.exists():
                # actualiza el token de refresh y lo manda a la lista negra
                RefreshToken.for_user(user.first())
                return Response({'message': 'Sesion cerrada correctamente'}, status=status.HTTP_200_OK)
            return Response({'error': 'No existe este usuario'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Servicio no disponible: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProtectedView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            return Response({'message': 'Acceso permitido a la vista protegida.'})
        except Exception:
            return Response({'error': 'Servicio no disponible'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
