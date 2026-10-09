#!/usr/bin/env bash
# build_static.sh — Produit le site statique SwarmDrones pour likec4.breizh.ai
#
# Remplace la logique de restart du dev server LikeC4 : on compile le modèle
# en site statique, puis on le publie dans ./site/ (servi par nginx).
#
# USAGE :
#   ./build_static.sh            # build + publication dans ./site/
#
# PRÉREQUIS : image ghcr.io/likec4/likec4:1.59.2 disponible localement.
# Le modèle source est /home/hermesagent/workspace/swarmdrones_likec4.

set -euo pipefail

SRC="${LIKEC4_SRC:-/home/hermesagent/workspace/swarmdrones_likec4}"
DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_DIR="$DEPLOY_DIR/site"
IMAGE="${LIKEC4_IMAGE:-ghcr.io/likec4/likec4:1.59.2}"
TITLE="${LIKEC4_TITLE:-SwarmDrones — Architecture}"

echo "=== Build statique SwarmDrones ==="
echo "Source : $SRC"
echo "Cible  : $SITE_DIR"

if [ ! -d "$SRC" ]; then
  echo "ERREUR : source introuvable : $SRC" >&2
  exit 1
fi

# --- Build dans un conteneur jetable, sortie dans un volume temporaire -------
TMP_BUILD="$(mktemp -d)"
trap 'rm -rf "$TMP_BUILD"' EXIT

echo "--- Compilation (likec4 build) ---"
# --memory=3g : borne la consommation. Sans limite, Graphviz `unflatten` peut
# être tué par SIGTERM quand la machine est sous pression mémoire (7,8 Go au
# total sur cet hôte). Le build échoue alors en boucle sur les vues.
docker run --rm --memory=3g \
  -v "$SRC":/data:ro \
  -v "$TMP_BUILD":/out \
  "$IMAGE" \
  build -o /out --public /data/public --use-hash-history /data \
  2>&1 | tail -4

if [ ! -f "$TMP_BUILD/index.html" ]; then
  echo "ERREUR : le build n'a pas produit index.html" >&2
  exit 1
fi

# --- Correction du titre (bug v1.59.2 : --title n'atteint pas le HTML) ------
for f in "$TMP_BUILD/index.html" "$TMP_BUILD/404.html"; do
  [ -f "$f" ] || continue
  sed -i "s|<title>LikeC4</title>|<title>$TITLE</title>|" "$f"
done

# --- Publication atomique ---------------------------------------------------
rm -rf "$SITE_DIR.new" "$SITE_DIR.old"
mv "$TMP_BUILD" "$SITE_DIR.new"
trap - EXIT
[ -d "$SITE_DIR" ] && mv "$SITE_DIR" "$SITE_DIR.old"
mv "$SITE_DIR.new" "$SITE_DIR"
rm -rf "$SITE_DIR.old"

echo "✓ Site statique publié dans $SITE_DIR"
du -sh "$SITE_DIR"
