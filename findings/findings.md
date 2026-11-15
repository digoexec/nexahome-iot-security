# Achados e classificação de riscos

## Critério

Escala simples, sem pretensão de CVSS: impacto e probabilidade de 1 a 3 (baixo, médio, alto). Risco = impacto × probabilidade: 1-2 baixo, 3-4 médio, 6-9 alto. O impacto considera um monitor ambiental com LED, não equipamento médico ou de segurança de pessoas. A probabilidade pressupõe acesso físico para UART ou alcance à rede do dispositivo para HTTP. O loopback restringe a exposição deste laboratório.

| Achado | Evidência e situação | Impacto | Probabilidade | Risco | Recomendação |
|---|---|---|---|---|---|
| F01 Diagnóstico excessivo em UART e /debug | `src/main.cpp`, `firmware/evidence/interesting-strings.txt`; UART confirmado pela captura UART virtual; HTTP confirmado por requisições e respostas reais | Médio 2: revela detalhes internos úteis ao reconhecimento | Média 2: exige acesso serial ou à rede | Médio 4 | Reduzir logs e remover diagnóstico público de produção |
| F02 Configuração de alerta sem autorização | Handler /config no código; confirmado por requisições e respostas reais | Médio 2: altera integridade e confiabilidade do alerta | Alta 3: uma chamada basta para cliente que alcança a rota | Alto 6 | Autenticar, autorizar e usar POST/PUT com validação e proteção de sessão |
| F03 Telemetria e controle por HTTP sem TLS | WebServer(80), encaminhamento em `wokwi.toml`; confirmado por requisições e respostas reais | Médio 2: dados e comandos expostos a observação/manipulação na rede sob ameaça | Alta 3: uso rotineiro do canal sem proteção em rede acessível ao adversário | Alto 6 | HTTPS com verificação de certificado e identidade individual |

## Encadeamento dos achados

F01: código e strings mostram diagnóstico -> divulgação de detalhes -> adversário com acesso físico ou de rede reconhece versão e configuração -> facilita preparação de ataques -> risco médio -> remover detalhes sem utilidade operacional. Não há segredo real exposto e nenhuma escalação foi comprovada.

F02: /config não chama autenticação -> qualquer cliente que alcance a rota pode ajustar o limite -> alteração do critério do alerta -> redução de confiança do monitor -> risco alto no contexto de implantação proposto -> autorização por função e auditoria. O ensaio previsto troca 30 por 10 e restaura; o impacto demonstrável limita-se ao alerta virtual.

F03: servidor HTTP simples -> falta de proteção criptográfica de transporte -> um adversário em posição de rede pode observar ou modificar fluxos -> afeta confidencialidade/integridade -> risco alto na rede de implantação considerada -> TLS corretamente configurado. Interceptação ativa não foi ensaiada. O risco não implica que terceiros remotos tenham acesso à porta loopback deste computador.

## Relação com referências

F01 se relaciona às áreas de interfaces internas UART e serviços de troca de dados do OWASP ISTG e às capacidades de acesso lógico a interfaces e proteção de dados do NIST IR 8259A. F02 se relaciona à capacidade de configuração do dispositivo e de acesso lógico a interfaces. F03 se relaciona à proteção de dados e à análise de serviços/comunicação do ISTG. São relações conceituais dos achados; não são declarações de conformidade.

## Itens que não são vulnerabilidades confirmadas

JTAG acessível, falta de Secure Boot, ausência de Flash Encryption, leitura de NVS e comprometimento de atualização não foram comprovados em placa física. A imagem contém constantes legíveis, mas o teste usa uma cópia já autorizada. A presença de uma string ou biblioteca OTA não comprova rota de atualização explorável. Não foram realizados brute force, varredura de rede, negação de serviço, glitching ou programação de eFuses.
