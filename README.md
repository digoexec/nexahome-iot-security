# Avaliação de segurança do NexaSense no Wokwi

Trabalho de Hardware Hacking e IoT. Projeto simples em C++ com ESP32, DHT22 e LED de alerta. O protótipo contém condições inseguras intencionais para uma avaliação de laboratório. Não é firmware de produção.

## Objetivo e escopo

Relacionar hardware, firmware, comunicação, evidências, riscos e correções antes de um piloto comercial fictício da NexaHome. A montagem foi criada para este trabalho porque não foi fornecida uma imagem original de um produto real.

Somente o ESP32 virtual deste projeto e as portas locais encaminhadas pelo Wokwi estão no escopo. Não testar outros dispositivos, endereços de terceiros ou redes de produção. O firmware não envia requisições para a Internet. Todos os identificadores e o marcador `LAB_ONLY_CONFIG_nao_e_segredo_real` são fictícios; não existem senhas ou tokens reais neste projeto.

## Arquitetura

```text
DHT22 (GPIO15) --> ESP32 --> LED de alerta (GPIO2)
                    |
                    +-- Flash: firmware e partições
                    +-- RAM: leituras e limite de alerta
                    +-- UART0: diagnóstico em 115200 baud
                    +-- Wi-Fi virtual Wokwi-GUEST
                              |
                       HTTP servidor porta 80
                              |
                       gateway da extensão
                              |
                   cliente local 127.0.0.1:8180
```

A plataforma de monitoramento é representada por um cliente local que consulta a telemetria. Essa adaptação evita usar nuvem ou broker de terceiros. A arquitetura mantém sensor, firmware, flash, UART e comunicação de rede. O arquivo `architecture/architecture-diagram.png` apresenta o diagrama visual.

## Ferramentas

VS Code, Wokwi Simulator, PlatformIO Core, framework Arduino para ESP32, biblioteca DHT da Adafruit e Python para hashes, análise binária e captura de HTTP/UART. Versões e resultados efetivos ficam nas evidências e no relatório. As dependências de compilação estão fixadas em `platformio.ini`.

## Abrir e executar no VS Code

1. Abra esta pasta inteira no VS Code. Se estiver em Restricted Mode, revise a pasta e marque-a como confiável para usar extensões.
2. Instale Wokwi Simulator e PlatformIO IDE. A licença da extensão Wokwi deve ser ativada pela própria conta do usuário em **F1 > Wokwi: Request a New License**. Não inclua a licença no repositório.
3. A imagem preservada em `firmware/original/` é a usada por `wokwi.toml`. Não precisa recompilar para reproduzir a avaliação.
4. Use **F1 > Wokwi: Start Simulator** e mantenha a aba do simulador visível. Espere aparecer HTTP pronto e a primeira leitura do sensor, configurado para 24 °C e 50%.
5. Acesse [telemetria local](http://localhost:8180/telemetry). O gateway é incluído pela extensão; não exponha a porta à Internet.
6. Para repetir a demonstração, use os scripts abaixo. Eles têm destino fixo no loopback e restauram o limite após a coleta.

```powershell
# Ambiente Python local deste computador
.\.tools\venv\Scripts\python.exe scripts\verify_integrity.py
.\.tools\venv\Scripts\python.exe scripts\analyze_firmware.py
.\.tools\venv\Scripts\python.exe scripts\capture_serial.py
.\.tools\venv\Scripts\python.exe scripts\capture_http.py
```

Em outro computador, instale Python e PlatformIO, crie o ambiente e instale pyserial. Os scripts de integridade, análise binária e HTTP usam somente a biblioteca padrão do Python. O de serial usa `pyserial==3.5`.

```powershell
py -m venv .tools\venv
.\.tools\venv\Scripts\python.exe -m pip install platformio==6.2.0 pyserial==3.5
.\.tools\venv\Scripts\python.exe -m platformio run
```

Compilar gera `.pio/build/esp32dev/firmware.bin` e `.elf`; isso não substitui a imagem original preservada. Para experimentar alterações, aponte firmware/elf em uma cópia de `wokwi.toml` para a saída `.pio`. O atalho Ctrl+Shift+B executa a tarefa de compilação local.

## Demonstração controlada

O limite inicial do alerta é 30 °C. Com o sensor em 24 °C, o alerta fica desligado. Uma chamada sem usuário, senha ou cabeçalho Authorization a `/config?threshold=10` muda o limite e acende o alerta. A chamada `/config?threshold=30` restaura o estado. O teste não mede indisponibilidade real nem aciona equipamento físico.

O comando serial `INFO` e a rota `/debug` mostram o identificador, versão e configuração fictícia. A fragilidade é o comportamento de divulgar detalhes internos sem necessidade. O marcador fictício não é uma credencial válida e sua presença não demonstra roubo de segredo real.

## Organização das evidências

| Pasta | Conteúdo |
|---|---|
| `architecture/` | Diagrama e fronteiras de confiança |
| `firmware/original/` | Primeira compilação preservada, fonte e configurações |
| `firmware/working/` | Cópia binária para análise |
| `firmware/evidence/` | Estrutura, partições, strings com offsets e registro de compilação |
| `hardware/` | Mapa das interfaces e captura UART virtual |
| `network/` | Análise e requisições/respostas HTTP realmente coletadas |
| `findings/` | Achados, critérios de risco e limites das conclusões |
| `remediation/` | Prioridades e critérios de aceitação do hardening |
| `scripts/` | Coleta local e verificações reproduzíveis |
| `output/` | Relatório e vídeo de apresentação |

## Resumo da avaliação

Firmware: foram analisados a imagem de aplicação ESP32, as strings e a tabela de partições. O `.bin` da aplicação não deve ser confundido com dump integral da flash. O hash inicial registra integridade, não autenticidade. Não há filesystem montado pela aplicação nem implementação de OTA; atualização didática ocorre por recompilação e recarga no simulador.

Hardware: UART0 expõe diagnóstico. JTAG, flash SPI, programação e alimentação são discutidos com limites explícitos. A avaliação virtual não comprova leitura de memória por JTAG ou extração física da flash.

Protocolos: o DHT22 usa protocolo próprio; UART usa 115200 baud; o servidor usa HTTP em TCP/80 sobre a rede virtual. Identificar HTTP sozinho não basta: é necessário examinar o conteúdo, o transporte e os controles de acesso de cada rota. A coleta salva bytes de aplicação, não uma captura PCAP de Wi-Fi.

Principais problemas investigados: diagnóstico excessivo, configuração sem autorização e exposição de dados em HTTP sem TLS. As recomendações são restringir diagnóstico, autenticar/autorizar, adotar TLS e planejar armazenamento e atualização seguros. Consulte `findings/findings.md` para separar evidências efetivas de riscos apenas propostos.

## Entregas e vídeo

Relatório: [avaliação técnica em PDF](output/relatorio-nexasense.pdf). Vídeo: [demonstração legendada](output/demonstracao-nexasense.mp4), com duração inferior a quatro minutos. O trecho de execução usa capturas reais da janela do VS Code, aproximadamente um quadro por segundo, com os intervalos preservados. O LED foi observado desligado, ligado e novamente desligado após a restauração. A identificação da conta foi ocultada no cabeçalho. O registro de origem está em `hardware/evidence/video-provenance.json`.

O projeto, o firmware preservado e as evidências são entregues neste repositório. O relatório PDF e o vídeo MP4 podem ser baixados diretamente pelos links acima. Se a instituição exigir uma plataforma de streaming, o vídeo pode ser publicado como não listado e o link acrescentado aqui.

As referências e o caso real estão em [references.md](references.md). A cobertura de cada requisito está em [requirements-checklist.md](requirements-checklist.md).
