from pathlib import Path

from UsuarioPersonalizado.mainUP import run_pipeline
from UsuarioPersonalizado.configUP import SETTINGS
from data_processor import build_dataset


def run_main_pipeline() -> None:
    root_dir = Path(__file__).resolve().parent
    json_path = root_dir / 'dataset_specific_user.json'
    players_output = root_dir / 'dataset_players.csv'
    team_output = root_dir / 'dataset_team_metrics.csv'

    print('=== Iniciando MainPipeline ===')
    print('1) Descargando partidas del usuario específico...')
    run_pipeline()

    print('2) Preparando datasets para análisis...')
    build_dataset(
        input_path=json_path,
        target_name=SETTINGS['TARGET_NAME'],
        target_tag=SETTINGS['TARGET_TAG'],
        players_output=players_output,
        team_output=team_output,
        eda_output=None,
    )

    print('=== MainPipeline completado ===')
    print(f'- JSON de partidas: {json_path}')
    print(f'- CSV de jugadores: {players_output}')
    print(f'- CSV de métricas de equipo: {team_output}')


if __name__ == '__main__':
    run_main_pipeline()
