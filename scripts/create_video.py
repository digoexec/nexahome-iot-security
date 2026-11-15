"""Monta video legendado com evidencias reais e trecho gravado do Wokwi."""
from pathlib import Path
import hashlib
import json
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

root=Path(__file__).resolve().parents[1]
tmp=root/'tmp/video'
tmp.mkdir(parents=True,exist_ok=True)
out=root/'output'
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
clip=root/'hardware/evidence/wokwi-demonstration.mp4'
assert clip.exists(), 'Grave primeiro a demonstracao real no Wokwi.'
assert (root/'network/evidence/test-result.txt').exists(), 'Teste HTTP ainda nao passou.'
assert (root/'hardware/evidence/uart-info.txt').exists(), 'Captura UART ausente.'
regular='C:/Windows/Fonts/arial.ttf'
bold='C:/Windows/Fonts/arialbd.ttf'
font=ImageFont.truetype(regular,28)
small=ImageFont.truetype(regular,24)
titlefont=ImageFont.truetype(bold,43)
mono=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',25)

def run(args):
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y']+args,check=True)

def slide(number,title,caption,image_path=None,lines=None):
    canvas=Image.new('RGB',(1600,1000),'white')
    draw=ImageDraw.Draw(canvas)
    draw.text((55,35),title,font=titlefont,fill='black')
    if image_path:
        picture=Image.open(image_path).convert('RGB')
        picture.thumbnail((1490,710),Image.Resampling.LANCZOS)
        canvas.paste(picture,((1600-picture.width)//2,115+(710-picture.height)//2))
    if lines:
        y=160
        for line in lines:
            for row in textwrap.wrap(line,99,break_long_words=False,break_on_hyphens=False) or ['']:
                draw.text((65,y),row,font=mono if line.startswith('0x') else font,fill='black')
                y+=39
            y+=17
    y=850
    for row in textwrap.wrap(caption,108,break_long_words=False,break_on_hyphens=False):
        draw.text((55,y),row,font=font,fill='#222222')
        y+=40
    draw.text((55,962),'NexaSense | Hardware Hacking e IoT | Laboratório autorizado',font=small,fill='#555555')
    imagefile=tmp/f'slide-{number}.png'
    canvas.save(imagefile)
    segment=tmp/f'segment-{number}.mp4'
    run(['-loop','1','-i',str(imagefile),'-t','18','-r','15','-c:v','libx264','-preset','fast',
         '-crf','22','-pix_fmt','yuv420p',str(segment)])
    return segment

segments=[]
segments.append(slide('01','NexaSense no Wokwi dentro do VS Code',
 'ESP32, sensor DHT22 e LED de alerta. A avaliação usa apenas este dispositivo virtual e o cliente local.',
 root/'hardware/evidence/wokwi-running.png'))
segments.append(slide('02','Arquitetura e superfície de ataque',
 'Os pontos analisados são firmware e flash, diagnóstico UART e rotas HTTP. JTAG e eFuses não foram ensaiados.',
 root/'architecture/architecture-diagram.png'))
meta=json.loads((root/'firmware/evidence/image-structure.json').read_text())
strings=(root/'firmware/evidence/interesting-strings.txt').read_text(encoding='utf-8').splitlines()
selected=[s for s in strings if any(t in s for t in ['LAB_ONLY','nexasense-lab','/telemetry','/debug'])]
segments.append(slide('03','Firmware preservado e análise da cópia',
 'As strings foram extraídas do binário. O marcador é fictício. O teste não demonstra extração de uma placa física.',
 lines=[f"firmware.bin: {meta['size']} bytes; formato ESP32, magic {meta['magic']}",
        'SHA-256: '+meta['sha256'][:32],meta['sha256'][32:],
        'Strings e offsets em bytes:']+selected[:5]))
uart=(root/'hardware/evidence/uart-info.txt').read_text(encoding='utf-8').splitlines()
interesting=[l for l in uart if any(t in l for t in ['device=','firmware=','internal_config=','transport=','update='])]
segments.append(slide('04','UART virtual e diagnóstico excessivo',
 'O comando INFO retorna configuração sem autenticação. A evidência é da UART virtual encaminhada pelo Wokwi, em 115200 baud.',
 lines=['Captura real: hardware/evidence/uart-info.txt','Comando enviado: INFO']+interesting[:5]))

# Insere a gravacao real, com legenda; nao substitui a execucao por animacao.
overlay=Image.new('RGBA',(1600,1000),(255,255,255,0))
draw=ImageDraw.Draw(overlay)
draw.rectangle((0,835,1600,1000),fill=(255,255,255,255))
draw.text((55,855),'Demonstração real: limite 30 -> 10 °C sem autenticação.',font=font,fill='black')
draw.text((55,901),'O alerta acende e o teste restaura o limite para 30 °C.',font=font,fill='black')
draw.text((55,956),'Nenhum atuador físico ou serviço de terceiros foi usado.',font=small,fill='#555555')
overlayfile=tmp/'overlay.png'
overlay.save(overlayfile)
live=tmp/'segment-05.mp4'
run(['-i',str(clip),'-i',str(overlayfile),'-filter_complex',
     '[0:v]scale=1600:830:force_original_aspect_ratio=decrease,pad=1600:1000:(ow-iw)/2:0:white[base];[base][1:v]overlay=0:0',
     '-t','32','-r','15','-an','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p',str(live)])
segments.append(live)
records=json.loads((root/'network/evidence/http-session.json').read_text())
before=records[0]['response'].split('\r\n\r\n',1)[1]
after=records[3]['response'].split('\r\n\r\n',1)[1]
segments.append(slide('06','Comunicação HTTP registrada',
 'Requisições sem Authorization e sem TLS. São bytes reais de aplicação, não uma captura PCAP nem interceptação Wi-Fi.',
 lines=['GET /telemetry HTTP/1.1','Estado inicial: '+before,
        'GET /config?threshold=10 HTTP/1.1','Estado após alteração: '+after,
        'Resultado: PASS; entrada inválida rejeitada e limite restaurado.']))
segments.append(slide('07','Riscos e hardening antes do piloto',
 'Classificação contextual: impacto x probabilidade. A existência de uma UART sozinha não prova que o dispositivo é inseguro.',
 lines=['F01: diagnóstico excessivo. Risco médio (2 x 2 = 4).',
        'F02: configuração sem autorização. Risco alto (2 x 3 = 6).',
        'F03: HTTP sem TLS. Risco alto (2 x 3 = 6).',
        'Prioridades: menos debug; autenticação e autorização; HTTPS.',
        'Produção: credenciais únicas, armazenamento protegido, atualização assinada,',
        'recuperação e controle de debug. Secure Boot e Flash Encryption são complementares.']))
segments.append(slide('08','Caso real e conclusão',
 'O laboratório reproduz falhas simples e reúne evidências rastreáveis. Revisar as recomendações em uma placa real antes de um produto comercial.',
 lines=['CVE-2023-35818 / Espressif AR2023-005:',
        'injeção eletromagnética de falhas em ESP32, com acesso físico e',
        'equipamento sofisticado. Esse ataque não foi reproduzido aqui.',
        'Lição: considerar revisão do chip e limitar danos com identidade individual.',
        'Referências: OWASP ISTG, NIST IR 8259A e documentação Espressif.',
        'Relatório, fontes, capturas e scripts acompanham o projeto.']))
playlist=tmp/'segments.txt'
playlist.write_text('\n'.join("file '"+p.as_posix()+"'" for p in segments),encoding='utf-8')
run(['-f','concat','-safe','0','-i',str(playlist),'-c','copy','-movflags','+faststart',str(out/'demonstracao-nexasense.mp4')])
print(out/'demonstracao-nexasense.mp4')
