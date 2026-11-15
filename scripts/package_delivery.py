"""Compacta somente os entregaveis, sem ferramentas locais ou credenciais."""
from pathlib import Path
import hashlib
import json
import zipfile

root=Path(__file__).resolve().parents[1]
destination=root/'output/nexahome-iot-security.zip'
excluded={'.git','.tools','.pio','tmp','__pycache__'}
files=[]
for path in root.rglob('*'):
    relative=path.relative_to(root)
    if any(part in excluded for part in relative.parts):
        continue
    if not path.is_file() or path.suffix.lower() in {'.zip','.pyc'}:
        continue
    if path.name in {'c_cpp_properties.json','launch.json'} or path.name.startswith('.browse.c_cpp.'):
        continue
    files.append(path)
with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for path in sorted(files):
        archive.write(path,'nexahome-iot-security/'+path.relative_to(root).as_posix())
with zipfile.ZipFile(destination) as archive:
    assert archive.testzip() is None
    names=archive.namelist()
    required=['README.md','diagram.json','wokwi.toml','firmware/manifest.json',
              'network/evidence/test-result.txt','output/relatorio-nexasense.pdf',
              'output/demonstracao-nexasense.mp4']
    for name in required:
        assert 'nexahome-iot-security/'+name in names,name
print(json.dumps({'zip':str(destination),'files':len(files),'bytes':destination.stat().st_size,
                  'sha256':hashlib.file_digest(destination.open('rb'),'sha256').hexdigest()},indent=2))
