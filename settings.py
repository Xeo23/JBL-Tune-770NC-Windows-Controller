import json, os, re
from pathlib import Path

APP_DIR = Path(os.environ.get('APPDATA', str(Path.home()))) / 'JBLTune770NC'
CONFIG_FILE = APP_DIR / 'config.json'

def load_config():
    try:
        obj = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        if isinstance(obj, dict):
            return obj
    except (OSError, ValueError):
        pass
    return {'bluetooth_address': ''}

def save_address(address):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({'bluetooth_address': address}, indent=2), encoding='utf-8')

def normalize_address(value):
    value = value.strip().replace('-', ':').upper()
    if not re.fullmatch(r'(?:[0-9A-F]{2}:){5}[0-9A-F]{2}', value):
        raise ValueError('Enter a valid MAC address, e.g. 88:92:CC:D9:90:7D.')
    return value
