import csv, json
from pathlib import Path
from .models import Move, Pokemon

REQUIRED = [
 '13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv','14_POKEMON_INDEX_FULL_CLEAN.csv','15_MOVES_LINKED_FULL_CLEAN.csv',
 '16_ITEMS_FULL_CLEAN.csv','17_ABILITIES_FULL_CLEAN.csv','11_POKEMON_PROFILES_FULL_CLEAN.jsonl']

class DataLoadError(RuntimeError): pass

def _norm_row(row):
    return {k.lstrip('\ufeff'): v for k,v in row.items()}

def _read_csv(path: Path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return [_norm_row(r) for r in csv.DictReader(f)]

def _int(v):
    try: return int(v)
    except Exception: return 0

class ChampionsData:
    def __init__(self, data_dir: Path | str = None):
        self.data_dir = Path(data_dir or Path.cwd()/'data_pack'/'upload_these_files')
        self.pokemon: dict[str, Pokemon] = {}
        self.moves: dict[str, Move] = {}
        self.items = {}; self.abilities = {}; self.alias: dict[str, str] = {}

    def validate(self):
        missing=[f for f in REQUIRED if not (self.data_dir/f).exists()]
        if missing:
            raise DataLoadError('필수 데이터 파일이 없습니다: '+', '.join(missing)+f'\n데이터 위치: {self.data_dir}')

    def load(self):
        self.validate()
        move_meta = {}
        for r in _read_csv(self.data_dir/'15_MOVES_LINKED_FULL_CLEAN.csv'):
            m=Move(r['move_id'],r['move_name_en'],r['move_name_ko'],r['move_type'],r['move_type_ko'],r['category'],r['category_ko'],r.get('power',''),r.get('accuracy',''),r.get('priority',''),r.get('description_ko',''))
            self.moves[m.id]=m; move_meta[m.id]=m
        moves_by_poke={}
        for r in _read_csv(self.data_dir/'13_POKEMON_MOVES_OPGG_VERIFIED_KO_FULL.csv'):
            mid=r['move_id']; m=move_meta.get(mid) or Move(mid,r['move_name_en'],r['move_name_ko'],r['move_type'],r['move_type_ko'],r['category'],r['category_ko'])
            moves_by_poke.setdefault(r['pokemon_id'], []).append(m)
        for r in _read_csv(self.data_dir/'14_POKEMON_INDEX_FULL_CLEAN.csv'):
            types=tuple(t for t in [r.get('type1',''),r.get('type2','')] if t)
            types_ko=tuple(t for t in [r.get('type1_ko',''),r.get('type2_ko','')] if t)
            stats={k:_int(r.get(k)) for k in ['hp','atk','def','spa','spd','spe','total']}
            p=Pokemon(r['pokemon_id'],r['dex_id'],r['name_en'],r['name_ko'],types,types_ko,tuple(filter(None,r.get('abilities','').split(';'))),stats,tuple(moves_by_poke.get(r['pokemon_id'],[])))
            self.pokemon[p.id]=p
            for a in [p.id,p.name_en.lower(),p.name_ko.lower()]: self.alias[a]=p.id
        for r in _read_csv(self.data_dir/'16_ITEMS_FULL_CLEAN.csv'): self.items[r['item_id']]=r
        for r in _read_csv(self.data_dir/'17_ABILITIES_FULL_CLEAN.csv'): self.abilities[r['ability_id']]=r
        return self

    def search_pokemon(self, text: str, limit=20):
        q=(text or '').strip().lower()
        if not q: return list(self.pokemon.values())[:limit]
        ids=[]
        for p in self.pokemon.values():
            if q in p.name_ko.lower() or q in p.name_en.lower() or q in p.id: ids.append(p.id)
        return [self.pokemon[i] for i in ids[:limit]]

    def get_pokemon(self, name_or_id: str):
        key=(name_or_id or '').strip().lower()
        pid=self.alias.get(key)
        if pid: return self.pokemon[pid]
        hits=self.search_pokemon(key,1)
        return hits[0] if hits else None
