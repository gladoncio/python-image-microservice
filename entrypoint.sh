#!/bin/sh
set -e

mkdir -p /app/fonts

echo "Copiando fuentes .ttf desde /usr/share/fonts..."

# Buscar recursivamente archivos .ttf y copiarlos a /app/fonts sin carpetas
find /usr/share/fonts -type f -name '*.ttf' -exec cp {} /app/fonts/ \; || echo "No se pudieron copiar algunas fuentes .ttf"

echo "Fuentes copiadas: $(ls /app/fonts | wc -l)"

exec "$@"
