import datetime
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import ListarUsuarioSerializer, CrearUsuarioSerializer, ActualizarUsuarioSerializer, \
    LoginUsuarioSerializer


# Create your views here.

def get_usuario(id):

    Usuario = get_user_model()
    try:
        # Intenta obtener el usuario por ID que esté activo
        usuario = Usuario.objects.get(id=id, is_active=True, is_superuser=False)
        return usuario

    except Exception:
        # Manejar otras excepciones
        return None


class ListarUsuario(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = []

    def get(self, request, id=None):

        try:
            # Captura el modelo de usuarios actual
            User = get_user_model()

            if id is not None:
                # Obtener un solo usuario por ID
                usuario = get_usuario(id)

                if usuario:
                    serializer = ListarUsuarioSerializer(usuario)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Listar todos los usuarios
                usuarios = User.objects.filter(is_active=True, is_superuser=False).all()
                serializer = ListarUsuarioSerializer(usuarios, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:

            return Response({"error": f'Error al listar usuarios: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CrearUsuario(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = []

    def post(self, request):
        # Deserializar la solicitud para obtener los datos del nuevo usuario
        serializer = CrearUsuarioSerializer(data=request.data)

        if serializer.is_valid():
            # Guardar el nuevo usuario en la base de datos
            serializer.save()

            # Devolver una respuesta exitosa
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Devolver una respuesta con errores de validación si los datos no son válidos
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModificarUsuario(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = []

    def put(self, request, id):
        # Obtener el objeto del usuario que se va a actualizar
        usuario = get_usuario(id)

        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Deserializar la solicitud para obtener los datos actualizados del usuario
        serializer = ActualizarUsuarioSerializer(usuario, data=request.data)

        try:
            if serializer.is_valid():
                # Guardar los datos actualizados en la base de datos
                serializer.save()
                # Devolver una respuesta exitosa
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Error al modificar usuario: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        # Obtener el objeto del usuario que se va a "eliminar"
        usuario = get_usuario(id)

        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # "Desactivar" el usuario estableciendo is_active en False
            usuario.is_active = False
            usuario.save()
            return Response({"mensaje": "Usuario eliminado correctamente"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Error al desactivar usuario: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginUsuario(ObtainAuthToken):
    authentication_classes = [TokenAuthentication]
    permission_classes = []

    def post(self, request, **kwargs):
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
