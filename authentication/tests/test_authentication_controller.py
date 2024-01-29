from django.test import TestCase
from rest_framework.utils.serializer_helpers import ReturnDict
from ..controllers.AuthenticationController import AuthenticationController
from ..models import Usuario


class TestAuthenticationController(TestCase):
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

        self.controller = AuthenticationController()

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
        :return:
        """

        _, response = self.controller.login(
            password=self.valid_user_data['password'],
            email=self.valid_user_data['email']
        )
        print(response)
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de exito: se proveen credenciales de un usuario valido
        """
        user = self.crear_usuario()
        _, response = self.controller.login(
            password=self.valid_user_data['password'],
            email=self.valid_user_data['email']
        )
        print(response)
        self.assertEqual(_, 200)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('access_token', response)
        self.assertIn('refresh_token', response)

        """
        Caso de fallo: se proveen credenciales totalmente invalidas 
        """
        _, response = self.controller.login(
            password=10.6,
            email=True
        )
        print(response)
        self.assertEqual(_, 500)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de fallo: se proveen credenciales totalmente invalidas 
        """
        _, response = self.controller.login(
            password='fwefwfwfwef',
            email=False
        )
        print(response)
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

    def test_logout(self):
        """
        Caso de fallo: se provee un id inexistente en base de datos
        :return:
        """
        id = 100
        _, response = self.controller.logout(
            user_id=id
        )
        print(response)
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de exito: se provee un id valido, pero que no inicio sesion
        """
        user = self.crear_usuario()
        id = user.id
        _, response = self.controller.logout(
            user_id=id
        )
        print(response)
        self.assertEqual(_, 200)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('message', response)
        user.delete()

        """
        Caso de exito: se provee un id valido, pero que si inicio sesion
        """
        # Crea un usuario e inicia sesion
        user = self.crear_usuario()
        _, response = self.controller.login(
            password=self.valid_user_data['password'],
            email=self.valid_user_data['email']
        )
        self.assertEqual(_, 200)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('access_token', response)
        self.assertIn('refresh_token', response)
        #####################
        # logout de usuario
        id = user.id
        _, response = self.controller.logout(
            user_id=id
        )
        print(response)
        self.assertEqual(_, 200)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('message', response)

        """
        Caso de fallo: se provee un id totalmente invalido
        """
        id = 'wgfergewgewrge'
        _, response = self.controller.logout(
            user_id=id
        )
        print(response)
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de fallo: se provee un id totalmente invalido
        """
        id = True
        _, response = self.controller.logout(
            user_id=id
        )
        print(response)
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)
