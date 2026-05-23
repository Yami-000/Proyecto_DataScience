from __future__ import annotations
import os
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

def load_matches_json(path: Path) -> List[Dict[str, Any]]:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

def flatten_match(match: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Procesa una partida completa, extrayendo a los 10 jugadores y los objetivos de ambos equipos."""
    info = match.get('info', {})
    metadata = match.get('metadata', {})
    game_duration = float(info.get('gameDuration', 0) or 0)

    # 1. Extraer Objetivos Globales de AMBOS equipos
    team_objectives = {}
    for t in info.get('teams', []):
        t_id = t.get('teamId')
        
        def safe_obj(team_dict, obj_name, key):
            try:
                return team_dict.get('objectives', {}).get(obj_name, {}).get(key, 0)
            except Exception:
                return 0
                
        team_objectives[t_id] = {
            'first_blood': int(safe_obj(t, 'champion', 'first')),
            'first_dragon': int(safe_obj(t, 'dragon', 'first')),
            'first_tower': int(safe_obj(t, 'tower', 'first')),
            'total_dragons': int(safe_obj(t, 'dragon', 'kills')),
            'total_towers': int(safe_obj(t, 'tower', 'kills')),
            'total_barons': int(safe_obj(t, 'baron', 'kills')),
        }

    rows: List[Dict[str, Any]] = []
    
    # 2. Extraer métricas de los 10 jugadores
    for participant in info.get('participants', []) or []:
        team_id = participant.get('teamId')
        challs = participant.get('challenges', {})
        t_objs = team_objectives.get(team_id, {})

        row = {
            'match_id': metadata.get('matchId'),
            'platform_id': metadata.get('platformId'),
            'game_creation': info.get('gameCreation'),
            'game_duration_s': game_duration,
            'game_duration_min': round(game_duration / 60.0, 2) if game_duration >= 0 else np.nan,
            'team_id': team_id,
            'match_win': int(participant.get('win', False)),
            'participant_id': participant.get('participantId'),
            'is_target_player': 0, # Variable anulada para modo aleatorio
            'summoner_name': participant.get('summonerName') or participant.get('riotIdGameName') or 'Unknown',
            'riot_id_game_name': participant.get('riotIdGameName'),
            'riot_id_tagline': participant.get('riotIdTagline'),
            'champion': participant.get('championName', 'Unknown'),
            'team_position': participant.get('teamPosition'),
            'kills': participant.get('kills', 0) or 0,
            'deaths': participant.get('deaths', 0) or 0,
            'assists': participant.get('assists', 0) or 0,
            'gold_earned': participant.get('goldEarned', 0) or 0,
            'vision_score': participant.get('visionScore', 0) or 0,
            'total_damage_to_champions': participant.get('totalDamageDealtToChampions', 0) or 0,
            'magic_damage_to_champions': participant.get('magicDamageDealtToChampions', 0) or 0,
            'physical_damage_to_champions': participant.get('physicalDamageDealtToChampions', 0) or 0,
            'total_minions_killed': participant.get('totalMinionsKilled', 0) or 0,
            'neutral_minions_killed': participant.get('neutralMinionsKilled', 0) or 0,
            'cs_total': (participant.get('totalMinionsKilled', 0) or 0) + (participant.get('neutralMinionsKilled', 0) or 0),
            'time_ccing_others': participant.get('timeCCingOthers', 0) or 0,
            'total_time_spent_dead': participant.get('totalTimeSpentDead', 0) or 0,
            'gold_per_min': challs.get('goldPerMinute') or np.nan,
            'vision_score_per_min': challs.get('visionScorePerMinute') or np.nan,
            'kda': challs.get('kda') or np.nan,
            
            # Variables de Presión y Eficiencia
            'damage_dealt_to_turrets': participant.get('damageDealtToTurrets', 0) or 0,
            'damage_dealt_to_objectives': participant.get('damageDealtToObjectives', 0) or 0,
            'kill_participation': challs.get('killParticipation', 0) or 0,
            'damage_per_minute': challs.get('damagePerMinute', 0) or 0,
            'damage_per_gold': challs.get('damagePerGold', 0) or 0,

            # Objetivos del equipo asignados a la fila del jugador
            'first_blood': t_objs.get('first_blood', 0),
            'first_dragon': t_objs.get('first_dragon', 0),
            'first_tower': t_objs.get('first_tower', 0),
            'total_dragons': t_objs.get('total_dragons', 0),
            'total_towers': t_objs.get('total_towers', 0),
            'total_barons': t_objs.get('total_barons', 0),
        }
        rows.append(row)

    return rows

def flatten_matches(matches: List[Dict[str, Any]]) -> pd.DataFrame:
    records: List[Dict[str, Any]] = []
    for match in matches:
        rows = flatten_match(match)
        if not rows:
            continue
        records.extend(rows)
    return pd.DataFrame(records)

def clean_player_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.drop_duplicates(subset=['match_id', 'participant_id'])
    df = df.dropna(subset=['match_id', 'team_id', 'champion'])
    df['champion'] = df['champion'].fillna('Unknown')
    df['summoner_name'] = df['summoner_name'].fillna('Unknown')

    numeric_cols = [
        'game_duration_s', 'game_duration_min', 'match_win', 'kills', 'deaths', 'assists',
        'gold_earned', 'vision_score', 'total_damage_to_champions', 'magic_damage_to_champions',
        'physical_damage_to_champions', 'total_minions_killed', 'neutral_minions_killed', 'cs_total',
        'time_ccing_others', 'total_time_spent_dead', 'gold_per_min', 'vision_score_per_min', 'kda',
        'is_target_player', 'damage_dealt_to_turrets', 'damage_dealt_to_objectives', 
        'kill_participation', 'damage_per_minute', 'damage_per_gold', 'first_blood', 
        'first_dragon', 'first_tower', 'total_dragons', 'total_towers', 'total_barons'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df['is_target_player'] = df['is_target_player'].fillna(0).astype(int)
    df['match_win'] = df['match_win'].fillna(0).astype(int)

    fill_median = ['gold_per_min', 'vision_score_per_min', 'kda', 'kill_participation', 'damage_per_minute', 'damage_per_gold']
    for col in fill_median:
        if col in df.columns:
            median = df[col].median(skipna=True)
            df[col] = df[col].fillna(median)

    df = df.fillna(0)
    return df

def engineer_team_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    agg = df.groupby(['match_id', 'team_id'], as_index=False).agg(
        match_win=('match_win', 'first'),
        team_size=('participant_id', 'count'),
        total_kills=('kills', 'sum'),
        total_deaths=('deaths', 'sum'),
        total_assists=('assists', 'sum'),
        total_gold=('gold_earned', 'sum'),
        average_gold=('gold_earned', 'mean'),
        total_vision=('vision_score', 'sum'),
        average_vision=('vision_score', 'mean'),
        total_damage_to_champions=('total_damage_to_champions', 'sum'),
        total_cs=('cs_total', 'sum'),
        total_cc=('time_ccing_others', 'sum'),
        average_gpm=('gold_per_min', 'mean'),
        average_vpm=('vision_score_per_min', 'mean'),
        average_kda=('kda', 'mean'),
        champion_diversity=('champion', 'nunique'),
        
        total_damage_to_turrets=('damage_dealt_to_turrets', 'sum'),
        total_damage_to_objectives=('damage_dealt_to_objectives', 'sum'),
        team_kill_participation_avg=('kill_participation', 'mean'),
        team_damage_per_minute=('damage_per_minute', 'sum'),
        team_damage_per_gold=('damage_per_gold', 'mean'),
        
        first_blood=('first_blood', 'first'),
        first_dragon=('first_dragon', 'first'),
        first_tower=('first_tower', 'first'),
        total_dragons=('total_dragons', 'first'),
        total_towers=('total_towers', 'first'),
        total_barons=('total_barons', 'first'),
    )

    agg['kill_death_ratio'] = agg.apply(
        lambda row: row['total_kills'] / row['total_deaths'] if row['total_deaths'] > 0 else row['total_kills'],
        axis=1,
    )
    agg['gold_variation'] = df.groupby(['match_id', 'team_id'])['gold_earned'].std().reset_index(drop=True).fillna(0)
    agg['vision_variation'] = df.groupby(['match_id', 'team_id'])['vision_score'].std().reset_index(drop=True).fillna(0)
    agg['team_champion_max_kills'] = df.groupby(['match_id', 'team_id'])['kills'].max().reset_index(drop=True)
    agg['win_rate'] = agg['match_win']

    return agg

def eda_report(player_df: pd.DataFrame, team_df: pd.DataFrame, output_dir: Path) -> None:
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    print('\n--- Resumen de datos ---')
    print('Players dataset:', player_df.shape)
    print('Team dataset:', team_df.shape)
    print('\nDistribución de win en el equipo (Debe ser ~50%):')
    if not team_df.empty:
        print(team_df['match_win'].value_counts(normalize=True))

def build_dataset(
    input_path: Path,
    players_output: Path,
    team_output: Path,
    eda_output: Optional[Path] = None,
) -> None:
    matches = load_matches_json(input_path)
    player_df = flatten_matches(matches)
    
    if player_df.empty:
        raise ValueError(f'No se encontraron partidas válidas en {input_path}')

    player_df = clean_player_df(player_df)
    team_df = engineer_team_features(player_df)

    player_df.to_csv(players_output, index=False)
    team_df.to_csv(team_output, index=False)

    print(f'Guardado player-level CSV: {players_output}')
    print(f'Guardado team-level CSV: {team_output}')

    if eda_output is not None:
        eda_report(player_df, team_df, eda_output)
        print(f'Guardado gráficos de EDA en: {eda_output}')

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Pipeline de datos para modo aleatorio global.')
    parser.add_argument('--input', type=Path, default=Path('dataset_random_gold.json'), help='Ruta al JSON')
    parser.add_argument('--players-output', type=Path, default=Path('dataset_players.csv'), help='CSV de jugadores')
    parser.add_argument('--team-output', type=Path, default=Path('dataset_team_metrics.csv'), help='CSV de equipos')
    parser.add_argument('--eda-output', type=Path, default=Path('eda_outputs'), help='Directorio para guardar EDA')
    parser.add_argument('--no-eda', action='store_true', help='No generar gráficos de EDA')
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    eda_dir = None if args.no_eda else args.eda_output
    build_dataset(
        input_path=args.input,
        players_output=args.players_output,
        team_output=args.team_output,
        eda_output=eda_dir,
    )

if __name__ == '__main__':
    main()