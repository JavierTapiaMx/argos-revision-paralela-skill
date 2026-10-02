#!/bin/bash
# Preparación del entorno (B.1): idioma español de tesseract, utilerías PDF y tipografías. Idempotente.
# Uso (desde la carpeta de trabajo que contiene scripts/):  bash scripts/setup.sh
# Orden para el idioma español: (1) ya instalado; (2) apt; (3) descarga de spa.traineddata a ARGOS_TESSDATA
# (por defecto ~/.cache/argos-tessdata); ocr_all.py usa esa carpeta por sí solo, no hace falta exportar nada.
TESS_DIR="${ARGOS_TESSDATA:-$HOME/.cache/argos-tessdata}"
URL_SPA="https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/spa.traineddata"
tiene_spa(){ tesseract --list-langs 2>/dev/null | grep -qx spa || TESSDATA_PREFIX="$TESS_DIR" tesseract --list-langs 2>/dev/null | grep -qx spa; }
if command -v tesseract >/dev/null && ! tiene_spa; then
  (apt-get update -qq && apt-get install -y -qq tesseract-ocr-spa) >/dev/null 2>&1 || true
fi
if command -v tesseract >/dev/null && ! tiene_spa; then
  mkdir -p "$TESS_DIR"
  SYS="$(dirname "$(find /usr/share -name eng.traineddata 2>/dev/null | head -1)")"
  [ -n "$SYS" ] && cp -n "$SYS"/eng.traineddata "$SYS"/osd.traineddata "$TESS_DIR"/ 2>/dev/null
  curl -fsSL -m 120 -o "$TESS_DIR/spa.traineddata.tmp" "$URL_SPA" 2>/dev/null \
    && [ "$(stat -c %s "$TESS_DIR/spa.traineddata.tmp")" -gt 1000000 ] \
    && mv "$TESS_DIR/spa.traineddata.tmp" "$TESS_DIR/spa.traineddata" \
    || { rm -f "$TESS_DIR/spa.traineddata.tmp"; echo "AVISO: no se pudo obtener spa.traineddata; pide al usuario el archivo o instálalo en TESSDATA_PREFIX"; }
fi
tiene_spa && echo "tesseract spa: OK" || echo "tesseract spa: FALTA"
for c in pdftoppm pdfinfo pdftotext tesseract; do command -v $c >/dev/null && echo "$c: OK" || echo "$c: FALTA"; done
python3 - <<'PY'
import importlib
for m in ['reportlab','PIL']:
    try: importlib.import_module(m); print(m+': OK')
    except Exception: print(m+': FALTA (pip install reportlab pillow --break-system-packages)')
import os
print('Liberation Sans:', 'OK' if os.path.exists('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf') else 'FALTA (apt-get install -y fonts-liberation)')
PY
mkdir -p img tsv ocr capturas salida
