# Roteiro da apresentação de até quatro minutos

Gravar apenas a janela do VS Code e evidências locais. Não mostrar licença Wokwi, contas, arquivos pessoais ou credenciais. O vídeo pode ser legendado; o aluno deve revisar o conteúdo e saber explicá-lo antes da entrega.

| Tempo | Mostrar | Explicação simples |
|---|---|---|
| 0:00 a 0:25 | Montagem no Wokwi com ESP32, DHT22 e LED | Este protótipo monitora temperatura e umidade. O LED representa um alerta. É um laboratório virtual autorizado. |
| 0:25 a 0:50 | architecture/architecture-diagram.png | O sensor envia dados ao ESP32. Temos flash, firmware, UART e Wi-Fi. O computador consulta o servidor HTTP local. |
| 0:50 a 1:20 | firmware/hashes.txt e interesting-strings.txt | A primeira imagem foi preservada e recebeu SHA-256. Na cópia binária encontrei rotas e o marcador fictício. Isso não é extração física. |
| 1:20 a 1:45 | UART do Wokwi e uart-info.txt | INFO revela identificador, versão e configuração interna sem autenticação. O problema é o excesso de diagnóstico. |
| 1:45 a 2:40 | Simulador e respostas HTTP antes e depois | Com 24 graus e limite de 30, o alerta está desligado. Uma requisição sem autenticação muda o limite para 10 e acende o alerta. Depois o teste restaura 30. |
| 2:40 a 3:05 | network/evidence/http-session.json | Os dados aparecem em HTTP legível. Não existe TLS ou Authorization nessa sessão. Esta evidência é de aplicação, não uma captura PCAP. |
| 3:05 a 3:40 | findings e plano de hardening | Prioridades: autorização, HTTPS, menos debug e identidade individual. Para produção: atualização assinada, Secure Boot e Flash Encryption conforme a placa. Não foram gravados eFuses. |
| 3:40 a 3:55 | references.md | A CVE-2023-35818 mostra a importância do acesso físico e da revisão do chip. Esse ataque sofisticado não foi reproduzido aqui. |

Somente afirmar que um teste foi executado depois de confirmar seus arquivos de evidência. O vídeo final não deve ultrapassar quatro minutos. Publicar como não listado ou enviar o arquivo à plataforma aceita pela instituição e registrar o link no README quando houver publicação.
