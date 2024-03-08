from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as st, status
from rest_framework_simplejwt.views import TokenObtainPairView
from .mixins import LoginAndIsOwnerMixin, AllowAny, IsAuthenticated
from .services.UsuarioService import UsuarioService
from .services.PerfilService import PerfilService
from .services.AuthenticationService import AuthenticationService
from .services.JWTService import JWTService


# Create your views here.


class UsuarioViewSet(GenericViewSet, LoginAndIsOwnerMixin):
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
        status, data = UsuarioService().list_all_users()
        if status == 200:
            return Response(data, status=st.HTTP_200_OK)
        else:
            return Response({'error': 'Servicio no disponible'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """
        Retorna un usuario


        :param request:
        :param pk: int
        :return: El usuario (id, username, password, email, first_name, last_name) o error: usuario no encontrado
        """
        controller = UsuarioService()
        status, data = controller.list_one_user(pk)
        if status == 200:
            return Response(data, status=st.HTTP_200_OK)
        elif status == 400:
            return Response({'error': 'Usuario no encontrado'}, status=st.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': f'Servicio no disponible'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """
        Crea un usuario


        :param request: username, password, email, first_name, last_name.
        :return: message: usuario creado. o error en el/los campos.
        """

        username = request.data.get('username', None)
        password = request.data.get('password', None)
        email = request.data.get('email', None)
        status, data = UsuarioService().create_user(
            username=username, password=password, email=email
        )

        if status == 200:
            return Response(
                {'message': 'Usuario creado'}, status=st.HTTP_201_CREATED
            )
        elif status == 400:
            return Response({
                'message': 'Error al registrarse',
                'errors': data
            }, status=st.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {'error': f'Servicio no disponible'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='add_perfil')
    def add_perfil_to_user(self, request, pk=None):
        """
                Agrega un perfil a un usuario


                :param request: nombre, apellido, fecha_nacimiento(opcional)
                :param pk: int
                :return: message: Perfil Agregado a usuario o {message: Error al agregar el perfil de usuario, errors: [los campos incorrectos]}
                """

        nombre = request.data.get('nombre', None)
        apellido = request.data.get('apellido', None)
        fecha_nacimiento = request.data.get('fecha_nacimiento', None)
        imagen = request.data.get('imagen', None)

        controller = PerfilService()

        status, data = controller.add_perfil_to_user(
            id=pk,
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimiento,
        )

        if status == 200:
            return Response(
                {'message': 'Perfil Agregado a usuario'}, status=st.HTTP_201_CREATED
            )
        elif status == 400:
            return Response(
                data, status=st.HTTP_400_BAD_REQUEST
            )
        elif status == 404:
            return Response(
                data, status=st.HTTP_404_NOT_FOUND
            )
        else:
            return Response(
                {'error': f'Servicio no disponible'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'], url_path='update_username')
    def update_username(self, request, pk=None):
        """
        Actualiza un usuario


        :param request: username
        :param pk: int
        :return: message: Username Actualizado o {message: error al actualizar el username, errors: [los campos incorrectos]}
        """

        username = request.data.get('username', None)

        controller = UsuarioService()

        status, data = controller.update_username_user(
            id=pk,
            username=username
        )

        if status == 200:
            return Response(
                {'message': 'Username Actualizado'}, status=st.HTTP_200_OK
            )
        elif status == 400:
            return Response({
                'message': 'Error al actualizar el username',
                'errors': data
            }, status=st.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {'error': f'Servicio no disponible'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['put'], url_path='update_perfil')
    def update_perfil(self, request, pk=None):
        """
        Actualiza el perfil del usuario


        :param request: nombre, apellido, fecha_de_nacimeinto(opcional)
        :param pk: int
        :return: message: Perfil Actualizado o {message: error al actualizar el perfil, errors: [los campos incorrectos]}
        """
        nombre = request.data.get('nombre', None)
        apellido = request.data.get('apellido', None)
        fecha_nacimeinto = request.data.get('fecha_nacimiento', None)
        imagen = request.data.get('imagen', None)

        controller = PerfilService()
        status, data = controller.update_perfil_to_user(
            user_id=pk,
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimeinto,
        )

        if status == 200:
            return Response(
                {'message': 'Perfil actualizado'}, status=st.HTTP_200_OK
            )
        elif status == 400:
            return Response({
                'message': 'Error al actualizar el perfil de usuario',
                'errors': data
            }, status=st.HTTP_400_BAD_REQUEST
            )
        elif status == 404:
            return Response(
                {'error': 'El usuario que desea actualizar no tiene datos de perfil'},
                status=st.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {'error': f'Servicio no disponible:'},
                status=st.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='set_password')
    def set_password(self, request, pk=None):
        """
        Actualiza la contraseña de un usuario


        :param request: password y password2
        :param pk: int
        :return: message: Contraseña Actualizada o {message: Error al actualizar la contraseña, errors: [los campos incorrectos]}
        """

        password = request.data.get('password', None)
        password2 = request.data.get('password2', None)

        status, data = UsuarioService().set_password_user(
            id=pk,
            password=password,
            password2=password2
        )
        if status == 200:
            return Response(
                {'message': 'Contraseña Actualizada'}, status=st.HTTP_200_OK
            )
        elif status == 400:
            return Response({
                'message': 'Error al actualizar la contraseña',
                'errors': data},
                status=st.HTTP_400_BAD_REQUEST
            )
        elif status == 404:
            return Response(
                {'errors': 'Usuario no encontrado'},
                status=st.HTTP_404_NOT_FOUND
            )
        else:
            return Response(
                {'error': 'Servicio no disponible'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='update_email')
    def update_email(self, request, pk=None):
        """
            Actualiza el email de un usuario


            :param request: email, password
            :param pk: int
            :return: message: Email Actualizado o {message: Error al actualizar el email, errors: [los campos incorrectos]}
        """

        email = request.data.get('email', None)
        password = request.data.get('password', None)

        status, data = UsuarioService().update_email_user(
            id=pk,
            email=email,
            password=password
        )

        if status == 200:
            return Response(
                {'message': 'Email Actualizado'}, status=st.HTTP_200_OK
            )
        elif status == 400:
            return Response(
                {
                    'message': 'Error al actualizar el email',
                    'errors': data},
                status=st.HTTP_400_BAD_REQUEST
            )
        elif status == 401:
            return Response(
                {'error': 'La contraseña es invalida'},
                status=st.HTTP_401_UNAUTHORIZED
            )
        else:
            return Response(
                {'error': 'Servicio no disponible'},
                status=st.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """
        Elimina un usuario


        :param request:
        :param pk: int
        :return: message, Usuario eliminado. O error: Usuario no encontrado.
        """
        status, data = UsuarioService().delete_user(
            id=pk
        )

        if status == 200:
            return Response(
                {'message': 'Usuario eliminado'}, status=st.HTTP_204_NO_CONTENT
            )
        elif status == 404:
            return Response(
                {'error': 'Usuario no encontrado'}, status=st.HTTP_404_NOT_FOUND
            )
        else:
            return Response(
                {'error': 'Servicio no disponible'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR
            )


class Login(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        password = request.data.get('password', None)
        email = request.data.get('email', None)

        controller = AuthenticationService()
        status, data = controller.login(
            email=email,
            password=password
        )

        if status == 200:
            return Response(
                data,
                status=st.HTTP_200_OK,
                content_type='application/json'
            )

        elif status == 400:
            Response(
                {'error': 'Contraseña o nombre de usuario incorrectos'},
                status=st.HTTP_400_BAD_REQUEST,
                content_type='application/json'
            )
        else:
            return Response(
                {'error': f'Servicio no disponible'},
                status=st.HTTP_500_INTERNAL_SERVER_ERROR
            )


class Logout(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        id = request.user.id or 0
        controller = AuthenticationService()

        status, data = controller.logout(user_id=id)

        if status == 200:
            return Response(
                {'message': 'Sesion cerrada correctamente'}, status=st.HTTP_200_OK
            )
        elif status == 400:
            return Response(
                {'error': 'No existe este usuario'}, status=st.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {'error': f'Servicio no disponible'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProtectedView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            return Response({'message': 'Acceso permitido a la vista protegida.'})
        except Exception:
            return Response({'error': 'Servicio no disponible'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)


class VeriifcarTokenView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.data.get('access_token', None)

        controller = JWTService()
        response = controller.validate_token(token)
        return Response({'access_token': response}, status=status.HTTP_200_OK)
