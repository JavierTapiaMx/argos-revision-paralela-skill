# -*- coding: utf-8 -*-
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from rep import *
from reportlab.lib.pagesizes import letter
W,H=letter; FW=W-56
sf=S('f',7.6,9.6); sfb=S('fb',7.6,9.6,font='LS-B'); sfh=S('fh',8.8,font='LS-B',spaceBefore=5,spaceAfter=2,color=HexColor('#263238'))
def build(path):
    doc=BaseDocTemplate(path,pagesize=(W,H),leftMargin=28,rightMargin=28,topMargin=34,bottomMargin=32,title='Ficha ejecutiva '+d.NUM,author='El Despacho')
    doc.addPageTemplates([PageTemplate(id='p',frames=[Frame(28,32,FW,H-34-32,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)])])
    cnt=d.computar(); R=cnt['resultados']; K=cnt['riesgos']; fa=cnt['fuera_del_alcance']; al=cnt['con_alusion']
    el=[]
    el.append(Paragraph(f'Ficha ejecutiva · {esc(d.NUM)}',S('t',13,font='LS-B',color=HexColor('#263238'),spaceAfter=3)))
    FE=d.FE
    enc=[[P('Proveedor',sfb),P(FE['proveedor_linea'],sf)],[P('Procedimiento y fundamento',sfb),P(FE['procedimiento'],sf)]]
    el.append(tbl(enc,[110,FW-110],head=False,extra=[('BACKGROUND',(0,0),(0,-1),HEAD)]))
    el.append(Paragraph('Datos esenciales',sfh))
    dat=[[P(k,sfb),P(v,sf)] for k,v in FE['datos']]
    el.append(tbl(dat,[110,FW-110],head=False,extra=[('BACKGROUND',(0,0),(0,-1),HEAD)]))
    el.append(Paragraph('Dictamen',sfh))
    el.append(P(FE['dictamen'],sf))
    el.append(Paragraph('Semáforo de resultados',sfh))
    sem=[[Paragraph(f'<font color="{hx(RES_COL[k][1])}"><b>{v}</b></font> {k}',sf) for k,v in R.items()],[Paragraph(f'<font color="{hx(RIE_TXT[k])}"><b>{K[k]}</b></font> riesgo {k}',sf) for k in ['Alto','Medio','Bajo']]+[Paragraph(f'de los {R["No acreditado"]} No acreditado, {fa} fuera del alcance documental',sf),'']]
    t=Table(sem,colWidths=[FW/5]*5); t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.4,LINEA),('SPAN',(3,1),(4,1)),('LEFTPADDING',(0,0),(-1,-1),3),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)])); el.append(t)
    el.append(Paragraph('Riesgo máximo por rubro',sfh))
    cells=[]
    for r in d.RUBROS:
        m=d.rubro_max(r[3]); 
        cells.append((P(f'{r[0]}. {r[1]}',sf),Paragraph(f'<font name="LS-B" color="#FFFFFF">{m}</font>' if m else '<font name="LS-I" size="6">sin riesgo determinante</font>',ParagraphStyle('x',parent=sf,alignment=1)),m))
    rows=[];ex=[]
    for i in range(6):
        a=cells[i]; b=cells[i+6]; rows.append([a[0],a[1],b[0],b[1]])
        if a[2]: ex.append(('BACKGROUND',(1,i),(1,i),RIE_COL[a[2]]))
        if b[2]: ex.append(('BACKGROUND',(3,i),(3,i),RIE_COL[b[2]]))
    el.append(tbl(rows,[FW/2-60,60,FW/2-60,60],head=False,extra=ex))
    el.append(Paragraph('Hallazgos principales',sfh))
    for hb in FE['hallazgos']:
        tit,r,tx=hb['titulo'],hb['riesgo'],hb['texto']; pu=('punto ' if len(hb['puntos'])==1 else 'puntos ')+(', '.join(str(x) for x in hb['puntos'][:-1])+' y '+str(hb['puntos'][-1]) if len(hb['puntos'])>1 else str(hb['puntos'][0]))
        el.append(Paragraph(f'<b>{esc(tit)}</b> <font name="LS-B" color="{hx(RIE_TXT[r])}">({r})</font> · {pu}. {esc(tx)}',S('bl',7.2,8.9,leftIndent=9,bulletIndent=0),bulletText='•'))
    el.append(Paragraph('Acciones prioritarias',sfh))
    for i,a in enumerate(FE['acciones'],1):
        el.append(Paragraph(esc(a),S('ac',7.4,9.2,leftIndent=11,bulletIndent=0),bulletText=f'{i}.'))
    el.append(PageBreak())
    el.append(Tablero(FW,372))
    doc.build(el,canvasmaker=canvas_for('Ficha ejecutiva'))
if __name__=='__main__':
    build(os.path.join(os.environ.get('ARGOS_SALIDA','.'),f'Ficha_ejecutiva_{d.NUMF}.pdf'))
