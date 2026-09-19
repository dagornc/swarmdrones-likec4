#!/usr/bin/env bash
# sync_likec4.sh — Synchronise le repo git LikeC4 vers le répertoire servi par le conteneur.
#
# PROBLÈME RÉSOLU : le conteneur likec4 monte /docker/likec4/workspace -> /data (bind mount).
# Le repo de développement est /home/hermesagent/workspace/swarmdrones_likec4.
# Toute édition du repo git est INVISIBLE sur likec4.breizh.ai tant qu'elle n'est pas copiée.
#
# USAGE :
#   ./sync_likec4.sh              # synchronise + redémarre le conteneur si un .c4 a changé
#   ./sync_likec4.sh --dry-run    # montre ce qui serait copié, sans rien modifier
#   ./sync_likec4.sh --check      # vérifie l'état de synchronisation (exit 1 si divergence)
#   ./sync_likec4.sh --no-restart # synchronise sans redémarrer le conteneur
#
# SÉCURITÉ : ne supprime jamais de fichier dans la destination ; ne copie que les .c4
# et le contenu de public/. Sauvegarde horodatée avant chaque copie.
#
# REDÉMARRAGE : le dev server LikeC4 (Vite) ne recharge PAS le modèle de façon fiable
# quand un .c4 change (HMR inopérant sur le modèle compilé). Un `docker restart` est
# nécessaire pour que likec4.breizh.ai serve le modèle à jour. Le redémarrage est un
# acte MANUEL soumis à l'AUTORISATION EXPLICITE de Christophe (service en production) :
#   - Le mode apply par défaut (sans --no-restart) redémarre le conteneur si un .c4 a
#     changé, puis VÉRIFIE que le modèle servi contient bien les changements (preuve,
#     pas supposition). Réservé à un opérateur qui a cette autorisation.
#   - L'automatisation git (.git/hooks/post-commit) appelle TOUJOURS ce script avec
#     --no-restart : aucun redémarrage n'est effectué automatiquement ; le hook signale
#     alors « docker restart likec4 requis (autorisation Christophe) ».

set -euo pipefail

SRC="${LIKEC4_SRC:-/home/hermesagent/workspace/swarmdrones_likec4}"
DST="${LIKEC4_DST:-/docker/likec4/workspace}"
BACKUP_DIR="${LIKEC4_BACKUP:-/home/hermesagent/workspace/likec4_sync_backups}"
CONTAINER="${LIKEC4_CONTAINER:-likec4}"
SITE="${LIKEC4_SITE:-https://likec4.breizh.ai}"
RESTART_WAIT="${LIKEC4_RESTART_WAIT:-30}"

MODE="apply"
RESTART=1
for arg in "$@"; do
  case "$arg" in
    --dry-run)    MODE="dry-run" ;;
    --check)      MODE="check" ;;
    --no-restart) RESTART=0 ;;
    "")           ;;
    *) echo "Usage: $0 [--dry-run|--check|--no-restart]" >&2; exit 2 ;;
  esac
done

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
CHANGED_C4=()
for f in "${C4_FILES[@]}"; do
  if [ -f "$DST/$f" ] && cmp -s "$SRC/$f" "$DST/$f"; then
    continue
  fi
  if [ "$MODE" = "dry-run" ]; then
    echo "  [dry-run] copierait $f"
  else
    cp -p "$SRC/$f" "$DST/$f"
    echo "  copié $f"
    CHANGED_C4+=("$f")
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

# --- Validation + redémarrage + vérification du modèle servi ------------------
if [ "$MODE" = "apply" ]; then
  echo "=== Validation du modèle ==="
  # NB: capturer la sortie AVANT le test — avec `set -o pipefail`, un `grep -q`
  # qui ferme le pipe prématurément fait échouer `docker exec` (SIGPIPE) et
  # propage un faux négatif.
  VALID_OUT="$(docker exec "$CONTAINER" npx likec4 validate 2>&1 || true)"
  if printf '%s' "$VALID_OUT" | grep -qE "Valid"; then
    echo "✓ likec4 validate : Valid"
  else
    echo "✗ likec4 validate : ÉCHEC — restauration recommandée depuis $BACKUP_DIR/$TS" >&2
    printf '%s\n' "$VALID_OUT" | tail -5 >&2
    exit 1
  fi

  # --- Redémarrage si un .c4 a changé (usage opérateur direct, AUTORISÉ) -----
  # Cette branche n'est atteinte qu'en mode apply SANS --no-restart, c'est-à-dire
  # uniquement lorsqu'un opérateur disposant de l'autorisation explicite de
  # Christophe invoque ce script directement. Le hook post-commit utilise toujours
  # --no-restart et n'atteint JAMAIS cette branche.
  # Le dev server Vite ne recharge pas le modèle compilé de façon fiable : sans
  # redémarrage, likec4.breizh.ai continue de servir l'ANCIEN modèle (HTTP 200
  # trompeur). On redémarre donc, puis on VÉRIFIE le contenu réellement servi.
  if [ "$n" -gt 0 ] && [ "$RESTART" -eq 1 ]; then
    echo
    echo "=== Redémarrage du conteneur ($CONTAINER) ==="
    echo "  raison : $n fichier(s) modifié(s) — le dev server ne recharge pas le modèle"
    docker restart "$CONTAINER" >/dev/null
    echo "  conteneur redémarré, attente de la régénération (max ${RESTART_WAIT}s)..."

    # Attendre que le serveur réponde ET que le modèle soit régénéré.
    ready=0
    for i in $(seq 1 "$RESTART_WAIT"); do
      sleep 1
      code="$(curl -s -o /dev/null -w '%{http_code}' "$SITE/" 2>/dev/null || echo 000)"
      if [ "$code" = "200" ]; then
        # le modèle compilé doit être servi (taille > 1 Mo = vrai modèle, pas le fallback HTML)
        msz="$(curl -s -o /dev/null -w '%{size_download}' \
               "$SITE/@id/likec4:plugin/swarmdrones/model.js" 2>/dev/null || echo 0)"
        if [ "${msz:-0}" -gt 1000000 ]; then
          ready=1
          echo "  ✓ serveur prêt après ${i}s (modèle servi : ${msz} octets)"
          break
        fi
      fi
    done

    if [ "$ready" -eq 0 ]; then
      echo "  ✗ le serveur n'a pas régénéré le modèle en ${RESTART_WAIT}s" >&2
      echo "    vérifier : docker logs $CONTAINER --tail 30" >&2
      exit 1
    fi

    # --- Preuve : le modèle servi contient-il les fichiers modifiés ? --------
    echo
    echo "=== Vérification du modèle réellement servi ==="
    # NB: écrire le modèle dans un FICHIER, pas dans une variable shell.
    # Un `grep -q` sur une variable de ~7,7 Mo ferme le pipe au premier match
    # (SIGPIPE sur printf) et produit un faux négatif — même piège que plus haut.
    MODEL_TMP="$(mktemp)"
    if ! curl -s -o "$MODEL_TMP" "$SITE/@id/likec4:plugin/swarmdrones/model.js" 2>/dev/null; then
      echo "  ✗ modèle servi illisible" >&2
      rm -f "$MODEL_TMP"
      exit 1
    fi
    if [ ! -s "$MODEL_TMP" ]; then
      echo "  ✗ modèle servi vide" >&2
      rm -f "$MODEL_TMP"
      exit 1
    fi
    # Pour chaque .c4 modifié, on extrait un identifiant distinctif et on vérifie
    # sa présence dans le modèle compilé servi.
    miss=0
    for f in "${CHANGED_C4[@]}"; do
      # premier identifiant d'élément du fichier (ex: "algTaskAllocation = algorithm")
      id="$(grep -oE '^[[:space:]]*[a-zA-Z][a-zA-Z0-9_]*[[:space:]]*=[[:space:]]*(algorithm|component|specDoc|system|software|message|scenario|risk|blindspot|hypothesis|decision)' \
            "$DST/$f" 2>/dev/null | head -1 | sed -E 's/^[[:space:]]*([a-zA-Z0-9_]+).*/\1/')"
      if [ -z "$id" ]; then
        echo "  ? $f : aucun identifiant détectable (ignoré)"
        continue
      fi
      if grep -q "$id" "$MODEL_TMP"; then
        echo "  ✓ $f : '$id' présent dans le modèle servi"
      else
        echo "  ✗ $f : '$id' ABSENT du modèle servi" >&2
        miss=$((miss+1))
      fi
    done
    rm -f "$MODEL_TMP"
    if [ "$miss" -gt 0 ]; then
      echo "  ✗ $miss fichier(s) non reflété(s) dans le modèle servi" >&2
      exit 1
    fi
    echo "  ✓ modèle servi à jour"
  elif [ "$n" -gt 0 ] && [ "$RESTART" -eq 0 ]; then
    echo
    echo "NOTE: --no-restart — le conteneur n'a PAS été redémarré."
    echo "      Le modèle servi peut être périmé : docker restart $CONTAINER"
    echo "      (redémarrage = acte MANUEL, autorisation Christophe requise)"
  else
    echo
    echo "Aucun fichier modifié — pas de redémarrage nécessaire."
  fi
fi
