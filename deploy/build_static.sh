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
# Les fichiers produits par le conteneur appartiennent a root : un `rm -rf`
# depuis l'hote echoue (Permission denied). On nettoie via un conteneur.
cleanup() {
  docker run --rm -v "$TMP_BUILD":/x alpine sh -c 'rm -rf /x/* /x/.[!.]* 2>/dev/null' >/dev/null 2>&1 || true
  rm -rf "$TMP_BUILD" 2>/dev/null || true
}
trap cleanup EXIT

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

# --- Correction du robots.txt ----------------------------------------------
# LikeC4 genere un robots.txt avec `Disallow: /` (site entier interdit aux
# moteurs) et ecrase celui de public/. Pour une vitrine publique c'est
# contre-productif : on le remplace apres build.
# Le fichier appartient a root : on le supprime puis on le recree.
rm -f "$TMP_BUILD/robots.txt" 2>/dev/null || \
  docker run --rm -v "$TMP_BUILD":/x alpine rm -f /x/robots.txt >/dev/null 2>&1 || true
printf 'User-agent: *\nAllow: /\n' > "$TMP_BUILD/robots.txt"

# --- Publication en place ---------------------------------------------------
# PIEGE 1 : remplacer le repertoire monte (mv/rm) invalide le bind mount Docker.
# Le conteneur continue de pointer vers l'inode supprime -> 403/404 sur tout.
# PIEGE 2 : les fichiers produits par le conteneur appartiennent a root ; un
# `cp`/`rm` depuis l'hote echoue et le repertoire doit rester traversable (755)
# sinon nginx (autre UID) renvoie 403.
# Solution : publier DEPUIS un conteneur (root), en place, puis normaliser les
# permissions pour que nginx puisse lire.
mkdir -p "$SITE_DIR"
docker run --rm \
  -v "$TMP_BUILD":/src:ro \
  -v "$SITE_DIR":/dst \
  alpine sh -c '
    set -e
    find /dst -mindepth 1 -delete 2>/dev/null || true
    cp -a /src/. /dst/
    chmod 755 /dst
    chmod -R a+rX /dst
  '

echo "✓ Site statique publié dans $SITE_DIR"
du -sh "$SITE_DIR"
