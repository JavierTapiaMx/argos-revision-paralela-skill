# argos-revision-paralela

Skill de Claude que ejecuta la revisión Argos de un expediente de contratación pública (Matriz Operativa de 70 puntos de control) repartiendo el trabajo entre subagentes: hechos neutros únicos, calificación en paralelo por grupos de puntos, consolidación centralizada y verificación independiente de los hallazgos graves.

Este skill **no contiene reglas de revisión**. Solo organiza el trabajo. Las reglas viven en los archivos del proyecto Argos, que deben estar cargados.

## Contenido del repositorio

```
argos-revision-paralela/
├── SKILL.md    Instrucciones del skill (lo que Claude lee y ejecuta)
└── README.md   Este archivo
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

1. Comprime la carpeta `argos-revision-paralela` en un archivo `.zip`, de modo que `SKILL.md` quede dentro de esa carpeta.
2. En la configuración de Claude, en la sección de Skills, sube el archivo `.zip`. Si ya existe un skill con el mismo nombre, reemplázalo. El nombre exacto del menú puede variar según la versión de la aplicación.
3. Comprueba que el skill aparezca con el nombre `argos-revision-paralela` y su descripción.

Subir el repositorio a GitHub no instala ni actualiza el skill en Claude: cada instalación o actualización se hace con el paso anterior.

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
