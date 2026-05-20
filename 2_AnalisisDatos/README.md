# Análisis de Datos

Este directorio contiene la lógica de análisis ejecutable sobre los datos descargados por el pipeline.

## Archivos

- `data_processor.py`: carga el JSON de partidas de Riot (`MATCH-V5`), extrae características del equipo aliado del usuario objetivo, genera CSV de jugadores y métricas de equipo, y produce gráficos de EDA.
- `feature_factory.py`: funciones auxiliares para extracción de features a nivel de equipo y análisis de correlación.
- `eda_outputs/`: carpeta de salida para gráficos de análisis exploratorio.

## Uso

Desde `2_AnalisisDatos`:

```bash
python data_processor.py --input ../1_PipeLine_API_Riot/dataset_specific_user.json --players-output dataset_players.csv --team-output dataset_team_metrics.csv
```

Para evitar gráficos de EDA:

```bash
python data_processor.py --no-eda
```
