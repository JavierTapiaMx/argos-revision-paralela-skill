# argos-revision-paralela

Skill de Claude que ejecuta la revisión Argos de un expediente de contratación pública (70 puntos de control de Argos 360) repartiendo el trabajo entre subagentes: hechos neutros únicos, calificación en paralelo por grupos de puntos, consolidación centralizada y verificación independiente de los hallazgos graves.

Este skill **no contiene reglas de revisión**. Solo organiza el trabajo. Las reglas viven en los archivos del proyecto Argos, que deben estar cargados.

## Contenido del repositorio

```
argos-revision-paralela/
├── SKILL.md                         Instrucciones del skill (lo que Claude lee y ejecuta)
├── datos_revision.plantilla.json    Esquema del único insumo específico del expediente
└── scripts/                         Código genérico, sin datos de expedientes
    ├── setup.sh, ocr_all.py         Preparación y OCR en paralelo con enderezado automático
    ├── cap.py, capturas.py, grid.py, montage.py   Capturas declarativas y revisión visual
    ├── calc_lib.py, datos.py, protocolo_const.py, lib.py, rep.py   Cálculos y estructuras
    ├── mk_tablero.py, mk_informe.py, mk_ficha.py, mk_anexo.py, mk_json.py   Generadores
    ├── qc.py                        Control de calidad mecánico (no modifica resultados)
    └── build_all.sh                 Capturas, cinco generadores en paralelo y qc.py
README.md                            Este archivo (en la raíz del repositorio)
```

## Requisitos

Para que el skill funcione, la sesión de Claude debe tener acceso a estos insumos. Lo más práctico es ejecutarlo dentro del proyecto Argos 360, donde ya están cargados. Las constantes de los scripts corresponden a Argos 360 1.3.1 (`VERSION_BASE` en `protocolo_const.py`); con otra versión, el skill avisa antes de calificar.

| Insumo                     | Archivo                              | Para qué sirve                                                                                                                       |
| -------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| Instrucciones del proyecto | `01-instrucciones-claude-desktop.md` | Flujo de la conversación y qué hacer si faltan archivos o las versiones no coinciden                                                 |
| Metodología                | `02-metodologia.md`                  | Pasos del análisis, calificación interna, reglas de decisión G1 a G9, pruebas transversales B.0 a B.9, rigor jurídico y estilo       |
| Catálogo                   | `03-catalogo.md`                     | Las fichas de los 70 puntos de control en 12 rubros, con su riesgo por defecto y su etapa y documento ancla                          |
| Entregables                | `04-entregables.md`                  | Tablero, informe, ficha ejecutiva, anexo de evidencias, datos estructurados y control de calidad                                     |
| Esquema del marco          | `05-esquema-del-marco.md`            | Campos que trae todo marco jurídico y la regla que usa cada uno                                                                      |
| Marco jurídico             | `marco-<ámbito>.md`                  | Normativa del ámbito que se revisa (estatal o federal): ley, reglamento, régimen temporal, preceptos, parámetros y valores de umbral |

Los demás archivos del proyecto (`00-producto.md`, `06-solo-claude-desktop.md`, `CHANGELOG.md` y los `ejemplo-*.pdf`) también deben estar cargados. El paso 0 verifica que los archivos de Argos 360 tengan la misma versión en su primera línea.

Si falta el marco jurídico, el skill avisa antes de calificar y sigue solo si el usuario lo decide: todo precepto se cita «precepto por confirmar» y el marco se pide en «Documentación por requerir».

El entorno también necesita las herramientas técnicas que pide Argos 360 para leer digitalizaciones (OCR en español y rasterizado de PDF) y una carpeta de trabajo donde guardar los entregables.

## Cómo funciona

1. **Inventario, ficha, cronología y OCR.** La instancia principal lee todas las páginas y declara el ámbito, la entidad (o la Federación) y la fecha de verificación del marco jurídico.
2. **Hechos neutros.** Se escribe `hechos.md` con la ficha, el inventario, la cronología, los cálculos y las citas textuales, sin calificaciones. Se copian al directorio de trabajo la metodología, el catálogo, el esquema del marco, el marco jurídico, los hechos y el OCR.
3. **Calificación paralela.** Cinco subagentes califican por grupos: puntos 1-19, 20-34, 35-46, 47-60 y 61-70. Todo dato normativo se toma solo del marco jurídico.
4. **Pruebas transversales.** La instancia principal ejecuta B.0 a B.9 mientras corren los subagentes.
5. **Consolidación.** Una sola instancia reaplica las reglas que cruzan puntos: rigor jurídico y citas (régimen aplicable, preceptos y umbrales), niveles de riesgo, y las reglas G1 a G5 y G8 de la metodología (documentos citados y no exhibidos, riesgo de cada resultado, riesgo por defecto, fuera del alcance documental, alusión documental al hecho y lecturas dudosas), con el tipo y alcance del legajo (B.0).
6. **Verificación independiente.** Un subagente revisa cada resultado «No cumple» y cada riesgo Alto o Crítico, y lo confirma o refuta con el texto del OCR.
7. **Entregables.** Se generan el Tablero de control, el Informe de revisión, la Ficha ejecutiva, el Anexo de evidencias y el archivo de datos en JSON, y se guardan directamente en la carpeta de trabajo.

### Por qué se paraleliza así

La lectura de pruebas se reparte para ganar tiempo, pero el juicio se centraliza: la divergencia entre calificadores independientes nace de las reglas que se aplican entre puntos, por eso las reaplica una sola instancia al consolidar.

## Instalación

**Opción 1: pedírselo a Claude.** En una sesión del proyecto Argos, escribe: «Instala el skill argos-revision-paralela desde https://github.com/JavierTapiaMx/argos-revision-paralela-skill/tree/main». Claude lee el `SKILL.md` del repositorio y te muestra una tarjeta de propuesta; al guardarla se instala el skill. La tarjeta solo guarda el `SKILL.md`: los scripts no se instalan, el skill los descarga de este repositorio al ejecutarse (necesita que la sesión tenga acceso a `github.com`; si no lo tiene, avisa y sigue con el flujo manual).

**Opción 2: archivo .zip.** Comprime la carpeta `argos-revision-paralela` (con `scripts/` y la plantilla JSON) de modo que `SKILL.md` quede dentro de esa carpeta, súbela en la sección de Skills de la configuración de Claude y reemplaza el skill si ya existe. El nombre exacto del menú puede variar según la versión de la aplicación.

En ambos casos comprueba que el skill aparezca con el nombre `argos-revision-paralela` y su descripción. Subir cambios a GitHub no actualiza por sí solo el `SKILL.md` instalado (sí actualiza los scripts, que se descargan en cada ejecución); para actualizar el `SKILL.md` repite la opción 1 o la 2.

Mantén el repositorio **público** y sin datos de expedientes: si se vuelve privado, la descarga de los scripts falla para quienes no tengan acceso.

## Uso

Abre una sesión dentro del proyecto Argos, carga los documentos del expediente y pide la revisión indicando el skill, por ejemplo:

> Revisa este expediente con el skill argos-revision-paralela.

Los entregables se guardan directamente en la carpeta de trabajo, sin subcarpetas. Si ya existe un archivo con el mismo nombre, se sobrescribe sin abrirlo; para conservar una versión anterior, renómbrala o muévela antes de volver a ejecutar.

## Independencia de las ejecuciones

Cada ejecución es independiente. El skill no consulta ni compara resultados, JSON, análisis ni cálculos de ejecuciones anteriores del mismo expediente, ni los entrega a ningún subagente.

## Cambiar de entidad federativa o de ámbito

El skill no cambia. Se carga en el proyecto el marco del ámbito que se revisa (`marco-<ámbito>.md`, por ejemplo `marco-chihuahua.md` o `marco-federal.md`), con todos los campos de `05-esquema-del-marco.md` en el mismo orden. Para crear el marco de un ámbito nuevo, sigue «Para agregar un ámbito», al final de `05-esquema-del-marco.md`.

## Actualizar el skill

Cada cambio sigue el flujo de [`docs/development/git-workflow.md`](docs/development/git-workflow.md): issue, rama, pull request a `develop` y release a `main` con una versión CalVer (`v2026.10.0`, `v2026.10.1`...). El skill descarga los scripts de `main`, así que un release los publica de inmediato. El `SKILL.md` instalado no se actualiza solo: después de cada release, reinstálalo con la opción 1 o la 2 de [Instalación](#instalación).

## Confidencialidad

El material que se revisa con este skill pertenece a clientes. Este repositorio debe contener únicamente el skill y su documentación: no agregues expedientes, documentos digitalizados, resultados de revisiones ni datos de contratos reales. Si el repositorio se comparte fuera del despacho, revisa antes que el contenido de `SKILL.md` no incluya datos de un expediente real.

## Historial de versiones

Desde `v2026.10.0`, el historial está en [Releases](https://github.com/JavierTapiaMx/argos-revision-paralela-skill/releases). Esta tabla conserva las versiones anteriores.

| Versión         | Cambios                                                                                                                                                                                                               |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026.10.02.1029 | El skill incluye el marco jurídico aplicable (estatal o federal) como insumo obligatorio, se elimina la dependencia de una carpeta de herramientas y los entregables se guardan directamente en la carpeta de trabajo |
| 2026.10.02.1930 | Se agrega la carpeta `scripts/` (OCR en paralelo con enderezado, capturas declarativas, generadores de los cuatro PDF y del JSON, `qc.py`) y `datos_revision.plantilla.json`; el único insumo del expediente es `datos_revision.json`. Los scripts no contienen datos de expedientes ni modifican resultados. Las constantes A.8 y A.9 viven en `protocolo_const.py` y deben actualizarse al cambiar la versión del protocolo |
| 2026.10.02.2000 | El skill obtiene `scripts/` por sí mismo (carpeta del skill, sesión o `git clone` de este repositorio) y ya no depende de una ruta local; `setup.sh` descarga el idioma español de tesseract si `apt` no lo tiene y `ocr_all.py` lo detecta solo; `mk_informe.py` ya no supone que los archivos se llamen A, B y C; `mk_anexo.py` toma los nombres de archivo de los datos y no de un expediente concreto; se quita un dato de expediente de `rep.py` |
| 2026.10.03.1513 | Alineación con las instrucciones del proyecto: el paso 0 declara la versión del protocolo (la de su primera línea), la compara con `PROTOCOLO_BASE` de `protocolo_const.py` y avisa si difieren |
| 2026.10.04.1226 | Alineación con el protocolo 2026.10.04.1144 y la Matriz en formato Markdown: el punto 7 (Previsión de la contratación) pasa al rubro 2 (rubro 1: puntos 1 a 6; rubro 2: puntos 7 a 11), seis nombres de puntos se alinean con la Matriz y `PROTOCOLO_BASE` pasa a 2026.10.04.1144; la Matriz se carga como `.md` y no como PDF |
| 2026.10.04.1326 | Alineación con el protocolo 2026.10.04.1324: A.8 completa (se agregan los puntos 25, 26, 43, 61 y 65) y la regla del riesgo de los puntos fuera del alcance documental sin alusión (Medio los de la fila Alto); `PROTOCOLO_BASE` pasa a 2026.10.04.1324 |
