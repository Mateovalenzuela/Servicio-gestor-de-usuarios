
SWAGGER_SETTINGS = {
    'DOC_EXPANSION': 'none',
    "SECURITY_DEFINITIONS": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "scheme": "bearer",
                "bearerFormat": "jwt",
            }
    },
}
