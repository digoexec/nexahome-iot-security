"""Registra HTTP real e testa apenas o ESP32 virtual em 127.0.0.1:8180."""
from datetime import datetime, timezone
from pathlib import Path
import json
import socket

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'network' / 'evidence'

def request(path):
    # Destino fixo: nao aceita endereco de terceiros como argumento.
    raw = f'GET {path} HTTP/1.1\r\nHost: localhost:8180\r\nConnection: close\r\n\r\n'.encode()
    with socket.create_connection(('127.0.0.1', 8180), timeout=15) as connection:
        connection.settimeout(15)
        connection.sendall(raw)
        response = b''
        while True:
            block = connection.recv(4096)
            if not block:
                break
            response += block
            # O gateway pode encerrar a conexao com reset. Content-Length
            # permite reconhecer o fim da resposta antes desse fechamento.
            if b'\r\n\r\n' in response:
                header, body = response.split(b'\r\n\r\n', 1)
                lengths = [line.split(b':', 1)[1].strip() for line in header.split(b'\r\n')
                           if line.lower().startswith(b'content-length:')]
                if lengths and len(body) >= int(lengths[0]):
                    break
    return raw, response

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    steps = [('01-before', '/telemetry'), ('02-debug', '/debug'),
             ('03-change', '/config?threshold=10'), ('04-after', '/telemetry'),
             ('05-invalid', '/config?threshold=abc'), ('06-restore', '/config?threshold=30')]
    for name, path in steps:
        raw, response = request(path)
        (OUT / f'{name}-request.http').write_bytes(raw)
        (OUT / f'{name}-response.http').write_bytes(response)
        records.append({'step': name, 'utc': datetime.now(timezone.utc).isoformat(),
                        'request': raw.decode(), 'response': response.decode(errors='replace')})
        print(name, response.decode(errors='replace'))
    (OUT / 'http-session.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    before = json.loads(records[0]['response'].split('\r\n\r\n', 1)[1])
    after = json.loads(records[3]['response'].split('\r\n\r\n', 1)[1])
    assert before['threshold'] == 30 and before['alert'] is False
    assert after['threshold'] == 10 and after['alert'] is True
    assert '200 OK' in records[1]['response']
    assert 'LAB_ONLY_CONFIG' in records[1]['response']
    assert '400 Bad Request' in records[4]['response']
    assert '"threshold":30.0' in records[5]['response']
    (OUT / 'test-result.txt').write_text(
        'PASS: HTTP real sem Authorization e sem TLS; configuracao alterada de 30 para 10; '
        'alerta false -> true; entrada invalida rejeitada; limite restaurado para 30.\n', encoding='utf-8')

if __name__ == '__main__':
    main()
