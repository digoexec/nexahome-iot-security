"""Atualiza o relato a partir de artefatos existentes, sem inventar execucoes."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
def write(path, content):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + '\n', encoding='utf-8')

image = json.loads((root/'firmware/evidence/image-structure.json').read_text())
partitions = json.loads((root/'firmware/evidence/partitions.json').read_text())
has_http = (root/'network/evidence/test-result.txt').exists()
has_uart = (root/'hardware/evidence/uart-info.txt').exists()
has_video = (root/'output/demonstracao-nexasense.mp4').exists()
has_wokwi = (root/'hardware/evidence/wokwi-running.png').exists()
strings = (root/'firmware/evidence/interesting-strings.txt').read_text(encoding='utf-8').splitlines()
selected = [line for line in strings if any(t in line for t in ['LAB_ONLY', 'nexasense-lab', '/telemetry', '/debug', 'Wokwi-GUEST'])]
partition_rows = '\n'.join(f"| {p['label']} | {p['type']} | {p['subtype']} | {p['offset']} | {p['size']} |" for p in partitions)
write('firmware/analysis-notes.md', f'''
# Análise do firmware

## Origem e preservação

A primeira compilação local deste protótipo educacional foi preservada antes da análise em `original/`. Não foi fornecido firmware de produto comercial. O arquivo `manifest.json` registra nome, tamanho, origem, data e SHA-256; `hashes.txt` permite leitura simples. A cópia usada é `working/firmware.bin`. Os arquivos originais receberam o atributo somente leitura. Esse atributo evita alterações acidentais, mas não é proteção contra um administrador.

Imagem de aplicação: **{image['size']} bytes**. SHA-256: `{image['sha256']}`. Data da análise: 05/11/2026. A integridade da cópia é conferida antes da análise. O SHA-256 compara conteúdo; sozinho não prova origem confiável nem substitui assinatura digital.

## Formato e estrutura

Primeiro byte `{image['magic']}`, formato de imagem ESP32, {image['segment_count']} segmentos, entrada `{image['entry_address']}`. O script lê o cabeçalho de 24 bytes e os cabeçalhos de segmento de 8 bytes. O resultado completo está em `evidence/image-structure.json`.

O `.bin` é a aplicação, não um dump integral de 4 MiB. Bootloader e tabela de partições da compilação estão preservados separadamente. O Wokwi carrega a aplicação com sua configuração padrão; não se afirma que a flash efetiva do simulador foi extraída e comparada a esses arquivos.

| Partição da compilação | Tipo | Subtipo | Offset | Tamanho |
|---|---|---|---|---|
{partition_rows}

A existência de partições OTA ou SPIFFS na tabela padrão não prova que o aplicativo implemente atualização OTA ou use sistema de arquivos. O código não monta SPIFFS/LittleFS e não chama APIs de OTA. Configuração de alerta fica em RAM; constantes ficam na imagem. O framework pode usar NVS internamente, mas não foi realizado dump do NVS em execução.

## Bibliotecas e textos relevantes

O build usa Arduino ESP32, WiFi, WebServer, DHT 1.4.6 e Adafruit Unified Sensor 1.1.15. `platformio.ini` e `evidence/build.log` registram a resolução das dependências. Não foi feita análise de CVEs de todas as dependências; o build de laboratório não é uma recomendação de versão de produção.

Trechos encontrados diretamente no binário, com offsets em bytes:

```text
{chr(10).join(selected[:12])}
```

Esses textos identificam rede virtual, rotas, dispositivo e um marcador de configuração interno. A recuperação do marcador a partir do `.bin` é uma demonstração estática reproduzível de que constantes ficam legíveis em uma imagem sem proteção. O marcador é fictício, não uma senha, e o teste pressupõe posse autorizada da imagem. Isso não comprova extração de uma placa real.

## Atualização

O mecanismo observado no projeto é recompilar e carregar outro arquivo pela extensão. Não há endpoint de upload nem OTA implementada no aplicativo. Trocar um arquivo no computador não equivale a contornar Secure Boot de hardware. Para produção, propõem-se atualização assinada, autenticação do servidor, controle de versão e recuperação após falha. Nenhum eFuse foi programado.

Referência de formato: [Espressif App Image Format](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/app_image_format.html).
''')

write('network/protocol-analysis.md', f'''
# Análise das comunicações

## Situação da coleta

{'Coleta HTTP real concluída; consulte evidence/http-session.json e test-result.txt.' if has_http else 'PENDENTE: a simulação no VS Code ainda não foi executada e não há captura de tráfego. A descrição abaixo decorre da inspeção do código e da configuração, não de uma sessão observada.'}

## Fluxos e protocolos

O cliente de teste conecta a 127.0.0.1:8180. O gateway incluído na extensão encaminha para a porta TCP/80 do ESP32 virtual. O IP virtual efetivo deve ser obtido dos logs do simulador, sem presumir um endereço de placa física. O firmware associa-se à rede virtual aberta Wokwi-GUEST, por DHCP, e recebe requisições HTTP. Não implementa MQTT, NTP, nuvem, envio de e-mail ou requisições a serviços externos.

| Rota | Dado ou operação | Autenticação no código | Confidencialidade e integridade |
|---|---|---|---|
| GET /telemetry | JSON com identificador, temperatura, umidade, limite e estado do alerta | Ausente | HTTP, sem TLS |
| GET /debug | Versão e configuração fictícia | Ausente | HTTP, sem TLS |
| GET /config?threshold=10 | Altera o limite do alerta | Ausente | HTTP, sem TLS; muda estado por GET |

O firmware valida faixa e formato do parâmetro, mas validação de entrada não substitui autorização. O identificador divulgado permite reconhecer o dispositivo, mas não é segredo. Em uma instalação real, séries de temperatura e umidade podem revelar padrões de uso de um ambiente. A integridade TCP protege contra erros acidentais e não autentica mensagens contra adversários.

## Procedimento reproduzível

Com a aba do Wokwi visível e o sensor em 24 °C/50%, executar `scripts/capture_http.py`. O script salva os bytes enviados e recebidos sem cabeçalho Authorization, consulta o estado inicial, lê /debug, muda o limite de 30 para 10, consulta o alerta, testa uma entrada inválida e restaura o limite para 30. Os testes confirmam o comportamento ou falham explicitamente; não produzem resultado de sucesso sem conexão real.

Essa coleta registra HTTP na camada de aplicação. Não é PCAP, não mede segurança de rádio Wi-Fi, não demonstra interceptação de um terceiro e não confirma resistência a ataque de intermediário. Como não há TLS no cliente nem no servidor, a análise do código e dos bytes pode comprovar ausência de proteção de transporte nesta sessão, quando executada.

Para um produto comercial, usar HTTPS validando certificados, identidade individual e autorização nas rotas; limitar acesso à rede de manutenção. A rede aberta virtual do Wokwi é uma condição do laboratório e não comprova que um produto comercial use Wi-Fi aberto.
''')

uart_status = 'confirmado pela captura UART virtual' if has_uart else 'identificado no código; captura UART pendente'
http_status = 'confirmado por requisições e respostas reais' if has_http else 'identificado no código; execução HTTP pendente'
write('findings/findings.md', f'''
# Achados e classificação de riscos

## Critério

Escala simples, sem pretensão de CVSS: impacto e probabilidade de 1 a 3 (baixo, médio, alto). Risco = impacto × probabilidade: 1-2 baixo, 3-4 médio, 6-9 alto. O impacto considera um monitor ambiental com LED, não equipamento médico ou de segurança de pessoas. A probabilidade pressupõe acesso físico para UART ou alcance à rede do dispositivo para HTTP. O loopback restringe a exposição deste laboratório.

| Achado | Evidência e situação | Impacto | Probabilidade | Risco | Recomendação |
|---|---|---|---|---|---|
| F01 Diagnóstico excessivo em UART e /debug | `src/main.cpp`, `firmware/evidence/interesting-strings.txt`; UART {uart_status}; HTTP {http_status} | Médio 2: revela detalhes internos úteis ao reconhecimento | Média 2: exige acesso serial ou à rede | Médio 4 | Reduzir logs e remover diagnóstico público de produção |
| F02 Configuração de alerta sem autorização | Handler /config no código; {http_status} | Médio 2: altera integridade e confiabilidade do alerta | Alta 3: uma chamada basta para cliente que alcança a rota | Alto 6 | Autenticar, autorizar e usar POST/PUT com validação e proteção de sessão |
| F03 Telemetria e controle por HTTP sem TLS | WebServer(80), encaminhamento em `wokwi.toml`; {http_status} | Médio 2: dados e comandos expostos a observação/manipulação na rede sob ameaça | Alta 3: uso rotineiro do canal sem proteção em rede acessível ao adversário | Alto 6 | HTTPS com verificação de certificado e identidade individual |

## Encadeamento dos achados

F01: código e strings mostram diagnóstico -> divulgação de detalhes -> adversário com acesso físico ou de rede reconhece versão e configuração -> facilita preparação de ataques -> risco médio -> remover detalhes sem utilidade operacional. Não há segredo real exposto e nenhuma escalação foi comprovada.

F02: /config não chama autenticação -> qualquer cliente que alcance a rota pode ajustar o limite -> alteração do critério do alerta -> redução de confiança do monitor -> risco alto no contexto de implantação proposto -> autorização por função e auditoria. O ensaio previsto troca 30 por 10 e restaura; o impacto demonstrável limita-se ao alerta virtual.

F03: servidor HTTP simples -> falta de proteção criptográfica de transporte -> um adversário em posição de rede pode observar ou modificar fluxos -> afeta confidencialidade/integridade -> risco alto na rede de implantação considerada -> TLS corretamente configurado. Interceptação ativa não foi ensaiada. O risco não implica que terceiros remotos tenham acesso à porta loopback deste computador.

## Relação com referências

F01 se relaciona às áreas de interfaces internas UART e serviços de troca de dados do OWASP ISTG e às capacidades de acesso lógico a interfaces e proteção de dados do NIST IR 8259A. F02 se relaciona à capacidade de configuração do dispositivo e de acesso lógico a interfaces. F03 se relaciona à proteção de dados e à análise de serviços/comunicação do ISTG. São relações conceituais dos achados; não são declarações de conformidade.

## Itens que não são vulnerabilidades confirmadas

JTAG acessível, falta de Secure Boot, ausência de Flash Encryption, leitura de NVS e comprometimento de atualização não foram comprovados em placa física. A imagem contém constantes legíveis, mas o teste usa uma cópia já autorizada. A presença de uma string ou biblioteca OTA não comprova rota de atualização explorável. Não foram realizados brute force, varredura de rede, negação de serviço, glitching ou programação de eFuses.
''')

write('requirements-checklist.md', f'''
# Cobertura dos requisitos

Este quadro é um registro de cobertura, não uma declaração de que um teste planejado foi executado.

| Requisito do enunciado | Entrega ou evidência | Situação |
|---|---|---|
| Descrição, MCU, memória, sensores, alimentação e armazenamento | architecture/ e hardware/interface-map.md | Documentado |
| Diagrama e mapa da superfície de ataque | architecture/architecture-diagram.png e architecture.md | Concluído |
| Preservação antes de alteração, origem, tamanho, data e SHA-256 | firmware/original/, manifest.json, hashes.txt, verify_integrity.py | Concluído |
| Formato, segmentos, partições, bibliotecas, textos e parâmetros | firmware/analysis-notes.md e evidence/ | Análise estática concluída |
| Interfaces físicas, UART e JTAG quando presente | hardware/interface-map.md | Mapeamento documentado; UART {'coletada' if has_uart else 'pendente'}; JTAG não ensaiado |
| Mecanismo de atualização | firmware/analysis-notes.md | Recarga local identificada; OTA ausente na aplicação |
| Comunicação, origem/destino, protocolos e controles | network/protocol-analysis.md | {'HTTP coletado e testado' if has_http else 'Inspeção de código concluída; coleta HTTP pendente'} |
| Demonstração controlada | Extração do marcador fictício de firmware/evidence/interesting-strings.txt | Concluída estaticamente; {'demonstração HTTP concluída' if has_http else 'demonstração dinâmica pendente'} |
| Evidência, ameaça, impacto, probabilidade e risco | findings/findings.md | Classificação contextual; status de confirmação explícito |
| Relação com referência reconhecida | findings/findings.md e references.md | OWASP ISTG, NIST e Espressif |
| Mitigações e hardening comercial | remediation/hardening-plan.md | Concluído conceitualmente; sem eFuses |
| Exemplo real pesquisado | references.md, AR2023-005/CVE-2023-35818 | Concluído; não reproduzido |
| README com escopo e reprodução | README.md | Concluído |
| Relatório técnico PDF | output/relatorio-nexasense.pdf | {'Gerado; revisão visual registrada em validation.md' if (root/'output/relatorio-nexasense.pdf').exists() else 'Pendente de geração'} |
| Utilização da extensão Wokwi no VS Code | hardware/evidence/wokwi-running.png | {'Execução registrada' if has_wokwi else 'PENDENTE de confiança da pasta e eventual licença pelo usuário'} |
| Vídeo de até 4 minutos | output/ | {'Vídeo local gerado; publicação pelo aluno' if has_video else 'PENDENTE da execução da simulação; roteiro preparado'} |

As capturas UART/HTTP, as imagens de execução e o trecho do vídeo vêm do laboratório real no Wokwi. O vídeo é entregue como arquivo local. Se a instituição exigir hospedagem, publicar esse arquivo na plataforma aceita e registrar o link no README. JTAG e mecanismos irreversíveis de hardware permanecem propostas conceituais conforme o escopo permitido.
''')
print('Documentacao atualizada. HTTP:', has_http, 'UART:', has_uart, 'Wokwi:', has_wokwi, 'video:', has_video)
