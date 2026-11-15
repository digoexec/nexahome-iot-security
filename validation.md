# Registro de validação

Data: 5 de novembro de 2026, horário de São Paulo. Ambiente: VS Code com Wokwi Simulator 4.1.0, PlatformIO Core 6.2.0 e ESP32 DevKit v1 virtual.

| Verificação | Resultado | Evidência |
|---|---|---|
| Compilação Arduino para ESP32 | SUCCESS; imagem de 790368 bytes | firmware/evidence/build.log |
| Integridade dos oito arquivos preservados | Todos os tamanhos e SHA-256 conferidos | firmware/evidence/integrity-check.txt |
| Análise do binário | Cabeçalho 0xe9, cinco segmentos e strings com offsets | firmware/evidence/ |
| UART0 virtual | INFO retorna versão, identificador e marcador fictício | hardware/evidence/uart-info.txt |
| Sensor | 24,0 °C e 50,0% de umidade | network/evidence/01-before-response.http |
| Diagnóstico HTTP | Resposta 200 sem Authorization | network/evidence/02-debug-response.http |
| Configuração sem autenticação | Limite 30 -> 10; alerta false -> true | network/evidence/03-change-response.http e 04-after-response.http |
| Entrada inválida | HTTP 400 para threshold=abc | network/evidence/05-invalid-response.http |
| Restauração | Limite retorna a 30; alerta false | network/evidence/06-restore-response.http |
| Demonstração visual real | LED desligado, ligado e desligado novamente | hardware/evidence/wokwi-demonstration.mp4 |
| PDF | Cinco páginas renderizadas e inspecionadas; tabelas, diagrama e links legíveis | output/relatorio-nexasense.pdf |
| Vídeo final | MP4 H.264, 1600 × 1000, aproximadamente 2 min 37 s, sem áudio e com explicações em texto | output/demonstracao-nexasense.mp4 |

A gravação usa capturas diretas reais da janela, aproximadamente uma por segundo, mantendo os intervalos registrados. A identificação da conta foi ocultada e a faixa inferior de notificações foi recortada. A sequência do circuito não foi sintetizada. O método e os horários estão em hardware/evidence/video-provenance.json.

O relatório descreve os limites do simulador. Não foram ensaiados JTAG, extração física da flash, injeção de falhas ou programação de eFuses. Não foram usados serviços de terceiros como alvo. A publicação externa do vídeo não foi realizada; o arquivo local e seu link no README acompanham a entrega.
