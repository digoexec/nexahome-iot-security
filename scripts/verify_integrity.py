"""Confere todas as evidencias preservadas contra o manifesto inicial."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'firmware' / 'manifest.json').read_text(encoding='utf-8'))
for item in manifest['files']:
    file = root / item['path']
    data = file.read_bytes()
    assert len(data) == item['size_bytes'], item['path']
    assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    print('OK', item['path'])
