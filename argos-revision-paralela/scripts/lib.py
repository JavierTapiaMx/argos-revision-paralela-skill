# -*- coding: utf-8 -*-
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas as rlcanvas
from reportlab.platypus import Flowable
from reportlab.lib.styles import ParagraphStyle
import os
import datos as d
FD='/usr/share/fonts/truetype/liberation/'
for n,f in [('LS','LiberationSans-Regular'),('LS-B','LiberationSans-Bold'),('LS-I','LiberationSans-Italic'),('LS-BI','LiberationSans-BoldItalic')]:
    pdfmetrics.registerFont(TTFont(n,FD+f+'.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('LS',normal='LS',bold='LS-B',italic='LS-I',boldItalic='LS-BI')
# colores de calificación
VERDE=HexColor('#2E7D32'); AMBAR=HexColor('#E69F00'); AMBAR_T=HexColor('#9A6500'); ROJO=HexColor('#C62828'); ROJO_OSC=HexColor('#7F0000'); GRIS_A=HexColor('#607D8B'); GRIS_C=HexColor('#BDBDBD'); GRIS_CT=HexColor('#757575')
TXT=HexColor('#222222'); LINEA=HexColor('#CFD8DC')
RES_COL={'Cumple':(VERDE,VERDE),'Cumple parcialmente':(AMBAR,AMBAR_T),'No cumple':(ROJO,ROJO),'No acreditado':(GRIS_A,GRIS_A),'No aplica':(GRIS_C,GRIS_CT)}
EST_COL={'sin observación':RES_COL['Cumple'],'observación':RES_COL['Cumple parcialmente'],'hallazgo':RES_COL['No cumple'],'pendiente':RES_COL['No acreditado']}
RIE_COL={'Bajo':VERDE,'Medio':AMBAR,'Alto':ROJO,'Crítico':ROJO_OSC}
RIE_TXT={'Bajo':VERDE,'Medio':AMBAR_T,'Alto':ROJO,'Crítico':ROJO_OSC}
RIE_L={'Bajo':'B','Medio':'M','Alto':'A','Crítico':'C'}
def hx(c): return '#%02X%02X%02X'%(int(c.red*255),int(c.green*255),int(c.blue*255))

def trunc(txt,font,size,maxw):
    if pdfmetrics.stringWidth(txt,font,size)<=maxw: return txt
    while txt and pdfmetrics.stringWidth(txt+'…',font,size)>maxw: txt=txt[:-1]
    return txt+'…'

def draw_tablero(c,x,y,w,h):
    """x,y esquina inferior izquierda; w,h ancho y alto."""
    cnt=d.computar(); R=cnt['resultados']; K=cnt['riesgos']; P=d.P
    total=70+len(d.PRUEBAS)
    # banda de título
    bh=26
    c.setFillColor(HexColor('#263238')); c.rect(x,y+h-bh,w,bh,stroke=0,fill=1)
    c.setFillColor(white); c.setFont('LS-B',12.5); c.drawString(x+8,y+h-bh+9,f'Tablero de control · {total} aspectos revisados')
    c.setFont('LS',8.5); c.drawRightString(x+w-8,y+h-bh+9,f'{d.NUM} · {d.PROV}')
    # indicadores
    ih=36; iy=y+h-bh-ih-4
    items=[('Cumple',R['Cumple']),('Cumple parcialmente',R['Cumple parcialmente']),('No cumple',R['No cumple']),('No acreditado',R['No acreditado']),('No aplica',R['No aplica'])]
    kk=k0=min(1.0,w/736); bw=82*kk; gap=4*kk; cx=x
    for k,v in items:
        col=RES_COL[k][0]; c.setFillColor(col); c.rect(cx,iy,bw,ih,stroke=0,fill=1)
        c.setFillColor(white if k!='No aplica' else TXT); c.setFont('LS-B',17); c.drawString(cx+6,iy+13,str(v))
        c.setFont('LS',7 if k0>=0.99 else 5.6); c.drawString(cx+6,iy+3.5,k)
        cx+=bw+gap
    # riesgos
    bw2=60*kk; cx+=6*kk
    for k in ['Alto','Medio','Bajo']+(['Crítico'] if K['Crítico'] else []):
        col=RIE_COL[k]; c.setFillColor(col); c.rect(cx,iy,bw2,ih,stroke=0,fill=1)
        c.setFillColor(white); c.setFont('LS-B',17); c.drawString(cx+6,iy+13,str(K[k])); c.setFont('LS',7 if k0>=0.99 else 5.6); c.drawString(cx+6,iy+3.5,'Riesgo '+k)
        cx+=bw2+gap
    # riesgo global
    gw=x+w-cx; col=RIE_COL[cnt['riesgo_global']]
    c.setFillColor(col); c.rect(cx+4,iy,gw-4,ih,stroke=0,fill=1)
    c.setFillColor(white); c.setFont('LS',7); c.drawString(cx+10,iy+ih-9,'Riesgo global'); c.setFont('LS-B',15); c.drawString(cx+10,iy+7,cnt['riesgo_global'].upper())
    # subtotales de No acreditado y pruebas
    sy=iy-9
    fa=cnt['fuera_del_alcance']; al=cnt['con_alusion']
    narrow=w<700
    c.setFillColor(TXT); c.setFont('LS',6.8 if not narrow else 6.0)
    t1=f'No acreditado: {R["No acreditado"]-fa} dentro del alcance y {fa} «fuera del alcance documental» ({al} con alusión a la irregularidad).'
    t2='Pruebas B.0 a B.9: '+', '.join(f'{v} {k}' for k,v in cnt['pruebas'].items())+'.'
    if narrow:
        c.drawString(x,sy,t1); sy-=8; c.drawString(x,sy,t2)
    else:
        c.drawString(x,sy,t1+'   '+t2)
    # leyenda (abajo)
    ly=y+3+(8 if narrow else 0)
    lx=x; fsz=6.2 if not narrow else 5.6; c.setFont('LS',fsz)
    labs=[('Cumple / sin observación',RES_COL['Cumple'][0]),('Cumple parcialmente / observación',RES_COL['Cumple parcialmente'][0]),('No cumple / hallazgo',RES_COL['No cumple'][0]),('No acreditado / pendiente',RES_COL['No acreditado'][0]),('No aplica',RES_COL['No aplica'][0])]
    for lab,col in labs:
        c.setFillColor(col); c.rect(lx,ly,8,6,stroke=0,fill=1); c.setFillColor(TXT); c.drawString(lx+11,ly+0.5,lab); lx+=11+pdfmetrics.stringWidth(lab,'LS',fsz)+(8 if not narrow else 5)
    tl='Letra final: riesgo (A, M, B, C) · Negrita: Alto, Crítico y No cumple · Cursiva: fuera del alcance documental'
    if narrow: c.drawString(x,y+3,tl)
    else: c.drawString(lx,ly+0.5,tl)
    # rejilla
    gy_top=sy-6; gy_bot=ly+11
    cols=[[1,2,3],[4,5,6],[7,8,9,10],[11,12,'T']]
    nl=[]
    def lines(g):
        if g=='T': return 1+len(d.PRUEBAS)
        r=d.RUBROS[g-1]; return 1+len(r[3])
    maxl=max(sum(lines(g) for g in col) for col in cols)
    lh=(gy_top-gy_bot)/maxl
    cw=(w-3*8)/4
    fs=min(6.4,lh*0.78)
    for ci,col in enumerate(cols):
        cx0=x+ci*(cw+8); yy=gy_top
        for g in col:
            # encabezado de rubro
            yy-=lh
            if g=='T':
                title='Pruebas transversales'; tag=None
            else:
                r=d.RUBROS[g-1]; title=f'{r[0]}. {r[2]}'; tag=d.rubro_max(r[3])
            c.setFillColor(HexColor('#ECEFF1')); c.rect(cx0,yy+0.5,cw,lh-1,stroke=0,fill=1)
            c.setFillColor(TXT); c.setFont('LS-B',fs+0.6); c.drawString(cx0+3,yy+lh*0.28,title)
            if g!='T':
                if tag:
                    tw=34; c.setFillColor(RIE_COL[tag]); c.roundRect(cx0+cw-tw-2,yy+1.5,tw,lh-3,2,stroke=0,fill=1)
                    c.setFillColor(white); c.setFont('LS-B',fs-0.3); c.drawCentredString(cx0+cw-tw/2-2,yy+lh*0.3,'Riesgo '+RIE_L[tag] if False else tag)
                else:
                    c.setFillColor(GRIS_CT); c.setFont('LS-I',fs-0.3); c.drawRightString(cx0+cw-3,yy+lh*0.3,'sin riesgo determinante')
            # aspectos
            items=[]
            if g=='T':
                for k,nm in d.PRUEBAS:
                    est=d.PRUEBAS_RES[k][0]; items.append((k,nm,EST_COL[est],False,False,None))
            else:
                for n in r[3]:
                    p=P[n]; col=RES_COL[p['resultado']]
                    bold=(p['riesgo'] in ('Alto','Crítico')) or p['resultado']=='No cumple'
                    items.append((str(n),d.NOMBRES[n],col,bold,p['fuera_del_alcance'],p['riesgo']))
            for key,nm,col,bold,ital,rie in items:
                yy-=lh
                chw=22 if len(key)<=2 else 27
                c.setFillColor(col[0]); c.roundRect(cx0,yy+1,chw,lh-2,2,stroke=0,fill=1)
                c.setFillColor(white if col[0] not in (GRIS_C,) else TXT); c.setFont('LS-B',fs-0.2); c.drawCentredString(cx0+chw/2,yy+lh*0.28,key)
                font='LS-BI' if (bold and ital) else 'LS-B' if bold else 'LS-I' if ital else 'LS'
                c.setFillColor(col[1]); c.setFont(font,fs)
                c.drawString(cx0+chw+3,yy+lh*0.28,trunc(nm,font,fs,cw-chw-3-12))
                if rie:
                    c.setFillColor(RIE_TXT[rie]); c.setFont('LS-B',fs); c.drawRightString(cx0+cw-2,yy+lh*0.28,RIE_L[rie])
            yy-=0
        # separadores
    return

class Tablero(Flowable):
    def __init__(self,w,h): Flowable.__init__(self); self.w=w; self.h=h; self.width=w; self.height=h
    def wrap(self,aw,ah): return self.w,self.h
    def draw(self): draw_tablero(self.canv,0,0,self.w,self.h)

class NumCanvas(rlcanvas.Canvas):
    tipo='Documento'
    def __init__(self,*a,**k): rlcanvas.Canvas.__init__(self,*a,**k); self._saved=[]
    def showPage(self): self._saved.append(dict(self.__dict__)); self._startPage()
    def save(self):
        n=len(self._saved)
        for st in self._saved:
            self.__dict__.update(st); self.decor(n); rlcanvas.Canvas.showPage(self)
        rlcanvas.Canvas.save(self)
    def decor(self,n):
        W,H=self._pagesize
        self.setFont('LS',7.5); self.setFillColor(GRIS_CT)
        self.drawString(28,H-20,f'El Despacho · {self.tipo} · {d.NUM}')
        self.drawRightString(W-28,H-20,'Documento de trabajo · Confidencial')
        self.setStrokeColor(LINEA); self.line(28,H-24,W-28,H-24); self.line(28,24,W-28,24)
        self.drawString(28,14,d.FECHA)
        self.drawRightString(W-28,14,f'Página {self._pageNumber} de {n}')
def canvas_for(tipo):
    class C(NumCanvas): pass
    C.tipo=tipo; return C
