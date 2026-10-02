# -*- coding: utf-8 -*-
import sys,os,json; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from rep import *
def build(path):
    inv=[]
    for k,arch,h,n,meta,cont in d.INVENT:
        inv.append(dict(clave=k,archivo=arch,hash=h,paginas=n,metadatos=meta,contenido_por_pagina=[dict(pagina=pk,contenido=tx) for pk,tx in d.PAGINAS[k]]))
    out=dict(protocolo=d.PROTO,fecha=d.FECHA,contrato=d.NUM,proveedor=d.PROV,
      ficha=[dict(campo=a,valor=b) for a,b in d.FICHA],
      inventario=inv,
      cronologia=[dict(fecha=c[0],hora=c[1],documento=c[2],emisor=c[3],archivo_pagina=c[4],fuera_de_secuencia=bool(c[6]),observacion=c[5]) for c in d.CRON],
      lecturas_dudosas=[dict(id=i,archivo_pagina=pg,campo=campo,lecturas_candidatas=lec,implicacion=imp) for i,pg,campo,lec,imp in d.LDS],
      puntos=[dict(n=n,nombre=d.NOMBRES[n],resultado=p['resultado'],riesgo=p['riesgo'],fuera_del_alcance=p['fuera_del_alcance'],con_alusion=p['con_alusion'],evidencia=p['evidencia'],analisis=p['analisis'],accion=p['accion']) for n,p in sorted(d.P.items())],
      pruebas=[dict(clave=k,nombre=nm,estado=d.PRUEBAS_RES[k][0],nota=d.PRUEBAS_RES[k][1]) for k,nm in d.PRUEBAS],
      hallazgos=[dict(id=h['id'],titulo=h['titulo'],riesgo=h['riesgo'],puntos=h['puntos'],filas=[dict(campo=a,texto=b) for a,b in h['filas']]) for h in d.H],
      calculos=[dict(concepto=c['concepto'],operacion=c['operacion'],resultado=c['resultado']) for c in d.CALCULOS],
      criterios_a_validar=[dict(id=i,puntos=pu,criterio=tx) for i,pu,tx in d.CRITERIOS],
      documentacion_por_requerir=[dict(orden=int(n),documento=doc_,emisor_esperado=em,puntos=pu) for n,doc_,em,pu in d.DOCS],
      capa_externa=[dict(consulta=a,resultado=b,fuente=c) for a,b,c in d.CAPA],
      conteos=d.computar())
    json.dump(out,open(path,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
if __name__=='__main__':
    build(os.path.join(os.environ.get('ARGOS_SALIDA','.'),f'Datos_{d.NUMF}.json'))
