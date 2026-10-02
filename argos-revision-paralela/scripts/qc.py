# -*- coding: utf-8 -*-
"""Control de calidad automático (apartado D). NO modifica resultados: solo informa. Sale con código 1 si hay errores.
Uso: ARGOS_DATOS=datos_revision.json ARGOS_SALIDA=. python3 qc.py"""
import os,sys,re,json,subprocess,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import datos as d, protocolo_const as K
SAL=os.environ.get('ARGOS_SALIDA','.')
err=[];adv=[]
def E(m): err.append(m)
def A(m): adv.append(m)
P=d.P
# 1. 70 puntos
if sorted(P)!=list(range(1,71)): E('Faltan puntos o hay duplicados: '+str(sorted(set(range(1,71))-set(P))))
for n,p in P.items():
    if p['resultado'] not in K.RESULTADOS: E(f'Punto {n}: resultado inválido')
    if p['resultado'] in ('Cumple','No aplica') and p['riesgo']: E(f'Punto {n}: {p["resultado"]} no lleva riesgo')
    if p['resultado'] not in ('Cumple','No aplica') and p['riesgo'] not in K.RIESGOS: E(f'Punto {n}: falta riesgo')
    if not p.get('evidencia') or not p.get('analisis') or not p.get('accion'): E(f'Punto {n}: faltan evidencia, análisis o acción')
    if p['fuera_del_alcance'] and p['resultado']!='No acreditado': E(f'Punto {n}: marca fuera del alcance en resultado distinto de No acreditado')
    if p['fuera_del_alcance'] and 'fuera del alcance documental' not in p['analisis']: A(f'Punto {n}: el análisis no cita la marca «(fuera del alcance documental)»')
    if p['con_alusion'] and not (p['fuera_del_alcance'] and p['riesgo']=='Alto'): E(f'Punto {n}: alusión solo con fuera del alcance y riesgo Alto')
    if p['fuera_del_alcance'] and p['riesgo']=='Alto' and not p['con_alusion']: E(f'Punto {n}: Alto fuera del alcance sin alusión (B.0)')
    if n in K.PUNTOS_SIEMPRE_EN_ALCANCE and p['fuera_del_alcance']: E(f'Punto {n}: transversal, nunca fuera del alcance (A.9)')
    if p['resultado']=='No acreditado' and n in K.A8 and p['riesgo']!=K.A8[n] and not re.search(r'A\.8|raz[oó]n|excepci',p['analisis']): A(f'Punto {n}: riesgo {p["riesgo"]} difiere de A.8 ({K.A8[n]}) sin razón citada')
    if p['resultado']=='No acreditado' and 'documentación puesta a disposición' not in p['analisis']: A(f'Punto {n}: falta la fórmula «no acreditado con la documentación puesta a disposición para la revisión»')
# 2. hallazgos
prim={}
for h in d.H:
    for n in h['puntos']: prim.setdefault(n,[]).append(h['id'])
    if len(h['filas'])!=8 or [f[0] for f in h['filas']]!=['Obligación','Fundamento','Actuación','Documento','Evidencia','Resultado','Riesgo','Acción recomendada']: E(f'{h["id"]}: debe tener las ocho filas en orden')
if len(d.H)>7: E('Más de siete hallazgos (C.1.1)')
for n,v in prim.items():
    if len(v)>1: E(f'Punto {n} es principal en más de un hallazgo: {v}')
for n,p in P.items():
    if (p['riesgo'] in ('Alto','Crítico') or p['resultado']=='No cumple') and n not in prim: E(f'Punto {n} (Alto/Crítico/No cumple) no pertenece a ningún hallazgo')
orden=[(-K.RIESGOS.index(h['riesgo']),h['puntos'][0]) for h in d.H]
if orden!=sorted(orden): A('Los hallazgos no siguen el orden de C.1.1 (riesgo y primer punto)')
caps={}
for c in d.CAP['capturas']: caps.setdefault(c['h'],[]).append(c['key'])
for h in d.H:
    crit=h['riesgo'] in ('Alto','Crítico') or any(P[n]['resultado']=='No cumple' for n in h['puntos'])
    if crit and not caps.get(h['id']): E(f'{h["id"]}: hallazgo Alto/Crítico/No cumple sin captura')
for c in d.CAP['capturas']+d.CAP.get('capturas_ld',[]):
    if not os.path.exists(os.path.join(os.environ.get('ARGOS_CAPS','capturas'),c['key']+'.png')): E(f'Captura {c["key"]}: falta el PNG')
# 3. referencias de página
paginas=set()
for k,pl in d.PAGINAS.items():
    for pk,_ in pl: paginas.add((pk.split('-')[0],int(pk.split('-')[1])))
def revisa(txt,donde):
    for m in re.finditer(r'(?<![A-Za-z0-9])([A-Z])-(\d{1,2})(?![\d/])',txt):
        if m.group(1) in {k for k,_ in paginas} and (m.group(1),int(m.group(2))) not in paginas: A(f'{donde}: referencia a página inexistente {m.group(0)}')
for n,p in P.items(): revisa(p['evidencia']+' '+p['analisis'],f'Punto {n}')
for h in d.H:
    for a,b in h['filas']: revisa(b,h['id'])
# 4. fechas en sábado o domingo
for c in d.CRON:
    try:
        dt=datetime.date.fromisoformat(c[0][:10])
        if dt.weekday()>=5: A(f'Cronología: {c[0]} cae en fin de semana ({c[2][:50]}); confirmar que la cronología lo declare')
    except Exception: pass
# 5. PDFs
cnt=d.computar(); R=cnt['resultados']
pdfs={'tablero':f'Tablero_{d.NUMF}.pdf','informe':f'Revision_{d.NUMF}_{d.PROVC}.pdf','ficha':f'Ficha_ejecutiva_{d.NUMF}.pdf','anexo':f'Evidencias_{d.NUMF}.pdf'}
def txt(fn,page=None):
    cmd=['pdftotext','-layout']+(['-f',str(page),'-l',str(page)] if page else [])+[os.path.join(SAL,fn),'-']
    return subprocess.run(cmd,capture_output=True,text=True).stdout
def npag(fn): return int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',os.path.join(SAL,fn)],capture_output=True,text=True).stdout).group(1))
for k,fn in pdfs.items():
    if not os.path.exists(os.path.join(SAL,fn)): E(f'Falta el archivo {fn}'); continue
    n=npag(fn)
    if k=='ficha' and n>2: E(f'La ficha excede dos páginas ({n})')
    if k=='tablero' and n!=1: E('El tablero debe ocupar una página')
    for pg in range(1,n+1):
        t=txt(fn,pg)
        if 'El Despacho · ' not in t or 'Documento de trabajo · Confidencial' not in t or f'Página {pg} de {n}' not in t: E(f'{fn} p.{pg}: falta encabezado, leyenda o numeración')
    if k=='informe':
        t=txt(fn)
        for pal in ('Resumen ejecutivo','Marco teórico','Bibliografía'):
            if pal.lower() in t.lower(): E(f'El informe contiene «{pal}»')
        if 'Tablero de control' not in txt(fn,1): E('El informe no abre con el tablero')
        s=f'Cumple {R["Cumple"]}; Cumple parcialmente {R["Cumple parcialmente"]}; No cumple {R["No cumple"]}; No acreditado {R["No acreditado"]}'
        if re.sub(r'\s+',' ',s) not in re.sub(r'\s+',' ',t): E('El informe no declara los conteos del tablero')
    if k=='ficha':
        t=re.sub(r'\s+',' ',txt(fn))
        for kk,v in R.items():
            if f'{v} {kk}' not in t: E(f'La ficha no muestra «{v} {kk}»')
        if len(d.FE['hallazgos'])<5 or len(d.FE['hallazgos'])>7: E('La ficha debe tener de 5 a 7 hallazgos')
        if len(d.FE['acciones'])!=5: E('La ficha debe tener 5 acciones')
# 6. JSON
jf=os.path.join(SAL,f'Datos_{d.NUMF}.json')
if os.path.exists(jf):
    j=json.load(open(jf,encoding='utf-8'))
    for k in ['protocolo','fecha','contrato','proveedor','ficha','inventario','cronologia','lecturas_dudosas','puntos','pruebas','hallazgos','calculos','criterios_a_validar','documentacion_por_requerir','capa_externa','conteos']:
        if k not in j: E(f'JSON: falta la clave {k}')
    if j.get('conteos')!=cnt: E('JSON: conteos distintos de los calculados')
else: E('Falta el JSON de datos')
if not d.CALCULOS: E('Sin cálculos registrados (B.3)')
if len(d.PRUEBAS_RES)!=12: E('Deben registrarse 12 pruebas (B.0 a B.9 con B.3 bis y B.5 bis)')
if not d.LDS: A('Sin lecturas dudosas registradas: confirmar que la lista cerrada de B.1 se revisó')
print(f'Conteos: {R} | riesgos {cnt["riesgos"]} | fuera del alcance {cnt["fuera_del_alcance"]} (alusión {cnt["con_alusion"]}) | global {cnt["riesgo_global"]}')
print(f'Capturas: {sum(len(v) for v in caps.values())} + {len(d.CAP.get("capturas_ld",[]))} de lecturas dudosas. Pendiente manual: revisar visualmente cada captura (python3 montage.py ...).')
for m in adv: print('AVISO ',m)
for m in err: print('ERROR ',m)
print('QC: '+('SIN ERRORES' if not err else f'{len(err)} ERROR(ES)')+f'; {len(adv)} aviso(s)')
sys.exit(1 if err else 0)
