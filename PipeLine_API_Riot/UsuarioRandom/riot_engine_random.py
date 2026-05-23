from riotwatcher import LolWatcher, RiotWatcher, ApiError
from .configRandom import SETTINGS
import time

lol_watcher = LolWatcher(SETTINGS["API_KEY"])
riot_account_watcher = RiotWatcher(SETTINGS["API_KEY"])

region = SETTINGS["REGION"]
americas_region = SETTINGS["AMERICAS_REGION"]

def get_league_entries(queue, tier, division):
    """Obtiene una lista de jugadores (entries) de una liga específica."""
    try:
        entries = lol_watcher.league.entries(region, queue, tier, division)
        return entries
    except ApiError as err:
        print(f"Error en LEAGUE-V4: {err}")
        return []

def get_puuid_by_summoner_id(summoner_id):
    """Convierte el summonerId de la liga en el PUUID necesario para descargar partidas."""
    try:
        summoner_data = lol_watcher.summoner.by_id(region, summoner_id)
        return summoner_data['puuid']
    except ApiError as err:
        print(f"Error en SUMMONER-V4 (ID: {summoner_id}): {err}")
        return None

def get_matches_data(puuid, count):
    """Obtiene el JSON completo de las partidas usando MATCH-V5 con reintentos para evitar baneos."""
    match_details = []
    try:
        match_ids = lol_watcher.match.matchlist_by_puuid(americas_region, puuid, count=count)
        
        for m_id in match_ids:
            attempts = 0
            while attempts < 3:
                try:
                    data = lol_watcher.match.by_id(americas_region, m_id)
                    match_details.append(data)
                    break
                except ApiError as err:
                    attempts += 1
                    if '429' in str(err):
                        wait = 2.0 * attempts # Espera exponencial si Riot nos frena
                        print(f"⚠️ Límite de peticiones (429) en {m_id}. Pausa de {wait}s...")
                        time.sleep(wait)
                    else:
                        print(f"Error omitido al descargar {m_id}: {err}")
                        break
            time.sleep(1.2) # Respetar límite base por defecto
        return match_details
    except ApiError as err:
        print(f"Error en lista de MATCH-V5: {err}")
        return []