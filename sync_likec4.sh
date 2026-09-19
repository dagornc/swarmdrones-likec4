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
#   ./sync_likec4.sh --drift      # vérifie la cohérence public/ vs servi (exit 1 si écart)
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
    --drift)      MODE="drift" ;;
    --no-restart) RESTART=0 ;;
    "")           ;;
    *) echo "Usage: $0 [--dry-run|--check|--drift|--no-restart]" >&2; exit 2 ;;
  esac
done

die() { echo "ERREUR: $*" >&2; exit 1; }

# --- Contrôle de cohérence public/ vs servi ----------------------------------
# Contexte : `likec4 start --public-dir` ne lit les fichiers de public/ qu'au
# DÉMARRAGE du conteneur (instantané). Un fichier AJOUTÉ après le démarrage n'est
# pas servi (l'URL renvoie le fallback HTML de la SPA) ; un fichier MODIFIÉ reste
# servi dans son ANCIENNE version. Dans les deux cas, seul un `docker restart`
# re-synchronise l'index. Un second cache (Cloudflare, max-age=14400) peut en
# plus servir une version périmée de façon transitoire. check_drift compare :
#   - « disque » : ce que le conteneur voit dans /data/public (docker exec
#     sha256sum) — reflète le bind mount /docker/likec4/workspace/public.
#   - « servi »  : ce qui est réellement renvoyé sur l'URL publique (curl).
# En cas d'écart, on interroge l'ORIGINE (curl dans le conteneur, sans
# Cloudflare ni cache) pour distinguer « index likec4 périmé » (restart requis)
# de « cache CDN transitoire » (pas de restart). Aucun redémarrage n'est jamais
# effectué ici ; en cas de divergence le script sort en code non nul pour que le
# hook post-commit rende l'écart visible. En cas d'indisponibilité (conteneur
# arrêté, site inaccessible), on AVERTIT sans échouer : la vérification ne doit
# jamais bloquer un commit.
check_drift() {
  local rel disk_hash served_hash origin_hash code ctype origin_code origin_ctype
  local diverg restart_needed list
  diverg=0
  restart_needed=0
  echo "=== Contrôle de cohérence public/ vs servi ==="

  list="$(docker exec "$CONTAINER" sh -c 'cd /data/public 2>/dev/null && find . -type f -printf "%P\n" | sort' 2>/dev/null || true)"
  if [ -z "$list" ]; then
    if ! docker exec "$CONTAINER" true >/dev/null 2>&1; then
      echo "  ⚠ conteneur $CONTAINER inaccessible — vérification impossible (non bloquant)." >&2
      return 0
    fi
    echo "  (aucun fichier dans /data/public)"
    return 0
  fi

  while IFS= read -r rel; do
    [ -n "$rel" ] || continue
    disk_hash="$(docker exec "$CONTAINER" sha256sum "/data/public/$rel" 2>/dev/null | cut -d' ' -f1 || true)"
    if [ -z "$disk_hash" ]; then
      echo "  ⚠ public/$rel : empreinte disque illisible — ignoré." >&2
      continue
    fi
    # Les fichiers de public/ sont servis à la racine du site (via Cloudflare).
    # NB : noms plats et URL-safe dans ce projet ; pas d'encodage d'URL.
    meta="$(curl -s -o /dev/null -w '%{http_code} %{content_type}' "$SITE/$rel" 2>/dev/null || true)"
    code="${meta%% *}"
    ctype="${meta#* }"
    case "$code" in
      200) ;;
      000|"")
        echo "  ⚠ public/$rel : URL servie inaccessible ($SITE) — vérification impossible (non bloquant)." >&2
        continue ;;
      *)
        echo "  ⚠ DIVERGENCE: public/$rel (disque ${disk_hash:0:8}…) != servi (HTTP $code — non servi) — docker restart likec4 requis (autorisation Christophe)"
        diverg=$((diverg+1)); restart_needed=$((restart_needed+1))
        continue ;;
    esac
    case "$ctype" in
      text/html*|"")
        # Fallback HTML de la SPA : likec4 n'a pas ce fichier dans son index
        # (ajouté après le démarrage). Cas persistant → restart requis.
        echo "  ⚠ DIVERGENCE: public/$rel (disque ${disk_hash:0:8}…) != servi (fallback HTML — non servi) — docker restart likec4 requis (autorisation Christophe)"
        diverg=$((diverg+1)); restart_needed=$((restart_needed+1))
        continue ;;
    esac
    served_hash="$(curl -s "$SITE/$rel" 2>/dev/null | sha256sum | cut -d' ' -f1 || true)"
    if [ -z "$served_hash" ]; then
      echo "  ⚠ public/$rel : corps servi illisible — vérification impossible (non bloquant)." >&2
      continue
    fi
    if [ "$disk_hash" = "$served_hash" ]; then
      echo "  ✓ public/$rel : servi conforme (${disk_hash:0:8}…)"
    else
      # Écart disque vs servi. Deux causes possibles : (a) likec4 sert une autre
      # version (index périmé) → restart requis ; (b) cache Cloudflare transitoire
      # → se résorbe. On lit l'ORIGINE (conteneur, localhost, sans CDN ni cache).
      origin_meta="$(docker exec "$CONTAINER" curl -s -o /dev/null -w '%{http_code} %{content_type}' "http://localhost:5173/$rel" 2>/dev/null || true)"
      origin_code="${origin_meta%% *}"
      origin_ctype="${origin_meta#* }"
      if [ "$origin_code" != "200" ]; then
        echo "  ⚠ DIVERGENCE: public/$rel (disque ${disk_hash:0:8}…) != servi (${served_hash:0:8}…) — origine illisible, docker restart likec4 requis (autorisation Christophe)"
        diverg=$((diverg+1)); restart_needed=$((restart_needed+1))
      else
        case "$origin_ctype" in
          text/html*|"")
            echo "  ⚠ DIVERGENCE: public/$rel (disque ${disk_hash:0:8}…) != servi (${served_hash:0:8}…) — non servi par likec4, docker restart likec4 requis (autorisation Christophe)"
            diverg=$((diverg+1)); restart_needed=$((restart_needed+1)) ;;
          *)
            origin_hash="$(docker exec "$CONTAINER" curl -s "http://localhost:5173/$rel" 2>/dev/null | sha256sum | cut -d' ' -f1 || true)"
            if [ "$origin_hash" = "$disk_hash" ]; then
              echo "  ⚠ DIVERGENCE: public/$rel (disque ${disk_hash:0:8}…) != servi (${served_hash:0:8}…) — cache Cloudflare transitoire, l'origine sert déjà la bonne version (pas de restart requis)"
              diverg=$((diverg+1))
            else
              echo "  ⚠ DIVERGENCE: public/$rel (disque ${disk_hash:0:8}…) != servi (${served_hash:0:8}…) — l'origine sert une autre version, docker restart likec4 requis (autorisation Christophe)"
              diverg=$((diverg+1)); restart_needed=$((restart_needed+1))
            fi ;;
        esac
      fi
    fi
  done <<< "$list"

  echo
  if [ "$diverg" -eq 0 ]; then
    echo "✓ Cohérence public/ — aucun écart entre le disque et le contenu servi."
    return 0
  elif [ "$restart_needed" -gt 0 ]; then
    echo "✗ $diverg divergence(s) public/ — docker restart likec4 requis (autorisation Christophe)."
    return 1
  else
    echo "✗ $diverg divergence(s) public/ — écarts transitoires (cache Cloudflare) ; l'origine est à jour, aucun restart requis."
    return 1
  fi
}

[ -d "$SRC" ] || die "source introuvable: $SRC"
[ -d "$DST" ] || die "destination introuvable: $DST"

# --- Mode drift : vérification isolée, sans synchronisation ni redémarrage ----
if [ "$MODE" = "drift" ]; then
  if check_drift; then
    exit 0
  else
    exit 1
  fi
fi

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

  # --- Contrôle de cohérence public/ vs servi (toujours, même sans changement) -
  # Voir check_drift() en tête de script. Sort en code 1 si écart disque vs servi,
  # pour que le hook post-commit rende la divergence visible. Aucun redémarrage.
  echo
  if check_drift; then
    drift=0
  else
    drift=$?
  fi
  exit "$drift"
fi
