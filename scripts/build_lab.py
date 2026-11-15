"""Compila e preserva a primeira imagem sem sobrescrever evidencias existentes."""
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
log=root/'.tools/build.log'
log.parent.mkdir(exist_ok=True)
print('Compilando com PlatformIO...',flush=True)
with log.open('w',encoding='utf-8') as stream:
    result=subprocess.run([sys.executable,'-m','platformio','run'],cwd=root,stdout=stream,stderr=subprocess.STDOUT)
if result.returncode:
    print(log.read_text(encoding='utf-8',errors='replace')[-6000:])
    raise SystemExit(result.returncode)
for script in (['preserve_firmware.py'] if not (root/'firmware/manifest.json').exists() else []) + [
        'verify_integrity.py','analyze_firmware.py','build_documentation.py']:
    subprocess.run([sys.executable,str(root/'scripts'/script)],cwd=root,check=True)
print('Compilacao, preservacao e analise estatica concluidas.',flush=True)
