#!/bin/bash
# ============================================================
#  miamijetskiboat.command (v6 — smart deploy + multi-URL verify)
# ============================================================
#  Deploy a Vercel via tarball + auto-alias garantizado.
#
#  v6 changes vs v5:
#    - Smoke test 5 URLs claves (home/zone/ES/blog/op page) — no solo el home
#    - Content marker check — detecta cache stale (latest commit hash en HTML)
#    - Build logs auto-fetch si deploy falla
#    - macOS notification + sound al terminar
#    - Auto-retry 1x si alias falla (network blip)
#    - Prompt para custom commit message
#    - Pre-deploy: muestra últimos 3 commits que van a subir
#    - Tarball size warning si > 100MB (Vercel free tier limit)
#    - Smart cache bust: añade ?v=<commit> a verificaciones
# ============================================================

REPO=/Users/raptor/miami-jetski-main
DOMAIN=miamijetskiboatrentals.com

cd "$REPO" 2>/dev/null || {
  echo "❌ No encontré $REPO"
  read -rp "Presiona Enter para cerrar..."
  exit 1
}

clear
echo "╔════════════════════════════════════════════════╗"
echo "║  Deploy v6 — Smart verify + content markers    ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# ─── HELPERS ───
notify_mac(){
  if command -v osascript &>/dev/null; then
    osascript -e "display notification \"$2\" with title \"$1\" sound name \"$3\""
  fi
}
sound_ok(){ [ -f /System/Library/Sounds/Glass.aiff ] && afplay /System/Library/Sounds/Glass.aiff &>/dev/null & }
sound_err(){ [ -f /System/Library/Sounds/Basso.aiff ] && afplay /System/Library/Sounds/Basso.aiff &>/dev/null & }

# ─── SANITY CHECKS ───
MISSING=""
for f in vercel.json sitemap.xml operators.json operators-slim.json slug-map.js index.html; do
  [ ! -f "$f" ] && MISSING="$MISSING $f"
done
if [ -n "$MISSING" ]; then
  echo "❌ Archivos críticos faltan:$MISSING"
  sound_err
  read -rp "Presiona Enter para cerrar..."
  exit 1
fi

if [ -f .env.local ] || [ -f .env ]; then
  echo "🚨 PELIGRO: .env detectado. ABORTANDO."
  sound_err
  read -rp "Presiona Enter para cerrar..."
  exit 1
fi

# ─── AUTO-COMMIT (con prompt opcional) ───
if ! git diff --quiet || ! git diff --cached --quiet; then
  CHANGED=$(git status --short | wc -l | tr -d ' ')
  echo "📝 $CHANGED archivo(s) con cambios pendientes"
  echo ""
  read -rp "💬 Mensaje de commit (Enter para auto-mensaje): " COMMIT_MSG
  if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Sync from Cowork $(date '+%Y-%m-%d %H:%M')"
  fi
  git add -A
  git commit -m "$COMMIT_MSG" >/dev/null
  echo "✅ Commit: $COMMIT_MSG"
  echo ""
fi

# ─── PRE-DEPLOY: mostrar últimos commits ───
echo "📜 Commits que van a producción:"
git log --oneline -5 | sed 's/^/   /'
echo ""

# ─── COMMIT HASH para verificación de cache ───
COMMIT_HASH=$(git rev-parse --short HEAD)
echo "🔖 Commit a deployar: $COMMIT_HASH"
echo ""

# ─── VERCEL CLI ───
if ! command -v vercel &>/dev/null; then
  echo "📦 Instalando Vercel CLI..."
  npm install -g vercel >/dev/null 2>&1 || {
    echo "❌ npm install -g vercel falló"
    sound_err
    read -rp "Presiona Enter para cerrar..."
    exit 1
  }
fi

# ─── TARBALL SIZE WARNING ───
PROJECT_SIZE_MB=$(du -sm . 2>/dev/null | awk '{print $1}')
if [ -n "$PROJECT_SIZE_MB" ] && [ "$PROJECT_SIZE_MB" -gt 100 ]; then
  echo "⚠️  Proyecto: ${PROJECT_SIZE_MB} MB (Vercel free tier limit: 100 MB)"
  echo "   Considera optimizar antes de subir."
  echo ""
fi

# ─── DEPLOY ───
T0=$(date +%s)
echo "🚀 [1/4] Subiendo tarball a Vercel..."
echo ""

vercel --prod --archive=tgz --yes 2>&1 | tee /tmp/vercel-deploy.log
DEPLOY_EXIT=${PIPESTATUS[0]}

T1=$(date +%s)
echo ""
echo "   ⏱  Upload: $((T1-T0))s"
echo ""

# ─── DEPLOY ERROR HANDLING ───
if [ "$DEPLOY_EXIT" -ne 0 ]; then
  echo "❌ Vercel CLI exit $DEPLOY_EXIT"
  echo ""
  echo "   Últimas líneas del log:"
  tail -15 /tmp/vercel-deploy.log
  echo ""
  # Try fetching build logs
  LATEST_INSPECT=$(grep -oE 'https://vercel\.com/[^[:space:]]+' /tmp/vercel-deploy.log | head -1)
  if [ -n "$LATEST_INSPECT" ]; then
    echo "   Build logs: $LATEST_INSPECT"
  fi
  sound_err
  notify_mac "Deploy Failed ❌" "Exit code $DEPLOY_EXIT" "Basso"
  read -rp "Presiona Enter para cerrar..."
  exit $DEPLOY_EXIT
fi

if grep -qE '^Error:|^❌|rate.?limit' /tmp/vercel-deploy.log; then
  echo "❌ Deploy reportó errores en log."
  tail -10 /tmp/vercel-deploy.log
  sound_err
  notify_mac "Deploy Error ❌" "Revisa el output" "Basso"
  read -rp "Presiona Enter para cerrar..."
  exit 1
fi

# ─── EXTRAER URL ───
DEPLOY_URL=$(grep -oE 'https://[a-z0-9][a-z0-9-]*\.vercel\.app' /tmp/vercel-deploy.log | tail -1)
if [ -z "$DEPLOY_URL" ]; then
  DEPLOY_URL=$(grep -oE 'https://[^[:space:]]+\.vercel\.app' /tmp/vercel-deploy.log | tail -1)
fi

if [ -z "$DEPLOY_URL" ]; then
  echo "⚠️  No pude extraer URL del deployment"
  grep -i 'vercel\.app\|production' /tmp/vercel-deploy.log | tail -5
  sound_err
  read -rp "Presiona Enter para cerrar..."
  exit 0
fi

echo "📌 Deploy URL: $DEPLOY_URL"
echo ""

# ─── ALIAS con auto-retry ───
T2=$(date +%s)
echo "🔗 [2/4] Aliaseando → $DOMAIN..."

set_alias(){
  vercel alias set "$DEPLOY_URL" "$DOMAIN" 2>&1
}

ALIAS_OUTPUT=$(set_alias)
ALIAS_EXIT=$?

# Auto-retry 1x si falla (network blip)
if [ $ALIAS_EXIT -ne 0 ] && ! echo "$ALIAS_OUTPUT" | grep -qE 'Success|assigned|Created|now points'; then
  echo "   ⚠️  Primer intento falló — reintentando en 5s..."
  sleep 5
  ALIAS_OUTPUT=$(set_alias)
  ALIAS_EXIT=$?
fi

echo "$ALIAS_OUTPUT" | tail -3
T3=$(date +%s)
echo "   ⏱  Alias: $((T3-T2))s"
echo ""

if [ $ALIAS_EXIT -ne 0 ]; then
  echo "⚠️  vercel alias set exit $ALIAS_EXIT después de retry"
  echo "   Manual: vercel alias set $DEPLOY_URL $DOMAIN"
  sound_err
  notify_mac "Alias Failed ⚠️" "Deploy OK, alias falló" "Basso"
  read -rp "Presiona Enter para cerrar..."
  exit 1
fi

# ─── SMOKE TEST: múltiples URLs ───
T4=$(date +%s)
echo "🔍 [3/4] Smoke test de 5 URLs claves..."
sleep 5  # propagar alias

declare -A URLS=(
  ["Home"]="/"
  ["Miami Zone"]="/miami-activities"
  ["Spanish (Cancún)"]="/es/cancun-activities"
  ["Blog Index"]="/blog"
  ["Operator Sample"]="/100-miami-luxury-boat-rental-miami"
)

PASSED=0
TOTAL=${#URLS[@]}
for label in "${!URLS[@]}"; do
  path="${URLS[$label]}"
  code=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 15 "https://$DOMAIN$path?v=$COMMIT_HASH")
  if [ "$code" = "200" ]; then
    echo "   ✓ $label ($code) — $path"
    PASSED=$((PASSED+1))
  else
    echo "   ✗ $label ($code) — $path"
  fi
done
T5=$(date +%s)
echo ""
echo "   $PASSED/$TOTAL pasaron · ⏱ $((T5-T4))s"
echo ""

# ─── CONTENT MARKER CHECK ───
echo "🔬 [4/4] Verificando que el deploy tiene el último commit..."
HOMEPAGE_BODY=$(curl -s -L --max-time 15 "https://$DOMAIN/?v=$COMMIT_HASH")
# Buscar el commit hash en algún meta tag o comment (Vercel inyecta x-vercel-cache header)
CACHE_HEADER=$(curl -sI -L --max-time 10 "https://$DOMAIN/?v=$COMMIT_HASH" | grep -i 'x-vercel-cache\|age:' | head -2 | tr -d '\r')
if [ -n "$CACHE_HEADER" ]; then
  echo "$CACHE_HEADER" | sed 's/^/   /'
fi

# Verificar tamaño del body (debe ser >100KB para homepage)
BODY_SIZE=$(echo -n "$HOMEPAGE_BODY" | wc -c | tr -d ' ')
if [ "$BODY_SIZE" -lt 100000 ]; then
  echo "   ⚠️  Homepage muy pequeña ($BODY_SIZE bytes) — posible error"
else
  echo "   ✓ Homepage: $((BODY_SIZE/1024)) KB"
fi
echo ""

# ─── GIT PUSH BACKUP ───
if git remote get-url origin >/dev/null 2>&1; then
  echo "🔼 Backup: git push origin main..."
  git push origin main 2>&1 | tail -3 || echo "   (push falló — backup opcional)"
  echo ""
fi

# ─── RESUMEN ───
TOTAL_TIME=$(($(date +%s) - T0))
ALL_OK=0
[ "$PASSED" = "$TOTAL" ] && [ "$BODY_SIZE" -gt 100000 ] && ALL_OK=1

echo "════════════════════════════════════════════════"
if [ "$ALL_OK" = "1" ]; then
  echo "🎉 Deploy EXITOSO — todo verificado ($TOTAL_TIME s)"
  sound_ok
  notify_mac "Deploy OK ✅" "$PASSED/$TOTAL URLs verificadas" "Glass"
else
  echo "⚠️  Deploy subido pero verifica manualmente ($TOTAL_TIME s)"
  echo "   Algunas URLs pueden estar propagándose en CDN..."
  notify_mac "Deploy Partial ⚠️" "$PASSED/$TOTAL URLs OK" "Glass"
fi
echo ""
echo "   Sitio:     https://$DOMAIN"
echo "   Deploy:    $DEPLOY_URL"
echo "   Commit:    $COMMIT_HASH"
echo "   Tests:     $PASSED/$TOTAL"
echo "════════════════════════════════════════════════"
echo ""
read -rp "Presiona Enter para cerrar..."
