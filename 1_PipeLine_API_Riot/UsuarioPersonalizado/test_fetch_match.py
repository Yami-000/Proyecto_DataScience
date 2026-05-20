from riot_engineUP import lol_watcher, americas_region

# Match ID de muestra (puedes cambiarlo por otro de tu interés)
match_id = 'LA2_1596496298'
print(f"Intentando descargar match {match_id} en region {americas_region}...")
try:
    data = lol_watcher.match.by_id(americas_region, match_id)
    print('Éxito: claves top-level en el JSON:', list(data.keys()))
    print('info keys:', list(data.get('info', {}).keys()))
except Exception as e:
    print('Error al descargar match:', e)
