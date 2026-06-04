from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

def load_matches(path: Path) -> List[Dict[str, Any]]:
    """Carga JSON de partidas."""
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

def extract_players_from_match(match: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrae los 10 jugadores de una partida con sus estadísticas.
    
    FLUJO: 1 partida → 10 jugadores + estadísticas
    
    Aquí es donde agregar nuevas variables para cada jugador:
    - match['info']['participants'][i] contiene datos individuales del jugador
    - match['info']['teams'] contiene datos del equipo
    - match['metadata'] contiene info de la partida
    """
    info = match.get('info', {})
    meta = match.get('metadata', {})
    game_duration = float(info.get('gameDuration', 0) or 0)

    # Datos de objetivos por equipo
    team_objs = {}
    for team in info.get('teams', []):
        t_id = team.get('teamId')
        def get_obj(obj_name, key):
            return team.get('objectives', {}).get(obj_name, {}).get(key, 0)
        team_objs[t_id] = {
            'first_blood': int(get_obj('champion', 'first')),
            'first_dragon': int(get_obj('dragon', 'first')),
            'first_tower': int(get_obj('tower', 'first')),
            'total_dragons': int(get_obj('dragon', 'kills')),
            'total_towers': int(get_obj('tower', 'kills')),
            'total_barons': int(get_obj('baron', 'kills')),
        }

    rows = []
    for p in info.get('participants', []) or []:
        team_id = p.get('teamId')
        challs = p.get('challenges', {})
        t_obj = team_objs.get(team_id, {})

        row = {
            'match_id': meta.get('matchId'),
            'platform_id': meta.get('platformId'),
            'game_creation': info.get('gameCreation'),
            'game_duration_s': game_duration,
            'game_duration_min': round(game_duration / 60.0, 2) if game_duration >= 0 else np.nan,
            'team_id': team_id,
            'match_win': int(p.get('win', False)),
            'participant_id': p.get('participantId'),
            
            # === IDENTIDAD DEL JUGADOR ===
            'summoner_name': p.get('summonerName') or p.get('riotIdGameName') or 'Unknown',
            'riot_id_game_name': p.get('riotIdGameName'),
            'riot_id_tagline': p.get('riotIdTagline'),
            'champion': p.get('championName', 'Unknown'),
            'team_position': p.get('teamPosition'),
            
            # === ESTADÍSTICAS DE COMBATE ===
            'kills': p.get('kills', 0) or 0,
            'deaths': p.get('deaths', 0) or 0,
            'assists': p.get('assists', 0) or 0,
            'gold_earned': p.get('goldEarned', 0) or 0,
            'vision_score': p.get('visionScore', 0) or 0,
            'total_damage_to_champions': p.get('totalDamageDealtToChampions', 0) or 0,
            'magic_damage_to_champions': p.get('magicDamageDealtToChampions', 0) or 0,
            'physical_damage_to_champions': p.get('physicalDamageDealtToChampions', 0) or 0,
            'total_minions_killed': p.get('totalMinionsKilled', 0) or 0,
            'neutral_minions_killed': p.get('neutralMinionsKilled', 0) or 0,
            'cs_total': (p.get('totalMinionsKilled', 0) or 0) + (p.get('neutralMinionsKilled', 0) or 0),
            'time_ccing_others': p.get('timeCCingOthers', 0) or 0,
            'total_time_spent_dead': p.get('totalTimeSpentDead', 0) or 0,
            
            # === MÉTRICAS PER-MINUTO ===
            'gold_per_min': challs.get('goldPerMinute') or np.nan,
            'vision_score_per_min': challs.get('visionScorePerMinute') or np.nan,
            'kda': challs.get('kda') or np.nan,
            'damage_per_minute': challs.get('damagePerMinute', 0) or 0,
            'damage_per_gold': challs.get('damagePerGold', 0) or 0,
            
            # === DAÑO A OBJETIVOS ===
            'damage_dealt_to_turrets': p.get('damageDealtToTurrets', 0) or 0,
            'damage_dealt_to_objectives': p.get('damageDealtToObjectives', 0) or 0,
            'kill_participation': challs.get('killParticipation', 0) or 0,
            
            # === OBJETIVOS DEL EQUIPO ===
            'first_blood': t_obj.get('first_blood', 0),
            'first_dragon': t_obj.get('first_dragon', 0),
            'first_tower': t_obj.get('first_tower', 0),
            'total_dragons': t_obj.get('total_dragons', 0),
            'total_towers': t_obj.get('total_towers', 0),
            'total_barons': t_obj.get('total_barons', 0),
            
            # === NUEVA VARIABLE A AGREGAR AQUÍ POR EL USUARIO ===
            # Ejemplo: 'nuevavar': p.get('path.to.value', 0)
        }
        rows.append(row)

    return rows

def process_all_matches(matches: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convierte lista de partidas a DataFrame."""
    records = []
    for match in matches:
        rows = extract_players_from_match(match)
        if rows:
            records.extend(rows)
    return pd.DataFrame(records)

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y normaliza el DataFrame."""
    if df.empty:
        return df

    # Eliminar duplicados
    df = df.drop_duplicates(subset=['match_id', 'participant_id'])
    df = df.dropna(subset=['match_id', 'team_id', 'champion'])
    
    # Llenar valores faltantes
    df['champion'] = df['champion'].fillna('Unknown')
    df['summoner_name'] = df['summoner_name'].fillna('Unknown')
    
    # Convertir a numéricas
    numeric_cols = [
        'game_duration_s', 'game_duration_min', 'match_win', 'kills', 'deaths', 'assists',
        'gold_earned', 'vision_score', 'total_damage_to_champions', 'magic_damage_to_champions',
        'physical_damage_to_champions', 'total_minions_killed', 'neutral_minions_killed', 'cs_total',
        'time_ccing_others', 'total_time_spent_dead', 'gold_per_min', 'vision_score_per_min', 'kda',
        'damage_dealt_to_turrets', 'damage_dealt_to_objectives', 'kill_participation', 
        'damage_per_minute', 'damage_per_gold', 'first_blood', 'first_dragon', 'first_tower',
        'total_dragons', 'total_towers', 'total_barons'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Llenar NaN con mediana en métricas
    for col in ['gold_per_min', 'vision_score_per_min', 'kda', 'kill_participation', 'damage_per_minute', 'damage_per_gold']:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    
    df = df.fillna(0)
    return df

def build_dataset(input_path: Path, output_path: Path) -> None:
    """
    Flujo completo:
    1. Cargar JSON de partidas
    2. Extraer 10 jugadores de cada partida
    3. Limpiar datos
    4. Guardar en CSV
    """
    matches = load_matches(input_path)
    df = process_all_matches(matches)
    
    if df.empty:
        raise ValueError(f'No se encontraron partidas válidas en {input_path}')

    df = clean_dataframe(df)
    df.to_csv(output_path, index=False)
    
    print(f'✓ {len(df)} registros (10 jugadores × partidas) guardados en: {output_path}')

if __name__ == '__main__':
    input_json = Path('dataset_random_gold.json')
    output_csv = Path('dataset_playersXpartida.csv')
    build_dataset(input_json, output_csv)