"""Preserva a primeira compilacao; recusa sobrescrever a evidencia original."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import stat

root = Path(__file__).resolve().parents[1]
destination = root / 'firmware' / 'original'
if (root / 'firmware' / 'manifest.json').exists():
    raise SystemExit('Manifesto ja existe. Use verify_integrity.py; nao sobrescreva o original.')
destination.mkdir(parents=True, exist_ok=True)
build = root / '.pio' / 'build' / 'esp32dev'
files = [(build / name, name) for name in ['firmware.bin', 'firmware.elf', 'bootloader.bin', 'partitions.bin']]
files += [(root / 'src/main.cpp', 'main.cpp'), (root / 'platformio.ini', 'platformio.ini'),
          (root / 'diagram.json', 'diagram.json'), (root / 'wokwi.toml', 'wokwi.toml')]
entries = []
now = datetime.now(timezone.utc).isoformat()
for source, name in files:
    target = destination / name
    if target.exists():
        raise SystemExit(f'Ja existe: {target}. Verifique antes de continuar.')
    shutil.copy2(source, target)
    data = target.read_bytes()
    entries.append({'path': target.relative_to(root).as_posix(), 'size_bytes': len(data),
                    'sha256': hashlib.sha256(data).hexdigest(), 'preserved_utc': now})
    target.chmod(stat.S_IREAD)
(root / 'firmware' / 'working').mkdir(exist_ok=True)
shutil.copyfile(destination / 'firmware.bin', root / 'firmware' / 'working' / 'firmware.bin')
manifest = {'origin': 'Primeira compilacao local do firmware educacional NexaSense criado para esta atividade. '
                      'Nao e imagem obtida de produto comercial nem dump fisico.',
            'analysis_date': '2026-11-05', 'preserved_utc': now, 'files': entries}
(root / 'firmware' / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
lines = ['SHA-256 | tamanho em bytes | arquivo', 'Origem: ' + manifest['origin'], 'Preservado UTC: ' + now, '']
lines += [f"{item['sha256']} | {item['size_bytes']} | {item['path']}" for item in entries]
(root / 'firmware' / 'hashes.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
evidence = root / 'firmware' / 'evidence'
evidence.mkdir(exist_ok=True)
shutil.copyfile(root / '.tools' / 'build.log', evidence / 'build.log')
print('\n'.join(lines))
