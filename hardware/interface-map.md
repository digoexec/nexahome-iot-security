# Mapa das interfaces do NexaSense

O equipamento analisado é uma montagem virtual, não uma placa comercial da NexaHome. As ligações efetivas estão em `diagram.json`.

| Elemento | Ligação ou função | Observação de segurança |
|---|---|---|
| ESP32 DevKit v1 | MCU Xtensa com Wi-Fi; flash virtual padrão de 4 MiB | O tamanho virtual não comprova o modelo de uma placa real |
| DHT22 | VCC em 3V3, GND comum, dados em GPIO15; pull-up de 10 kΩ | Protocolo próprio do DHT, não I²C apesar do nome SDA no simulador |
| LED vermelho | GPIO2, resistor de 330 Ω e GND | Representa alerta de temperatura; não controla atuador real |
| UART0 | TX0 GPIO1 e RX0 GPIO3, 115200 baud | O comando INFO revela diagnóstico sem autenticação |
| USB e alimentação | Alimentação virtual e ponte serial do DevKit | Em montagem real, lógica de 3,3 V; nunca aplicar 5 V em GPIO |
| GPIO0 e EN | Seleção de boot e reset na família ESP32 | Programação física a avaliar em placa real; não foi extraído firmware por esses pinos |
| JTAG convencional | GPIO12 MTDI, 13 MTCK, 14 MTMS e 15 MTDO | Mapeamento documental; GPIO15 está no sensor. Não foi conectado depurador nem comprovada leitura JTAG |
| Flash SPI | Armazena aplicação e partições | Não foi feita leitura direta do barramento nem dessoldagem |
| Wi-Fi virtual | Wokwi-GUEST; encaminhamento localhost:8180 para ESP32:80 | Rede de simulação; somente endpoints do dispositivo do laboratório foram testados |

## O que a UART permite

A aplicação imprime identificador, versão, modo de atualização e um marcador de configuração fictício. O comando INFO repete essa informação. Não existe shell, senha real nem comando de gravação na UART da aplicação. O risco identificado é a divulgação excessiva de configuração para quem tiver acesso à serial; a presença dos pinos isoladamente não comprova comprometimento.

O encaminhamento RFC2217 em localhost:4000 é uma facilidade de teste do Wokwi no computador, não um serviço TCP implementado no ESP32 comercial. A evidência deve distinguir esses dois níveis.

## Limites

Não foram medidos sinais elétricos, resistência física, tensão, eFuses, proteção efetiva de flash ou estado real de JTAG. Secure Boot, Flash Encryption e bloqueio de debug são recomendações para validação em hardware, não resultados desta simulação. Nenhum eFuse será programado.

Referência: [Espressif Security Overview](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/security/security.html).
