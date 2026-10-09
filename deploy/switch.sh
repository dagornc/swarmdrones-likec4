#!/usr/bin/env bash
# switch.sh — Bascule likec4.breizh.ai du dev server vers le site statique.
#
# USAGE :
#   ./switch.sh status    # état actuel (qui sert le site)
#   ./switch.sh to-static # bascule vers le site statique nginx
#   ./switch.sh to-dev    # ROLLBACK vers le dev server LikeC4
#
# PRÉREQUIS : ./site/ doit contenir un build valide (voir build_static.sh).
# Traefik route via labels Docker : les deux conteneurs déclarent le même Host,
# donc un seul doit tourner à la fois.

set -euo pipefail

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_DIR="$DEPLOY_DIR/site"
SITE_URL="https://likec4.breizh.ai"

check_url() {
  local code
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$SITE_URL/" || echo "000")"
  echo "  $SITE_URL -> HTTP $code"
}

status() {
  echo "=== État du service ==="
  docker ps --filter "name=likec4" --format "  {{.Names}} : {{.Status}}" || true
  check_url
}

to_static() {
  if [ ! -f "$SITE_DIR/index.html" ]; then
    echo "ERREUR : $SITE_DIR/index.html absent — lancez build_static.sh d'abord" >&2
    exit 1
  fi
  echo "=== Bascule vers le site statique ==="
  echo "--- Arrêt du dev server ---"
  docker stop likec4 2>&1 | tail -1 || true
  echo "--- Démarrage de likec4-static ---"
  cd "$DEPLOY_DIR"
  docker compose up -d 2>&1 | tail -3
  sleep 3
  status
}

to_dev() {
  echo "=== ROLLBACK vers le dev server LikeC4 ==="
  echo "--- Arrêt du site statique ---"
  cd "$DEPLOY_DIR"
  docker compose down 2>&1 | tail -2 || true
  echo "--- Redémarrage du dev server ---"
  docker start likec4 2>&1 | tail -1 || true
  sleep 5
  status
}

case "${1:-status}" in
  status)    status ;;
  to-static) to_static ;;
  to-dev)    to_dev ;;
  *) echo "Usage: $0 {status|to-static|to-dev}" >&2; exit 1 ;;
esac
