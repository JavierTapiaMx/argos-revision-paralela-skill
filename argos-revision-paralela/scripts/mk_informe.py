# -*- coding: utf-8 -*-
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from rep import *
from reportlab.platypus import CondPageBreak
from reportlab.lib.pagesizes import letter, landscape
W,H=landscape(letter); FW=W-56
def build(path):
    doc=BaseDocTemplate(path,pagesize=(W,H),leftMargin=28,rightMargin=28,topMargin=34,bottomMargin=32,title='Informe de revisión '+d.NUM,author='El Despacho')
    doc.addPageTemplates([PageTemplate(id='p',frames=[Frame(28,32,FW,H-34-32,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)])])
    el=[Tablero(FW,372),PageBreak()]
    cnt=d.computar()
    # 1
    el+=[CondPageBreak(70),Paragraph('1. Datos del contrato y documentación revisada',sth1)]
    el.append(tbl([[P(a,stcb),P(b,stc)] for a,b in d.FICHA],[150,FW-150],head=False,extra=[('BACKGROUND',(0,0),(0,-1),HEAD)]))
    el+=[CondPageBreak(70),Paragraph('Archivos revisados',sth2)]
    rows=[hdr('Clave','Archivo','SHA-256','Págs.','Metadatos de digitalización','Contenido')]
    for k,arch,h,n,meta,cont in d.INVENT:
        rows.append([P(k,stcb),P(arch,stc),Paragraph(f'<font size="5.6">{h}</font>',stc),P(str(n),stc),P(meta,stc),P(cont,stc)])
    el.append(tbl(rows,[30,110,190,28,150,FW-508]))
    el.append(Spacer(1,3))
    el.append(P(d.T['nota_inventario'],stc))
    el+=[CondPageBreak(70),Paragraph('Contenido por página',sth2)]
    rows=[hdr('Clave','Documento')]
    for f in 'ABC':
        for k,txt in d.PAGINAS[f]: rows.append([P(k,stcb),P(txt,stc)])
    el.append(tbl(rows,[40,FW-40]))
    el+=[CondPageBreak(70),Paragraph('Lecturas dudosas (B.1)',sth2)]
    rows=[hdr('Id','Página','Campo','Lecturas candidatas','Implicación')]
    for i,pg,campo,lec,imp in d.LDS: rows.append([P(i,stcb),P(pg,stc),P(campo,stc),P(' · '.join(lec),stc),P(imp,stc)])
    el.append(tbl(rows,[32,50,240,130,FW-452]))
    el+=[CondPageBreak(70),Paragraph('Alcance (B.0)',sth2)]
    el.append(P(d.PRUEBAS_RES['B.0'][1]+' '+d.T['alcance_no_obran'],st))
    el+=[CondPageBreak(70),Paragraph('Marco jurídico (A.1)',sth2)]
    el.append(P(d.T['marco'],st))
    # 2
    el+=[CondPageBreak(70),Paragraph('2. Criterio de aplicación',sth1)]
    el.append(P('Cada uno de los 70 puntos se califica con una de cinco categorías: Cumple; Cumple parcialmente (hay evidencia con alguna deficiencia o el soporte está citado con folio, fecha o firmante y no obra, pues la cita acredita su existencia y no su contenido); No cumple (exige evidencia material en los propios documentos: una contradicción, un cálculo que no cuadra, una fecha imposible o un texto contrario a la norma o al contrato); No acreditado (ningún rastro del soporte «con la documentación puesta a disposición para la revisión», sin afirmar incumplimiento) y No aplica (el punto no es exigible por la naturaleza del procedimiento). A todo resultado distinto de Cumple y No aplica se asigna riesgo Bajo (deficiencia formal), Medio (falta de soporte que impide verificar), Alto (indicio documental de irregularidad que puede afectar la validez o la aplicación de los recursos) o Crítico (pago sin contraprestación acreditada, pago en exceso cuantificado, contratación sin procedimiento o sin suficiencia, o indicios de falsedad). El legajo es mixto: los puntos de etapas que no cubre llevan la marca «(fuera del alcance documental)»; solo determinan el riesgo máximo del rubro y el global cuando hay alusión a la irregularidad citada textualmente. '+d.T['criterio_regimen']+' Las lecturas dudosas o ambiguas se resuelven con la más favorable al ente que sea razonable y se registran en la sección 9.',st))
    # 3
    el+=[CondPageBreak(70),Paragraph('3. Cronología maestra',sth1)]
    rows=[hdr('Fecha','Hora','Hecho','Emisor','Archivo y página','Observación')]; ex=[]
    for i,c in enumerate(d.CRON,1):
        rows.append([P(fecha_larga(c[0]) if len(c[0])==10 else c[0],stc),P(c[1],stc),P(c[2],stc),P(c[3],stc),P(c[4],stc),P(c[5],stc)])
        if fuera_seq(c): ex.append(('BACKGROUND',(0,i),(-1,i),HexColor('#FDECEA')))
    el.append(tbl(rows,[62,52,250,110,80,FW-554],extra=ex))
    el.append(P(d.T['nota_cronologia'],sts))
    # 4
    el+=[CondPageBreak(70),Paragraph('4. Resultado por rubro',sth1)]
    rows=[hdr('Rubro','Cumple','Cumple parc.','No cumple','No acred.','de ellos fuera del alcance','No aplica','Alto','Medio','Bajo','Riesgo máximo')]
    tot=[0]*9; ex=[]
    for i,r in enumerate(d.RUBROS,1):
        c,rr,fa=conteos_rubro(r); m=d.rubro_max(r[3])
        vals=[c['Cumple'],c['Cumple parcialmente'],c['No cumple'],c['No acreditado'],fa,c['No aplica'],rr['Alto'],rr['Medio'],rr['Bajo']]
        tot=[a+b for a,b in zip(tot,vals)]
        rows.append([P(f'{r[0]}. {r[1]}',stc)]+[P(str(v),stc) for v in vals]+[Paragraph(f'<font name="LS-B" color="#FFFFFF">{m}</font>' if m else '<font name="LS-I" size="6">sin riesgo determinante (fuera del alcance)</font>',stc)])
        if m: ex.append(('BACKGROUND',(10,i),(10,i),RIE_COL[m]))
    rows.append([P('Total',stcb)]+[P(str(v),stcb) for v in tot]+[Paragraph(f'<font name="LS-B" color="#FFFFFF">{cnt["riesgo_global"]}</font>',stc)])
    ex.append(('BACKGROUND',(10,len(rows)-1),(10,len(rows)-1),RIE_COL[cnt['riesgo_global']]))
    el.append(tbl(rows,[190,42,54,46,46,70,46,36,40,36,FW-606],extra=ex))
    el.append(P(f'Totales idénticos al tablero: Cumple {cnt["resultados"]["Cumple"]}; Cumple parcialmente {cnt["resultados"]["Cumple parcialmente"]}; No cumple {cnt["resultados"]["No cumple"]}; No acreditado {cnt["resultados"]["No acreditado"]} (de ellos {cnt["fuera_del_alcance"]} «fuera del alcance documental», {cnt["con_alusion"]} con alusión a la irregularidad); No aplica {cnt["resultados"]["No aplica"]}. Riesgos: Alto {cnt["riesgos"]["Alto"]}; Medio {cnt["riesgos"]["Medio"]}; Bajo {cnt["riesgos"]["Bajo"]}; Crítico {cnt["riesgos"]["Crítico"]}. Riesgo global: {cnt["riesgo_global"]}.',sts))
    # 5
    el+=[CondPageBreak(70),Paragraph('5. Hallazgos principales',sth1)]
    for h in d.H:
        t=[[Paragraph(f'<b>{h["id"]}. {esc(h["titulo"])}</b>',st),'']]
        for a,b in h['filas']:
            if a=='Riesgo': t.append([P(a,stcb),Paragraph(f'<font name="LS-B" color="{hx(RIE_TXT[h["riesgo"]])}">{esc(b)}</font>',stc)])
            else: t.append([P(a,stcb),P(b,stc)])
        tb=Table(t,colWidths=[90,FW-90],splitByRow=1)
        tb.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.4,LINEA),('SPAN',(0,0),(1,0)),('BACKGROUND',(0,0),(1,0),HEAD),('BACKGROUND',(0,1),(0,-1),HEAD),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),3),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),('LINEBEFORE',(0,0),(0,0),3,RIE_COL[h['riesgo']])]))
        el+= [tb,Spacer(1,6)]
    # 6
    el.append(PageBreak()); el+=[CondPageBreak(70),Paragraph('6. Matriz de 70 puntos',sth1)]
    rows=[hdr('Nº','Punto de control','Resultado','Riesgo','Evidencia y análisis','Acción recomendada')]; ex=[]; spans=[]
    for r in d.RUBROS:
        rows.append([Paragraph(f'<b>Rubro {r[0]}. {esc(r[1])}</b>',stc),'','','','',''])
        ri=len(rows)-1; ex+=[('SPAN',(0,ri),(-1,ri)),('BACKGROUND',(0,ri),(-1,ri),HEAD)]
        for n in r[3]:
            p=d.P[n]
            rows.append([P(str(n),stcb),P(d.NOMBRES[n],stc),reschip(p['resultado'],p['fuera_del_alcance'],p['con_alusion']),riesgo_cell(p['riesgo']),
              Paragraph(f'<b>Evidencia:</b> {esc(p["evidencia"])}. {esc(p["analisis"])}',stc),P(p['accion'],stc)])
            ex+=riesgo_style(len(rows)-1,p['riesgo'])
    el.append(tbl(rows,[20,78,66,36,360,FW-560],extra=ex))
    # 7
    el+=[CondPageBreak(70),Paragraph('7. Pruebas transversales',sth1)]
    rows=[hdr('Prueba','Estado','Resultado')]; ex=[]
    for i,(k,nm) in enumerate(d.PRUEBAS,1):
        est,nota=d.PRUEBAS_RES[k]
        rows.append([P(f'{k} {nm}',stcb),Paragraph(f'<font name="LS-B" color="{hx(EST_COL[est][1])}">{est}</font>',stc),P(nota,stc)])
    el.append(tbl(rows,[120,60,FW-180]))
    el+=[CondPageBreak(70),Paragraph('Cálculos registrados (B.3 y B.9)',sth2)]
    rows=[hdr('Concepto','Operación','Resultado')]
    for c in calculos():
        res=c['resultado']
        try:
            v=float(res.replace(',','')); 
            res=f'{v:,.2f}' if abs(v)>=1000 or '.' in res else res
        except Exception: pass
        rows.append([P(c['concepto'],stc),P(c['operacion'],stc),P(res,stc)])
    el.append(tbl(rows,[330,260,FW-590]))
    # 8
    el+=[CondPageBreak(70),Paragraph('8. Documentación por requerir',sth1)]
    rows=[hdr('Nº','Documento','Emisor esperado','Puntos a los que sirve')]
    for n,doc_,em,pu in d.DOCS: rows.append([P(n,stcb),P(doc_,stc),P(em,stc),P(pu,stc)])
    el.append(tbl(rows,[22,360,190,FW-572]))
    # 9
    el+=[CondPageBreak(70),Paragraph('9. Criterios a validar',sth1)]
    rows=[hdr('Id','Puntos','Criterio: lecturas posibles, calificación adoptada y documento que lo resolvería')]
    for i,pu,tx in d.CRITERIOS: rows.append([P(i,stcb),P(pu,stc),P(tx,stc)])
    el.append(tbl(rows,[32,110,FW-142]))
    el+=[CondPageBreak(70),Paragraph('Capa externa (B.8)',sth2)]
    rows=[hdr('Consulta','Resultado','Fuente')]
    for a,b,c in d.CAPA: rows.append([P(a,stc),P(b,stc),P(c,stc)])
    el.append(tbl(rows,[190,FW-330,140]))
    doc.build(el,canvasmaker=canvas_for('Informe de revisión'))
if __name__=='__main__':
    build(os.path.join(os.environ.get('ARGOS_SALIDA','.'),f'Revision_{d.NUMF}_{d.PROVC}.pdf'))
