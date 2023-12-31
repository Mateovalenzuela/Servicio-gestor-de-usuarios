from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import permissions
from rest_framework.permissions import AllowAny, IsAuthenticated


class LoginAndIsOwnerMixin(permissions.BasePermission):
    """
    Permite el acceso solo a los usuarios autenticados con su propio token.
    """

    def has_permission(self, request, view):
        # Verificar si el usuario está autenticado


        if request.user.is_authenticated:
            # Obtener el identificador de la URL
            url_user_id = view.kwargs.get('pk')

            # Verificar si el identificador de la URL coincide con el del usuario autenticado
            return str(request.user.id) == url_user_id

        return False
