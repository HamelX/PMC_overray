from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = APP_ROOT / 'data_pack' / 'upload_these_files'
STATE_FILE = APP_ROOT / 'state' / 'current_state.json'
DEFAULT_TARGET_WINDOW_TITLE = 'Pokémon Champions'
