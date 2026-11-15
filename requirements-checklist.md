# Cobertura dos requisitos

Este quadro é um registro de cobertura, não uma declaração de que um teste planejado foi executado.

| Requisito do enunciado | Entrega ou evidência | Situação |
|---|---|---|
| Descrição, MCU, memória, sensores, alimentação e armazenamento | architecture/ e hardware/interface-map.md | Documentado |
| Diagrama e mapa da superfície de ataque | architecture/architecture-diagram.png e architecture.md | Concluído |
| Preservação antes de alteração, origem, tamanho, data e SHA-256 | firmware/original/, manifest.json, hashes.txt, verify_integrity.py | Concluído |
| Formato, segmentos, partições, bibliotecas, textos e parâmetros | firmware/analysis-notes.md e evidence/ | Análise estática concluída |
| Interfaces físicas, UART e JTAG quando presente | hardware/interface-map.md | Mapeamento documentado; UART coletada; JTAG não ensaiado |
| Mecanismo de atualização | firmware/analysis-notes.md | Recarga local identificada; OTA ausente na aplicação |
| Comunicação, origem/destino, protocolos e controles | network/protocol-analysis.md | HTTP coletado e testado |
| Demonstração controlada | Extração do marcador fictício de firmware/evidence/interesting-strings.txt | Concluída estaticamente; demonstração HTTP concluída |
| Evidência, ameaça, impacto, probabilidade e risco | findings/findings.md | Classificação contextual; status de confirmação explícito |
| Relação com referência reconhecida | findings/findings.md e references.md | OWASP ISTG, NIST e Espressif |
| Mitigações e hardening comercial | remediation/hardening-plan.md | Concluído conceitualmente; sem eFuses |
| Exemplo real pesquisado | references.md, AR2023-005/CVE-2023-35818 | Concluído; não reproduzido |
| README com escopo e reprodução | README.md | Concluído |
| Relatório técnico PDF | output/relatorio-nexasense.pdf | Gerado; revisão visual registrada em validation.md |
| Utilização da extensão Wokwi no VS Code | hardware/evidence/wokwi-running.png | Execução registrada |
| Vídeo de até 4 minutos | output/ | Vídeo local gerado; publicação pelo aluno |

As capturas UART/HTTP, as imagens de execução e o trecho do vídeo vêm do laboratório real no Wokwi. O vídeo é entregue como arquivo local. Se a instituição exigir hospedagem, publicar esse arquivo na plataforma aceita e registrar o link no README. JTAG e mecanismos irreversíveis de hardware permanecem propostas conceituais conforme o escopo permitido.
