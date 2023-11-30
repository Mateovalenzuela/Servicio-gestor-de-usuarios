import datetime
from django.contrib.sessions.models import Session
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import LoginUsuarioSerializer, UsuarioSerializer


# Create your views here.

class UsuarioViewSet(GenericViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    serializer_class = UsuarioSerializer

    def get_queryset(self, pk=None):
        if pk is None:
            return self.get_serializer().Meta.model.objects.filter(is_active=True, is_superuser=False)
        return self.get_serializer().Meta.model.objects.filter(id=pk, is_active=True, is_superuser=False).first()

    def list(self, request):
        """
        Retorna un listado de todos los usuarios


        :param request:
        :return: Lista vacía o Lista con todos los usuarios
        """

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        Retorna un usuario


        :param request:
        :param pk: int
        :return: El usuario (id, username, password, email, first_name, last_name) o error: usuario no encontrado
        """

        usuario = self.get_queryset(pk)
        if usuario:
            serializer = self.get_serializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        """
        Crea un usuario


        :param request: username, password, email, first_name, last_name.
        :return: message: usuario creado. o error en el/los campos.
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Usuario creado'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Actualiza un usuario


        :param request: Todos opcionales, password, first_name, last_name
        :param pk: int
        :return: El usuario actualizado (id, username, password, email, first_name, last_name) o error: usuario no encontrado
        """

        usuario = self.get_queryset(pk)
        if usuario:
            serializer = self.get_serializer(usuario, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Elimina un usuario


        :param request:
        :param pk: int
        :return: message, Usuario eliminado. O error: Usuario no encontrado.
        """

        usuario = self.get_queryset(pk).filter(id=pk).first()
        if usuario:
            usuario.is_active = False
            usuario.save()
            Response({'message': 'Usuario eliminado'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)


class LoginUsuario(ObtainAuthToken):
    authentication_classes = [TokenAuthentication]
    permission_classes = []

    def post(self, request, **kwargs):

        """
        Inicia la session de un usuario


        :param request: username, password.
        :return: {token, username y message} o error de varios tipos
        """


        try:

            # Obtiene las credenciales del cuerpo de la solicitud
            login_serializer = self.serializer_class(data=request.data, context={'request': request})
            if login_serializer.is_valid():  # valida si el usuario existe

                user = login_serializer.validated_data['user']  # obtiene los datos
                if user.is_active:  # valida si el usuario esta activo
                    # Genera o recupera el token
                    token, created = Token.objects.get_or_create(user=user)

                    # serializa los datos del usuario
                    user_serializer = LoginUsuarioSerializer(user)
                    if created:
                        # si se creeo el token,
                        # Devuelve el token y otros detalles si es necesario
                        return Response({
                            'token': token.key,
                            'username': user_serializer.data,
                            'message': 'Inicio de Sesión Exitoso'
                        }, status=status.HTTP_201_CREATED)
                    else:
                        # Si no se creó el token, se eliminan las sesiones, se borra el token viejo y se crea un token nuevo
                        all_session = Session.objects.filter(expire_date__gte=datetime.datetime.now())
                        if all_session.exists():
                            # borra las sessiones, en caso de que las haya
                            for session in all_session:
                                session_data = session.get_decoded()
                                if user.id == int(session_data.get('_auth_user_id')):
                                    session.delete()

                        token.delete()
                        token = Token.objects.create(user=user)
                        return Response({
                            'token': token.key,
                            'username': user_serializer.data,
                            'message': 'Inicio de Sesión Exitoso'
                        }, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Usuario inactivo'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': 'Nombre de usuario o contraseña incorrectos'},
                                status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Manejar otras excepciones si es necesario
            return Response({'error': f'Error en la autenticación: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutUsuario(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Elimia la session de un usuario


        :param request: token
        :return: {message: Token eliminado} o error de varios tipos
        """


        try:
            # obtiene el token
            token = request.auth
            token = Token.objects.filter(key=token).first()
            # valida que exista el token en base de datos
            if token:
                # obtiene el usuario del token
                user = token.user
                all_session = Session.objects.filter(expire_date__gte=datetime.datetime.now())
                if all_session.exists():
                    for session in all_session:
                        session_data = session.get_decoded()
                        if user.id == int(session_data.get('_auth_user_id')):
                            session.delete()
                # borra las sessiones, en caso de que las haya
                # borra el token
                token.delete()
                message = 'Token Eliminado'
                return Response({'message': message},
                                status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No se ha encontrado un usuario con estas credenciales'},
                                status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Error durante el logout: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Acción que solo puede ser realizada por usuarios autenticados
        return Response({'message': 'Acceso permitido a la vista protegida.'})
