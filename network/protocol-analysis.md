# Análise das comunicações

## Situação da coleta

Coleta HTTP real concluída; consulte evidence/http-session.json e test-result.txt.

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
