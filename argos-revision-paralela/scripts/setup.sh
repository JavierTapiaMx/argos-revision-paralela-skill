#!/bin/bash
# Preparación del entorno (B.1): idioma español de tesseract, utilerías PDF y tipografías. Idempotente.
set -e
if ! tesseract --list-langs 2>/dev/null | grep -qx spa; then
  (apt-get update -qq && apt-get install -y -qq tesseract-ocr-spa) >/dev/null 2>&1 || echo "AVISO: no se pudo instalar tesseract-ocr-spa; descargar spa.traineddata en TESSDATA_PREFIX"
fi
tesseract --list-langs 2>/dev/null | grep -qx spa && echo "tesseract spa: OK" || echo "tesseract spa: FALTA"
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
