# riot_engineUP.py
from riotwatcher import LolWatcher, RiotWatcher, ApiError
from configUP import SETTINGS
import time

lol_watcher = LolWatcher(SETTINGS["API_KEY"])       # Para MATCH-V5 y LEAGUE-V4
riot_account_watcher = RiotWatcher(SETTINGS["API_KEY"]) # Para ACCOUNT-V1 (Riot IDs globales)

region = SETTINGS["REGION"]
americas_region = SETTINGS["AMERICAS_REGION"]

def get_league_players():
    try:
        league_data = lol_watcher.league.entries(region, SETTINGS["MODALIDAD"], SETTINGS["TIER"], SETTINGS["DIVISION"])
        
        if not league_data:
            print("No se encontraron datos.")
            return []

        # Extraemos el PUUID directamente
        puuids = [player.get('puuid') for player in league_data[:SETTINGS["PLAYERS_LIMIT"]]]
        return [p for p in puuids if p is not None]

    except ApiError as err:
        print(f"Error en LEAGUE-V4: {err}")
        return []
    pass

def get_puuid_from_summoner(summoner_id):
    """Convierte summonerId en puuid usando SUMMONER-V4."""
    try:
        user_data = lol_watcher.summoner.by_id(region, summoner_id)
        return user_data['puuid']
    except ApiError as err:
        print(f"Error en SUMMONER-V4: {err}")
        return None

def get_matches_data(puuid):
    """Obtiene el JSON completo de las partidas usando MATCH-V5."""
    match_details = []
    try:
        # Obtiene lista de IDs de partidas
        match_ids = lol_watcher.match.matchlist_by_puuid(region, puuid, count=SETTINGS["NUMBER_MATCHES"])
        
        for m_id in match_ids:
            # Descarga el detalle de cada partida
            data = lol_watcher.match.by_id(region, m_id)
            match_details.append(data)
            # Pequeño delay para respetar el Rate Limit de desarrollo
            time.sleep(1.2) 
        return match_details
    except ApiError as err:
        print(f"Error en MATCH-V5: {err}")
        return []

def get_puuid_by_riot_id(game_name, tag_line):
    """Convierte Nombre#Tag en puuid usando la API global de cuentas de Riot."""
    try:
        # Aquí usamos riot_account_watcher en lugar de lol_watcher
        account_data = riot_account_watcher.account.by_riot_id(americas_region, game_name, tag_line)
        return account_data['puuid']
    except ApiError as err:
        print(f"Error en ACCOUNT-V1 para {game_name}#{tag_line}: {err}")
        return None

def get_matches_data(puuid, count):
    """Obtiene el detalle de partidas."""
    match_details = []
    try:
        # Aquí usamos lol_watcher
        match_ids = lol_watcher.match.matchlist_by_puuid(americas_region, puuid, count=count)
        if not match_ids:
            print(f"get_matches_data: no se encontraron match IDs para puuid={puuid} en region={americas_region}")
        else:
            print(f"get_matches_data: encontrado {len(match_ids)} match IDs (muestra 5): {match_ids[:5]}")
        
        for m_id in match_ids:
            attempts = 0
            while attempts < 3:
                try:
                    # Y aquí también usamos lol_watcher
                    data = lol_watcher.match.by_id(americas_region, m_id)
                    match_details.append(data)
                    break
                except ApiError as err:
                    attempts += 1
                    err_str = str(err)
                    # Si es 429, esperar más antes de reintentar
                    if '429' in err_str:
                        wait = 1.5 * attempts
                        print(f"429 recibido para {m_id}, esperando {wait}s y reintentando (intento {attempts})")
                        time.sleep(wait)
                        continue
                    else:
                        print(f"Warning: fallo al descargar match {m_id}: {err} — se omite")
                        break
            time.sleep(1.2) # Respetar Rate Limit
        return match_details
    except ApiError as err:
        print(f"Error en MATCH-V5: {err}")
        return []