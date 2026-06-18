
"""
Build sprite manifest by matching downloaded Champions menu sprites to Pokemon index.

Input:
  ../upload_these_files/14_POKEMON_INDEX_FULL_CLEAN.csv
  ../sprites/champions_menu/champions_menu_sprites_raw.csv

Output:
  ../upload_these_files/19_SPRITE_MANIFEST_CHAMPIONS_MENU.csv
  ../sprites/champions_menu/unmatched_sprite_files.csv
  ../sprites/champions_menu/unmatched_pokemon.csv

Run:
  python build_sprite_manifest_champions_menu.py
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
UPLOAD = ROOT / 'upload_these_files'
SPRITES = ROOT / 'sprites' / 'champions_menu'
POKEMON_CSV = UPLOAD / '14_POKEMON_INDEX_FULL_CLEAN.csv'
RAW_CSV = SPRITES / 'champions_menu_sprites_raw.csv'
OUT_CSV = UPLOAD / '19_SPRITE_MANIFEST_CHAMPIONS_MENU.csv'

FORM_SYNONYMS = {
    'alolan': 'Alola', 'alola': 'Alola',
    'galarian': 'Galar', 'galar': 'Galar',
    'hisui': 'Hisui', 'hisuian': 'Hisui',
    'paldean': 'Paldea', 'paldea': 'Paldea',
    'mega': 'Mega',
    'mega-x': 'Mega X', 'mega-y': 'Mega Y',
    'female': 'Female', 'male': 'Male',
    'dusk': 'Dusk', 'midnight': 'Midnight',
    'wash': 'Wash', 'heat': 'Heat', 'frost': 'Frost', 'fan': 'Fan', 'mow': 'Mow',
    'family-of-four': 'Family of Four', 'family-of-three': 'Family of Three',
    'average': 'Average', 'large': 'Large', 'small': 'Small', 'super': 'Super',
    'aqua': 'Aqua', 'blaze': 'Blaze', 'combat': 'Combat',
    'eternal-flower': 'Eternal Flower',
}

# Manual base dex fixes for OP.GG internal form IDs or names that need base dex for sprite filename.
MANUAL_BASE_BY_POKEMON_ID = {
    'mega-venusaur': 3, 'mega-charizard-x': 6, 'mega-charizard-y': 6, 'mega-blastoise': 9,
    'mega-beedrill': 15, 'mega-pidgeot': 18, 'mega-raichu-x': 26, 'mega-raichu-y': 26,
    'mega-clefable': 36, 'mega-alakazam': 65, 'mega-slowbro': 80, 'mega-gengar': 94,
    'mega-kangaskhan': 115, 'mega-starmie': 121, 'mega-pinsir': 127, 'mega-gyarados': 130,
    'mega-aerodactyl': 142, 'mega-dragonite': 149, 'mega-meganium': 154, 'mega-typhlosion': 157,
    'mega-feraligatr': 160, 'mega-ampharos': 181, 'mega-steelix': 208, 'mega-scizor': 212,
    'mega-heracross': 214, 'mega-skarmory': 227, 'mega-houndoom': 229, 'mega-tyranitar': 248,
    'mega-sceptile': 254, 'mega-blaziken': 257, 'mega-swampert': 260, 'mega-gardevoir': 282,
    'mega-sableye': 302, 'mega-mawile': 303, 'mega-aggron': 306, 'mega-medicham': 308,
    'mega-manectric': 310, 'mega-sharpedo': 319, 'mega-camerupt': 323, 'mega-chimecho': 358,
    'mega-absol': 359, 'mega-glalie': 362, 'mega-metagross': 376, 'mega-lopunny': 428,
    'mega-gallade': 475, 'mega-froslass': 478, 'mega-emboar': 500, 'mega-samurott': 503,
    'mega-excadrill': 530, 'mega-audino': 531, 'mega-scolipede': 545, 'mega-scrafty': 560,
    'mega-chandelure': 609, 'mega-eelektross': 604, 'mega-golurk': 623, 'mega-greninja': 658,
    'mega-chesnaught': 652, 'mega-delphox': 655, 'mega-pyroar': 668, 'mega-meowstic': 678,
    'mega-malam ar': 687, # harmless typo fallback not used
    'mega-malamar': 687, 'mega-barbaracle': 689, 'mega-dragalge': 691, 'mega-hawlucha': 701,
    'mega-floette': 670, 'mega-drampa': 780, 'mega-falinks': 870, 'mega-crabominable': 740,
    'mega-victreebel': 71, 'mega-glimmora': 970, 'mega-scovillain': 952,
    'raichu-alolan': 26, 'ninetales-alolan': 38,
    'arcanine-hisui': 59, 'typhlosion-hisui': 157, 'samurott-hisui': 503, 'decidueye-hisui': 724,
    'goodra-hisui': 706, 'avalugg-hisui': 713, 'zoroark-hisui': 571,
    'slowbro-galarian': 80, 'slowking-galarian': 199, 'stunfisk-galarian': 618,
    'tauros-paldean-combat': 128, 'tauros-paldean-blaze': 128, 'tauros-paldean-aqua': 128,
}


def norm(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', str(s).lower()).strip('-')


def expected_base_dex(row) -> int:
    pid = row['pokemon_id']
    if pid in MANUAL_BASE_BY_POKEMON_ID:
        return int(MANUAL_BASE_BY_POKEMON_ID[pid])
    dex = int(row['dex_id'])
    # OP.GG internal ids 10000+ usually indicate forms; fall back to current dex only when no manual exists.
    return dex


def expected_form_labels(row) -> list[str]:
    pid = row['pokemon_id']
    name = row.get('name_en', '')
    labels = ['']
    n = norm(pid)

    if n.startswith('mega-'):
        if n.endswith('-x'):
            return ['Mega X']
        if n.endswith('-y'):
            return ['Mega Y']
        return ['Mega']

    for key, label in FORM_SYNONYMS.items():
        if key in n:
            labels.append(label)

    # Name-based hints
    low_name = str(name).lower()
    if 'alolan' in low_name: labels.append('Alola')
    if 'galarian' in low_name: labels.append('Galar')
    if 'hisui' in low_name or 'hisuian' in low_name: labels.append('Hisui')
    if 'female' in low_name: labels.append('Female')
    if 'male' in low_name: labels.append('Male')

    # Unique while preserving order
    out=[]
    for x in labels:
        if x not in out:
            out.append(x)
    return out


def choose_sprite(raw_df, dex_base: int, labels: list[str], variant: str):
    sub = raw_df[(raw_df['variant'] == variant) & (raw_df['dex_id_base'] == dex_base)].copy()
    if sub.empty:
        return None, 'no_dex_match', 0

    # Exact label first
    for label in labels:
        label_norm = norm(label)
        candidates = sub[sub['sprite_form_label'].fillna('').map(norm) == label_norm]
        if not candidates.empty:
            return candidates.iloc[0].to_dict(), 'dex_form_exact', 100

    # Base form should prefer blank sprite label.
    if labels == [''] or labels[0] == '':
        blank = sub[sub['sprite_form_label'].fillna('') == '']
        if not blank.empty:
            return blank.iloc[0].to_dict(), 'dex_base_exact', 95

    # Loose contains
    for label in labels:
        if not label: continue
        label_norm = norm(label)
        candidates = sub[sub['sprite_form_label'].fillna('').map(lambda x: label_norm in norm(x) or norm(x) in label_norm)]
        if not candidates.empty:
            return candidates.iloc[0].to_dict(), 'dex_form_loose', 80

    # If only one sprite exists for that dex, use low confidence.
    if len(sub) == 1:
        return sub.iloc[0].to_dict(), 'dex_only_single_candidate', 60
    return None, 'ambiguous_or_missing_form', 0


def main():
    if not RAW_CSV.exists():
        raise SystemExit(f'Missing {RAW_CSV}. Run download_champions_menu_sprites.py first.')
    pokemon = pd.read_csv(POKEMON_CSV)
    raw = pd.read_csv(RAW_CSV)
    raw['sprite_form_label'] = raw['sprite_form_label'].fillna('')

    rows=[]
    matched_files=set()
    for _, p in pokemon.iterrows():
        base = expected_base_dex(p)
        labels = expected_form_labels(p)
        normal, method_n, conf_n = choose_sprite(raw, base, labels, 'normal')
        shiny, method_s, conf_s = choose_sprite(raw, base, labels, 'shiny')
        if normal: matched_files.add(normal['file_name'])
        if shiny: matched_files.add(shiny['file_name'])
        conf = max(conf_n, conf_s)
        method = method_n if conf_n >= conf_s else method_s
        rows.append({
            'pokemon_id': p['pokemon_id'],
            'dex_id': p['dex_id'],
            'sprite_base_dex': base,
            'pokemon_display_en': p.get('name_en',''),
            'pokemon_display_ko': p.get('name_ko',''),
            'expected_form_labels': ';'.join(labels),
            'sprite_file_normal': normal['file_name'] if normal else '',
            'sprite_path_normal': normal['relative_path'] if normal else '',
            'sprite_file_shiny': shiny['file_name'] if shiny else '',
            'sprite_path_shiny': shiny['relative_path'] if shiny else '',
            'sprite_source': 'bulbagarden_archives_champions_menu_sprites',
            'match_method': method,
            'match_confidence': conf,
            'notes': '' if conf >= 80 else 'review recommended',
        })

    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False, encoding='utf-8-sig')

    raw[~raw['file_name'].isin(matched_files)].to_csv(SPRITES/'unmatched_sprite_files.csv', index=False, encoding='utf-8-sig')
    out[out['match_confidence'] < 80].to_csv(SPRITES/'unmatched_pokemon.csv', index=False, encoding='utf-8-sig')

    print(f'DONE: {OUT_CSV}')
    print('Pokemon rows:', len(out))
    print('Matched normal:', int((out['sprite_file_normal'] != '').sum()))
    print('Matched shiny:', int((out['sprite_file_shiny'] != '').sum()))
    print('Review rows:', int((out['match_confidence'] < 80).sum()))


if __name__ == '__main__':
    main()
