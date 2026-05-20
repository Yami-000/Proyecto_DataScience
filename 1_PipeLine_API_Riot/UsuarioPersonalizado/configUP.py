# configUP.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

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
    "QUEUE": "RANKED_SOLO_5x5",
    "MATCHES_PER_PLAYER_SPECIFIC": 10,
    "TARGET_NAME": TARGET_NAME.strip(),
    "TARGET_TAG": TARGET_TAG.strip(),
}