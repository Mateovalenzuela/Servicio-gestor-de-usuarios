"""
URL configuration for djangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *
urlpatterns = [
    path('', ListarUsuario.as_view(), name='listar-usuarios'),
    path('registrar/', CrearUsuario.as_view(), name='registrar-usuario'),
    path('modificar/<int:id>', ModificarUsuario.as_view(), name='modificar-usuario'),
    path('login/', LoginUsuario.as_view(), name='login-usuario'),
    path('logout/', LogoutUsuario.as_view(), name='logout-usuario'),
    path('vista/', ProtectedView.as_view(), name='vista-protegida')
]
