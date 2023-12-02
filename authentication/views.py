from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UsuarioSerializer, CustomTokenObtainPairSerializer


# Create your views here.

class UsuarioViewSet(GenericViewSet):
    model = get_user_model()
    # authentication_classes = []
    permission_classes = [AllowAny]

    serializer_class = UsuarioSerializer
    queryset = None

    def get_object(self, pk):
        return get_object_or_404(self.model, pk=pk, is_active=True, is_superuser=False)

    def get_queryset(self):
        if self.queryset is None:
            return self.model.objects.filter(is_active=True, is_superuser=False)
        return self.queryset

    def list(self, request):
        """
        Retorna un listado de todos los usuarios


        :param request:
        :return: Lista vacía o Lista con todos los usuarios
        """

        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        Retorna un usuario


        :param request:
        :param pk: int
        :return: El usuario (id, username, password, email, first_name, last_name) o error: usuario no encontrado
        """

        usuario = self.get_object(pk)
        if usuario:
            serializer = self.serializer_class(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        """
        Crea un usuario


        :param request: username, password, email, first_name, last_name.
        :return: message: usuario creado. o error en el/los campos.
        """

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Usuario creado'}, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'Error al registrarse',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Actualiza un usuario


        :param request: Todos opcionales, password, first_name, last_name
        :param pk: int
        :return: El usuario actualizado (id, username, password, email, first_name, last_name) o error: usuario no encontrado
        """

        usuario = self.get_object(pk)
        serializer = self.serializer_class(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Usuario Actualizado'}, status=status.HTTP_200_OK)
        return Response({
            'message': 'Error al actualizar el usuario',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Elimina un usuario


        :param request:
        :param pk: int
        :return: message, Usuario eliminado. O error: Usuario no encontrado.
        """

        updated_rows = not self.model.objects.filter(id=pk, is_active=True, is_superuser=False).update(is_active=False)
        if updated_rows == 1:
            Response({'message': 'Usuario eliminado'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class Login(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        user = authenticate(
            username=username,
            password=password
        )  # devuelve un bool si existe o no un usuario para esas credenciales
        if user:
            login_serializer = self.serializer_class(data=request.data)
            if login_serializer.is_valid():
                user_serializer = UsuarioSerializer(user)
                return Response({
                    'token': login_serializer.validated_data.get('access'),
                    'refresh-token': login_serializer.validated_data.get('refresh'),
                    'user': user_serializer.data,
                    'message': 'Inicio de Sesion Exitoso'
                }, status=status.HTTP_200_OK, content_type='application/json')

        return Response({'error': 'Contraseña o nombre de usuario incorrectos'}, status=status.HTTP_400_BAD_REQUEST,content_type='application/json')


class Logout(GenericAPIView):
    def post(self, request, *args, **kwargs):
        id = request.data.get('user', 0)
        user = UsuarioSerializer.Meta.model.objects.filter(id=id)
        if user.exists():
            RefreshToken.for_user(user.first())
            return Response({'message': 'Sesion cerrada correctamente'}, status=status.HTTP_200_OK)

        return Response({'error': 'No existe este usuario'}, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Acción que solo puede ser realizada por usuarios autenticados
        return Response({'message': 'Acceso permitido a la vista protegida.'})
