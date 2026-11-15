"""Gera um diagrama simples do projeto, sem simular evidencias de execucao."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
out = root / 'architecture'
out.mkdir(exist_ok=True)
image = Image.new('RGB', (1600, 900), 'white')
draw = ImageDraw.Draw(image)
font_path = 'C:/Windows/Fonts/arial.ttf'
bold_path = 'C:/Windows/Fonts/arialbd.ttf'
title = ImageFont.truetype(bold_path, 42)
font = ImageFont.truetype(font_path, 27)
small = ImageFont.truetype(font_path, 23)

draw.text((65, 40), 'NexaSense no Wokwi', font=title, fill='black')
draw.text((65, 100), 'Arquitetura do laboratório e pontos de avaliação', font=font, fill='#444444')

def box(bounds, heading, lines):
    draw.rounded_rectangle(bounds, radius=12, fill='#f4f5f6', outline='#555555', width=2)
    x, y = bounds[:2]
    draw.text((x+20, y+18), heading, font=ImageFont.truetype(bold_path, 29), fill='black')
    for i, line in enumerate(lines):
        draw.text((x+20, y+65+i*34), line, font=small, fill='#222222')

def arrow(start, end):
    draw.line((start, end), fill='#333333', width=4)
    x, y = end
    if start[0] == end[0]:
        direction = 1 if y > start[1] else -1
        draw.polygon([(x,y),(x-9,y-16*direction),(x+9,y-16*direction)],fill='#333333')
    else:
        direction = 1 if x > start[0] else -1
        draw.polygon([(x,y),(x-16*direction,y-9),(x-16*direction,y+9)],fill='#333333')

box((60,220,365,405),'Sensor DHT22',['Temperatura e umidade','GPIO15 + pull-up 10 kΩ','3,3 V e GND'])
box((485,205,1020,435),'ESP32 DevKit v1',['Firmware Arduino em C++','RAM: leituras e limite do alerta','Flash virtual: aplicação e partições','LED de alerta em GPIO2'])
box((1140,220,1540,405),'UART0',['TX GPIO1 / RX GPIO3','115200 baud; comando INFO','Diagnóstico interno exposto'])
arrow((365,310),(485,310))
arrow((1020,310),(1140,310))
box((485,525,1020,735),'Wi-Fi virtual e HTTP',['Rede Wokwi-GUEST; TCP/80','/telemetry   /debug   /config','Sem TLS e sem autenticação'])
arrow((755,435),(755,525))
box((1140,525,1540,735),'Cliente do laboratório',['127.0.0.1:8180','Gateway da extensão VS Code','Consulta JSON e testa limite'])
arrow((1020,630),(1140,630))
draw.text((65,790),'Somente o dispositivo virtual e o cliente local estão no escopo.',font=font,fill='black')
draw.text((65,837),'JTAG, extração física, eFuses e segurança elétrica não foram ensaiados.',font=small,fill='#444444')
image.save(out/'architecture-diagram.png')
print(out/'architecture-diagram.png')
