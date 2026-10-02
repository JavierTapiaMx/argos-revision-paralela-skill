#!/bin/bash
# Genera capturas, los cuatro PDF, el JSON y corre el control de calidad.
# Requiere: datos_revision.json (único insumo del expediente), img/*_r.png y tsv/*.tsv (de ocr_all.py).
# Uso:  ARGOS_DATOS=datos_revision.json ARGOS_SALIDA=. bash build_all.sh
set -e
D="$(cd "$(dirname "$0")" && pwd)"
export ARGOS_DATOS="${ARGOS_DATOS:-datos_revision.json}" ARGOS_SALIDA="${ARGOS_SALIDA:-.}"
mkdir -p "$ARGOS_SALIDA"
python3 "$D/capturas.py"
python3 "$D/mk_tablero.py" & python3 "$D/mk_informe.py" & python3 "$D/mk_ficha.py" & python3 "$D/mk_anexo.py" & python3 "$D/mk_json.py" &
wait
python3 "$D/qc.py"
