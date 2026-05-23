from .riot_engine_random import get_league_entries, get_puuid_by_summoner_id, get_matches_data
from .configRandom import SETTINGS
from pathlib import Path
import json
import time

def run_pipeline_random():
    all_matches_dataset = []
    
    tier = SETTINGS['TIER']
    div = SETTINGS['DIVISION']
    p_limit = SETTINGS['PLAYERS_LIMIT']
    m_limit = SETTINGS['MATCHES_PER_PLAYER']

    print(f"--- MODO LIGA: Buscando {p_limit} jugadores en {tier} {div} ---")
    
    # 1. Obtener la lista de la liga
    entries = get_league_entries(SETTINGS['QUEUE'], tier, div)
    if not entries:
        print("No se encontraron jugadores.")
        return

    target_entries = entries[:p_limit]
    
    print(f"Procesando {len(target_entries)} jugadores. Esto tomará varios minutos debido a los límites de la API...")

    # 2. Iterar sobre cada jugador de forma segura (Tolerancia a fallos)
    for idx, entry in enumerate(target_entries, 1):
        # Usamos .get() en lugar de [] para no romper el código si Riot quita llaves
        puuid = entry.get('puuid')
        summoner_id = entry.get('summonerId')
        
        # Riot ahora usa 'riotIdGameName' en lugar de 'summonerName'. Buscamos ambos.
        player_name = entry.get('riotIdGameName') or entry.get('summonerName') or f'Jugador_{idx}'
        
        print(f"\n[{idx}/{len(target_entries)}] Extrayendo a: {player_name}...")
        
        # 2.1 Obtener PUUID: Si la liga no lo trae directo, lo convertimos usando el Summoner ID antiguo
        if not puuid and summoner_id:
            puuid = get_puuid_by_summoner_id(summoner_id)
            time.sleep(1) # Pausa por hacer una llamada extra a SUMMONER-V4
            
        if not puuid:
            print(f" -> ⚠️ Saltando. No se encontró PUUID ni SummonerID válido para este jugador.")
            continue
            
        # 2.2 Descargar sus partidas
        player_matches = get_matches_data(puuid, m_limit)
        all_matches_dataset.extend(player_matches)
        
        print(f" -> {len(player_matches)} partidas guardadas.")

    # 3. Guardar el JSON gigante
    output_dir = Path(__file__).resolve().parent.parent
    output_path = output_dir / "dataset_random_gold.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_matches_dataset, f)

    print(f"\n--- ÉXITO: {len(all_matches_dataset)} partidas totales guardadas en: {output_path} ---")

if __name__ == "__main__":
    run_pipeline_random()