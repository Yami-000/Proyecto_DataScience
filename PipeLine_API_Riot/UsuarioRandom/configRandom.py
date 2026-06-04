from pathlib import Path
from dotenv import dotenv_values

# Cargar solo RIOT_API_KEY desde .env sin inyectar variables de usuario.
ruta_env = Path(__file__).resolve().parent.parent.parent / '.env'
config = dotenv_values(dotenv_path=ruta_env)
api_key = config.get('RIOT_API_KEY')

if not api_key:
    raise RuntimeError('RIOT_API_KEY debe estar definida en .env')

SETTINGS = {
    "API_KEY": api_key,
    "REGION": "la2",
    "AMERICAS_REGION": "americas",
    
    # === FLUJO: Identificar jugadores → Descargar partidas → Extraer 10 jugadores/partida ===
    "QUEUE": "RANKED_SOLO_5x5",
    "TIER": "GOLD",
    "DIVISION": "I",
    
    # Paso 1: Identificar X jugadores únicos de Oro I
    "PLAYERS_LIMIT": 1,
    
    # Paso 2: Descargar Y partidas de cada jugador
    "MATCHES_PER_PLAYER": 1,
    
    # Total esperado: PLAYERS_LIMIT * MATCHES_PER_PLAYER = 10,000 partidas
    # Paso 3: De cada partida, extraer 10 jugadores → ~100,000 registros en dataset_playersXpartida.csv
}