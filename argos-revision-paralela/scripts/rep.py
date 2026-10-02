# -*- coding: utf-8 -*-
import json
from xml.sax.saxutils import escape
from reportlab.platypus import Paragraph,Table,TableStyle,Spacer,PageBreak,KeepTogether,SimpleDocTemplate,PageTemplate,Frame,BaseDocTemplate
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,white
from lib import *
import datos as d
def S(name,size=7.5,lead=None,font='LS',color=TXT,**k):
    return ParagraphStyle(name,fontName=font,fontSize=size,leading=lead or size*1.28,textColor=color,**k)
st=S('n'); stb=S('b',font='LS-B'); sth1=S('h1',11,font='LS-B',spaceBefore=8,spaceAfter=4,color=HexColor('#263238'))
sth2=S('h2',8.5,font='LS-B',spaceBefore=6,spaceAfter=3,color=HexColor('#263238'))
stc=S('c',6.8); stcb=S('cb',6.8,font='LS-B'); sts=S('s',6.3,color=GRIS_CT)
def esc(t): return escape(str(t))
def P(t,style=st): return Paragraph(esc(t),style)
def PR(t,style=st): return Paragraph(t,style)   # markup ya escapado
HEAD=HexColor('#ECEFF1')
def tbl(rows,widths,head=True,extra=None,repeat=1,zebra=False):
    t=Table(rows,colWidths=widths,repeatRows=repeat if head else 0,splitByRow=1)
    sty=[('GRID',(0,0),(-1,-1),0.4,LINEA),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)]
    if head: sty+=[('BACKGROUND',(0,0),(-1,0),HEAD)]
    if extra: sty+=extra
    t.setStyle(TableStyle(sty)); return t
def hdr(*cols): return [Paragraph(esc(c),stcb) for c in cols]
def reschip(res,fa=False,al=False):
    col=RES_COL[res][1]
    s=f'<font name="LS-B" color="{hx(col)}">{esc(res)}</font>'
    if fa: s+=f'<br/><font name="LS-I" size="6" color="{hx(GRIS_CT)}">(fuera del alcance documental)</font>'
    if al: s+=f'<br/><font name="LS-I" size="6" color="{hx(ROJO)}">(con alusión a la irregularidad)</font>'
    return Paragraph(s,stc)
def riesgo_cell(r):
    if not r: return Paragraph('—',stc)
    return Paragraph(f'<font name="LS-B" color="#FFFFFF">{r}</font>',ParagraphStyle('rc',parent=stc,alignment=1))
def riesgo_style(row,r):
    return [('BACKGROUND',(3,row),(3,row),RIE_COL[r])] if r else []
def conteos_rubro(r):
    nums=list(r[3]); c={k:0 for k in ['Cumple','Cumple parcialmente','No cumple','No acreditado','No aplica']}; rr={'Alto':0,'Medio':0,'Bajo':0,'Crítico':0}; fa=0
    for n in nums:
        p=d.P[n]; c[p['resultado']]+=1
        if p['riesgo']: rr[p['riesgo']]+=1
        if p['fuera_del_alcance']: fa+=1
    return c,rr,fa
def fuera_seq(c):
    return bool(c[6])
def fecha_larga(f):
    import datetime
    meses=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
    try:
        y,m,dd=f.split('-'); return f'{int(dd):02d}-{meses[int(m)-1][:3]}-{y}'
    except Exception: return f
def calculos(): return d.CALCULOS
