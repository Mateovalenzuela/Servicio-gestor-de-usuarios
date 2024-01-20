from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SIMPLE_JWT = {
    # Configuraciones
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'BLACKLIST_ENABLED': True,  # Habilitar la blacklist,
    # Firma y verificacion
    'SIGNING_KEY': open(os.getenv('SIGNING_KEY_NAME_FILE', ''), 'r').read(),
    'VERIFYING_KEY': open(os.getenv('VERIFYING_KEY_NAME_FILE', ''), 'r').read(),
    'ALGORITHM': os.getenv('ALGORITHM', ''),
}

