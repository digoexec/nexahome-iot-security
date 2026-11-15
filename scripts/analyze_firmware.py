"""Analise simples e reproduzivel da copia, sem alterar o original."""
from pathlib import Path
import hashlib
import json
import re
import struct

root = Path(__file__).resolve().parents[1]
original = root / 'firmware' / 'original' / 'firmware.bin'
working = root / 'firmware' / 'working' / 'firmware.bin'
data = working.read_bytes()
assert hashlib.sha256(data).digest() == hashlib.sha256(original.read_bytes()).digest()
out = root / 'firmware' / 'evidence'
out.mkdir(parents=True, exist_ok=True)
header = {'magic': hex(data[0]), 'segment_count': data[1], 'spi_mode': data[2],
          'entry_address': hex(struct.unpack_from('<I', data, 4)[0]), 'size': len(data),
          'sha256': hashlib.sha256(data).hexdigest()}
assert data[0] == 0xE9
segments = []
offset = 24
for i in range(data[1]):
    address, size = struct.unpack_from('<II', data, offset)
    segments.append({'index': i, 'header_offset': hex(offset), 'load_address': hex(address), 'size': size})
    offset += 8 + size
header['segments'] = segments
(out / 'image-structure.json').write_text(json.dumps(header, indent=2), encoding='utf-8')
interesting = []
for match in re.finditer(rb'[\x20-\x7e]{5,}', data):
    value = match.group().decode('ascii')
    if any(item in value for item in ['NexaSense', 'nexasense', 'LAB_ONLY', '/telemetry', '/debug',
                                     'threshold', 'Wokwi-GUEST', 'HTTP', 'UART', '1.0.0-lab']):
        interesting.append(f'0x{match.start():08x}  {value}')
(out / 'interesting-strings.txt').write_text('\n'.join(interesting) + '\n', encoding='utf-8')
partition_data = (root / 'firmware' / 'original' / 'partitions.bin').read_bytes()
partitions = []
for position in range(0, len(partition_data) - 31, 32):
    magic, ptype, subtype, poffset, size, label, flags = struct.unpack_from('<HBBII16sI', partition_data, position)
    if magic != 0x50AA:
        break
    partitions.append({'label': label.split(b'\0')[0].decode(), 'type': hex(ptype), 'subtype': hex(subtype),
                       'offset': hex(poffset), 'size': hex(size), 'flags': flags})
(out / 'partitions.json').write_text(json.dumps(partitions, indent=2), encoding='utf-8')
print(json.dumps(header, indent=2))
print(json.dumps(partitions, indent=2))
print('\n'.join(interesting[:25]))
