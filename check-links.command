#!/bin/bash
# ─────────────────────────────────────────────────
#  check-links.command
#  Doble click → abre Terminal y audita el sitio
# ─────────────────────────────────────────────────

# Ir a la carpeta donde está este archivo
cd "$(dirname "$0")"

clear
echo "╔══════════════════════════════════════════════╗"
echo "║   miamijetskiboatrentals.com — Link Checker  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "  Iniciando auditoría con 30 workers..."
echo "  Esto tarda ~3-4 minutos."
echo ""

python3 check-links.py --workers 30 --out link-check-results.json

echo ""
echo "──────────────────────────────────────────────"
echo "  Resultados guardados en: link-check-results.json"
echo "──────────────────────────────────────────────"
echo ""
echo "  Presiona cualquier tecla para cerrar..."
read -n 1
