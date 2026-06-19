#!/bin/bash
# ============================================================
#  miamijetskiboat.command (v5 — reliable deploy + verify)
# ============================================================
#  Deploy a Vercel via tarball (--archive=tgz) + auto-alias
#  garantizado al dominio custom miamijetskiboatrentals.com.
#
#  v5 changes vs v4:
#    - SIEMPRE hace CLI deploy + alias explícito
#      (no confía en GitHub auto-deploy de Vercel — eso fallaba)
#    - Git push después del deploy exitoso (backup, no como deploy)
#    - Regex de URL más permisivo (cubre todos los formatos Vercel)
#    - Detección de errores más precisa (solo Error: al final + códigos exit)
#    - Verifica el deploy con curl al dominio (HTTP 200)
#    - Mejor logging con timing por etapa
# ============================================================

REPO=/Users/raptor/miami-jetski-main
DOMAIN=miamijetskiboatrentals.com

cd "$REPO" 2>/dev/null || {
  echo "❌ No encontré $REPO"
  read -rp "Presiona Enter para cerrar..."
  exit 1
}

clear
echo "╔══════════════════════════════════════════════╗"
echo "║   Deploy a Vercel v5 (CLI + alias + verify)  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ─── SANITY CHECKS ───
MISSING=""
for f in vercel.json sitemap.xml operators.json operators-slim.json slug-map.js index.html; do
  [ ! -f "$f" ] && MISSING="$MISSING $f"
done
if [ -n "$MISSING" ]; then
  echo "❌ Archivos críticos faltan:$MISSING"
  read -rp "Presiona Enter para cerrar..."
  exit 1
fi

if [ -f .env.local ] || [ -f .env ]; then
  echo "🚨 PELIGRO: .env detectado. ABORTANDO."
  read -rp "Presiona Enter para cerrar..."
  exit 1
fi

# ─── AUTO-COMMIT (si hay cambios pendientes) ───
if ! git diff --quiet || ! git diff --cached --quiet; then
  CHANGED=$(git status --short | wc -l | tr -d ' ')
  echo "📝 $CHANGED archivo(s) con cambios — committing..."
  git add -A
  git commit -m "Sync from Cowork $(date '+%Y-%m-%d %H:%M')" >/dev/null
  echo "✅ Commit creado"
  echo ""
fi

# ─── VERCEL CLI INSTALL CHECK ───
if ! command -v vercel &>/dev/null; then
  echo "📦 Instalando Vercel CLI..."
  npm install -g vercel >/dev/null 2>&1 || {
    echo "❌ npm install -g vercel falló. Instala manualmente."
    read -rp "Presiona Enter para cerrar..."
    exit 1
  }
fi

# ─── DEPLOY DIRECTO: vercel --prod --archive=tgz ───
T0=$(date +%s)
echo "🚀 [1/3] Subiendo tarball a Vercel..."
echo "   (1 upload en vez de 10,000+ archivos — evita rate limit)"
echo ""

vercel --prod --archive=tgz --yes 2>&1 | tee /tmp/vercel-deploy.log
DEPLOY_EXIT=${PIPESTATUS[0]}

T1=$(date +%s)
echo ""
echo "   ⏱  Deploy: $((T1-T0))s"
echo ""

# Detectar errores reales (códigos exit + Error: al final del log, no en medio)
if [ "$DEPLOY_EXIT" -ne 0 ]; then
  echo "❌ Vercel CLI exit $DEPLOY_EXIT — deploy falló."
  echo ""
  echo "   Últimas líneas:"
  tail -10 /tmp/vercel-deploy.log
  read -rp "Presiona Enter para cerrar..."
  exit $DEPLOY_EXIT
fi

# Detección refinada: "Error:" como prefijo de línea (no en medio)
if grep -qE '^Error:|^❌|rate.?limit' /tmp/vercel-deploy.log; then
  echo "❌ Deploy reportó errores. Revisa /tmp/vercel-deploy.log"
  read -rp "Presiona Enter para cerrar..."
  exit 1
fi

# ─── EXTRAER URL DEL DEPLOYMENT ───
# Acepta cualquier *.vercel.app (https obligatorio)
DEPLOY_URL=$(grep -oE 'https://[a-z0-9][a-z0-9-]*\.vercel\.app' /tmp/vercel-deploy.log | tail -1)

# Fallback: buscar "Inspect:" o "Preview:" o "Production:"
if [ -z "$DEPLOY_URL" ]; then
  DEPLOY_URL=$(grep -oE 'https://[^[:space:]]+\.vercel\.app' /tmp/vercel-deploy.log | tail -1)
fi

if [ -z "$DEPLOY_URL" ]; then
  echo "⚠️  No pude extraer la URL del deployment."
  echo "   Buscando en log:"
  grep -i 'vercel\.app\|production\|preview' /tmp/vercel-deploy.log | tail -5
  echo ""
  echo "   El deploy se subió pero el alias debe hacerse manual."
  read -rp "Presiona Enter para cerrar..."
  exit 0
fi

echo "📌 Deployment URL: $DEPLOY_URL"
echo ""

# ─── ALIAS AL DOMINIO CUSTOM ───
T2=$(date +%s)
echo "🔗 [2/3] Aliaseando → $DOMAIN..."
ALIAS_OUTPUT=$(vercel alias set "$DEPLOY_URL" "$DOMAIN" 2>&1)
ALIAS_EXIT=$?

# Mostrar últimas 3 líneas
echo "$ALIAS_OUTPUT" | tail -3
T3=$(date +%s)
echo "   ⏱  Alias: $((T3-T2))s"
echo ""

# Verificar éxito (soporta varios phrasings de Vercel CLI)
if [ $ALIAS_EXIT -ne 0 ]; then
  echo "⚠️  vercel alias set exit $ALIAS_EXIT"
  echo "   Verifica con: vercel alias ls | grep $DOMAIN"
  echo "   Manual: vercel alias set $DEPLOY_URL $DOMAIN"
  read -rp "Presiona Enter para cerrar..."
  exit 1
fi

if ! echo "$ALIAS_OUTPUT" | grep -qE 'Success|assigned|Created|now points'; then
  echo "⚠️  El output no confirma éxito explícito. Verificando con curl..."
fi

# ─── VERIFICAR CON CURL ───
T4=$(date +%s)
echo "🔍 [3/3] Verificando $DOMAIN con HTTP request..."
sleep 5  # Dar tiempo a propagar el alias

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 15 "https://$DOMAIN/")
T5=$(date +%s)
echo "   HTTP $HTTP_CODE  (⏱ $((T5-T4))s)"

if [ "$HTTP_CODE" = "200" ]; then
  VERIFY_OK=1
else
  VERIFY_OK=0
  echo "   ⚠️  Esperaba 200, recibí $HTTP_CODE — el sitio puede estar propagando"
fi

# ─── GIT PUSH (backup, no como deploy) ───
if git remote get-url origin >/dev/null 2>&1; then
  echo ""
  echo "🔼 Backup: git push origin main..."
  git push origin main 2>&1 | tail -3 || echo "   (push falló pero deploy ya está en producción)"
fi

# ─── RESUMEN ───
TOTAL=$(($(date +%s) - T0))
echo ""
echo "════════════════════════════════════════════════"
if [ "$VERIFY_OK" = "1" ]; then
  echo "🎉 Deploy completado exitosamente ($TOTAL s)"
else
  echo "✅ Deploy subido pero verifica manualmente ($TOTAL s)"
fi
echo ""
echo "   Sitio:     https://$DOMAIN"
echo "   Deploy:    $DEPLOY_URL"
echo "   HTTP:      $HTTP_CODE"
echo ""
echo "   Cambios visibles en ~10-30 segundos (CDN cache)"
echo "════════════════════════════════════════════════"
echo ""
read -rp "Presiona Enter para cerrar..."
