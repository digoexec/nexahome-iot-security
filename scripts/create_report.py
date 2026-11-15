"""Produz o PDF curto com dados reais dos arquivos de evidencia."""
from pathlib import Path
from html import escape
import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak

root = Path(__file__).resolve().parents[1]
out = root / 'output'
out.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='ArialBold')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportTitle', fontName='ArialBold', fontSize=21, leading=25, spaceAfter=14, textColor=colors.black))
styles.add(ParagraphStyle(name='SectionTitle', fontName='ArialBold', fontSize=14, leading=18, spaceBefore=12, spaceAfter=8, textColor=colors.black))
styles.add(ParagraphStyle(name='ReportBody', fontName='Arial', fontSize=10.4, leading=15, spaceAfter=9, textColor=colors.black))
styles.add(ParagraphStyle(name='SmallBody', fontName='Arial', fontSize=8.7, leading=12, spaceAfter=7, textColor=colors.black))
styles.add(ParagraphStyle(name='CellBody', fontName='Arial', fontSize=8.3, leading=11, spaceAfter=0, textColor=colors.black))
styles.add(ParagraphStyle(name='CodeBody', fontName='Courier', fontSize=8.1, leading=11, spaceAfter=9, wordWrap='CJK'))
story = []
def p(text, style='ReportBody'):
    story.append(Paragraph(text, styles[style]))
def h(text): p(text, 'SectionTitle')
def table(rows, widths):
    data = [[Paragraph(escape(str(cell)), styles['CellBody']) for cell in row] for row in rows]
    obj = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    obj.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#d9d9d9')),
                            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8e8e8')),
                            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),7),
                            ('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),
                            ('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(obj)
    story.append(Spacer(1,9))
def page(): story.append(PageBreak())

meta = json.loads((root/'firmware/evidence/image-structure.json').read_text())
partitions = json.loads((root/'firmware/evidence/partitions.json').read_text())
strings = (root/'firmware/evidence/interesting-strings.txt').read_text(encoding='utf-8').splitlines()
http_ok = (root/'network/evidence/test-result.txt').exists()
uart_ok = (root/'hardware/evidence/uart-info.txt').exists()
video_ok = (out/'demonstracao-nexasense.mp4').exists()
complete = http_ok and uart_ok and video_ok

p('Avaliação de segurança do NexaSense', 'ReportTitle')
p('Hardware Hacking e IoT | Ciências da Computação | 5 de novembro de 2026', 'SmallBody')
if not complete:
    p('<b>Versão em preparação.</b> A execução da simulação, as capturas e/ou o vídeo ainda têm pendências. Os resultados estáticos abaixo são reais; procedimentos pendentes não são apresentados como realizados.')
p('Foi construído um protótipo educacional com ESP32 e DHT22 para avaliar como hardware, firmware e comunicação influenciam a segurança de um monitor ambiental. O código apresenta diagnóstico excessivo, configuração sem autorização e HTTP sem TLS. A prioridade antes de um piloto é corrigir os controles de acesso e proteger os dados em trânsito.')
h('1 Dispositivo e arquitetura')
p('A montagem usa ESP32 DevKit v1, sensor DHT22 no GPIO15, resistor de pull-up de 10 kΩ, LED no GPIO2 e resistor de 330 Ω. A alimentação do sensor é 3,3 V com GND comum. A flash virtual padrão é de 4 MiB; RAM guarda leituras e limite de alerta. A UART0 usa TX GPIO1 e RX GPIO3 em 115200 baud.')
story.append(Image(str(root/'architecture/architecture-diagram.png'),width=450,height=253))
p('Figura 1. Arquitetura criada para o laboratório. O cliente local representa a plataforma de monitoramento. O dispositivo disponibiliza JSON por HTTP, sem recorrer a broker ou nuvem de terceiros.', 'SmallBody')
h('Escopo e limites')
p('Somente esta montagem virtual e o cliente local estão autorizados. Não foi fornecido firmware comercial: a imagem original desta atividade é a primeira compilação do código educacional. Não foram testados dispositivos de terceiros, redes de produção, eFuses, resistência elétrica, glitching ou extração física de memória. Todos os identificadores e marcadores usados são fictícios.')

page()
h('2 Método e preservação do firmware')
p('A sequência foi reconhecer a montagem, compilar, preservar a primeira imagem e seus arquivos de origem, calcular SHA-256, analisar uma cópia, examinar interfaces e comunicações e relacionar evidências a riscos. O OWASP ISTG orientou a divisão por firmware, memória, serviços e interfaces; o NIST IR 8259A apoiou as recomendações [1, 2].')
p('Os originais ficam em firmware/original com atributo somente leitura. A análise usa firmware/working/firmware.bin. O manifesto registra os arquivos preservados, incluindo aplicação, ELF, bootloader, partições, fonte e configurações. O script verify_integrity.py confere tamanho e hash. O atributo somente leitura evita erro acidental; não é garantia contra alteração deliberada.')
p(f"<b>Registro da imagem</b><br/>Arquivo: firmware/original/firmware.bin<br/>Tamanho: {meta['size']} bytes<br/>Origem: primeira compilação local do protótipo educacional<br/>Data da análise: 05/11/2026", 'SmallBody')
p('SHA-256 da aplicação', 'SmallBody')
digest = meta['sha256']
p(digest[:32]+'<br/>'+digest[32:], 'CodeBody')
p('O hash permite detectar alteração do conteúdo. Ele não prova autenticidade nem substitui assinatura digital. O registro completo, com horário UTC, está em firmware/manifest.json.')
h('3 Análise estática da imagem')
p(f"O primeiro byte é {meta['magic']}, compatível com imagem ESP32. Foram lidos {meta['segment_count']} segmentos e a entrada {meta['entry_address']}. O .bin é uma aplicação, não um dump completo da flash. O JSON image-structure.json registra offsets, endereços e tamanhos [6].")
rows=[['Partição do build','Offset','Tamanho']]+[[q['label'],q['offset'],q['size']] for q in partitions]
table(rows,[225,137,137])
selected = [s for s in strings if 'LAB_ONLY' in s or '/telemetry' in s or '/debug' in s]
p('<br/>'.join(escape(s) for s in selected[:4]), 'CodeBody')
p('Essas strings foram recuperadas da cópia binária, com offsets em bytes. Isso demonstra que constantes internas podem permanecer legíveis para quem possui a imagem. O marcador LAB_ONLY_CONFIG não é uma senha real; não foi comprovada extração de uma placa protegida.', 'SmallBody')

page()
h('4 Interfaces físicas e atualização')
p('A UART da aplicação mostra versão, identificador, modo de atualização e um marcador interno. O comando INFO repete o diagnóstico sem autenticação. '+('A captura real da UART virtual está em hardware/evidence/uart-info.txt.' if uart_ok else '<b>A captura da UART virtual está pendente.</b> Esse comportamento foi identificado no código.'))
p('A presença dos pinos não é suficiente para declarar uma vulnerabilidade. Neste caso, a questão é a informação entregue a quem obtém acesso à interface. Não há shell, senha real nem comando de gravação na UART da aplicação. O RFC2217 na porta 4000 é um recurso de encaminhamento do Wokwi, não um serviço TCP do produto.')
p('O JTAG convencional do ESP32 utiliza GPIO12 a GPIO15; o GPIO15 está no sensor. O mapeamento é documental: não houve conexão de depurador ou leitura de memória. Também não foram comprovados estado dos eFuses, bloqueio de download UART ou proteção de flash. Essas verificações precisam de placa e revisão definidas.')
p('A atualização do laboratório consiste em recompilar e carregar uma imagem pela extensão. Não existe OTA ou endpoint de upload no aplicativo. A tabela padrão pode conter slots OTA e SPIFFS, mas sua presença não comprova uso. O código não monta sistema de arquivos e mantém o limite do alerta em RAM. Não se afirma que substituir o arquivo no computador contorne Secure Boot de uma placa real.')
h('5 Comunicações e demonstração controlada')
p('O DHT22 usa protocolo próprio, e não I²C. A rede virtual Wokwi-GUEST fornece conectividade ao ESP32. O cliente usa 127.0.0.1:8180, encaminhado pelo gateway da extensão à porta TCP/80 do dispositivo. O firmware não realiza requisições a serviços externos. O IP virtual efetivo deve ser lido no log, sem confundi-lo com endereço de uma placa física [5].')
table([['Rota HTTP','Informação ou efeito'],['GET /telemetry','Identificador, temperatura, umidade, limite e alerta em JSON'],['GET /debug','Versão e configuração fictícia'],['GET /config?threshold=10','Altera o limite sem autenticação ou autorização']], [217,282])
if http_ok:
    p('O teste real registrou requisições sem Authorization e respostas HTTP legíveis. Com sensor em 24 °C, o limite passou de 30 para 10 °C e o alerta de false para true. Uma entrada inválida foi rejeitada, e o limite foi restaurado para 30 °C. As evidências estão em network/evidence/http-session.json e nos arquivos .http.')
else:
    p('<b>Execução HTTP pendente.</b> O procedimento preparado consulta telemetria, lê /debug, muda o limite de 30 para 10 °C, verifica o alerta, testa entrada inválida e restaura 30 °C. Não existe registro de sucesso de rede antes de uma conexão real.')
p('Os bytes HTTP coletados são evidência de aplicação, não PCAP nem interceptação Wi-Fi. Identificar o protocolo não basta: é necessário verificar autenticação, autorização e proteção do transporte. HTTP simples não oferece TLS; checksum TCP não garante integridade contra um adversário. O efeito demonstrado limita-se ao alerta virtual.', 'SmallBody')

page()
h('6 Achados e riscos')
p('Escala: impacto e probabilidade de 1 a 3. Risco é o produto: 1-2 baixo, 3-4 médio, 6-9 alto. As notas consideram um monitor ambiental. Probabilidade pressupõe acesso físico à UART ou alcance à rede da aplicação; a porta loopback deste laboratório restringe o acesso remoto.')
status = 'Captura real' if http_ok else 'Código; ensaio pendente'
table([['Achado','Evidência','Impacto','Prob.','Risco','Recomendação'],
       ['F01 Diagnóstico excessivo','debugInfo; strings no .bin; '+('UART capturada' if uart_ok else 'UART pendente'),'Médio 2','Média 2','Médio 4','Remover diagnóstico público e reduzir logs'],
       ['F02 Configuração sem autorização','/config; '+status,'Médio 2','Alta 3','Alto 6','Autenticar, autorizar e usar método de alteração adequado'],
       ['F03 HTTP sem TLS','WebServer(80); '+status,'Médio 2','Alta 3','Alto 6','HTTPS e validação de certificado']], [86,119,57,49,52,136])
p('F01 pode facilitar reconhecimento de versão e configuração por alguém com acesso serial ou de rede. F02 pode alterar o critério do alerta e reduzir a confiança do monitor. F03 pode expor dados e comandos a um adversário em posição de rede. Não houve demonstração de invasão remota, captura por terceiro ou roubo de credencial real.')
p('F01 se relaciona às áreas de UART e serviços do OWASP ISTG e às capacidades de acesso lógico e proteção de dados do NIST. F02 se relaciona à configuração do dispositivo e ao controle de acesso. F03 se relaciona à proteção de dados e à análise dos serviços de comunicação. Essa associação não representa certificação [1, 2].')
h('7 Mitigações e hardening comercial')
p('<b>Antes do piloto:</b> remover /debug, reduzir diagnóstico serial, exigir identidade individual e autorização por função, adotar HTTPS com verificação de certificado e trocar GET por POST/PUT para alterar estado. Quando houver sessão de navegador, prever proteção contra CSRF. A validação de formato e faixa já existente não substitui autorização.')
p('<b>Na engenharia:</b> provisionar credenciais únicas, proteger parâmetros em armazenamento adequado e planejar atualização assinada com transporte seguro, política de versão, recuperação e autoteste. Validar atualização adulterada, falha de energia, rejeição de cliente anônimo e recuperação de versão.')
p('<b>No hardware de produção:</b> avaliar Secure Boot, Flash Encryption e restrição de JTAG/download UART conforme chip e revisão. Secure Boot trata autenticidade do software; Flash Encryption trata confidencialidade da flash. As funções são complementares. Não foram habilitados recursos irreversíveis nesta atividade [3].')
p('<b>Na manutenção:</b> manter inventário de dependências, prazo de suporte, canal de relato e procedimento de correção. Logs devem ajudar a identificar falhas sem divulgar segredos. Os critérios de aceitação detalhados estão em remediation/hardening-plan.md.')

page()
h('8 Exemplo real pesquisado')
p('O comunicado Espressif AR2023-005 descreve a CVE-2023-35818. Pesquisadores da Raelize e do TII demonstraram injeção eletromagnética de falhas em ESP32, alterando o fluxo de execução para alcançar código de download UART na ROM. O ataque demanda acesso físico e equipamento sofisticado [4].')
p('O caso envolve execução e memória do chip e pode contornar proteções nas condições do comunicado. O fabricante discute revisões v3.0 e v3.1, recomenda chaves individuais para limitar o alcance de uma extração e menciona encapsulamentos que dificultem a manipulação da flash. A seleção de um chip deve considerar modelo e revisão exatos.')
p('Para a NexaHome, a lição é combinar proteção de firmware com controle de acesso físico e identidade individual. A divulgação de detalhes de debug merece revisão mesmo quando outros mecanismos existem. Essa CVE não foi reproduzida no Wokwi e não é um achado confirmado na montagem virtual.')
h('9 Conclusão e reprodução')
p('O projeto permite estudar falhas simples de um protótipo antes de levá-lo ao mercado. A evidência estática mostra rotas, parâmetros e diagnóstico no firmware. '+('A execução no Wokwi confirma a exposição serial e a alteração não autorizada do alerta por HTTP.' if http_ok and uart_ok else 'As capturas dinâmicas ainda precisam ser concluídas no Wokwi para validar o comportamento de UART e rede.'))
p('A reprodução segue o README: abrir a pasta no VS Code, ativar a licença Wokwi, iniciar o simulador, manter a aba visível e executar os scripts de integridade, UART e HTTP. JTAG, extração física e mecanismos de proteção comercial permanecem propostas de validação em placa real.')
if video_ok:
    p('Vídeo de demonstração: <link href="demonstracao-nexasense.mp4" color="black"><u>demonstracao-nexasense.mp4</u></link>, entregue junto ao relatório. O arquivo local está referenciado no README. A publicação na plataforma escolhida pelo aluno deve preservar as licenças e os dados pessoais.')
else:
    p('<b>Vídeo pendente.</b> O roteiro de até quatro minutos está preparado em output/roteiro-video.md. O link de publicação não foi inventado. A entrega só estará completa após gravação da demonstração e inclusão do vídeo ou link aceito pela instituição.')
h('Referências')
references=[
 ('[1] OWASP IoT Security Testing Guide','https://github.com/OWASP/owasp-istg'),
 ('[2] NIST IR 8259A de 2020','https://doi.org/10.6028/NIST.IR.8259A'),
 ('[3] Espressif Security Overview para ESP32','https://docs.espressif.com/projects/esp-idf/en/stable/esp32/security/security.html'),
 ('[4] Espressif AR2023-005 CVE-2023-35818','https://documentation.espressif.com/AR2023-005%20Security%20Advisory%20Concerning%20Bypassing%20Secure%20Boot%20and%20Flash%20Encryption%20Using%20EMFI%20EN.html'),
 ('[5] Wokwi configuração do projeto','https://docs.wokwi.com/vscode/project-config'),
 ('[6] Espressif App Image Format','https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/app_image_format.html')]
for label,url in references:
    p(f'<link href="{escape(url, quote=True)}" color="black"><u>{escape(label)}</u></link>', 'SmallBody')
p('Fontes consultadas em 05/11/2026. A documentação estável Espressif consultada orienta o hardening; sua versão não deve ser confundida com o SDK do build de laboratório. Evidências e scripts completos acompanham o projeto.', 'SmallBody')

def footer(canvas, doc):
    canvas.setFont('Arial', 8)
    canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawString(48,28,'NexaSense | Avaliação educacional em ambiente autorizado')
    canvas.drawRightString(A4[0]-48,28,str(doc.page))

doc=SimpleDocTemplate(str(out/'relatorio-nexasense.pdf'),pagesize=A4,rightMargin=48,leftMargin=48,
                      topMargin=39,bottomMargin=46,title='Avaliação de segurança do NexaSense',author='Trabalho de Ciências da Computação')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out/'relatorio-nexasense.pdf')
