# argos-revision-paralela

Skill de Claude que ejecuta la revisión Argos de un expediente de contratación pública (Matriz Operativa de 70 puntos de control) repartiendo el trabajo entre subagentes: hechos neutros únicos, calificación en paralelo por grupos de puntos, consolidación centralizada y verificación independiente de los hallazgos graves.

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

Para que el skill funcione, la sesión de Claude debe tener acceso a estos insumos. Lo más práctico es ejecutarlo dentro del proyecto Argos, donde ya están cargados:

| Insumo                     | Archivo                                                     | Para qué sirve                                                                                                         |
| -------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Instrucciones del proyecto | (configuración del proyecto)                                | Definen el flujo de trabajo del apartado 3 que el skill ejecuta con subagentes                                         |
| Protocolo de revisión      | `protocolo-de-revision-argos.md`                            | Reglas punto por punto, niveles de riesgo, tablero y entregables                                                       |
| Marco jurídico aplicable   | `marco-juridico-aplicable.md`                               | Normativa del ámbito que se revisa (estatal o federal): ley, reglamento, preceptos, parámetros y valores de referencia |
| Matriz Operativa           | `matriz-operativa-revision-contractual-y-fiscalizacion.pdf` | Los 70 puntos de control, las categorías de resultado y la regla de trazabilidad                                       |

Si falta el marco jurídico, el skill se detiene: sin él, las referencias M.x del protocolo quedan sin dato y las calificaciones que dependen de ellas se descartan.

El entorno también necesita las herramientas técnicas que pide el protocolo para leer digitalizaciones (OCR en español y rasterizado de PDF) y una carpeta de trabajo donde guardar los entregables.

## Cómo funciona

1. **Inventario, ficha, cronología y OCR.** La instancia principal lee todas las páginas y declara el ámbito, la entidad (o la Federación) y la fecha de verificación del marco jurídico.
2. **Hechos neutros.** Se escribe `hechos.md` con la ficha, el inventario, la cronología, los cálculos y las citas textuales, sin calificaciones. Se copian al directorio de trabajo el protocolo, el marco jurídico, los hechos y el OCR.
3. **Calificación paralela.** Cinco subagentes califican por grupos: puntos 1–19, 20–34, 35–46, 47–60 y 61–70. Todo dato normativo se toma solo del marco jurídico.
4. **Pruebas transversales.** La instancia principal ejecuta B.0 a B.9 mientras corren los subagentes.
5. **Consolidación.** Una sola instancia reaplica las reglas que cruzan puntos (marco jurídico, niveles de riesgo, régimen por defecto, documentos citados y no exhibidos, riesgo por defecto, etapa y documento ancla, y alcance del expediente).
6. **Verificación independiente.** Un subagente revisa cada resultado «No cumple» y cada riesgo Alto o Crítico, y lo confirma o refuta con el texto del OCR.
7. **Entregables.** Se generan el Tablero de control, el Informe de revisión, la Ficha ejecutiva, el Anexo de evidencias y el archivo de datos en JSON, y se guardan directamente en la carpeta de trabajo.

### Por qué se paraleliza así

La lectura de pruebas se reparte para ganar tiempo, pero el juicio se centraliza: la divergencia entre calificadores independientes nace de las reglas que se aplican entre puntos, por eso las reaplica una sola instancia al consolidar.

## Instalación

**Opción 1: pedírselo a Claude.** En una sesión del proyecto Argos, escribe: «Instala el skill argos-revision-paralela desde https://github.com/JavierTapiaMx/argos-revision-paralela-skill». Claude lee el `SKILL.md` del repositorio y te muestra una tarjeta de propuesta; al guardarla se instala el skill. La tarjeta solo guarda el `SKILL.md`: los scripts no se instalan, el skill los descarga de este repositorio al ejecutarse (necesita que la sesión tenga acceso a `github.com`; si no lo tiene, avisa y sigue con el flujo manual).

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

El skill no cambia. Se sustituye solo el contenido de `marco-juridico-aplicable.md`, conservando su nombre y su estructura (M.0 a M.5). Esa guía está al final del propio archivo del marco jurídico.

## Actualizar el skill

1. Edita `SKILL.md` en este repositorio.
2. Revisa los cambios con `git diff`.
3. Registra el cambio con un mensaje que lleve la versión en el formato `versión yyyy.MM.dd.HHmm`, y súbelo con `git push`.
4. Vuelve a comprimir la carpeta y súbela a Claude para reemplazar el skill instalado.

## Confidencialidad

El material que se revisa con este skill pertenece a clientes. Este repositorio debe contener únicamente el skill y su documentación: no agregues expedientes, documentos digitalizados, resultados de revisiones ni datos de contratos reales. Si el repositorio se comparte fuera del despacho, revisa antes que el contenido de `SKILL.md` no incluya datos de un expediente real.

## Historial de versiones

| Versión         | Cambios                                                                                                                                                                                                               |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026.10.02.1029 | El skill incluye el marco jurídico aplicable (estatal o federal) como insumo obligatorio, se elimina la dependencia de una carpeta de herramientas y los entregables se guardan directamente en la carpeta de trabajo |
| 2026.10.02.1930 | Se agrega la carpeta `scripts/` (OCR en paralelo con enderezado, capturas declarativas, generadores de los cuatro PDF y del JSON, `qc.py`) y `datos_revision.plantilla.json`; el único insumo del expediente es `datos_revision.json`. Los scripts no contienen datos de expedientes ni modifican resultados. Las constantes A.8 y A.9 viven en `protocolo_const.py` y deben actualizarse al cambiar la versión del protocolo |
| 2026.10.02.2000 | El skill obtiene `scripts/` por sí mismo (carpeta del skill, sesión o `git clone` de este repositorio) y ya no depende de una ruta local; `setup.sh` descarga el idioma español de tesseract si `apt` no lo tiene y `ocr_all.py` lo detecta solo; `mk_informe.py` ya no supone que los archivos se llamen A, B y C; `mk_anexo.py` toma los nombres de archivo de los datos y no de un expediente concreto; se quita un dato de expediente de `rep.py` |
