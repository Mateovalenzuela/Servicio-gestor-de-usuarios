from rest_framework import serializers


class GatewaySerializer(serializers.Serializer):
    path = serializers.CharField(required=True)

    def validate_path(self, value):
        """
        Verifica que el campo 'path' comience con 'service_gastos/'.
        """

        services = ['api/']

        if not value.startswith(services[0]):
            raise serializers.ValidationError(f"El campo 'path' debe comenzar con {services[0]}")
        return value
