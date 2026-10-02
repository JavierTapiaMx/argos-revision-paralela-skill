# -*- coding: utf-8 -*-
"""Inventario + rasterizado a 300 ppp + enderezado automático + OCR (txt y tsv) en paralelo.
Uso:  python3 ocr_all.py A=ruta/archivo1.pdf B=ruta/archivo2.pdf ... [--hilos 8]
Salida (en el directorio actual): img/K-n.png y img/K-n_r.png (enderezada), ocr/K-n.txt, tsv/K-n.tsv, inventario.json
Los números de página llevan ceros a la izquierda si el archivo tiene 10 o más páginas (C-01).
Marca como 'revisar_visualmente' toda página con OCR pobre (candidata a lectura dudosa, B.1)."""
import sys,os,re,json,hashlib,subprocess,shutil
from multiprocessing import Pool
from PIL import Image
ENV=dict(os.environ,OMP_THREAD_LIMIT='1')
def sh(cmd): return subprocess.run(cmd,capture_output=True,text=True,env=ENV)
def score(img_path,psm=4,tsv_text=None):
    stdout=tsv_text if tsv_text is not None else sh(['tesseract',img_path,'stdout','-l','spa','--psm',str(psm),'tsv']).stdout
    confs=[];chars=0
    for ln in stdout.split('\n')[1:]:
        p=ln.split('\t')
        if len(p)>=12 and p[0]=='5' and p[11].strip():
            try: c=float(p[10])
            except: continue
            if c>=0 and len(re.sub(r'\W','',p[11]))>=3: confs.append(c); chars+=len(p[11])
    good=sum(c for c in confs if c>60)
    return good,(sum(confs)/len(confs) if confs else 0),chars
def procesar(a):
    clave,n,total=a['clave'],a['n'],a['total']; w=len(str(total)) if total>=10 else 1
    base=f"{clave}-{n:0{w}d}"; src=f"img/{base}.png"; dst=f"img/{base}_r.png"
    im=Image.open(src).convert('L'); small=im.copy(); small.thumbnail((1400,1400))
    best=(-1,0); res={}
    for ang in (0,90,270,180):
        t=small.rotate(ang,expand=True); tp=f"/tmp/_t_{base}_{ang}.png"; t.save(tp)
        g,m,ch=score(tp); os.remove(tp); res[ang]=g
        if ang==0 and m>=70 and ch>=300: best=(g,0); break
        if g>best[0]: best=(g,ang)
    ang=best[1]
    Image.open(src).convert('RGB').rotate(ang,expand=True).save(dst) if ang else shutil.copyfile(src,dst)
    sh(['tesseract',dst,f'ocr/{base}','-l','spa','--psm','4','txt','tsv'])
    shutil.move(f'ocr/{base}.tsv',f'tsv/{base}.tsv')
    txt=open(f'ocr/{base}.txt',encoding='utf-8').read(); g,m,ch=score(None,tsv_text=open(f'tsv/{base}.tsv',encoding='utf-8').read())
    return dict(pagina=base,rotacion_aplicada=ang,caracteres=len(txt.strip()),confianza_media=round(m,1),revisar_visualmente=bool(m<65 or len(txt.strip())<120))
def main():
    args=[x for x in sys.argv[1:] if '=' in x]; hilos=os.cpu_count() or 4
    if '--hilos' in sys.argv: hilos=int(sys.argv[sys.argv.index('--hilos')+1])
    for dd in ('img','ocr','tsv'): os.makedirs(dd,exist_ok=True)
    inv=[];tareas=[]
    for a in args:
        clave,ruta=a.split('=',1); info=sh(['pdfinfo',ruta]).stdout
        pag=int(re.search(r'Pages:\s+(\d+)',info).group(1)); h=hashlib.sha256(open(ruta,'rb').read()).hexdigest()
        meta={k:(re.search(rf'{k}:\s+(.*)',info).group(1).strip() if re.search(rf'{k}:\s+(.*)',info) else '') for k in ('Producer','Creator','CreationDate','ModDate')}
        inv.append(dict(clave=clave,archivo=os.path.basename(ruta),hash=h,paginas=pag,metadatos=meta))
        w=len(str(pag)) if pag>=10 else 1
        sh(['pdftoppm','-r','300','-png',ruta,f'img/_{clave}'])
        for f in sorted(os.listdir('img')):
            m=re.match(rf'_{clave}-(\d+)\.png$',f)
            if m: os.replace('img/'+f,f"img/{clave}-{int(m.group(1)):0{w}d}.png")
        tareas+=[dict(clave=clave,n=i,total=pag) for i in range(1,pag+1)]
    hs={}
    for i in inv: hs.setdefault(i['hash'],[]).append(i['clave'])
    dup=[v for v in hs.values() if len(v)>1]
    with Pool(hilos) as p: pags=p.map(procesar,tareas)
    json.dump(dict(archivos=inv,duplicados_exactos=dup,paginas=pags),open('inventario.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(f'{len(pags)} páginas; giradas: {[p["pagina"] for p in pags if p["rotacion_aplicada"]]}; duplicados exactos: {dup or "ninguno"}')
    print('Revisar visualmente (OCR pobre):',[p['pagina'] for p in pags if p['revisar_visualmente']] or 'ninguna')
if __name__=='__main__': main()
