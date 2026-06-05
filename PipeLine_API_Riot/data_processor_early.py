from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from PipeLine_API_Riot.UsuarioRandom.configRandom import SETTINGS

EARLY_GAME_MINUTE = int(SETTINGS.get('EARLY_GAME_MINUTE', 10))


def load_timeline_matches(path: Path) -> List[Dict[str, Any]]:
    """Carga la lista de partidas con match + timeline."""
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def participant_team_map(match: Dict[str, Any]) -> Dict[int, int]:
    """Mapea participantId a teamId usando el match detail."""
    participants = match.get('info', {}).get('participants', []) or []
    return {
        int(p.get('participantId')): int(p.get('teamId'))
        for p in participants
        if p.get('participantId') is not None and p.get('teamId') is not None
    }


def frame_for_index(frames: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
    """Devuelve el frame en el índice solicitado o el último disponible antes de él."""
    if not frames:
        return {}
    if len(frames) > index:
        return frames[index] or {}
    return frames[-1] or {}


def safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0


def safe_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except Exception:
        return 0.0


def extract_frame_team_stats(match: Dict[str, Any], timeline: Dict[str, Any], minute: int = EARLY_GAME_MINUTE) -> Dict[int, Dict[str, float]]:
    """Extrae las métricas del frame seleccionado por equipo."""
    frames = (timeline.get('info', {}) or {}).get('frames', []) or []
    frames = frames[: minute + 1]
    frame_at_minute = frame_for_index(frames, minute)
    participant_frames = frame_at_minute.get('participantFrames', {}) or {}
    team_map = participant_team_map(match)

    teams: Dict[int, Dict[str, float]] = {
        100: {
            'total_gold': 0.0,
            'total_xp': 0.0,
            'total_minions': 0.0,
            'total_jungle_minions': 0.0,
            'player_count': 0,
        },
        200: {
            'total_gold': 0.0,
            'total_xp': 0.0,
            'total_minions': 0.0,
            'total_jungle_minions': 0.0,
            'player_count': 0,
        },
    }

    for pid_str, frame_data in participant_frames.items():
        try:
            participant_id = int(pid_str)
        except Exception:
            continue
        team_id = team_map.get(participant_id)
        if team_id not in teams:
            continue

        teams[team_id]['player_count'] += 1
        teams[team_id]['total_gold'] += safe_float(frame_data.get('totalGold'))
        teams[team_id]['total_xp'] += safe_float(frame_data.get('xp'))
        teams[team_id]['total_minions'] += safe_float(frame_data.get('minionsKilled'))
        teams[team_id]['total_jungle_minions'] += safe_float(frame_data.get('jungleMinionsKilled'))

    for team_id, metrics in teams.items():
        count = metrics['player_count'] or 5
        metrics['avg_gold'] = metrics['total_gold'] / count
        metrics['avg_xp'] = metrics['total_xp'] / count
        metrics['avg_minions'] = metrics['total_minions'] / count
        metrics['avg_jungle_minions'] = metrics['total_jungle_minions'] / count

    return teams


def extract_early_events(match: Dict[str, Any], timeline: Dict[str, Any]) -> Dict[int, Dict[str, int]]:
    """Cuenta eventos tempranos y asigna métricas por equipo."""
    frames = (timeline.get('info', {}) or {}).get('frames', []) or []
    frames = frames[:16]
    team_map = participant_team_map(match)

    team_events = {
        100: {
            'first_blood': 0,
            'early_dragons': 0,
            'early_heralds': 0,
            'early_item_purchases': 0,
        },
        200: {
            'first_blood': 0,
            'early_dragons': 0,
            'early_heralds': 0,
            'early_item_purchases': 0,
        },
    }
    first_blood_assigned = False

    for frame in frames:
        for event in (frame.get('events') or []):
            event_type = event.get('type')
            if event_type == 'CHAMPION_KILL':
                if not first_blood_assigned:
                    killer_id = safe_int(event.get('killerId'))
                    killer_team = team_map.get(killer_id)
                    if killer_team in (100, 200):
                        team_events[killer_team]['first_blood'] = 1
                        first_blood_assigned = True
            elif event_type == 'ELITE_MONSTER_KILL':
                monster_type = (event.get('monsterType') or '').upper()
                killer_id = safe_int(event.get('killerId'))
                killer_team = team_map.get(killer_id)
                if killer_team not in (100, 200):
                    continue
                if monster_type == 'DRAGON':
                    team_events[killer_team]['early_dragons'] += 1
                elif monster_type in ('RIFTHERALD', 'RIFT_HERALD'):
                    team_events[killer_team]['early_heralds'] += 1
            elif event_type == 'ITEM_PURCHASED':
                participant_id = safe_int(event.get('participantId'))
                team_id = team_map.get(participant_id)
                if team_id in (100, 200):
                    team_events[team_id]['early_item_purchases'] += 1

    return team_events


def extract_team_early_features(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Crea una fila por equipo con métricas tempranas únicamente."""
    match = record.get('match', {}) or {}
    timeline = record.get('timeline', {}) or {}
    match_id = record.get('match_id') or (match.get('metadata') or {}).get('matchId')
    def _team_win_value(team: Dict[str, Any]) -> int:
        win_value = team.get('win')
        if isinstance(win_value, bool):
            return 1 if win_value else 0
        if isinstance(win_value, str):
            return 1 if win_value.lower() == 'win' else 0
        return 0

    team_win_map = {
        int(team.get('teamId')): _team_win_value(team)
        for team in (match.get('info', {}) or {}).get('teams', []) or []
    }

    frame_stats = extract_frame_team_stats(match, timeline)
    event_stats = extract_early_events(match, timeline)

    rows: List[Dict[str, Any]] = []
    for team_id, team_metrics in frame_stats.items():
        if team_id not in team_win_map:
            continue

        team_event = event_stats.get(team_id, {
            'first_blood': 0,
            'early_dragons': 0,
            'early_heralds': 0,
            'early_item_purchases': 0,
        })

        row = {
            'match_id': match_id,
            'team_id': team_id,
            'match_win': int(team_win_map.get(team_id, 0)),
            'early_minute': EARLY_GAME_MINUTE,
            'first_blood': int(team_event['first_blood']),
            'early_dragons': int(team_event['early_dragons']),
            'early_heralds': int(team_event['early_heralds']),
            'early_item_purchases': int(team_event['early_item_purchases']),
            'team_total_gold': team_metrics['total_gold'],
            'team_avg_gold': team_metrics['avg_gold'],
            'team_total_xp': team_metrics['total_xp'],
            'team_avg_xp': team_metrics['avg_xp'],
            'team_total_minions': team_metrics['total_minions'],
            'team_avg_minions': team_metrics['avg_minions'],
            'team_total_jungle_minions': team_metrics['total_jungle_minions'],
            'team_avg_jungle_minions': team_metrics['avg_jungle_minions'],
        }
        rows.append(row)

    # Ajuste: si no se encontraron equipos válidos, devolver lista vacía.
    return rows


def build_early_team_dataset(input_path: Path, output_path: Path) -> None:
    """Genera un CSV de métricas tempranas por equipo hasta el minuto configurado."""
    records = load_timeline_matches(input_path)
    result_rows: List[Dict[str, Any]] = []
    for record in records:
        result_rows.extend(extract_team_early_features(record))

    if not result_rows:
        raise ValueError(f'No se extrajeron métricas tempranas desde {input_path}')

    df = pd.DataFrame(result_rows)
    df = df.drop_duplicates(subset=['match_id', 'team_id'])
    df = df.astype({
        'match_win': 'int64',
        'first_blood': 'int64',
        'early_dragons': 'int64',
        'early_heralds': 'int64',
        'early_item_purchases': 'int64',
        'team_id': 'int64',
        'early_minute': 'int64',
    })
    df[['team_total_gold', 'team_avg_gold', 'team_total_xp', 'team_avg_xp',
        'team_total_minions', 'team_avg_minions',
        'team_total_jungle_minions', 'team_avg_jungle_minions']] = df[[
            'team_total_gold', 'team_avg_gold', 'team_total_xp', 'team_avg_xp',
            'team_total_minions', 'team_avg_minions',
            'team_total_jungle_minions', 'team_avg_jungle_minions']].apply(pd.to_numeric, errors='coerce').fillna(0)

    df.to_csv(output_path, index=False)
    print(f'✓ {len(df)} filas tempranas guardadas en: {output_path}')


if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent
    input_json = base_dir / 'dataset_random_gold_timeline.json'
    output_csv = base_dir / f'dataset_team_metrics_early_{EARLY_GAME_MINUTE}min.csv'
    build_early_team_dataset(input_json, output_csv)
