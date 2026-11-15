"""Captura a UART virtual via encaminhamento RFC2217 do Wokwi."""
from datetime import datetime, timezone
from pathlib import Path
import time
import serial

root = Path(__file__).resolve().parents[1]
destination = root / 'hardware' / 'evidence' / 'uart-info.txt'
destination.parent.mkdir(parents=True, exist_ok=True)
with serial.serial_for_url('rfc2217://127.0.0.1:4000', baudrate=115200, timeout=1) as port:
    port.write(b'INFO\n')
    end = time.monotonic() + 12
    data = bytearray()
    while time.monotonic() < end:
        data.extend(port.read(4096))
text = data.decode(errors='replace')
destination.write_text('Captura real da UART virtual\nUTC: ' + datetime.now(timezone.utc).isoformat()
                       + '\nComando enviado: INFO\\n\n\n' + text, encoding='utf-8')
print(text)
assert 'LAB_ONLY_CONFIG' in text, 'Diagnostico nao recebido; verificar simulacao visivel.'
