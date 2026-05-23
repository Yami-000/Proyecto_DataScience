import os
from pathlib import Path
from dotenv import load_dotenv

# Subimos 3 niveles para encontrar el .env en la raíz
ruta_env = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=ruta_env)

api_key = os.getenv('RIOT_API_KEY')

if not api_key:
    raise RuntimeError(f'RIOT_API_KEY debe estar definida en .env')

SETTINGS = {
    "API_KEY": api_key,
    "REGION": "la2",
    "AMERICAS_REGION": "americas",
    
    # Parámetros de Extracción Aleatoria
    "QUEUE": "RANKED_SOLO_5x5",
    "TIER": "GOLD",
    "DIVISION": "I",
    
    # MATEMÁTICA DE EXTRACCIÓN: PLAYERS_LIMIT * MATCHES_PER_PLAYER = Total Partidas
    "PLAYERS_LIMIT": 100,     # Cuántos jugadores distintos de Oro I vamos a tomar
    "MATCHES_PER_PLAYER": 100    # Cuántas partidas recientes sacar de cada uno
}