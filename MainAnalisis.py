"""Main script que ejecuta el análisis de datos desde la carpeta 2_AnalisisDatos."""
from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
analysis_dir = root_dir / '2_AnalisisDatos'
pipeline_dir = root_dir / '1_PipeLine_API_Riot'

sys.path.insert(0, str(analysis_dir))
sys.path.insert(0, str(pipeline_dir / 'UsuarioPersonalizado'))
sys.path.insert(0, str(pipeline_dir))

from data_processor import build_dataset
from configUP import SETTINGS


def run_main_analisis() -> None:
    input_json = pipeline_dir / 'dataset_specific_user.json'
    players_output = analysis_dir / 'dataset_players.csv'
    team_output = analysis_dir / 'dataset_team_metrics.csv'
    eda_output = analysis_dir / 'eda_outputs'

    print('=== Iniciando MainAnalisis ===')
    print(f'Input JSON: {input_json}')
    print(f'Players CSV: {players_output}')
    print(f'Team CSV: {team_output}')

    build_dataset(
        input_path=input_json,
        target_name=SETTINGS['TARGET_NAME'],
        target_tag=SETTINGS['TARGET_TAG'],
        players_output=players_output,
        team_output=team_output,
        eda_output=eda_output,
    )

    print('=== MainAnalisis completado ===')
    print(f'- Players: {players_output}')
    print(f'- Team: {team_output}')
    print(f'- EDA outputs: {eda_output}')


if __name__ == '__main__':
    run_main_analisis()
