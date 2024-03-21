import os
from datetime import timedelta
from dotenv import load_dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

load_dotenv()


# Función para generar una clave RSA y guardarla en un archivo PEM
def generate_rsa_key():
    try:
        # Generar un par de claves (clave privada y pública) para RSA
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        with open('private.pem', 'wb') as private_file, open('public.pem', 'wb') as public_file:
            private_file.write(private_pem)
            public_file.write(public_pem)

    except Exception as e:
        raise Exception("Error al generar las claves rsa")


# Definir las rutas de los archivos de claves
SIGNING_KEY_FILE = os.getenv('SIGNING_KEY_NAME_FILE', 'private.pem')
VERIFYING_KEY_FILE = os.getenv('VERIFYING_KEY_NAME_FILE', 'public.pem')

# Generar las claves si no existen
if not os.path.exists(SIGNING_KEY_FILE) or not os.path.exists(VERIFYING_KEY_FILE):
    generate_rsa_key()

# Configuraciones de Simple JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'BLACKLIST_ENABLED': True,
    'SIGNING_KEY': open(SIGNING_KEY_FILE, 'rb').read(),
    'VERIFYING_KEY': open(VERIFYING_KEY_FILE, 'rb').read(),
    'ALGORITHM': 'RS256',
}
