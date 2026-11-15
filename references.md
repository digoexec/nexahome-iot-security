# Referências consultadas

Acesso em 5 de novembro de 2026. As fontes externas fundamentam a metodologia e as recomendações; não comprovam o funcionamento desta montagem. As evidências próprias ficam nas pastas firmware, hardware e network.

1. [OWASP IoT Security Testing Guide](https://github.com/OWASP/owasp-istg). Organização da avaliação por firmware, memória, serviços, interfaces físicas e sem fio. Os resultados são relacionados às áreas do guia, sem alegação de certificação.
2. [NIST IR 8259A de 2020](https://doi.org/10.6028/NIST.IR.8259A). Capacidades de identificação, configuração, proteção de dados, acesso lógico a interfaces, atualização e consciência do estado de segurança.
3. [Espressif Security Overview para ESP32](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/security/security.html). Secure Boot, Flash Encryption, interfaces de debug, TLS, armazenamento e atualização segura. A documentação estável consultada é de uma geração diferente do SDK Arduino usado no laboratório; recomendações devem ser ajustadas à versão escolhida para produção.
4. [Espressif AR2023-005 e CVE-2023-35818](https://documentation.espressif.com/AR2023-005%20Security%20Advisory%20Concerning%20Bypassing%20Secure%20Boot%20and%20Flash%20Encryption%20Using%20EMFI%20EN.html). Caso real descrito abaixo.
5. [Wokwi para VS Code](https://docs.wokwi.com/vscode/getting-started) e [configuração do projeto](https://docs.wokwi.com/vscode/project-config). Licença, firmware, UART encaminhada e gateway da extensão.
6. [Rede ESP32 no Wokwi](https://docs.wokwi.com/guides/esp32-wifi). Rede virtual e limites de acesso.

## Caso real pesquisado

O comunicado AR2023-005 descreve a CVE-2023-35818 em chips ESP32. Pesquisadores da Raelize e do TII usaram injeção eletromagnética de falhas para alterar o fluxo de execução e alcançar código de download UART na ROM. O ataque exige acesso físico e laboratório sofisticado; não é uma exploração remota comum.

O fabricante informa que a técnica pode contornar Secure Boot e Flash Encryption nas condições descritas. O comunicado trata das revisões v3.0 e v3.1 e explica a situação das anteriores. Entre as recomendações estão chaves únicas por dispositivo e encapsulamentos que dificultem manipular a flash. Outras famílias citadas possuem contramedidas na ROM; a escolha exige conferir o modelo e a revisão exatos.

Para a NexaHome, a lição é manter defesas em camadas e considerar o acesso físico no projeto. Uma chave compartilhada pode ampliar o dano de uma extração para toda a frota. A existência dessa CVE não comprova que o dispositivo virtual foi explorado ou que a montagem tem o mesmo comportamento elétrico. Nenhum ensaio de injeção de falhas foi realizado.
