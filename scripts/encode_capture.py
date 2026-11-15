"""Codifica capturas reais da janela, conservando os intervalos registrados."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import json
import subprocess
import imageio_ffmpeg

root=Path(__file__).resolve().parents[1]
source=root/'.tools/record-frames'
data=json.loads((source/'capture-log.json').read_text(encoding='utf-8'))
frames=[entry for entry in data if entry['kind']=='frame']
processed=root/'tmp/capture-frames'
processed.mkdir(parents=True,exist_ok=True)
sequence=[]
sheet=Image.new('RGB',(7*280,4*175),'white')
for i,entry in enumerate(frames):
    picture=Image.open(source/entry['file']).convert('RGB')
    w,h=picture.size
    ImageDraw.Draw(picture).rectangle((w-210,64,w,107),fill='#202020')
    picture=picture.crop((0,0,w,h-75))
    canvas=ImageOps.pad(picture,(1600,820),color='white')
    destination=processed/entry['file']
    canvas.save(destination)
    thumb=canvas.copy()
    thumb.thumbnail((280,155))
    sheet.paste(thumb,((i%7)*280,(i//7)*175))
    ImageDraw.Draw(sheet).text(((i%7)*280+5,(i//7)*175+155),f"{i:02d}  {entry['elapsed_ms']/1000:.1f}s",fill='black')
    duration=(frames[i+1]['elapsed_ms']-entry['elapsed_ms'])/1000 if i+1<len(frames) else 0.75
    sequence += ["file '"+destination.as_posix()+"'",f'duration {duration:.3f}']
sequence.append("file '"+(processed/frames[-1]['file']).as_posix()+"'")
sheet.save(root/'tmp/capture-contact-sheet.png')
playlist=processed/'capture.txt'
playlist.write_text('\n'.join(sequence),encoding='utf-8')
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y',
                '-f','concat','-safe','0','-i',str(playlist),'-r','15','-an','-c:v','libx264',
                '-preset','fast','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',
                str(root/'hardware/evidence/wokwi-demonstration.mp4')],check=True)
provenance={'method':'Capturas diretas reais da janela do VS Code com Wokwi, aproximadamente um quadro por segundo; intervalos preservados na codificacao.',
            'edits':'Identificacao da conta ocultada no cabecalho e faixa inferior de notificacoes recortada. Sem animacao sintetica do circuito.',
            'capture_log':data}
(root/'hardware/evidence/video-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'network/evidence/video-session.json').write_text(json.dumps([x for x in data if x['kind']=='http'],ensure_ascii=False,indent=2),encoding='utf-8')
print('Capturas reais codificadas:',len(frames))
