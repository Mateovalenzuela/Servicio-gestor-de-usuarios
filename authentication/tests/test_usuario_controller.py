from django.test import TestCase, Client
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict
from ..controllers.UsuarioController import UsuarioController
from ..models import Usuario


class TestUsuarioController(TestCase):

    def setUp(self):
        self.valid_user_data = {
            'username': 'test10',
            'email': 'test@email.com',
            'password': 'test1234'
        }

        self.controller = UsuarioController()

    def crear_usuario(self):
        # crea un usuario
        user = Usuario.objects.create_user(
            username=self.valid_user_data['username'],
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        user.save()
        return user

    def get_user(self, id):
        user = Usuario.objects.get(id=id, is_active=True)
        return user

    def test_get_object_user(self):

        """
        Caso de fallo: obtener un usuario con base de datos vacia
        :return: none
        """
        response = self.controller.get_object_user(1)
        self.assertEqual(response, None)


        """
        Caso de exito: obtener un usuario con id valido
        """
        user = self.crear_usuario()
        response = self.controller.get_object_user(1)
        self.assertEqual(response.id, user.id)

        """
        Caso de fallo: id inexistente
        """
        response = self.controller.get_object_user(100)
        self.assertEqual(response, None)

        """
        Caso de exito: id de tipo char
        """
        id = '1'
        with self.assertRaises(Exception):
            response = self.controller.get_object_user(id)

        """
        Caso de Fallo: id totalmente extraño de tipo string, lanza una excepcion
        """
        id = 'id_invalido'
        with self.assertRaises(Exception):
            self.controller.get_object_user(id)

    def test_list_all_users(self):
        """
        Caso de fallo: no hay usuarios en base de datos
        :return:
        """

        _, response = self.controller.list_all_users()
        self.assertEqual(_, 200)
        self.assertEqual(len(response), 0)
        self.assertTrue(isinstance(response, (list, ReturnList)))  # Ajuste aquí
        self.assertEqual(response, [])  # Verificar que la lista esté vacía

        """
        Caso de exito: obtener una lista de usuarios
        :return:
        """
        user = self.crear_usuario()
        _, response = self.controller.list_all_users()
        self.assertEqual(_, 200)
        self.assertTrue(isinstance(response, (list, ReturnList)))  # Ajuste aquí
        self.assertEqual(len(response), 1)  # Verificar que la lista tenga un elemento
        self.assertEqual(response[0]['username'], 'test10')  # Verificar el contenido del usuario

    def test_list_one_user(self):
        """
        Caso de fallo: no hay usuarios en base de datos
        :return:
        """
        id = 1
        _, response = self.controller.list_one_user(id)
        self.assertEqual(_, 404)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))


        """
        Caso de exito: obtener un usuario en formato dict
        """
        user = self.crear_usuario()
        id = user.id
        _, response = self.controller.list_one_user(id)
        self.assertEqual(_, 200)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))

        """
        Caso de fallo: id en formato str
        """
        id = str(user.id)
        _, response = self.controller.list_one_user(id)
        print(response)
        self.assertEqual(_, 500)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))

        """
        Caso de fallo: id valido pero inexistente
        """
        id = 100
        _, response = self.controller.list_one_user(id)
        self.assertEqual(_, 404)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))

        """
        Caso de fallo: id invalido, en formato str
        """
        id = 'id_invalido'
        _, response = self.controller.list_one_user(id)
        self.assertEqual(_, 500)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))

    def test_create_user(self):
        """
        Caso de exito: crear un usuario con datos validos
        :return:
        """
        _, response = self.controller.create_user(
            username=self.valid_user_data['username'],
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        self.assertEqual(_, 200)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))

        """
        Caso de fallo: username invalido
        """
        _, response = self.controller.create_user(
            username='I',
            email='email@valido.com',
            password='password123'
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('username', response)

        """
        Caso de fallo: password invalido
        """
        _, response = self.controller.create_user(
            username='username',
            email='email1@valido.com',
            password='pass'
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('password', response)

        """
        Caso de fallo: email invalido
        """
        _, response = self.controller.create_user(
            username='username2',
            email='emailInvalido.com.@.valido.com',
            password='password123'
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('email', response)

        """
        Caso de fallo: datos incompletos
        """
        _, response = self.controller.create_user(
            username=None,
            email=None,
            password=None
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('username', response)
        self.assertIn('password', response)
        self.assertIn('email', response)

        """
        Caso de fallo: datos incompleto, username
        """
        _, response = self.controller.create_user(
            username=None,
            email='valid.email@gmail.com',
            password='password111'
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('username', response)

        """
        Caso de fallo: datos incompletos, email
        """
        _, response = self.controller.create_user(
            username='user1212',
            email=None,
            password='password111'
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('email', response)

        """
        Caso de fallo: datos incompletos, password
        """
        _, response = self.controller.create_user(
            username='user5050',
            email='email@email.com',
            password=None
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('password', response)

        """
        Caso de fallo: datos repetidos, username, ya existe un usuario con este username
        """
        _, response = self.controller.create_user(
            username=self.valid_user_data['username'],
            email='email10@gmail.com',
            password='passs1234'
        )
        print(response)
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('username', response)

        """
        Caso de fallo: datos repetidos, email, ya existe un usuario con este email
        """
        _, response = self.controller.create_user(
            username='user777',
            email=self.valid_user_data['email'],
            password='pass34555'
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('email', response)

        """
        Caso de fallo: datos repetidos, username y email
        """
        _, response = self.controller.create_user(
            username=self.valid_user_data['username'],
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('username', response)
        self.assertIn('email', response)

        """
            Caso de fallo: parametros invalidos
        """
        _, response = self.controller.create_user(
            username=100,
            email=True,
            password=5.5
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('username', response)
        self.assertIn('email', response)
        self.assertIn('password', response)

    def test_set_password_user(self):
        """
        Caso de fallo: set password a un usuario que no existe en base de datos
        """
        _, response = self.controller.set_password_user(
            id=100,
            password='password',
            password2='password'
        )
        print(response)
        self.assertEqual(_, 404)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de exito: set password a un usuario valido
        """
        user = self.crear_usuario()
        id = user.id
        password = 'password'
        _, response = self.controller.set_password_user(
            id=id,
            password=password,
            password2=password
        )
        self.assertEqual(_, 200)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('message', response)
        user = self.get_user(id)
        self.assertTrue(user.check_password(password))

        """
        Caso de fallo: set password con id valido pero passwords distintos
        """

        id = user.id
        password = 'password'
        _, response = self.controller.set_password_user(
            id=id,
            password=password,
            password2='password distinto'
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('password', response)

        """
        Caso de fallo: set password con id valido pero passwords invalidos
        """

        id = user.id
        password = 'pass'
        _, response = self.controller.set_password_user(
            id=id,
            password=password,
            password2=password
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('password', response)

        """
        Caso de fallo: set password con id invalido en string
        """

        id = 'user.id'
        password = 'password'
        _, response = self.controller.set_password_user(
            id=id,
            password=password,
            password2=password
        )
        print(response)
        self.assertEqual(_, 500)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de fallo: set password con datos totalmente invalidos
        """

        id = '1'
        password = 'password'
        _, response = self.controller.set_password_user(
            id=id,
            password=10,
            password2=True
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))

    def test_update_email_user(self):
        """
        Caso de fallo: update un email de un usuario inexistente en base de datos
        :return:
        """

        _, response = self.controller.update_email_user(
            id=1,
            email='email@test.com',
            password=self.valid_user_data['password']
        )
        self.assertEqual(_, 404)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de exito: update un email de un usuario valido
        """
        user = self.crear_usuario()
        id = user.id
        email = 'nuevo_email@test.com'
        _, response = self.controller.update_email_user(
            id=id,
            email=email,
            password=self.valid_user_data['password']
        )
        self.assertEqual(_, 200)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('message', response)
        user = self.get_user(id)
        self.assertEqual(email, user.email)

        """
        Caso de fallo: update un email con contraseña incorrecta
        """
        _, response = self.controller.update_email_user(
            id=id,
            email=self.valid_user_data['email'],
            password='password_incorrecta_1'
        )
        self.assertEqual(_, 401)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de fallo, no se envia una contraseña del usuario
        """
        _, response = self.controller.update_email_user(
            id=id,
            email=self.valid_user_data['email'],
            password=None
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('password', response)

        """
        Caso de fallo, email nuevo invalido
        """
        email_nuevo = 'invalid_email@,com'
        _, response = self.controller.update_email_user(
            id=id,
            email=email_nuevo,
            password=self.valid_user_data['password']
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('email', response)

        """
        Caso de fallo, se actualiza el email de un usuario no existente
        """

        _, response = self.controller.update_email_user(
            id=100,
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        self.assertEqual(_, 404)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de fallo, datos totalmente invlaidos
        """
        _, response = self.controller.update_email_user(
            id='invalid_id',
            email=33,
            password=False
        )
        print(response)
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('email', response)
        self.assertIn('password', response)

    def test_update_username_user(self):
        """
        Caso de fallo, se intenta actualizar un username de un usuario con base de datos vacia
        """
        nuevo_username_valido = 'messi_10'
        _, response = self.controller.update_username_user(
            id=1,
            username=nuevo_username_valido
        )
        self.assertEqual(_, 404)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de exito, se actualiza un usuario existente con datos validos
        """
        usuario_nuevo = self.crear_usuario()
        id = usuario_nuevo.id
        _, response = self.controller.update_username_user(
            id=id,
            username=nuevo_username_valido,
        )
        self.assertEqual(_, 200)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('message', response)
        self.assertEqual(nuevo_username_valido, self.get_user(id).username)

        """
        Caso de fallo, se actualiza un usuario existente con datos invalidos
        """
        username_invalido = 'messi@10'
        id = usuario_nuevo.id
        _, response = self.controller.update_username_user(
            id=id,
            username=username_invalido,
        )
        self.assertEqual(_, 400)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('username', response)

        """
        Caso de fallo, id invalido
        """
        nuevo_username_valido += '10'
        id = usuario_nuevo.id
        _, response = self.controller.update_username_user(
            id=100,
            username=nuevo_username_valido,
        )
        print(response)
        self.assertEqual(_, 404)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de fallo, datos totalmente invlaidos
        """
        username_invalido = 'usuario_nuevo_id'
        id = 'usuario_nuevo.id'
        _, response = self.controller.update_username_user(
            id=id,
            username=username_invalido,
        )
        self.assertEqual(_, 500)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

    def test_delete_user(self):
        """
        Caso de fallo, se elimina un usuario inexistente
        """
        id = 100
        _, response = self.controller.delete_user(
            id=id,
        )
        self.assertEqual(_, 404)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        """
        Caso de fallo, se elimina un usuario existente
        """
        usuario_nuevo = self.crear_usuario()
        self.assertTrue(usuario_nuevo.is_active)
        id = usuario_nuevo.id
        _, response = self.controller.delete_user(
            id=id,
        )
        self.assertEqual(_, 200)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('message', response)
        with self.assertRaises(Exception):
            self.get_user(id)

        user = Usuario.objects.get(id=id)
        self.assertFalse(user.is_active)

        """
        Caso de fallo, se elimina un usuario ya eliminado
        """
        id = usuario_nuevo.id
        _, response = self.controller.delete_user(
            id=id,
        )
        self.assertEqual(_, 404)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)

        with self.assertRaises(Exception):
            self.get_user(id)
        user = Usuario.objects.get(id=id)
        self.assertFalse(user.is_active)

        """
        Caso de fallo, id totalmente invalido
        """
        id = 'usuario_nuevo.id'
        _, response = self.controller.delete_user(
            id=id,
        )
        self.assertEqual(_, 500)
        self.assertTrue(isinstance(response, (dict, ReturnDict)))
        self.assertIn('error', response)














    