---
name: "argos-revision-paralela"
description: "Orquesta con subagentes la revisión Argos de un expediente de contratación (70 puntos): OCR en paralelo, hechos únicos, calificación paralela por rubros, consolidación, verificación, capturas y entregables generados con scripts."
---

# Revisión Argos en paralelo

Ejecuta los pasos del análisis de Argos 360 (`02-metodologia.md`, Alcance del análisis) con subagentes y con los scripts de `scripts/`. Los archivos de Argos 360 (`02-metodologia.md`, `03-catalogo.md`, `04-entregables.md` y `05-esquema-del-marco.md`) y el marco jurídico del ámbito (`marco-<ámbito>.md`) son la única fuente de reglas; este skill solo reparte el trabajo y automatiza lo mecánico. Los scripts no califican ni deciden nada: leen, localizan, dibujan, calculan y verifican.

## Principio

Paralelizar la lectura de pruebas; centralizar el juicio; automatizar lo mecánico. Un piloto con un expediente real mostró que cinco calificadores en paralelo coinciden en 70/70 resultados y en ~90 % de riesgos, y que la divergencia nace de reglas transversales (riesgo por defecto, fuera del alcance documental y alusión documental al hecho: reglas G3, G4 y G5) aplicadas por separado. Esas reglas las aplica una sola instancia.

## Independencia

Toda ejecución es independiente. No busques, cargues, consultes ni compares resultados, JSON, análisis ni cálculos de ejecuciones anteriores del mismo expediente, aunque estén en la carpeta de trabajo o en el proyecto, y no se los entregues a ningún subagente. Los scripts de `scripts/` son código y no contienen datos de ningún expediente; su uso no viola la independencia. Los entregables se guardan directamente en la carpeta de trabajo, sin subcarpetas; si ya existe un archivo con el mismo nombre, se sobrescribe sin abrirlo ni leerlo.

## Scripts (carpeta `scripts/`)

Ubicación y obtención de `scripts/` (el skill instalado solo trae este `SKILL.md`; los scripts viven en el repositorio público del skill). Antes de cualquier paso, crea la carpeta de trabajo `argos/` y trabaja desde ella (los scripts usan rutas relativas y el entorno de ejecución puede olvidar el estado del shell entre llamadas: abre cada comando con `cd` a esa carpeta). Usa la primera de estas opciones que funcione:

1. `scripts/` junto a este `SKILL.md` (directorio base del skill), si existe: cópiala a `argos/scripts`.
2. `argos/scripts` ya existente en la sesión.
3. Descarga desde el repositorio del skill:

```bash
mkdir -p argos && cd argos && [ -d scripts ] || { git clone --branch main --depth 1 https://github.com/JavierTapiaMx/argos-revision-paralela-skill.git _repo \
  && cp -r _repo/argos-revision-paralela/scripts scripts && cp _repo/argos-revision-paralela/datos_revision.plantilla.json . ; }
```

4. Si no hay acceso de red a `github.com`, pide al usuario que conecte la carpeta de su copia del repositorio (o que adjunte la carpeta `scripts`) y cópiala con `device_stage_files`.
5. Si nada funciona, avisa al usuario en una frase y procede sin scripts: el flujo manual sigue siendo válido.

Usa únicamente scripts de esas fuentes y no los modifiques. Después corre `bash scripts/setup.sh` (instala o descarga el idioma español de tesseract; `ocr_all.py` lo detecta solo). La plantilla `datos_revision.plantilla.json` es un esqueleto del esquema, no un expediente de prueba: un `datos_revision.json` real debe tener los 70 puntos, las pruebas B.0 a B.9 y la sección `capturas` completa.

| Script | Para qué sirve |
| --- | --- |
| `setup.sh` | Verifica e instala `tesseract-ocr-spa`, utilerías PDF, reportlab, PIL y tipografías; crea carpetas. Idempotente. |
| `ocr_all.py` | Un solo comando para el inventario: hash, páginas y metadatos de cada PDF; rasterizado a 300 ppp; detección y corrección de páginas giradas; OCR en paralelo (`ocr/K-n.txt` y `tsv/K-n.tsv`); lista de páginas de OCR pobre (candidatas a lectura dudosa) y de duplicados exactos. Escribe `inventario.json`. |
| `calc_lib.py` | Funciones para registrar cálculos (IVA, porcentajes, límites en UMA, días naturales y hábiles, día de la semana) en el formato de `calculos`. |
| `grid.py`, `montage.py` | Cuadrícula de coordenadas para ubicar sellos y manuscritos; hoja de contacto para revisar muchas capturas en una sola vista. |
| `capturas.py` | Motor de capturas (`04-entregables.md`, Anexo de evidencias): genera un PNG por captura desde la lista declarativa del JSON; localiza texto con el TSV de tesseract y dibuja recuadro rojo con relleno amarillo translúcido; apila contrastes a la misma escala. |
| `mk_tablero.py`, `mk_informe.py`, `mk_ficha.py`, `mk_anexo.py`, `mk_json.py` | Generan Tablero, Informe, Ficha ejecutiva, Anexo de evidencias y `Datos_[número].json` con los nombres de archivo de `04-entregables.md`. |
| `qc.py` | Control de calidad automático (`04-entregables.md`, Control de calidad). Revisa los 70 puntos, riesgos, marcas, hallazgos y capturas, encabezados, conteos entre entregables, tamaño de la ficha, secciones prohibidas, esquema del JSON y referencias de página; avisa si algún riesgo de «No acreditado» difiere del riesgo por defecto de su ficha (regla G3) sin razón citada. No modifica resultados. |
| `build_all.sh` | Corre capturas, los cinco generadores y `qc.py`. |
| `protocolo_const.py` | Constantes de Argos 360 (nombres de presentación de los 70 puntos, rubros y pruebas; riesgo por defecto de la regla G3; etapas de la regla G4). El paso 0 compara su `VERSION_BASE` con la versión de Argos 360 cargada; si Argos 360 cambió, hay que actualizar el archivo en el repositorio del skill. |
| `datos.py`, `lib.py`, `rep.py`, `cap.py` | Módulos de apoyo (carga del JSON, dibujo del tablero, estilos y tablas, localización de texto). |

El único insumo específico del expediente es `datos_revision.json`; su esquema está en `datos_revision.plantilla.json`. Todo lo que se redacta (análisis, hallazgos, dictamen, acciones, criterios, textos de alcance y marco) lo escribe la instancia principal; los scripts solo lo maquetan.

## Pasos

0. **Preparación (en paralelo con la lectura).** Corre `bash scripts/setup.sh`. Verifica que estén cargados los archivos de Argos 360 (`00-producto.md` a `06-solo-claude-desktop.md`) y el marco del ámbito (`marco-<ámbito>.md`). Declara la versión de Argos 360, que está en la primera línea de cada archivo con la forma «(versión 1.3.1 · 2026.10.15.1456)», y la versión, el ámbito (estatal o federal), la entidad (o la Federación) y la fecha de verificación del marco (primera línea y campos Ámbito, Entidad y Fecha de verificación). Si los archivos de Argos 360 traen versiones distintas, falta alguno o falta el marco, aplica `01-instrucciones-claude-desktop.md` (Contradicciones y archivos faltantes). Compara la versión de Argos 360 con `VERSION_BASE` de `scripts/protocolo_const.py`: si difieren, avisa al usuario antes de calificar, porque las constantes (nombres de los 70 puntos, riesgo por defecto de G3, etapas de G4) podrían estar desactualizadas. En el campo `protocolo` de `datos_revision.json` registra la versión de Argos 360 que leíste.
1. **Inventario, ficha, cronología y OCR.** Lanza `python3 scripts/ocr_all.py A=<pdf> B=<pdf> ...` en segundo plano (usa un hilo por núcleo) y, mientras corre, lee `02-metodologia.md`, `03-catalogo.md`, `04-entregables.md` y el marco. Al terminar, revisa visualmente solo las páginas que el script marca como OCR pobre y las giradas; lo manuscrito, los sellos y las cifras dudosas se leen sobre recortes a 600 ppp (`grid.py` ayuda a ubicarlos) y se registran como LD-n. Criterio de cierre: cada página con OCR en `ocr/K-n.txt` y cada página de OCR vacío o pobre reprocesada, leída visualmente o listada como lectura dudosa.
2. **Hechos neutros.** Escribe `hechos.md` (ficha, inventario, cronología, cálculos hechos con `calc_lib.py`, citas textuales, ámbito y entidad del marco) sin calificaciones. Copia `02-metodologia.md`, `03-catalogo.md`, `05-esquema-del-marco.md`, el marco, los hechos y el OCR a un directorio de trabajo y verifica con `ls` que el OCR no esté vacío y que el marco jurídico esté presente antes de lanzar agentes.
3. **Calificación paralela.** Lanza en un solo mensaje un subagente por grupo: puntos 1-19, 20-34, 35-46, 47-60, 61-70. Cada uno recibe solo el directorio de trabajo (que incluye el marco jurídico), sus puntos y la orden de escribir `out_k.json` con `n, resultado, riesgo, fuera_del_alcance, con_alusion, evidencia, analisis, accion`. Cada subagente califica con la ficha de cada punto (`03-catalogo.md`) y las reglas G1 a G5 y G8 (`02-metodologia.md`), y toma todo dato normativo (parámetros, umbrales, preceptos, nombres de órganos y registros) únicamente de los campos del marco; si un dato no está, aplica `02-metodologia.md`, Rigor jurídico y citas («precepto por confirmar» y criterio a validar), y no lo suple. Criterio de cierre: los cinco JSON existen y cubren los 70 puntos sin huecos.
4. **Pruebas transversales B.0 a B.9** en la instancia principal mientras corren los agentes. En ese mismo tiempo, redacta la lista de capturas (`capturas` del JSON) para los hallazgos que ya se vean.
5. **Consolidación (instancia principal).** Reaplica a todos los puntos `02-metodologia.md`, Rigor jurídico y citas (régimen aplicable, preceptos y umbrales), los niveles de riesgo de la Escala de señales, las reglas G1 a G5 y G8, y la prueba B.0; recalcula el riesgo con G2 y G3 y exige razón citada para apartarse del riesgo por defecto de la ficha. Resuelve con la cronología completa los puntos que se basan en ella (9, 18, 27, 39, 47 y 57) y los puntos cruzados 59 y 61. Arma `datos_revision.json` y corre `python3 scripts/qc.py` para detectar de inmediato incongruencias mecánicas (riesgo sin resultado, marca de alcance indebida, punto Alto fuera de hallazgo, referencias a páginas inexistentes).
6. **Verificación independiente.** Un subagente por cada resultado «No cumple» o riesgo Alto/Crítico, en paralelo con la generación de capturas. Cada uno recibe la cita y las páginas, y responde confirmado o refutado con texto OCR.
7. **Capturas y entregables.** `ARGOS_DATOS=datos_revision.json ARGOS_SALIDA=. bash scripts/build_all.sh`. Si una frase de una captura no se encuentra, el script lo indica con página y frase: corrígela o usa un recuadro manual (`["b",x0,y0,x1,y1]`). Revisa visualmente todas las capturas con `python3 scripts/montage.py A.1 A.2 ...` y vuelve a correr `build_all.sh` tras cada corrección. Criterio de cierre: `qc.py` sin errores y la lista «Calificación interna» del control de calidad de `04-entregables.md` sin pendientes.

## Controles de certeza

- Un subagente que reporta OCR vacío o fuente faltante detiene el paso 3 hasta corregir la entrada; las calificaciones sin OCR se descartan.
- Un subagente que reporta que falta el marco detiene el paso 3 hasta incluirlo en el directorio de trabajo. Si el marco no está cargado, avisa al usuario y sigue solo si lo decide, como indica `01-instrucciones-claude-desktop.md` (Contradicciones y archivos faltantes): todo precepto va «precepto por confirmar» y el marco se lista en «Documentación por requerir».
- Una lectura dudosa nunca sustenta «No cumple» (regla G8).
- Los avisos de `qc.py` no cambian una calificación por sí solos: la instancia principal decide si hay razón citada.
- La revisión visual de cada captura no se automatiza: es obligatoria (`04-entregables.md`, Control de calidad).

## Ahorro esperado

La calificación pasa de decenas de minutos secuenciales a ~2 a 3 minutos de reloj. El OCR por lotes, el motor de capturas y los generadores evitan reescribir y depurar código en cada revisión; el control de calidad automático sustituye la revisión manual de la lista D en lo mecánico. El tiempo restante se concentra en lo que requiere criterio: lecturas dudosas, consolidación, redacción de hallazgos y revisión visual de capturas.