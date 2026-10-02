# -*- coding: utf-8 -*-
"""Motor de capturas (protocolo C.3): lee la lista declarativa d.CAP['capturas'] y genera un PNG por captura en ARGOS_CAPS.
Elementos de un panel:  ["t","frase inicial","frase final|null",n]  localiza texto con el TSV de tesseract (un recuadro por línea)
                        ["b",x0,y0,x1,y1] recuadro manual (sellos, manuscritos), px a 300 ppp sobre la página enderezada
                        ["c",x0,y0,x1,y1] recorte manual     ["x",x0,y0,x1,y1] solo contexto (amplía el recorte)
Un panel con varios paneles se apila (versión A arriba, B abajo) a la misma escala."""
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cap import *
from PIL import Image,ImageDraw,ImageFont
import datos as d
OUT=os.environ.get('ARGOS_CAPS','capturas')+'/'; os.makedirs(OUT,exist_ok=True)
FILE=d.CAP['archivos']
def fte(page):
    f,n=page.split('-'); return f'{FILE[f]}, p. {int(n)}'
def panel(spec):
    page=spec['page']; pad=tuple(spec.get('pad',(130,110))); boxes=[];crop=None;ctx=[]
    for it in spec['items']:
        k=it[0]
        if k=='t':
            bl=line_boxes(page,it[1],it[2],it[3] if len(it)>3 else 0)
            if not bl: raise SystemExit(f'NO ENCONTRADO {page}: {it[1]} | {it[2] if len(it)>2 else None}')
            boxes+=bl
        elif k=='b': boxes.append(tuple(it[1:5]))
        elif k=='c': crop=tuple(it[1:5])
        elif k=='x': ctx.append(tuple(it[1:5]))
    if crop is None:
        u=union(boxes+ctx); crop=(u[0]-pad[0],u[1]-pad[1],u[2]+pad[0],u[3]+pad[1])
    return dict(page=page,boxes=boxes,crop=crop,label=spec.get('label'))
def make(key,paneles,width=1500):
    ims=[]
    for i,sp in enumerate(paneles):
        p=panel(sp); fn=OUT+f'{key}_{i}.png'; render(p['page'],p['boxes'],p['crop'],fn); ims.append((Image.open(fn),p['label'],p['page']))
    lab=24 if len(ims)>1 else 0; tot=0; sc=[]
    for im,l,pg in ims:
        s=width/im.width; sc.append(s); tot+=int(im.height*s)+lab
    tot+=10*(len(ims)-1)
    S=Image.new('RGB',(width,tot),'white'); y=0; dr=ImageDraw.Draw(S)
    f=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',20)
    for (im,l,pg),s in zip(ims,sc):
        if lab:
            dr.rectangle((0,y,width,y+lab-2),fill=(236,239,241)); dr.text((6,y+2),l or pg,fill=(30,30,30),font=f); y+=lab
        r=im.resize((width,int(im.height*s)),Image.LANCZOS); S.paste(r,(0,y)); y+=r.height+10
    S.save(OUT+key+'.png'); return S.size
def todas():
    errores=[]
    for c in d.CAP['capturas']+d.CAP.get('capturas_ld',[]):
        try: print(c['key'],make(c['key'],c['paneles']))
        except SystemExit as e: errores.append(str(e)); print('ERROR',c['key'],e)
    return errores
if __name__=='__main__':
    errs=todas()
    if errs: sys.exit(1)
