from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as st, status
from rest_framework_simplejwt.views import TokenObtainPairView
from .mixins import LoginAndIsOwnerMixin, AllowAny, IsAuthenticated
from .services.UsuarioService import UsuarioService, UsuarioSerializer
from .services.PerfilService import PerfilService
from .services.AuthenticationService import AuthenticationService
from .services.JWTService import JWTService


# Create your views here.


class UsuarioViewSet(GenericViewSet, LoginAndIsOwnerMixin):
    serializer_class = UsuarioSerializer
    model = UsuarioSerializer.Meta.model
    queryset = UsuarioSerializer.Meta.model.objects.all()

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
        response = UsuarioService().list_all_users()
        return response

    def retrieve(self, request, pk=None):
        """
        Retorna un usuario


        :param request:
        :param pk: int
        :return: El usuario (id, username, password, email, first_name, last_name) o error: usuario no encontrado
        """
        controller = UsuarioService()
        response = controller.list_one_user(pk)
        return response

    def create(self, request):
        """
        Crea un usuario


        :param request: username, password, email, first_name, last_name.
        :return: message: usuario creado. o error en el/los campos.
        """

        username = request.data.get('username', None)
        password = request.data.get('password', None)
        email = request.data.get('email', None)

        response = UsuarioService().create_user(
            username=username, password=password, email=email
        )
        return response

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

        service = PerfilService()

        response = service.add_perfil_to_user(
            id=pk,
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimiento,
        )
        return response

    @action(detail=True, methods=['patch'], url_path='update_username')
    def update_username(self, request, pk=None):
        """
        Actualiza un usuario


        :param request: username
        :param pk: int
        :return: message: Username Actualizado o {message: error al actualizar el username, errors: [los campos incorrectos]}
        """

        username = request.data.get('username', None)

        service = UsuarioService()

        response = service.update_username_user(
            id=pk,
            username=username
        )
        return response

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

        service = PerfilService()
        response = service.update_perfil_to_user(
            user_id=pk,
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimeinto,
        )
        return response

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

        response = UsuarioService().set_password_user(
            id=pk,
            password=password,
            password2=password2
        )
        return response

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

        response = UsuarioService().update_email_user(
            id=pk,
            email=email,
            password=password
        )
        return response

    def destroy(self, request, pk=None):
        """
        Elimina un usuario


        :param request:
        :param pk: int
        :return: message, Usuario eliminado. O error: Usuario no encontrado.
        """
        response = UsuarioService().delete_user(
            id=pk
        )
        return response


class Login(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        password = request.data.get('password', None)
        email = request.data.get('email', None)

        service = AuthenticationService()
        response = service.login(
            email=email,
            password=password
        )
        return response


class Logout(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        id = request.user.id or 0

        service = AuthenticationService()
        response = service.logout(user_id=id)

        return response


class ProtectedView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def get(self, request):
        try:
            return Response({'message': 'Acceso permitido a la vista protegida.'})
        except Exception:
            return Response({'error': 'Servicio no disponible'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)


class VeriifcarTokenView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = None

    def get(self, request):
        token = request.data.get('access_token', None)

        service = JWTService()
        response = service.validate_token(token)
        return response
