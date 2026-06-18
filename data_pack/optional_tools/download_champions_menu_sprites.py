
"""
Download Pokémon Champions menu sprites from Bulbagarden Archives.

Outputs:
  ../sprites/champions_menu/normal/*.png
  ../sprites/champions_menu/shiny/*.png
  ../sprites/champions_menu/champions_menu_sprites_raw.csv

Install:
  pip install requests beautifulsoup4 pandas

Run:
  python download_champions_menu_sprites.py
"""
from __future__ import annotations

import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin, unquote

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'sprites' / 'champions_menu'
NORMAL_DIR = OUT / 'normal'
SHINY_DIR = OUT / 'shiny'
NORMAL_DIR.mkdir(parents=True, exist_ok=True)
SHINY_DIR.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'PokemonChampionsStrategyPack/2.1 personal data archive tool (contact: local user)'
})

CATEGORIES = [
    ('normal', 'https://archives.bulbagarden.net/wiki/Category:Champions_menu_sprites'),
    ('shiny', 'https://archives.bulbagarden.net/wiki/Category:Champions_Shiny_menu_sprites'),
]

FILE_RE = re.compile(r'Menu CP (\d{4})(?:-([^\.]+?))?(?: shiny)?\.png$', re.I)


def get(url: str) -> requests.Response:
    for i in range(4):
        r = SESSION.get(url, timeout=30)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(2 + i * 2)
            continue
        r.raise_for_status()
        return r
    r.raise_for_status()
    return r


def parse_category(category_url: str):
    seen_pages = set()
    queue = [category_url]
    files = []
    while queue:
        url = queue.pop(0)
        if url in seen_pages:
            continue
        seen_pages.add(url)
        print(f'[category] {url}')
        soup = BeautifulSoup(get(url).text, 'html.parser')

        # File links
        for a in soup.select('a[href^="/wiki/File:Menu_CP_"]'):
            title = a.get('title') or a.get_text(' ', strip=True)
            href = a.get('href')
            if not href:
                continue
            # title can be 'File:Menu CP 0006.png'
            file_name = title.replace('File:', '').strip()
            if FILE_RE.search(file_name):
                files.append({'file_name': file_name, 'file_page_url': urljoin(url, href)})

        # Pagination links: previous/next page are normal anchors on MediaWiki category pages.
        for a in soup.find_all('a'):
            text = a.get_text(' ', strip=True).lower()
            href = a.get('href')
            if href and 'pagefrom=' in href and ('next page' in text or 'previous page' in text or '다음' in text or '이전' in text):
                next_url = urljoin(url, href)
                if next_url not in seen_pages and next_url not in queue:
                    queue.append(next_url)
    # de-duplicate
    out = []
    seen = set()
    for item in files:
        if item['file_name'] not in seen:
            seen.add(item['file_name'])
            out.append(item)
    return out


def find_original_png(file_page_url: str) -> str | None:
    soup = BeautifulSoup(get(file_page_url).text, 'html.parser')
    # MediaWiki original file link often appears in fullMedia / internal anchors.
    candidates = []
    for a in soup.find_all('a'):
        href = a.get('href') or ''
        if '.png' in href.lower() and ('/archive/' not in href.lower()):
            candidates.append(urljoin(file_page_url, href))
    # prefer upload.wikimedia/bulbagarden style full image URLs
    for c in candidates:
        if '/thumb/' not in c and c.lower().endswith('.png'):
            return c
    for c in candidates:
        if c.lower().endswith('.png'):
            return c
    return None


def parse_file_meta(file_name: str) -> dict:
    m = FILE_RE.search(file_name)
    if not m:
        return {}
    dex = m.group(1)
    form = m.group(2) or ''
    shiny = ' shiny.png' in file_name.lower()
    return {
        'dex_4': dex,
        'dex_id_base': int(dex),
        'sprite_form_label': form,
        'is_shiny': int(shiny),
    }


def main():
    rows = []
    for variant, url in CATEGORIES:
        files = parse_category(url)
        print(f'[{variant}] category files: {len(files)}')
        for idx, item in enumerate(files, 1):
            file_name = item['file_name']
            target_dir = SHINY_DIR if variant == 'shiny' else NORMAL_DIR
            target = target_dir / file_name
            print(f'  [{idx}/{len(files)}] {file_name}')
            image_url = None
            if not target.exists():
                image_url = find_original_png(item['file_page_url'])
                if image_url:
                    img = get(image_url).content
                    target.write_bytes(img)
                    time.sleep(0.08)
            meta = parse_file_meta(file_name)
            rows.append({
                'variant': variant,
                'file_name': file_name,
                'relative_path': str(target.relative_to(ROOT)).replace('\\','/'),
                'file_page_url': item['file_page_url'],
                'image_url': image_url or '',
                **meta,
            })

    raw_csv = OUT / 'champions_menu_sprites_raw.csv'
    with raw_csv.open('w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['variant','file_name','relative_path','file_page_url','image_url','dex_4','dex_id_base','sprite_form_label','is_shiny']
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f'DONE: {raw_csv}')
    print('Next: python build_sprite_manifest_champions_menu.py')


if __name__ == '__main__':
    main()
