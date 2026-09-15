#!/usr/bin/env bash
# ==============================================================================
# export_likec4.sh — Export fiable du modele SwarmDrones (LikeC4 1.59.2)
# ------------------------------------------------------------------------------
# LECONS APPRISES (ne pas re-decouvrir) :
#
#  1. TIMEOUT PLAYWRIGHT (cause racine des "Failed 1 out of N views")
#     Le defaut est de 15 s de rendu. Les grosses vues le depassent largement
#     (ex: deploiement-30-plateformes = ~107 s, 41 noeuds / 30 plateformes).
#     => TOUJOURS passer `-t 300 --max-attempts 3`.
#
#  2. FICHIERS ROOT-OWNED
#     Le conteneur ecrit dans /data en root. Un `rm -rf` cote hote echoue
#     ("Permission denied") et, chaine avec `&&`, court-circuite tout l'export.
#     => Toujours nettoyer DEPUIS le conteneur : docker exec likec4 rm -rf ...
#
#  3. INCLUDE * EST DANGEREUX
#     `include *` tire tout ce qui est CONNECTE (donc les relations de
#     tracabilite derives-from vers docSource). Une vue "paysage" doit
#     LISTER ses noeuds explicitement, ou filtrer.
#     Filtre par kind :  include * where kind is not hypothesis and kind is not decision
#
#  4. COLOR : dans `style { color X }`, X est un NOM de couleur (theme ou
#     declare dans specification { color monNom #hex }), JAMAIS un #hex direct.
#
#  5. HOT-RELOAD WEB NON FIABLE : apres toute modif .c4, `docker restart likec4`
#     si le serveur web sert un modele perime (projet fige par Vite).
# ==============================================================================
set -euo pipefail

WS=/docker/likec4/workspace
CT=likec4

echo "=== [1/4] validate ==="
docker exec "$CT" likec4 validate /data 2>&1 | grep -E "Valid|error|Error" | tail -3

echo "=== [2/4] nettoyage (DEPUIS le conteneur) ==="
docker exec "$CT" rm -rf /data/out/png_final /data/out/drawio_final

# PITFALL : ne JAMAIS faire `chown -R` global sur /data — cela bascule les
# sources .c4 en un UID non lisible par l'hote (Permission denied, casse les
# patchs). Si des fichiers root-owned apparaissent dans out/, ne chowner que out/ :
#   docker exec $CT chown -R 1002:1002 /data/out

echo "=== [3/4] export PNG (timeout 300s) ==="
docker exec "$CT" likec4 export png /data -o /data/out/png_final -t 300 --max-attempts 3 2>&1 \
  | grep -E "exported|Failed|ERROR" | tail -3
docker exec "$CT" sh -c 'ls /data/out/png_final/*.png | wc -l'

echo "=== [4/4] export DrawIO ==="
docker exec "$CT" likec4 export drawio /data -o /data/out/drawio_final -t 300 --max-attempts 3 2>&1 \
  | grep -E "exported|Failed|ERROR" | tail -3
docker exec "$CT" sh -c 'ls /data/out/drawio_final/*.drawio | wc -l'

echo "=== rappel : docker restart likec4 pour rafraichir le web ==="
