from rest_framework.response import Response
from rest_framework import status


class SuccessResponse:
    @staticmethod
    def ok(data=None, message=None):
        return Response({'status': 'success', 'data': data, 'message': message}, status=status.HTTP_200_OK)

    @staticmethod
    def created(data=None, message=None):
        return Response({'status': 'success', 'data': data, 'message': message}, status=status.HTTP_201_CREATED)

    @staticmethod
    def no_content():
        return Response({'status': 'success', 'data': 'No content'}, status=status.HTTP_204_NO_CONTENT)


class ErrorResponse:
    @staticmethod
    def bad_request(errors=None, message=None):
        return Response({'status': 'error', 'detail': errors, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def credentials_not_found():
        return Response({'status': 'error', 'detail': 'Usuario o contraseña incorrectos'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def unauthorized():
        return Response({'status': 'error', 'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def forbidden():
        return Response({'status': 'error', 'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    @staticmethod
    def not_found():
        return Response({'status': 'error', 'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def user_not_found():
        return Response({'status': 'error', 'detail': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def perfil_not_found():
        return Response({'status': 'error', 'detail': 'Usuario sin datos de perfil'}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def conflict():
        return Response({'status': 'error', 'detail': 'Conflict'}, status=status.HTTP_409_CONFLICT)

    @staticmethod
    def server_error():
        return Response({'status': 'error', 'detail': 'Internal server error'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
