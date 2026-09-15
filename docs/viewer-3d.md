# Consommateur 3D — Piste A

> Carte `t_2304c46b` (E14) · Livrable : `viewer/index.html`
> Consomme : `export/scene.json` (produit par `tools/export/export_scene.py`)

## 1. Principe

Ce viewer est un **consommateur**, pas une source de vérité.

- Il ne connaît **aucun identifiant en dur** : tout vient de `scene.json` (REG-1).
- Il n'affiche **aucune valeur d'énergie** ni de **portée radio chiffrée** (REG-2 / REG-3).
- Toute scène à 30 porte la mention **« N=30 NON PROUVÉ »** (REG-4).
- La maquette de référence est **visuellement distincte** : cube filaire violet (REG-5).
- Les positions sont **calculées par le viewer**, jamais lues du modèle (REG-6 / INV-4).

## 2. Ce qui fait la valeur du livrable

Le viewer n'est pas un joli rendu : c'est un **vérificateur de contrat**.
Il applique les 8 contrôles suivants au fichier qu'on lui donne, et **refuse de
prétendre que tout va bien** si un contrôle échoue :

| Contrôle | Ce qu'il prouve |
|---|---|
| REG-6 / INV-4 | `transform = null` partout : le modèle ne spatialise pas |
| REG-5 | 30 plateformes opérationnelles + 1 maquette distincte |
| REG-1 | Aucun identifiant inventé : tout `class_id` vient du World Model |
| REG-4 | La limite N=30 est portée par la scène |
| REG-2 | Aucune valeur d'énergie (DE-07 ouvert) |
| REG-3 | Aucune portée radio chiffrée (annonces non vérifiées) |
| INTÉGRITÉ | Les compteurs déclarés correspondent aux instances réelles |
| GARDE-FOUS | Les 6 règles de rendu sont déclarées et vérifiables |

## 3. Comment l'utiliser

Le viewer charge `scene.json` par `fetch` : il **faut un serveur HTTP** (pas `file://`).

```bash
cd /home/hermesagent/workspace/swarmdrones_likec4/viewer
python3 -m http.server 8931
# puis ouvrir http://127.0.0.1:8931/index.html
```

### La scène servie au viewer est produite par l'export

`viewer/scene.json` est **écrit par `export_scene.py`**, en même temps que
`export/scene.json`. **Aucune copie manuelle n'est nécessaire** :

```bash
python3 tools/export/export_scene.py          # écrit les DEUX copies
python3 tools/export/export_scene.py --check  # vérifie, dont leur cohérence
```

`--check` échoue si les deux copies **divergent** — le viewer ne peut donc pas
afficher *et valider* une scène périmée sans que ce soit détecté. L'export est
déterministe : deux exécutions sur le même modèle produisent le même SHA256,
publié dans `export/scene.sha256` et `viewer/scene.sha256`.

## 4. Tests exécutés (preuves)

```bash
python3 tools/export/test_consumer_contract.py   # 8/8 + 7 mutations attrapées
node    viewer/test_viewer_logic.js              # 8/8 + 7 mutations attrapées
```

Les deux tests vérifient la **logique du viewer** sur l'artefact réel, **et**
sur des artefacts mutilés : chaque contrôle doit échouer quand sa contrainte
est violée. Un test qui ne peut pas échouer ne prouve rien.

## 5. Défauts trouvés par les tests (et corrigés à la source)

Ces trois défauts étaient dans **le viewer**, pas dans le modèle :

1. **REG-2 faux positif** — le scan incluait `render_rules`, dont le texte
   cite les unités interdites (*« aucune valeur Wh/min/Pct »*). Corrigé en
   scannant seulement les données consommées (états + obligations).
2. **REG-1 mal ancré** — le contrôle exigeait que tout `class_id` soit une clé
   racine de `scene.json`, ce qui est absurde (les classes viennent du modèle
   LikeC4, pas de la scène dérivée). Réancré sur `derivation_links` : tout
   `class_id` doit être **source d'un lien de dérivation**.
3. **REG-4 mal ciblé** — la limite vit dans **deux** sources légitimes
   (obligations + rendu de `stLeaderLost`). Le test ne retirait qu'une source,
   ce qui le rendait insensible. Mutation rendue exhaustive.

## 6. Vérification du rendu en navigateur réel

Le rendu a été **exécuté pour de vrai** dans Chromium headless (conteneur
`mcp-playwright`, binaire `/ms-playwright/chromium-1200/...`, moteur logiciel
`ANGLE / SwiftShader` — pas de GPU).

Mesures objectives, sur la page servie :

- **74 %** de pixels non-noirs dans le canvas (`readPixels` : 532 443 px)
- **93** couleurs distinctes → la scène n'est pas un aplat
- **8/8** contrôles de contrat, **0** échec, **0** erreur JS
- `scenebar` : 11 éléments construits (10 scénarios + libellé)

Capture : `viewer/screenshots/render-final.png`.

Harnais de vérification (réutilisable) :

```bash
# Prérequis : servir le viewer en HTTP, puis exécuter DANS le conteneur
# de navigateur (le script référence son Chromium et son playwright-core).
python3 -m http.server 8931 --bind 0.0.0.0 &      # depuis viewer/
docker cp tools/export/verify_final.js mcp-playwright:/tmp/vf.js
docker exec mcp-playwright node /tmp/vf.js        # rendu + mesures + verdict
```

Le script `verify_final.js` contient des chemins absolus propres au conteneur
(`/ms-playwright/chromium-1200/...`). Il n'est donc **pas** exécutable
directement depuis l'hôte — c'est une contrainte de l'environnement, pas un
choix. La cible HTTP est le gateway de l'hôte vu du conteneur
(`http://172.16.1.1:8931`).

### Un piège de vérification, à retenir

Le premier screenshot est sorti **entièrement noir**, alors que le rendu
fonctionnait : Three.js n'active pas `preserveDrawingBuffer`, donc le buffer
est vidé après composition et une capture tardive ne voit plus rien.
Un « écran noir » n'est donc **pas** une preuve d'absence de rendu — il faut
mesurer via `readPixels` dans la page, ou préserver le buffer. Le viewer
active désormais `preserveDrawingBuffer` pour rester inspectable.

### Limites qui subsistent

- Le **repli 2D** est codé et testé comme logique, mais n'a pas été déclenché
  en conditions réelles (il faudrait un navigateur sans WebGL du tout).
- Les **formations spatiales** sont déterministes (anneaux) : elles illustrent
  la population, elles ne simulent pas une dynamique de vol.
- Le rendu a été validé sur **moteur logiciel** ; le rendu GPU n'a pas été testé.

Le contrat, lui, est vérifié automatiquement dans les deux sens (Python + JS).
