#!/usr/bin/env bash
# check_likec4_sync.sh — Contrôle périodique dépôt ↔ copie servie (LikeC4).
#
# RÔLE : filet de sécurité qui détecte la divergence entre le dépôt de
#   développement et la copie servie par le conteneur likec4, INDÉPENDAMMENT de
#   tout commit. Le hook post-commit ne s'exécute qu'après un commit réussi :
#   un worker qui écrit des .c4 puis crashe SANS committer ne le déclenche
#   jamais, et la copie servie reste périmée (incident du 2026-09-29 : 12 blocs
#   dans science.c4 sans commit, copie servie en retard de 43 min). Ce contrôle
#   couvre exactement ce cas.
#
# CONTRAT (pattern watchdog hermes cron --no-agent) :
#   - Tout est synchronisé    → AUCUNE sortie, exit 0 (silencieux, pas de notif).
#   - Divergence détectée     → alerte nommant CHAQUE fichier divergent, exit 1.
#   - Vérification impossible → alerte, exit 1 (on ne reste pas silencieux).
#
# SÉCURITÉ : ce script n'effectue AUCUNE synchronisation et AUCUN redémarrage.
#   Il délègue la comparaison à sync_likec4.sh --check (lecture seule) et ne
#   fait que rapporter. Le redémarrage du conteneur likec4 reste un acte MANUEL
#   soumis à l'autorisation explicite de Christophe.
#
# USAGE :
#   ./tools/hooks/check_likec4_sync.sh                # silencieux si synchro OK
#   LIKEC4_REPO=/chemin/vers/repo ./tools/hooks/check_likec4_sync.sh

set -uo pipefail

REPO="${LIKEC4_REPO:-/home/hermesagent/workspace/swarmdrones_likec4}"
SYNC="$REPO/sync_likec4.sh"

if [ ! -x "$SYNC" ]; then
  echo "ALERTE SYNC LIKEC4 — contrôle introuvable ou non exécutable : $SYNC"
  exit 1
fi

OUT="$(bash "$SYNC" --check 2>&1)"
code=$?
if [ "$code" -eq 0 ]; then
  # Synchronisé : silencieux (aucune notification).
  exit 0
fi

# Divergence (ou vérification impossible) : alerte nommant chaque fichier.
echo "ALERTE SYNC LIKEC4 — le dépôt et la copie servie divergent"
echo "Date : $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "------------------------------------------------------------"
printf '%s\n' "$OUT" | grep -E 'MANQUANT|DIVERGENT|ERREUR' || printf '%s\n' "$OUT"
echo "------------------------------------------------------------"
echo "Cause probable : édition du dépôt sans synchronisation de la copie"
echo "  servie (/docker/likec4/workspace). Exemples :"
echo "  - un worker a écrit des .c4 puis a crashé SANS committer"
echo "    (le hook post-commit ne s'exécute qu'après un commit réussi) ;"
echo "  - un commit a été effectué sans le hook post-commit installé"
echo "    (clone neuf : penser à ./tools/hooks/install.sh)."
echo "Action : lancer $REPO/sync_likec4.sh pour recopier le dépôt vers la"
echo "  copie servie. AUCUN redémarrage du conteneur n'est effectué ici ;"
echo "  un éventuel 'docker restart likec4' reste un acte MANUEL soumis à"
echo "  l'autorisation explicite de Christophe."
exit 1
