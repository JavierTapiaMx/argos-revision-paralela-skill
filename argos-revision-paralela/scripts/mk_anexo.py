# -*- coding: utf-8 -*-
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from rep import *
from reportlab.platypus import CondPageBreak
from capturas import fte,OUT
CAPS=d.CAP['capturas']; LDCAPS=d.CAP.get('capturas_ld',[])
from reportlab.platypus import Image as RImage
from reportlab.lib.pagesizes import letter
from PIL import Image as PI
W,H=letter; FW=W-56
sf=S('f',7.4,9.2); sfb=S('fb',7.4,9.2,font='LS-B'); sk=S('k',9,font='LS-B',color=HexColor('#263238'),spaceBefore=6,spaceAfter=2)
SEC=[(x['letra'],x['hallazgo']) for x in d.CAP['secciones']]
COMP=d.CAP.get('comparativas',{})
PUNTOS=d.CAP.get('puntos_por_captura',{})
def captura(c,key):
    im=PI.open(OUT+c['key']+'.png'); w,h=im.size
    wd=FW; ht=wd*h/w
    if ht>330: wd=wd*330/ht; ht=330
    fu=[]
    for pg,txt in c['fuente']: fu.append(f'<b>{esc(fte(pg))}</b> · {esc(txt)}')
    t=[Paragraph(f'<b>{c["key"]}</b> · <b>{esc(c["titulo"])}</b>',S('ct',8,10,font='LS',color=HexColor('#263238'),keepWithNext=1)),
       Paragraph('Fuente: '+'<br/>'.join(fu),S('fu',6.8,8.4,color=GRIS_CT)),Spacer(1,2),RImage(OUT+c['key']+'.png',width=wd,height=ht,hAlign='LEFT'),Spacer(1,2),Paragraph('<b>Observación:</b> '+esc(c['obs']),S('ob',7.2,9)),Spacer(1,8)]
    return KeepTogether(t)
def build(path):
    doc=BaseDocTemplate(path,pagesize=(W,H),leftMargin=28,rightMargin=28,topMargin=34,bottomMargin=32,title='Anexo de evidencias '+d.NUM,author='El Despacho')
    doc.addPageTemplates([PageTemplate(id='p',frames=[Frame(28,32,FW,H-34-32,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)])])
    el=[Paragraph(f'Anexo de evidencias · {esc(d.NUM)}',S('t',13,font='LS-B',color=HexColor('#263238'),spaceAfter=3))]
    ARCH='; '.join(f'{k}: {v}' for k,v in d.CAP['archivos'].items())
    el.append(P(f'Los recortes proceden de las digitalizaciones recibidas, sin alteración alguna; el recuadro rojo con relleno amarillo solo señala el texto pertinente. Cada captura cita archivo y página ({ARCH}) y las páginas giradas se enderezaron antes de recortar.',sf))
    byh={h['id']:h for h in d.H}
    for letter_,hid in SEC:
        h=byh[hid]; caps=[c for c in CAPS if c['h']==hid]
        el+=[CondPageBreak(120),Paragraph(f'{letter_}. Hallazgo {hid} ({h["riesgo"]}): {esc(h["titulo"])}',sk)]
        if hid in COMP:
            rows=[[Paragraph(esc(x),sfb) for x in COMP[hid][0]]]+[[P(x,sf) for x in r] for r in COMP[hid][1:]]
            n=len(COMP[hid][0]); el.append(tbl(rows,[130]+[(FW-130)/(n-1)]*(n-1)))
            el.append(Spacer(1,5))
        for c in caps: el.append(captura(c,c['key']))
    el+=[CondPageBreak(150),Paragraph('H. Lecturas dudosas (B.1)',sk)]
    ref={'LD-3':'C.2','LD-4':'C.3','LD-5':'D.1','LD-6':'D.2','LD-8':'C.1 y C.2','LD-9':'C.3'}
    rows=[[Paragraph(esc(x),sfb) for x in ('Id','Página','Campo','Lecturas candidatas','Captura')]]
    cap_ld={c['ld']:c['key'] for c in LDCAPS}
    for i,pg,campo,lec,imp in d.LDS:
        rows.append([P(i,sfb),P(pg,sf),P(campo,sf),P(' · '.join(lec),sf),P(cap_ld.get(i) or ref.get(i,''),sf)])
    el.append(tbl(rows,[32,50,260,120,FW-462])); el.append(Spacer(1,6))
    for c in LDCAPS: el.append(captura(c,c['key']))
    el+=[CondPageBreak(120),Paragraph('Puntos de la matriz que sustentan las capturas',sk)]
    rows=[[Paragraph(esc(x),sfb) for x in ('Capturas','Hallazgo','Puntos de la matriz')]]
    for letter_,hid in SEC:
        ks=[c['key'] for c in CAPS if c['h']==hid]
        rows.append([P(', '.join(ks),sf),P(hid,sf),P(', '.join(str(p) for p in byh[hid]['puntos'])+' (referencias: '+'; '.join(sorted({PUNTOS[k] for k in ks}))+')',sf)])
    rows.append([P(', '.join(c['key'] for c in LDCAPS),sf),P('B.1',sf),P('Lecturas dudosas LD-1 a LD-9 (criterios CV-8 y CV-6)',sf)])
    el.append(tbl(rows,[120,50,FW-170]))
    doc.build(el,canvasmaker=canvas_for('Anexo de evidencias'))
if __name__=='__main__':
    build(os.path.join(os.environ.get('ARGOS_SALIDA','.'),f'Evidencias_{d.NUMF}.pdf'))
