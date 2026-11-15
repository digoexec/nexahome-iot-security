# Análise do firmware

## Origem e preservação

A primeira compilação local deste protótipo educacional foi preservada antes da análise em `original/`. Não foi fornecido firmware de produto comercial. O arquivo `manifest.json` registra nome, tamanho, origem, data e SHA-256; `hashes.txt` permite leitura simples. A cópia usada é `working/firmware.bin`. Os arquivos originais receberam o atributo somente leitura. Esse atributo evita alterações acidentais, mas não é proteção contra um administrador.

Imagem de aplicação: **790368 bytes**. SHA-256: `6f3ae6bae975276b08ecf8ada3550972f1d85b58174ffaea9916c7df2b52927f`. Data da análise: 05/11/2026. A integridade da cópia é conferida antes da análise. O SHA-256 compara conteúdo; sozinho não prova origem confiável nem substitui assinatura digital.

## Formato e estrutura

Primeiro byte `0xe9`, formato de imagem ESP32, 5 segmentos, entrada `0x40082bbc`. O script lê o cabeçalho de 24 bytes e os cabeçalhos de segmento de 8 bytes. O resultado completo está em `evidence/image-structure.json`.

O `.bin` é a aplicação, não um dump integral de 4 MiB. Bootloader e tabela de partições da compilação estão preservados separadamente. O Wokwi carrega a aplicação com sua configuração padrão; não se afirma que a flash efetiva do simulador foi extraída e comparada a esses arquivos.

| Partição da compilação | Tipo | Subtipo | Offset | Tamanho |
|---|---|---|---|---|
| nvs | 0x1 | 0x2 | 0x9000 | 0x5000 |
| otadata | 0x1 | 0x0 | 0xe000 | 0x2000 |
| app0 | 0x0 | 0x10 | 0x10000 | 0x140000 |
| app1 | 0x0 | 0x11 | 0x150000 | 0x140000 |
| spiffs | 0x1 | 0x82 | 0x290000 | 0x160000 |
| coredump | 0x1 | 0x3 | 0x3f0000 | 0x10000 |

A existência de partições OTA ou SPIFFS na tabela padrão não prova que o aplicativo implemente atualização OTA ou use sistema de arquivos. O código não monta SPIFFS/LittleFS e não chama APIs de OTA. Configuração de alerta fica em RAM; constantes ficam na imagem. O framework pode usar NVS internamente, mas não foi realizado dump do NVS em execução.

## Bibliotecas e textos relevantes

O build usa Arduino ESP32, WiFi, WebServer, DHT 1.4.6 e Adafruit Unified Sensor 1.1.15. `platformio.ini` e `evidence/build.log` registram a resolução das dependências. Não foi feita análise de CVEs de todas as dependências; o build de laboratório não é uma recomendação de versão de produção.

Trechos encontrados diretamente no binário, com offsets em bytes:

```text
0x0000132a  NexaSense LAB: /telemetry /debug /config?threshold=30
0x00001569  /debug
0x00001578  HTTP pronto. Acesso local: http://localhost:8180/telemetry
0x000015e7  @Wokwi-GUEST
0x000015f4  LAB_ONLY_CONFIG_nao_e_segredo_real
0x00001621  nexasense-lab-01
```

Esses textos identificam rede virtual, rotas, dispositivo e um marcador de configuração interno. A recuperação do marcador a partir do `.bin` é uma demonstração estática reproduzível de que constantes ficam legíveis em uma imagem sem proteção. O marcador é fictício, não uma senha, e o teste pressupõe posse autorizada da imagem. Isso não comprova extração de uma placa real.

## Atualização

O mecanismo observado no projeto é recompilar e carregar outro arquivo pela extensão. Não há endpoint de upload nem OTA implementada no aplicativo. Trocar um arquivo no computador não equivale a contornar Secure Boot de hardware. Para produção, propõem-se atualização assinada, autenticação do servidor, controle de versão e recuperação após falha. Nenhum eFuse foi programado.

Referência de formato: [Espressif App Image Format](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/app_image_format.html).
