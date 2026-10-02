"""Uso: python3 montage.py A.1 A.2 ...  -> hoja_contacto.png (2 columnas) para revisar varias capturas en una sola vista."""
import sys,os
from PIL import Image
keys=sys.argv[1:]
ims=[Image.open(os.environ.get('ARGOS_CAPS','capturas')+f'/{k}.png') for k in keys]
W=900
th=[i.resize((W,int(i.height*W/i.width))) for i in ims]
cols=2; rows=[th[i:i+cols] for i in range(0,len(th),cols)]
H=sum(max(i.height for i in r) for r in rows)
S=Image.new('RGB',(W*cols+10,H+10*len(rows)),(200,200,200)); y=0
for r in rows:
    x=0
    for i in r: S.paste(i,(x,y)); x+=W+10
    y+=max(i.height for i in r)+10
S.save('hoja_contacto.png'); print(S.size)
