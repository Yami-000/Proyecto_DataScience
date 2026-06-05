from .riot_engine_random import get_league_entries, get_puuid_by_summoner_id, get_matches_data
from .configRandom import SETTINGS
from pathlib import Path
import json
import time

def run_pipeline_random():
    """
    Flujo: 
    1. Obtener X jugadores de Oro I
    2. Descargar Y partidas de cada uno
    3. Guardar JSON con todas las partidas
    """
    all_matches = []
    
    tier = SETTINGS['TIER']
    div = SETTINGS['DIVISION']
    p_limit = SETTINGS['PLAYERS_LIMIT']
    m_limit = SETTINGS['MATCHES_PER_PLAYER']

    print(f"Paso 1: Buscando {p_limit} jugadores en {tier} {div}...")
    
    entries = get_league_entries(SETTINGS['QUEUE'], tier, div)
    if not entries:
        print("ERROR: No se encontraron jugadores.")
        return

    entries = entries[:p_limit]
    
    print(f"Paso 2: Descargando {m_limit} partidas de cada uno ({p_limit * m_limit} totales estimadas)...\n")

    for idx, entry in enumerate(entries, 1):
        puuid = entry.get('puuid')
        summoner_id = entry.get('summonerId')
        player_name = entry.get('riotIdGameName') or entry.get('summonerName') or f'Jugador_{idx}'
        
        if not puuid and summoner_id:
            puuid = get_puuid_by_summoner_id(summoner_id)
            time.sleep(1)
            
        if not puuid:
            print(f"[{idx}/{len(entries)}] {player_name}: SALTADO (sin PUUID)")
            continue
            
        matches = get_matches_data(puuid, m_limit)
        all_matches.extend(matches)
        
        print(f"[{idx}/{len(entries)}] {player_name}: {len(matches)} matches con timeline")

    output_path = Path(__file__).resolve().parent.parent / "dataset_random_gold_timeline.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_matches, f)

    print(f"\n✓ {len(all_matches)} partidas con timeline guardadas en: {output_path}")

if __name__ == "__main__":
    run_pipeline_random()