from django.test import TestCase
from rest_framework.utils.serializer_helpers import ReturnDict
from ..services.JWTService import JWTService
from ..models import Usuario


class TestJWTService(TestCase):
    def setUp(self):

        self.valid_user_data = {
            'username': 'test10',
            'email': 'test@email.com',
            'password': 'test1234'
        }

        self.valid_user_data2 = {
            'username': 'test_user',
            'email': 'test_user@gmail.com',
            'password': 'test1234'
        }

        self.service = JWTService()

    def crear_usuario(self):
        # crea un usuario
        user = Usuario.objects.create_user(
            username=self.valid_user_data['username'],
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        user.save()
        return user

    def crear_usuario2(self):
        # crea un usuario
        user = Usuario.objects.create_user(
            username=self.valid_user_data2['username'],
            email=self.valid_user_data2['email'],
            password=self.valid_user_data2['password']
        )
        user.save()
        return user

    def get_user(self, id):
        user = Usuario.objects.get(id=id, is_active=True)
        return user

    def test_create_token_for_user(self):
        """
        Caso de fallo: se proveen datos validos pero que no existen en base de datos
        """
        response = self.service.create_token_for_user(
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 500)
        self.assertIn('error', data)

        """
        Caso de exito: se proveen datos validos de un usuario valido
        """
        user = self.crear_usuario()
        response = self.service.create_token_for_user(
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

        """
        Caso de fallo: se proveen datos invalidos
        """
        response = self.service.create_token_for_user(
            email=True,
            password=False
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)
        self.assertIn('password', data)
        self.assertIn('email', data)

        """
        Caso de fallo: se proveen datos invalidos
        """
        response = self.service.create_token_for_user(
            email='True',
            password='False'
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 500)
        self.assertIn('error', data)

        """
        Caso de fallo: se proveen datos invalidos
        """
        response = self.service.create_token_for_user(
            email=10.43,
            password=7.55
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 500)
        self.assertIn('error', data)
    def test_validate_token(self):
        """
        Caso de fallo: se provee un token totalmente invalido
        """
        token = 'token_invalido'
        response = self.service.validate_token(token)
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)

        """
        Caso de fallo: se provee un token totalmente invalido
        """
        token = 30.5
        response = self.service.validate_token(token)
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)

        """
        Caso de exito: se provee un token valido
        """
        user = self.crear_usuario()
        response = self.service.create_token_for_user(
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        data = response.data.get('data', response.data.get('detail'))
        token = data.get('access_token')
        response = self.service.validate_token(token)
        status = response.status_code
        self.assertEqual(status, 200)

        """
        Caso de fallo: token expirado
        """
        token_expirado = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA2NTAzMDUyLCJpYXQiOjE3MDY1MDMwNTEsImp0aSI6ImVmZDYwM2E5MTcxZjQ5OGI5NjM2ZDRhNzNmNzU1ZWQyIiwidXNlcl9pZCI6MX0.RPj-VR9THd9JdQHbjLfV_t4PsX6lBuFE5fQGd_bU3DpH58au3FjUWmdtjboGkPnUWqfWlZVGo4Xj4qJDHXCpf9-oScUklEc4MHJDPoIOe2NIJTm61XhwDeKe0Q3uDYhx-283K6gHiDHSy-iA42rzIoZ0MhwqKVV0N8STOd3lrSc'
        response = self.service.validate_token(token_expirado)
        status = response.status_code
        self.assertEqual(status, 400)
