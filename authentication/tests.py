from django.test import TestCase
from django.contrib.auth.models import User


# Create your tests here.

class UsuarioTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='LeoMessi',
            first_name='Leo',
            last_name='Messi'

        )

        self.super_user = User.objects.create_superuser(
            username='Admin',
            password='adminPassword'
        )

        self.usuario_eliminado = User.objects.create_user(
            username='LuisSuarez',
            first_name='Luis',
            last_name='Suarez',
            is_active=False
        )

    def test_user_creation(self):
        self.assertIsInstance(self.user.id, int)
        self.assertEquals(self.user.is_staff, False)
        self.assertEquals(self.user.is_superuser, False)
        self.assertEquals(self.user.is_active, True)

    def test_superuser_creation(self):

        self.assertEquals(self.super_user.is_staff, True)
        self.assertEquals(self.super_user.is_superuser, True)
        self.assertEquals(self.super_user.is_active, True)

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'Leo Messi')

    def test_delete_user(self):
        self.assertIsInstance(self.usuario_eliminado.id, int)
        self.assertEquals(self.usuario_eliminado.is_staff, False)
        self.assertEquals(self.usuario_eliminado.is_superuser, False)
        self.assertEquals(self.usuario_eliminado.is_active, False)
