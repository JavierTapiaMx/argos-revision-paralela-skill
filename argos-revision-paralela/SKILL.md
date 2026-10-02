---
name: "argos-revision-paralela"
description: "Orquesta con subagentes la revisión Argos de un expediente de contratación (70 puntos): hechos únicos, calificación paralela por rubros, consolidación y verificación."
---

# Revisión Argos en paralelo

Ejecuta el flujo del apartado 3 de las instrucciones del proyecto Argos con subagentes. El protocolo vigente, el marco jurídico aplicable (`marco-juridico-aplicable.md`) y la Matriz son la única fuente de reglas; este skill solo reparte el trabajo.

## Principio

Paralelizar la lectura de pruebas; centralizar el juicio. Un piloto (expediente CM/SH/ADE/104/2022 UNO) mostró que cinco calificadores en paralelo coinciden en 70/70 resultados y en ~90 % de riesgos, y que la divergencia nace de reglas transversales (alusión a la irregularidad, A.8, A.9) aplicadas por separado. Esas reglas las aplica una sola instancia.

## Independencia

Toda ejecución es independiente. No busques, cargues, consultes ni compares resultados, JSON, análisis ni cálculos de ejecuciones anteriores del mismo expediente, aunque estén en la carpeta de trabajo o en el proyecto, y no se los entregues a ningún subagente. Los entregables se guardan directamente en la carpeta de trabajo, sin subcarpetas; si ya existe un archivo con el mismo nombre, se sobrescribe sin abrirlo ni leerlo.

## Pasos

1. **Inventario, ficha, cronología y OCR** (instancia principal, sin subagentes). Declara el ámbito (estatal o federal), la entidad o la Federación y la fecha de verificación del marco jurídico (M.0). Criterio de cierre: cada página leída con OCR en `pilot/ocr/<archivo>-<pág>.txt` y cada página con OCR vacío o girado reprocesada o listada como lectura dudosa.
2. **Hechos neutros.** Escribe `hechos.md` (ficha, inventario, cronología, cálculos, citas textuales, ámbito y entidad del marco) sin calificaciones. Copia protocolo, marco jurídico (`marco-juridico-aplicable.md`), hechos y OCR a un directorio de trabajo y verifica con `ls` que el OCR no esté vacío y que el marco jurídico esté presente antes de lanzar agentes.
3. **Calificación paralela.** Lanza en un solo mensaje un subagente por grupo: puntos 1–19, 20–34, 35–46, 47–60, 61–70. Cada uno recibe solo el directorio de trabajo (que incluye el marco jurídico), sus puntos, y la orden de escribir `out_k.json` con `n, resultado, riesgo, fuera_del_alcance, con_alusion, evidencia, analisis`. Cada subagente toma todo dato normativo (parámetros, umbrales, preceptos, nombres de órganos y registros) únicamente de las claves M.x del marco jurídico; si un dato no está, escribe «parámetro no definido en el marco» y no lo suple. Criterio de cierre: los cinco JSON existen y cubren los 70 puntos sin huecos.
4. **Pruebas transversales B.0–B.9** en la instancia principal mientras corren los agentes.
5. **Consolidación (instancia principal).** Reaplica a todos los puntos: A.1 (marco jurídico), A.5, A.6, A.7, A.8, A.9, A.10 y B.0; recalcula riesgo por tabla y exige razón citada para apartarse de A.8. Resuelve los puntos cruzados (9, 47, 59, 61) con la cronología completa.
6. **Verificación independiente.** Un subagente por cada resultado «No cumple» o riesgo Alto/Crítico. Cada uno recibe la cita y las páginas, y responde confirmado o refutado con texto OCR.
7. **Hallazgos, evidencias, tablero y entregables.** Instancia principal: genera los cuatro PDF y el JSON de datos (C.4) conforme al apartado C del protocolo y guárdalos directamente en la carpeta de trabajo. Criterio de cierre: la lista D del protocolo, sin pendientes.

## Controles de certeza

- Un subagente que reporta OCR vacío o fuente faltante detiene el paso 3 hasta corregir la entrada; las calificaciones sin OCR se descartan.
- Un subagente que reporta que falta el marco jurídico detiene el paso 3 hasta incluirlo en el directorio de trabajo; sin él, las referencias M.x del protocolo quedan sin dato y se descartan las calificaciones que dependen de ellas (puntos 2, 7, 18, 23, 24, 26, 28 y 63).
- Una lectura dudosa nunca sustenta «No cumple».

## Ahorro esperado

La calificación pasa de decenas de minutos secuenciales a ~2–3 minutos de reloj; consolidación y verificación añaden tiempo, pero protegen la consistencia.