import os
from datetime import timedelta
from dotenv import load_dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

load_dotenv()


# Función para generar una clave RSA y guardarla en un archivo PEM
def generate_rsa_key(filename_private, filename_public):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Guardar la clave privada en un archivo PEM
    with open(filename_private, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Obtener la clave pública
    public_key = private_key.public_key()

    # Guardar la clave pública en un archivo PEM
    with open(filename_public, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))


# Definir las rutas de los archivos de claves
SIGNING_KEY_FILE = os.getenv('SIGNING_KEY_NAME_FILE', 'signing_key.pem')
VERIFYING_KEY_FILE = os.getenv('VERIFYING_KEY_NAME_FILE', 'verifying_key.pem')

# Generar las claves si no existen
if not os.path.exists(SIGNING_KEY_FILE) or not os.path.exists(VERIFYING_KEY_FILE):
    generate_rsa_key(SIGNING_KEY_FILE, VERIFYING_KEY_FILE)

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
