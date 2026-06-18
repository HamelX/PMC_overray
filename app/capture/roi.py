import json
from pathlib import Path

def save_roi(path: str | Path, x:int, y:int, width:int, height:int):
    data={'x':x,'y':y,'width':width,'height':height}
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    return data

def load_roi(path: str | Path):
    return json.loads(Path(path).read_text(encoding='utf-8'))
