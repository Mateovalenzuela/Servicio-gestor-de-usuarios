from django.test import TestCase
from rest_framework.utils.serializer_helpers import ReturnDict
from ..services.AuthenticationService import AuthenticationService
from ..models import Usuario


class TestAuthenticationSercive(TestCase):
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

        self.service = AuthenticationService()

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

    def test_login(self):
        """
        Caso de fallo: se proveen credenciales de usuario inexistente
        """
        response = self.service.login(
            password=self.valid_user_data['password'],
            email=self.valid_user_data['email']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)

        """
        Caso de exito: se proveen credenciales de un usuario valido
        """
        user = self.crear_usuario()
        response = self.service.login(
            password=self.valid_user_data['password'],
            email=self.valid_user_data['email']
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

        """
        Caso de fallo: se proveen credenciales totalmente invalidas 
        """
        response = self.service.login(
            password=10.6,
            email=True
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 500)
        self.assertIn('error', data)

        """
        Caso de fallo: se proveen credenciales totalmente invalidas 
        """
        response = self.service.login(
            password='fwefwfwfwef',
            email=False
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 400)

    def test_logout(self):
        """
        Caso de fallo: se provee un id inexistente en base de datos
        """
        id = 100
        response = self.service.logout(
            user_id=id
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de exito: se provee un id valido, pero que no inició sesión
        """
        user = self.crear_usuario()
        id = user.id
        response = self.service.logout(
            user_id=id
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)
        user.delete()

        """
        Caso de exito: se provee un id valido, pero que sí inició sesión
        """
        # Crea un usuario e inicia sesión
        user = self.crear_usuario()
        login_response = self.service.login(
            password=self.valid_user_data['password'],
            email=self.valid_user_data['email']
        )
        login_data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(login_response.status_code, 200)


        # logout de usuario
        id = user.id
        response = self.service.logout(
            user_id=id
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 200)

        """
        Caso de fallo: se provee un id totalmente invalido
        """
        id = 'wgfergewgewrge'
        response = self.service.logout(
            user_id=id
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)

        """
        Caso de fallo: se provee un id totalmente invalido
        """
        id = True
        response = self.service.logout(
            user_id=id
        )
        status = response.status_code
        data = response.data.get('data', response.data.get('detail'))
        self.assertEqual(status, 404)
