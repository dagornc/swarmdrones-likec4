#!/usr/bin/env bash
# sync_likec4.sh — Synchronise le repo git LikeC4 vers le répertoire servi par le conteneur.
#
# PROBLÈME RÉSOLU : le conteneur likec4 monte /docker/likec4/workspace -> /data (bind mount).
# Le repo de développement est /home/hermesagent/workspace/swarmdrones_likec4.
# Toute édition du repo git est INVISIBLE sur likec4.breizh.ai tant qu'elle n'est pas copiée.
#
# USAGE :
#   ./sync_likec4.sh            # synchronise (dry-run par défaut ? non : applique)
#   ./sync_likec4.sh --dry-run  # montre ce qui serait copié, sans rien modifier
#   ./sync_likec4.sh --check    # vérifie l'état de synchronisation (exit 1 si divergence)
#
# SÉCURITÉ : ne supprime jamais de fichier dans la destination ; ne copie que les .c4
# et le contenu de public/. Sauvegarde horodatée avant chaque copie.

set -euo pipefail

SRC="${LIKEC4_SRC:-/home/hermesagent/workspace/swarmdrones_likec4}"
DST="${LIKEC4_DST:-/docker/likec4/workspace}"
BACKUP_DIR="${LIKEC4_BACKUP:-/home/hermesagent/workspace/likec4_sync_backups}"
CONTAINER="${LIKEC4_CONTAINER:-likec4}"

MODE="apply"
case "${1:-}" in
  --dry-run) MODE="dry-run" ;;
  --check)   MODE="check" ;;
  "")        MODE="apply" ;;
  *) echo "Usage: $0 [--dry-run|--check]" >&2; exit 2 ;;
esac

die() { echo "ERREUR: $*" >&2; exit 1; }

[ -d "$SRC" ] || die "source introuvable: $SRC"
[ -d "$DST" ] || die "destination introuvable: $DST"

# --- Inventaire des fichiers à synchroniser -----------------------------------
# 1. Tous les .c4 à la racine de SRC
# 2. Le contenu de public/ (PDF, assets)
mapfile -t C4_FILES < <(cd "$SRC" && find . -maxdepth 1 -name '*.c4' -printf '%f\n' | sort)
[ "${#C4_FILES[@]}" -gt 0 ] || die "aucun fichier .c4 dans $SRC"

# --- Mode check : rapport de divergence --------------------------------------
if [ "$MODE" = "check" ]; then
  diverg=0
  echo "=== Vérification de synchronisation ==="
  echo "SRC: $SRC"
  echo "DST: $DST"
  echo
  for f in "${C4_FILES[@]}"; do
    if [ ! -f "$DST/$f" ]; then
      echo "  MANQUANT  $f"; diverg=$((diverg+1)); continue
    fi
    if ! cmp -s "$SRC/$f" "$DST/$f"; then
      echo "  DIVERGENT $f"; diverg=$((diverg+1))
    fi
  done
  # public/
  if [ -d "$SRC/public" ]; then
    while IFS= read -r rel; do
      if [ ! -f "$DST/public/$rel" ]; then
        echo "  MANQUANT  public/$rel"; diverg=$((diverg+1))
      elif ! cmp -s "$SRC/public/$rel" "$DST/public/$rel"; then
        echo "  DIVERGENT public/$rel"; diverg=$((diverg+1))
      fi
    done < <(cd "$SRC/public" && find . -type f -printf '%P\n' | sort)
  fi
  echo
  if [ "$diverg" -eq 0 ]; then
    echo "✓ Synchronisé — aucune divergence."
    exit 0
  else
    echo "✗ $diverg divergence(s) détectée(s). Lancer: $0"
    exit 1
  fi
fi

# --- Mode dry-run / apply -----------------------------------------------------
TS="$(date -u +%Y%m%dT%H%M%SZ)"
if [ "$MODE" = "apply" ]; then
  mkdir -p "$BACKUP_DIR/$TS"
  echo "=== Sauvegarde de la destination -> $BACKUP_DIR/$TS ==="
  for f in "${C4_FILES[@]}"; do
    [ -f "$DST/$f" ] && cp -p "$DST/$f" "$BACKUP_DIR/$TS/" || true
  done
  [ -d "$DST/public" ] && cp -rp "$DST/public" "$BACKUP_DIR/$TS/public" 2>/dev/null || true
fi

echo "=== Synchronisation SRC -> DST ($MODE) ==="
n=0
for f in "${C4_FILES[@]}"; do
  if [ -f "$DST/$f" ] && cmp -s "$SRC/$f" "$DST/$f"; then
    continue
  fi
  if [ "$MODE" = "dry-run" ]; then
    echo "  [dry-run] copierait $f"
  else
    cp -p "$SRC/$f" "$DST/$f"
    echo "  copié $f"
  fi
  n=$((n+1))
done

# public/
if [ -d "$SRC/public" ]; then
  mkdir -p "$DST/public"
  while IFS= read -r rel; do
    if [ -f "$DST/public/$rel" ] && cmp -s "$SRC/public/$rel" "$DST/public/$rel"; then
      continue
    fi
    if [ "$MODE" = "dry-run" ]; then
      echo "  [dry-run] copierait public/$rel"
    else
      mkdir -p "$DST/public/$(dirname "$rel")"
      cp -p "$SRC/public/$rel" "$DST/public/$rel"
      echo "  copié public/$rel"
    fi
    n=$((n+1))
  done < <(cd "$SRC/public" && find . -type f -printf '%P\n' | sort)
fi

echo
echo "$n fichier(s) traité(s)."

# --- Validation post-synchronisation -----------------------------------------
if [ "$MODE" = "apply" ]; then
  echo "=== Validation du modèle ==="
  if docker exec "$CONTAINER" npx likec4 validate 2>&1 | grep -qE "Valid"; then
    echo "✓ likec4 validate : Valid"
  else
    echo "✗ likec4 validate : ÉCHEC — restauration recommandée depuis $BACKUP_DIR/$TS" >&2
    exit 1
  fi
  echo
  echo "NOTE: les fichiers .c4 sont rechargés automatiquement (dev server)."
  echo "      Les fichiers ajoutés dans public/ nécessitent un redémarrage :"
  echo "      docker restart $CONTAINER"
fi
