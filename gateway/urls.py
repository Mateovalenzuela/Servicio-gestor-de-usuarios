from django.urls import path, include
from .views import GastosServiceView, DocsGastosServiceView

urlpatterns = [
    path('service_gastos/', GastosServiceView.as_view(), name='service_gastos'),
    path('service_gastos/docs/', DocsGastosServiceView.as_view(), name='docs_service_gastos')
]