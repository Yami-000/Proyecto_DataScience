from riotwatcher import LolWatcher, ApiError
from .configRandom import SETTINGS
import time

lol = LolWatcher(SETTINGS["API_KEY"])

def _retry_request(callable_, *args, retries: int = 4, initial_wait: float = 1.0, backoff: float = 2.0, **kwargs):
    """Reintento genérico para peticiones Riot con backoff exponencial en 429."""
    attempt = 1
    while attempt <= retries:
        try:
            return callable_(*args, **kwargs)
        except ApiError as err:
            err_text = str(err)
            if '429' in err_text:
                wait = initial_wait * (backoff ** (attempt - 1))
                print(f"  Rate limit ({attempt}/{retries}). Esperando {wait:.1f}s...")
                time.sleep(wait)
                attempt += 1
                continue
            print(f"  Error Riot API: {err}")
            return None
    print(f"  Excedido reintentos para {callable_.__name__}")
    return None


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


def get_match_and_timeline(match_id):
    """Descarga el detalle de la partida y su timeline asociado."""
    match_data = _retry_request(lol.match.by_id, SETTINGS["AMERICAS_REGION"], match_id)
    if match_data is None:
        return None

    timeline_data = _retry_request(lol.match.timeline_by_match, SETTINGS["AMERICAS_REGION"], match_id)
    if timeline_data is None:
        print(f"  No se pudo obtener timeline para {match_id}")
        return None

    return {
        'match_id': match_id,
        'match': match_data,
        'timeline': timeline_data,
    }


def get_matches_data(puuid, count):
    """Obtiene match detail + timeline para cada partida de un jugador."""
    matches = []
    try:
        match_ids = lol.match.matchlist_by_puuid(SETTINGS["AMERICAS_REGION"], puuid, count=count)

        for m_id in match_ids:
            combined = get_match_and_timeline(m_id)
            if combined:
                matches.append(combined)
            time.sleep(1.4)
        return matches
    except ApiError as err:
        print(f"Error MATCH-V5: {err}")
        return []
