from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


def load_matches(path: Path) -> List[Dict[str, Any]]:
    """Carga JSON de partidas (MATCH-V5 response list)."""
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def team_objectives_from_info(team: Dict[str, Any]) -> Dict[str, int]:
    """Extrae los flags 'first' de objetivos tempranos del dict team."""
    obj = team.get('objectives', {}) or {}
    return {
        'first_blood': int(obj.get('champion', {}).get('first', 0) or 0),
        'first_dragon': int(obj.get('dragon', {}).get('first', 0) or 0),
        'first_tower': int(obj.get('tower', {}).get('first', 0) or 0),
        'first_rift_herald': int(obj.get('riftHerald', {}).get('first', 0) or 0),
    }


def safe_get_participant_challenge(p: Dict[str, Any], keys: List[str]) -> Optional[float]:
    """Busca varias keys dentro de participant['challenges'] o participant y devuelve la primera encontrada."""
    challs = p.get('challenges', {}) or {}
    for k in keys:
        if k in challs:
            try:
                return float(challs.get(k) or 0)
            except Exception:
                continue
    # fallback to timeline if present (e.g., xpPerMinDeltas)
    tl = p.get('timeline', {}) or {}
    # xpPerMinDeltas example: {'0-10': 300.0}
    xp = tl.get('xpPerMinDeltas', {}) or {}
    if '0-10' in xp:
        try:
            return float(xp.get('0-10') or 0)
        except Exception:
            pass
    return None


def extract_team_early_features(match: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrae métricas tempranas a nivel de equipo desde el JSON de MATCH-V5.

    - Usa flags 'first' desde info.teams.objectives (first_blood, first_dragon, first_tower, first_rift_herald)
    - Extrae CS en primeros 10 minutos si existe en participant['challenges'] (keys probables)
    - Extrae gold diff a 15' si existe (varias keys posibles en challenges)
    - Extrae xp per min en 0-10 desde participant['timeline']['xpPerMinDeltas'] si está
    - Composición por roles (porcentaje de soporte, jungle, carry)

    Nota: Si alguna métrica no está disponible en MATCH-V5 sin TIMELINE, la función la deja en NaN/0.
    """
    info = match.get('info', {}) or {}
    metadata = match.get('metadata', {}) or {}

    # Map teamId -> objective flags
    team_objs = {}
    for t in info.get('teams', []) or []:
        t_id = t.get('teamId')
        team_objs[t_id] = team_objectives_from_info(t)

    # Prepare per-team accumulators
    teams: Dict[int, Dict[str, Any]] = {}
    for p in info.get('participants', []) or []:
        t_id = p.get('teamId')
        if t_id not in teams:
            teams[t_id] = {
                'match_id': metadata.get('matchId'),
                'team_id': t_id,
                'match_win': int(p.get('win', False)),
                'player_count': 0,
                'cs_first_10_sum': 0.0,
                'cs_first_10_count': 0,
                'gold_diff_15_sum': 0.0,
                'gold_diff_15_count': 0,
                'xp_0_10_sum': 0.0,
                'xp_0_10_count': 0,
                'n_support': 0,
                'n_jungle': 0,
                'n_carry': 0,
            }

        rec = teams[t_id]
        rec['player_count'] += 1

        # CS first 10: common challenge keys
        cs = safe_get_participant_challenge(p, ['laneMinionsFirst10Minutes', 'minionsFirst10Minutes', 'creepsPerMinDeltas_0-10'])
        if cs is not None:
            rec['cs_first_10_sum'] += cs
            rec['cs_first_10_count'] += 1

        # gold diff at 15: different providers may name it differently
        gold15 = safe_get_participant_challenge(p, ['goldDiffAt15', 'goldDiff15', 'goldAt15', 'goldDiff'])
        if gold15 is not None:
            rec['gold_diff_15_sum'] += gold15
            rec['gold_diff_15_count'] += 1

        # xp per min 0-10 from timeline
        xp01 = safe_get_participant_challenge(p, ['xpPerMinDeltas_0-10', 'xpPerMinDeltas'])
        if xp01 is not None:
            rec['xp_0_10_sum'] += xp01
            rec['xp_0_10_count'] += 1

        # composition by team_position (roles provided in participant)
        role = (p.get('teamPosition') or '').upper()
        if role == 'UTILITY':
            rec['n_support'] += 1
        if role == 'JUNGLE':
            rec['n_jungle'] += 1
        if role in ('MIDDLE', 'BOTTOM'):
            rec['n_carry'] += 1

    # Convert accumulators to rows
    rows: List[Dict[str, Any]] = []
    for t_id, rec in teams.items():
        # objectives
        obj = team_objs.get(t_id, {})

        player_count = rec.get('player_count') or 5
        cs_mean = (rec['cs_first_10_sum'] / rec['cs_first_10_count']) if rec['cs_first_10_count'] > 0 else np.nan
        gold_diff_15 = (rec['gold_diff_15_sum'] / rec['gold_diff_15_count']) if rec['gold_diff_15_count'] > 0 else np.nan
        xp_0_10 = (rec['xp_0_10_sum'] / rec['xp_0_10_count']) if rec['xp_0_10_count'] > 0 else np.nan

        row = {
            'match_id': rec['match_id'],
            'team_id': t_id,
            'match_win': int(rec.get('match_win', 0)),

            # Early objective flags (booleans)
            'first_blood': int(obj.get('first_blood', 0)),
            'first_dragon': int(obj.get('first_dragon', 0)),
            'first_tower': int(obj.get('first_tower', 0)),
            'first_rift_herald': int(obj.get('first_rift_herald', 0)),

            # Early aggregated metrics
            'cs_first_10_mean': cs_mean,
            'gold_diff_15_mean': gold_diff_15,
            'xp_0_10_mean': xp_0_10,

            # Composition
            'pct_support': rec.get('n_support', 0) / player_count,
            'pct_jungle': rec.get('n_jungle', 0) / player_count,
            'pct_carry': rec.get('n_carry', 0) / player_count,
        }
        rows.append(row)

    return rows


def build_early_team_dataset(input_path: Path, output_path: Path) -> None:
    """
    Genera `dataset_team_metrics_early_game.csv` con filas por equipo (team 100 / 200).
    Cada fila contiene solo features tempranas y la variable objetivo `match_win`.
    """
    matches = load_matches(input_path)
    records: List[Dict[str, Any]] = []
    for match in matches:
        rows = extract_team_early_features(match)
        if rows:
            records.extend(rows)

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError(f'No se extrajeron features tempranas desde {input_path}')

    # Normalizar/limpiar
    df['cs_first_10_mean'] = pd.to_numeric(df['cs_first_10_mean'], errors='coerce')
    df['gold_diff_15_mean'] = pd.to_numeric(df['gold_diff_15_mean'], errors='coerce')
    df['xp_0_10_mean'] = pd.to_numeric(df['xp_0_10_mean'], errors='coerce')
    df[['first_blood', 'first_dragon', 'first_tower', 'first_rift_herald', 'match_win']] = df[['first_blood', 'first_dragon', 'first_tower', 'first_rift_herald', 'match_win']].fillna(0).astype(int)
    df[['pct_support', 'pct_jungle', 'pct_carry']] = df[['pct_support', 'pct_jungle', 'pct_carry']].fillna(0)

    # Evitar data leakage: NO incluir variables de final de partida
    # Guardar CSV
    df.to_csv(output_path, index=False)
    print(f'✓ {len(df)} filas guardadas en: {output_path}')


def build_dataset(input_path: Path, output_path: Path) -> None:
    """Compatibilidad hacia atrás: alias que delega a `build_early_team_dataset`.

    `MainPipeline.py` importa `build_dataset`. Este wrapper mantiene esa API y
    genera el CSV de métricas tempranas por equipo.
    """
    print('NOTICE: Using compatibility wrapper build_dataset -> build_early_team_dataset')
    return build_early_team_dataset(input_path=input_path, output_path=output_path)


if __name__ == '__main__':
    # Usar rutas relativas al archivo para permitir ejecución directa desde cualquier CWD
    base_dir = Path(__file__).resolve().parent
    input_json = base_dir / 'dataset_random_gold.json'
    output_csv = base_dir / 'dataset_team_metrics_early_game.csv'
    build_early_team_dataset(input_json, output_csv)