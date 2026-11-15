# Arquitetura e fronteiras de confiança

O NexaSense didático usa um ESP32 DevKit v1 com DHT22 em GPIO15, LED em GPIO2, flash virtual e UART0. O DHT22 fornece temperatura e umidade a cada 2,5 segundos. O firmware mantém as leituras e o limite do alerta em RAM.

A versão criada funciona como servidor HTTP. Um cliente local representa a plataforma de monitoramento e consulta JSON em `/telemetry`. O encaminhamento da extensão liga localhost:8180 à porta 80 do ESP32 virtual. Não existe broker MQTT nem nuvem neste projeto. Essa adaptação atende ao ambiente equivalente permitido pelo enunciado.

## Fronteiras

1. Sensor para MCU: sinais de uma origem física sem autenticação; manipulação de sensor fica fora dos ensaios.
2. Memória e firmware: imagem e strings disponíveis ao analista que possui a cópia autorizada; não equivale a provar extração de placa protegida.
3. Acesso físico e UART: leitura de diagnóstico para quem consegue conectar ao dispositivo. Nesta atividade a UART é virtual, encaminhada por RFC2217.
4. Rede e aplicação: clientes que alcançam o HTTP podem consultar e alterar parâmetros sem controle de acesso no protótipo.
5. Desenvolvimento e atualização: compilador e arquivos locais determinam a imagem carregada. O simulador não é uma cadeia de confiança de produção.

## Superfície de ataque

| Superfície | Ativo | Acesso necessário | Situação avaliada |
|---|---|---|---|
| UART0 e logs | Configuração e identificação | Acesso serial; em produto real, acesso físico | Diagnóstico excessivo confirmado na captura UART virtual |
| HTTP /telemetry | Temperatura, umidade e identificador | Acesso à rede do dispositivo | HTTP legível e sem autenticação confirmado na sessão local |
| HTTP /debug | Configuração interna fictícia | Acesso à rede do dispositivo | Diagnóstico obtido sem autenticação na sessão local |
| HTTP /config | Limite e integridade do alerta | Acesso à rede do dispositivo | Limite alterado de 30 para 10 e restaurado, sem autenticação |
| Imagem e flash | Código, bibliotecas e parâmetros | Cópia autorizada ou eventual extração física | Análise da imagem compilada; extração física não testada |
| JTAG e download UART | Execução e memória | Placa e ferramentas adequadas | Potenciais; sem comprovação de exploração |
| Atualização | Integridade do software | Ambiente de compilação/recarga | Recarga local, sem OTA no aplicativo |

Uma interface potencial não recebe automaticamente a classificação de vulnerabilidade. As conclusões dependem das evidências e das condições descritas em `findings/findings.md`.
