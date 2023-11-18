from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,
                                   HTTP_500_INTERNAL_SERVER_ERROR)
from django.contrib.auth import get_user_model
from .serializers import UsuarioSerializer


# Create your views here.

class ListarUsuario(APIView):

    def get(self, request):
        try:
            # captura el modelo de usuarios actual y los lista
            User = get_user_model()
            usuarios = User.objects.filter(is_active=True, is_superuser=False).all()

            # convierte usuarios a json
            serializer = UsuarioSerializer(usuarios, many=True)

            return Response(serializer.data, status=HTTP_200_OK)

        except Exception as e:
            # Manejar la excepción aquí, puedes imprimir un mensaje de error o retornar una respuesta de error.
            return Response({"error": f'Error al listar usuarios: {str(e)}'}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class CrearUsuario(APIView):

    def post(self, request):
        # Deserializar la solicitud para obtener los datos del nuevo usuario
        serializer = UsuarioSerializer(data=request.data)

        if serializer.is_valid():
            # Guardar el nuevo usuario en la base de datos
            serializer.save()

            # Devolver una respuesta exitosa
            return Response(serializer.data, status=HTTP_201_CREATED)

        # Devolver una respuesta con errores de validación si los datos no son válidos
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ModificarUsuario(APIView):

    def get_usuario(self, id):
        Usuario = get_user_model()

        try:
            # Intenta obtener el usuario por ID que esté activo
            usuario = Usuario.objects.get(id=id, is_active=True, is_superuser=False)
            return usuario
        except Usuario.DoesNotExist:
            return None
        except Exception as e:
            # Manejar otras excepciones de la base de datos
            return None

    def put(self, request, id):
        # Obtener el objeto del usuario que se va a actualizar
        usuario = self.get_usuario(id)

        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=HTTP_404_NOT_FOUND)

        # Deserializar la solicitud para obtener los datos actualizados del usuario
        serializer = UsuarioSerializer(usuario, data=request.data)

        try:
            if serializer.is_valid():
                # Guardar los datos actualizados en la base de datos
                serializer.save()
                # Devolver una respuesta exitosa
                return Response(serializer.data, status=HTTP_200_OK)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Error al modificar usuario: {str(e)}"}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        # Obtener el objeto del usuario que se va a "eliminar"
        usuario = self.get_usuario(id)

        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=HTTP_404_NOT_FOUND)

        try:
            # "Desactivar" el usuario estableciendo is_active en False
            usuario.is_active = False
            usuario.save()
            return Response({"mensaje": "Usuario eliminado correctamente"}, status=HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Error al desactivar usuario: {str(e)}"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class LoginUsuario(APIView):
    pass


class LogoutUsuario(APIView):
    pass
