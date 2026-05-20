"""
Feature Factory para matches de MATCH-V5 (Riot)

Extrae múltiples variables a nivel de equipo a partir de un diccionario `match`
proveniente de la API MATCH-V5 (campo `info`).

Funciones principales:
- extract_team_features(match, player_name=None, ally_team_id=None)
- build_team_df(matches, player_name=None, ally_team_id=None)
- plot_top_correlations(df, target='win', top_n=15, outpath=None)
- select_features_by_corr(df, target='win', thresh=0.15, collinear_thresh=0.95)

Uso: importar las funciones y pasar una lista de matches (lista de dicts).
Se usan `.get()` para evitar KeyError con partidas antiguas sin `challenges`.
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def _safe_chal(p: dict, key: str, default: float = 0.0) -> float:
    return float(p.get('challenges', {}).get(key, default) or default)


def extract_team_features(match: dict, player_name: Optional[str] = None, ally_team_id: Optional[int] = None) -> dict:
    info = match.get('info', {})
    participants = info.get('participants', []) or []

    # Determinar teamId aliado
    team_id = ally_team_id
    if team_id is None and player_name is not None:
        for p in participants:
            if p.get('summonerName') == player_name:
                team_id = p.get('teamId')
                break
    if team_id is None:
        # Si no se especifica, asumimos teamId del primer participante
        team_id = participants[0].get('teamId') if participants else 100

    ally = [p for p in participants if p.get('teamId') == team_id]

    # Seguridad: si no hay 5 aliados, igual procesamos lo que haya
    n_players = len(ally)

    # Combat metrics
    kp_vals = [p.get('challenges', {}).get('killParticipation') for p in ally]
    kp_vals = [float(x) for x in kp_vals if x is not None]
    kp_avg = float(np.mean(kp_vals)) if kp_vals else 0.0

    dpm_vals = [p.get('challenges', {}).get('damagePerMinute') for p in ally]
    dpm_vals = [float(x) for x in dpm_vals if x is not None]
    dpm_total = float(np.sum(dpm_vals)) if dpm_vals else 0.0

    dmg_champ_total = float(sum(p.get('totalDamageDealtToChampions', 0) or 0 for p in ally))
    dmg_turrets = float(sum(p.get('damageDealtToTurrets', 0) or 0 for p in ally))
    dmg_objectives = float(sum(p.get('damageDealtToObjectives', 0) or 0 for p in ally))

    magic_sum = float(sum(p.get('magicDamageDealtToChampions', 0) or 0 for p in ally))
    phys_sum = float(sum(p.get('physicalDamageDealtToChampions', 0) or 0 for p in ally))
    pct_magic = magic_sum / dmg_champ_total if dmg_champ_total > 0 else 0.0
    pct_phys = phys_sum / dmg_champ_total if dmg_champ_total > 0 else 0.0

    kda_vals = [p.get('challenges', {}).get('kda') for p in ally]
    kda_vals = [float(x) for x in kda_vals if x is not None]
    kda_avg = float(np.mean(kda_vals)) if kda_vals else 0.0

    # Economy / vision / utility
    gpm_vals = [p.get('challenges', {}).get('goldPerMinute') for p in ally]
    gpm_vals = [float(x) for x in gpm_vals if x is not None]
    gpm_total = float(np.sum(gpm_vals)) if gpm_vals else 0.0

    vpm_vals = [p.get('challenges', {}).get('visionScorePerMinute') for p in ally]
    vpm_vals = [float(x) for x in vpm_vals if x is not None]
    vpm_total = float(np.sum(vpm_vals)) if vpm_vals else 0.0

    cc_seconds = float(sum(p.get('timeCCingOthers', 0) or 0 for p in ally))

    dmg_per_gold_vals = [p.get('challenges', {}).get('damagePerGold') for p in ally]
    dmg_per_gold_vals = [float(x) for x in dmg_per_gold_vals if x is not None]
    dmg_per_gold_avg = float(np.mean(dmg_per_gold_vals)) if dmg_per_gold_vals else 0.0

    # CS por minuto
    total_minions = float(sum((p.get('totalMinionsKilled', 0) or 0) + (p.get('neutralMinionsKilled', 0) or 0) for p in ally))
    game_duration_s = float(info.get('gameDuration', 0) or 0)
    game_minutes = game_duration_s / 60.0 if game_duration_s > 0 else 1.0
    cs_per_min = total_minions / game_minutes if game_minutes > 0 else 0.0

    # Team-level objectives
    team_info = None
    for t in info.get('teams', []) or []:
        if t.get('teamId') == team_id:
            team_info = t
            break

    def _obj_bool(team_d, key1, key2='first'):
        try:
            return bool(team_d.get('objectives', {}).get(key1, {}).get(key2, False))
        except Exception:
            return False

    first_blood = _obj_bool(team_info, 'champion') if team_info else False
    first_dragon = _obj_bool(team_info, 'dragon') if team_info else False
    first_tower = _obj_bool(team_info, 'tower') if team_info else False
    first_rift = _obj_bool(team_info, 'riftHerald') if team_info else False

    def _obj_kills(team_d, key):
        try:
            return int(team_d.get('objectives', {}).get(key, {}).get('kills', 0) or 0)
        except Exception:
            return 0

    dragon_kills = _obj_kills(team_info, 'dragon') if team_info else 0
    baron_kills = _obj_kills(team_info, 'baron') if team_info else 0
    tower_kills = _obj_kills(team_info, 'tower') if team_info else 0

    win_flag = bool(team_info.get('win')) if team_info and team_info.get('win') is not None else False

    features = {
        'n_players': n_players,
        'kp_avg': kp_avg,
        'dpm_total': dpm_total,
        'dmg_champ_total': dmg_champ_total,
        'dmg_turrets': dmg_turrets,
        'dmg_objectives': dmg_objectives,
        'pct_magic_dmg': pct_magic,
        'pct_phys_dmg': pct_phys,
        'kda_avg': kda_avg,
        'gpm_total': gpm_total,
        'vpm_total': vpm_total,
        'cc_seconds': cc_seconds,
        'dmg_per_gold_avg': dmg_per_gold_avg,
        'cs_per_min': cs_per_min,
        'first_blood': int(first_blood),
        'first_dragon': int(first_dragon),
        'first_tower': int(first_tower),
        'first_riftHerald': int(first_rift),
        'dragon_kills': dragon_kills,
        'baron_kills': baron_kills,
        'tower_kills': tower_kills,
        'game_minutes': game_minutes,
        'win': int(win_flag),
    }

    return features


def build_team_df(matches: List[Dict], player_name: Optional[str] = None, ally_team_id: Optional[int] = None) -> pd.DataFrame:
    rows = []
    for m in matches:
        try:
            feat = extract_team_features(m, player_name=player_name, ally_team_id=ally_team_id)
            rows.append(feat)
        except Exception:
            # Si falla una partida, la ignoramos y seguimos
            continue
    if not rows:
        # Retornar DataFrame vacío con columnas esperadas para evitar KeyError downstream
        cols = ['n_players','kp_avg','dpm_total','dmg_champ_total','dmg_turrets','dmg_objectives',
                'pct_magic_dmg','pct_phys_dmg','kda_avg','gpm_total','vpm_total','cc_seconds',
                'dmg_per_gold_avg','cs_per_min','first_blood','first_dragon','first_tower',
                'first_riftHerald','dragon_kills','baron_kills','tower_kills','game_minutes','win']
        df = pd.DataFrame(columns=cols)
        # for numeric compatibility
        for c in cols:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df['win'] = df['win'].fillna(0).astype(int)
        return df

    df = pd.DataFrame(rows)
    # Asegurar tipos numéricos
    for c in df.columns:
        if c != 'win':
            df[c] = pd.to_numeric(df[c], errors='coerce')
    df['win'] = pd.to_numeric(df['win'], errors='coerce').fillna(0).astype(int)
    return df


def plot_top_correlations(df: pd.DataFrame, target: str = 'win', top_n: int = 15, outpath: Optional[str] = None) -> Tuple[pd.DataFrame, plt.Figure]:
    corr = df.corr().abs()[target].sort_values(ascending=False)
    # Excluir el target en la matriz
    top_features = corr.drop(labels=[target]).head(top_n).index.tolist()
    mat = df[top_features].corr()

    plt.figure(figsize=(10, 8))
    fig = sns.heatmap(mat, annot=True, cmap='vlag', center=0, fmt='.2f').get_figure()
    plt.title(f'Top {top_n} correlations (absolute) with {target}')
    plt.tight_layout()
    if outpath:
        fig.savefig(outpath, dpi=200)
    return mat, fig


def select_features_by_corr(df: pd.DataFrame, target: str = 'win', thresh: float = 0.15, collinear_thresh: float = 0.95) -> List[str]:
    # Correlación absoluta con target
    corr_with_target = df.corr().abs()[target]
    candidates = corr_with_target[corr_with_target > thresh].drop(labels=[target], errors='ignore')
    candidates = candidates.sort_values(ascending=False)
    features = list(candidates.index)

    # Eliminar colinealidad entre candidatos: estrategia greedy por importancia
    kept = []
    corr_matrix = df[features].corr().abs()
    for feat in features:
        too_similar = False
        for k in kept:
            if corr_matrix.loc[feat, k] >= collinear_thresh:
                too_similar = True
                break
        if not too_similar:
            kept.append(feat)

    return kept


if __name__ == '__main__':
    # Ejemplo de uso rápido cuando se ejecuta como script
    import json
    import sys

    if len(sys.argv) < 2:
        print('Uso: python feature_factory.py <matches_json_file> [summonerName]')
        sys.exit(0)

    path = sys.argv[1]
    player = sys.argv[2] if len(sys.argv) > 2 else None

    with open(path, 'r', encoding='utf-8') as f:
        matches = json.load(f)

    df = build_team_df(matches, player_name=player)
    print(f'Rows: {len(df)} — Columns: {list(df.columns)}')

    # Mostrar top correlaciones y guardar figura
    mat, fig = plot_top_correlations(df, target='win', top_n=15, outpath='top_corrs.png')
    kept = select_features_by_corr(df, target='win', thresh=0.15, collinear_thresh=0.95)
    print('Selected features (abs corr>|0.15| and no high collinearity):')
    print(kept)
