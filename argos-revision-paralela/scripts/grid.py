"""Uso: python3 grid.py PAGINA x0 y0 x1 y1 [escala]  -> g_PAGINA.png con cuadrícula cada 100 px (300 ppp) para ubicar sellos y manuscritos."""
import sys,os
from PIL import Image,ImageDraw
p=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2:6]); sc=float(sys.argv[6]) if len(sys.argv)>6 else 0.5
im=Image.open(os.environ.get('ARGOS_IMG','img')+f'/{p}_r.png').convert('RGB').crop((x0,y0,x1,y1))
im=im.resize((int(im.width*sc),int(im.height*sc)))
d=ImageDraw.Draw(im)
step=100
for gx in range((x0//step+1)*step,x1,step):
    X=(gx-x0)*sc; d.line([(X,0),(X,im.height)],fill=(0,160,255),width=1); d.text((X+2,2),str(gx),fill=(0,0,255))
for gy in range((y0//step+1)*step,y1,step):
    Y=(gy-y0)*sc; d.line([(0,Y),(im.width,Y)],fill=(0,160,255),width=1); d.text((2,Y+2),str(gy),fill=(0,0,255))
im.save(f'g_{p}.png')
