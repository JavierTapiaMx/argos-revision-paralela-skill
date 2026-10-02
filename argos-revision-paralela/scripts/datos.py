# -*- coding: utf-8 -*-
"""Carga datos_revision.json (único insumo específico del expediente) y expone las estructuras que usan los generadores.
Ruta: variable de entorno ARGOS_DATOS (por defecto ./datos_revision.json)."""
import json, os
from collections import Counter
import protocolo_const as K
_path=os.environ.get('ARGOS_DATOS','datos_revision.json')
J=json.load(open(_path,encoding='utf-8'))
PROTO=J['protocolo']; FECHA=J['fecha']; NUM=J['contrato']; NUMF=J['contrato_archivo']; PROV=J['proveedor']; PROVC=J['proveedor_corto']
NOMBRES=K.NOMBRES; PRUEBAS=K.PRUEBAS
RUBROS=[(a,b,c,range(*r)) for a,b,c,r in K.RUBROS]
FICHA=[tuple(x) for x in J['ficha']]
INVENT=[(i['clave'],i['archivo'],i['hash'],i['paginas'],i['metadatos'],i['contenido']) for i in J['inventario']]
PAGINAS={i['clave']:[tuple(p) for p in i['paginas_detalle']] for i in J['inventario']}
CRON=[(c['fecha'],c['hora'],c['hecho'],c['emisor'],c['archivo_pagina'],c['observacion'],bool(c.get('fuera_de_secuencia'))) for c in J['cronologia']]
LDS=[(l['id'],l['pagina'],l['campo'],l['lecturas'],l['implicacion']) for l in J['lecturas_dudosas']]
P={p['n']:p for p in J['puntos']}
PRUEBAS_RES={k:(v['estado'],v['nota']) for k,v in J['pruebas'].items()}
H=[dict(id=h['id'],titulo=h['titulo'],riesgo=h['riesgo'],puntos=h['puntos'],filas=[tuple(f) for f in h['filas']]) for h in J['hallazgos']]
CALCULOS=J['calculos']
CRITERIOS=[(c['id'],c['puntos'],c['texto']) for c in J['criterios']]
DOCS=[(str(x['n']),x['documento'],x['emisor'],x['puntos']) for x in J['documentacion']]
CAPA=[(c['consulta'],c['resultado'],c['fuente']) for c in J['capa_externa']]
T=J['textos']; FE=J['ficha_ejecutiva']; CAP=J['capturas']
RANK={'Crítico':4,'Alto':3,'Medio':2,'Bajo':1,None:0}
def computar():
    res=Counter(p['resultado'] for p in J['puntos']); rie=Counter(p['riesgo'] for p in J['puntos'] if p['riesgo'])
    riesgos={k:rie.get(k,0) for k in ['Crítico','Alto','Medio','Bajo']}
    glob='Crítico' if riesgos['Crítico'] else 'Alto' if riesgos['Alto'] else 'Medio' if riesgos['Medio'] else 'Bajo'
    # riesgo global: el más alto de los hallazgos (A.5); los fuera del alcance sin alusión no cuentan
    cand=[p['riesgo'] for p in J['puntos'] if p['riesgo'] and not (p['fuera_del_alcance'] and not p['con_alusion'])]
    glob=max(cand,key=lambda r:RANK[r]) if cand else 'Bajo'
    return dict(resultados={k:res.get(k,0) for k in K.RESULTADOS},riesgos=riesgos,
        fuera_del_alcance=sum(1 for p in J['puntos'] if p['fuera_del_alcance']),con_alusion=sum(1 for p in J['puntos'] if p['con_alusion']),riesgo_global=glob,
        pruebas={k:sum(1 for v in PRUEBAS_RES.values() if v[0]==k) for k in K.ESTADOS_PRUEBA})
def rubro_max(nums):
    best=None
    for n in nums:
        p=P[n]
        if not p['riesgo']: continue
        if p['fuera_del_alcance'] and not p['con_alusion']: continue
        if RANK[p['riesgo']]>RANK[best]: best=p['riesgo']
    return best
