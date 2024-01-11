from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'BLACKLIST_ENABLED': True,  # Habilitar la blacklist,
    'SIGNING_KEY': os.getenv('JWT_SIGNING_KEY'),
}