# -*- coding: utf-8 -*-
"""Ayudas de cálculo (B.3 y B.9). Cada función devuelve un dict {concepto, operacion, resultado} listo para `calculos` del JSON,
de modo que toda cifra del informe proceda de un cálculo registrado y hecho con script (no a mano)."""
from decimal import Decimal as D, ROUND_HALF_UP
import datetime
def q(x): return D(x).quantize(D('0.01'),rounding=ROUND_HALF_UP)
def f(x): return f'{q(x):,.2f}'
def sin_iva(total,tasa='0.16'):
    t=D(str(total)); s=q(t/(1+D(tasa))); return [dict(concepto='Subtotal = total ÷ 1.16',operacion=f'{f(t)} ÷ 1.16',resultado=str(s)),dict(concepto='IVA',operacion=f'{f(t)} − {f(s)}',resultado=str(q(t-s)))]
def porcentaje(concepto,a,b):
    return dict(concepto=concepto,operacion=f'{f(a)} ÷ {f(b)} × 100',resultado=str(q(D(str(a))/D(str(b))*100)))
def limite_uma(concepto,veces,uma_diaria=None,uma_anual=None):
    if uma_anual is not None: base=D(str(uma_anual)); op=f'{veces} × {f(base)} (UMA anual)'
    else: base=D(str(uma_diaria)); op=f'{veces} × {f(base)} (UMA diaria)'
    return dict(concepto=concepto,operacion=op,resultado=str(q(base*D(str(veces)))))
def veces(concepto,a,b): return dict(concepto=concepto,operacion=f'{f(a)} ÷ {f(b)}',resultado=str(q(D(str(a))/D(str(b)))))
def dia_semana(fecha):
    y,m,d=map(int,fecha.split('-')); return ['lunes','martes','miércoles','jueves','viernes','sábado','domingo'][datetime.date(y,m,d).weekday()]
def dias_naturales(f1,f2):
    a=datetime.date.fromisoformat(f1); b=datetime.date.fromisoformat(f2); return (b-a).days
def dias_habiles(f1,f2,inhabiles=()):
    a=datetime.date.fromisoformat(f1); b=datetime.date.fromisoformat(f2); n=0; inh={datetime.date.fromisoformat(x) for x in inhabiles}
    while a<b:
        a+=datetime.timedelta(days=1)
        if a.weekday()<5 and a not in inh: n+=1
    return n
if __name__=='__main__':
    print(sin_iva(900000)); print(porcentaje('Ampliación / máximo',900000,3000000)); print(dia_semana('2022-12-15'),dias_naturales('2022-09-06','2022-10-27'))
