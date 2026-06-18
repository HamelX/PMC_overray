import csv
from pathlib import Path

def load_sprite_manifest(path: str | Path):
    p=Path(path)
    if not p.exists(): return {}
    with p.open(newline='', encoding='utf-8-sig') as f:
        return {row.get('pokemon_id') or row.get('id'): row for row in csv.DictReader(f)}
