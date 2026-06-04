from riotwatcher import LolWatcher, RiotWatcher, ApiError
from .configRandom import SETTINGS
import time

lol = LolWatcher(SETTINGS["API_KEY"])
riot = RiotWatcher(SETTINGS["API_KEY"])

def get_league_entries(queue, tier, division):
    """Obtiene lista de jugadores de una liga específica."""
    try:
        return lol.league.entries(SETTINGS["REGION"], queue, tier, division)
    except ApiError as err:
        print(f"Error LEAGUE-V4: {err}")
        return []

def get_puuid_by_summoner_id(summoner_id):
    """Convierte summonerId antiguo a PUUID."""
    try:
        return lol.summoner.by_id(SETTINGS["REGION"], summoner_id)['puuid']
    except ApiError as err:
        print(f"Error SUMMONER-V4: {err}")
        return None

def get_matches_data(puuid, count):
    """Obtiene datos completos de partidas con reintentos ante rate limits."""
    matches = []
    try:
        match_ids = lol.match.matchlist_by_puuid(SETTINGS["AMERICAS_REGION"], puuid, count=count)
        
        for m_id in match_ids:
            attempts = 0
            while attempts < 3:
                try:
                    data = lol.match.by_id(SETTINGS["AMERICAS_REGION"], m_id)
                    matches.append(data)
                    break
                except ApiError as err:
                    attempts += 1
                    if '429' in str(err):
                        wait = 2.0 * attempts
                        print(f"  Rate limit en {m_id}. Esperando {wait}s...")
                        time.sleep(wait)
                    else:
                        break
            time.sleep(1.2)
        return matches
    except ApiError as err:
        print(f"Error MATCH-V5: {err}")
        return []