#!/usr/bin/env bash
# install.sh — Installe le hook post-commit versionné dans .git/hooks/.
#
# IDEMPOTENT : relancer ce script plusieurs fois produit le même état final
#   (le hook est copié seulement s'il diffère, puis rendu exécutable). La
#   sortie confirme l'état à chaque exécution, sans effet de bord répété.
#
# RÔLE : le hook post-commit vit dans .git/hooks/ (non versionné par git).
#   La source canonique est tools/hooks/post-commit. Un clone neuf ne possède
#   PAS le hook tant que cet installateur n'a pas été lancé — sans lui, la
#   synchronisation automatique LikeC4 (dépôt → copie servie) disparaît
#   silencieusement.
#
# USAGE :
#   ./tools/hooks/install.sh          # depuis la racine du dépôt (ou ailleurs)

set -euo pipefail

REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SRC="$REPO/tools/hooks/post-commit"
DST="$REPO/.git/hooks/post-commit"

[ -f "$SRC" ] || { echo "ERREUR: source introuvable : $SRC" >&2; exit 1; }
mkdir -p "$(dirname "$DST")"

if [ -f "$DST" ] && cmp -s "$SRC" "$DST"; then
  echo "post-commit : déjà installé et à jour (aucun changement)."
else
  cp "$SRC" "$DST"
  chmod +x "$DST"
  echo "post-commit : installé depuis tools/hooks/post-commit (copie + chmod +x)."
fi

# Vérification d'identité et d'exécutabilité (toujours exécutée).
[ -x "$DST" ] || { echo "ERREUR: $DST non exécutable" >&2; exit 1; }
if cmp -s "$SRC" "$DST"; then
  echo "identité vérifiée : $(md5sum "$DST" | cut -d' ' -f1)  .git/hooks/post-commit"
else
  echo "ERREUR: divergence inattendue entre $SRC et $DST" >&2
  exit 1
fi
