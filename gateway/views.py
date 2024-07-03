import os
import requests
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework.decorators import action
from django.conf import settings
from .serializers import GatewaySerializer


# Create your views here.


class GastosServiceView(GenericAPIView):
    service_host = settings.HOST_GASTOS_SERVICE
    serializer_class = GatewaySerializer
    permission_classes = [IsAuthenticated]

    def validate_and_extract_path(self, request):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return None, Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        path = request.data['path']
        return path, None

    def get(self, request):
        path, error_response = self.validate_and_extract_path(request)
        if error_response:
            return error_response

        url = f'{self.service_host}{path}'
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response(f'Error en la solicitud: {str(e)}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        path, error_response = self.validate_and_extract_path(request)
        if error_response:
            return error_response

        request.data.pop('path')
        body = request.data
        url = f'{self.service_host}{path}'
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=body, headers=headers, verify=False)
            response.raise_for_status()
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response(f'Error en la solicitud: {str(e)}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        path, error_response = self.validate_and_extract_path(request)
        if error_response:
            return error_response

        request.data.pop('path')
        body = request.data
        url = f'{self.service_host}{path}'
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.put(url, json=body, headers=headers, verify=False)
            response.raise_for_status()
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response(f'Error en la solicitud: {str(e)}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        path, error_response = self.validate_and_extract_path(request)
        if error_response:
            return error_response

        request.data.pop('path')
        body = request.data
        url = f'{self.service_host}{path}'
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.delete(url, json=body, headers=headers, verify=False)
            response.raise_for_status()
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response(f'Error en la solicitud: {str(e)}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocsGastosServiceView(GenericAPIView):
    service_host = settings.HOST_GASTOS_SERVICE

    def get(self, request):

        url = f'{self.service_host}swagger/v1/swagger.json'
        try:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, verify=False)
            response.raise_for_status()
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud a {url}: {str(e)}")
            return Response(f'Error en la solicitud: {str(e)}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
