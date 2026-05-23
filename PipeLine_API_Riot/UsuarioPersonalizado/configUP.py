# configUP.py
import os
from pathlib import Path
from dotenv import load_dotenv

ruta_env = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=ruta_env)

api_key = os.getenv('RIOT_API_KEY')

if not api_key:
    raise RuntimeError('RIOT_API_KEY debe estar definida en el archivo .env')

TARGET_NAME = os.getenv('TARGET_NAME')
TARGET_TAG = os.getenv('TARGET_TAG')

if not TARGET_NAME or not TARGET_TAG:
    raise RuntimeError('TARGET_NAME y TARGET_TAG deben estar definidas en el archivo .env')

SETTINGS = {
    "API_KEY": api_key,
    "REGION": "la2",
    "AMERICAS_REGION": "americas",  # ACCOUNT-V1 y MATCH-V5 usan regiones geográficas grandes
    "MODALIDAD": "RANKED_SOLO_5x5",
    "NUMBER_MATCHES": 1,
    "NAME_PLAYER": TARGET_NAME.strip(),
    "TAG_PLAYER": TARGET_TAG.strip(),
    "TIER": "DIAMOND",
    "DIVISION": "I",
    "PLAYERS_LIMIT": 10,# Para obtener PUUIDs de la liga (si se usara ese modo)
}