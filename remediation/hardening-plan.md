# Plano de hardening

As prioridades consideram o protótipo didático. Não representam certificação ou avaliação de produto real.

| Prioridade | Medida | Como verificar na versão comercial |
|---|---|---|
| P1 antes do piloto | Remover /debug e diagnóstico detalhado de produção | INFO e /debug não devolvem configuração interna; logs sem segredos |
| P1 antes do piloto | Autenticar usuário e dispositivo; autorizar alterações | Requisição anônima de configuração recebe 401 ou 403; usuário sem permissão não altera limite |
| P1 antes do piloto | HTTPS com validação de certificado; credenciais individuais | Cliente rejeita certificado inválido; captura mostra TLS; rotação e revogação funcionam |
| P1 antes do piloto | Usar POST ou PUT em alterações, validação de entrada e proteção contra CSRF quando houver sessão de navegador | GET não altera estado; valores fora da faixa são rejeitados; origem e autorização são verificadas |
| P2 engenharia | Não embutir segredos compartilhados no código; provisionar identidade única e proteger NVS quando necessário | Inspeção do binário não revela segredo da frota; dump autorizado não revela configuração protegida |
| P2 engenharia | Atualização assinada com transporte seguro e política de versão | Imagem adulterada ou de signatário incorreto é rejeitada; versão revogada não executa |
| P2 engenharia | Planejar OTA com slots A/B, autoteste e recuperação | Falha de energia ou novo firmware com defeito retorna à versão válida sem perder o dispositivo |
| P2 engenharia | Secure Boot e Flash Encryption em modo adequado ao chip e à revisão | Ensaios em placas de teste verificam assinatura e confidencialidade; chaves de assinatura ficam fora do firmware |
| P2 engenharia | Restringir JTAG, download UART, test points e acesso físico conforme modelo de ameaça | Testes autorizados verificam leitura e gravação bloqueadas; assistência tem processo controlado |
| P3 manutenção | Inventário e atualização de dependências, suporte e resposta a incidentes | Registro de versões, prazos de correção, canal de relato e logs úteis sem dados sensíveis |

Secure Boot verifica autenticidade do software. Flash Encryption protege a confidencialidade do conteúdo da flash. Um recurso não substitui o outro. A escolha e o provisionamento dependem do chip e de sua revisão. Alterações permanentes de eFuses exigem processo de fabricação validado; não fazem parte desta atividade.

A configuração do alerta fica só em RAM e volta a 30 °C no reinício. Em produção, persistência e recuperação devem ser definidas junto com disponibilidade e segurança do monitoramento.

Referências: [NIST IR 8259A](https://doi.org/10.6028/NIST.IR.8259A) e [documentação oficial da Espressif](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/security/security.html).
