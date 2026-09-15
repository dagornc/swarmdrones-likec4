# Piste B — Assets 3D Blender

## 1. Objet

Produire les **assets 3D** que le consommateur (viewer / Blender) utilise pour
représenter le système décrit dans `worldmodel.c4`, **sans inventer aucune
caractéristique du système**.

## 2. Le problème que ce pipeline résout

Le modèle LikeC4 décrit des **catégories visuelles qualitatives** :

- `multirotor` (entUavF, 8 instances) — vol stationnaire, manœuvre fine
- `fixed-wing` (entUavR, 18 instances) — voilure fixe, rayon d'action
- `surface-vessel` (entUsv, 4 instances) — plateforme de surface maritime
- `reference-mockup` (entReference, 1) — maquette de référence (RS-1)
- `ground-station` (entGroundStation, 1)
- `edge-node` (entEdgeNode, 1)
- `digital-twin` (entTwin, 1)

Il ne contient **aucune dimension** (INV-4 : `transform: null` partout). Or la 3D
a besoin de géométrie chiffrée. Le risque est d'introduire subrepticement des
valeurs physiques non tracées — exactement ce que REG-2/REG-3 interdisent côté
viewer.

**Décision structurante** : l'échelle d'un asset Blender est une **convention de
scène arbitraire**, pas une dimension revendiquée. Un cube de côté 1 n'affirme
pas « le drone mesure 1 m ». Le pipeline encode la **topologie** (combien de
corps, quelle disposition), jamais une caractéristique du système.

## 3. Ce que le pipeline garantit

Trois invariants, tous vérifiés par `--check` :

1. **Alignement sur le modèle** — chaque catégorie produite correspond à une
   catégorie *déclarée* dans `scene.json`. Une catégorie déclarée sans
   générateur fait **échouer** le contrôle ; un générateur orphelin est signalé.
2. **Traçabilité embarquée** — chaque GLB porte `source_category` et
   `source_class` dans ses `extras`, **écrits dans le binaire**. Le contrôle
   relit les octets du fichier : un asset qui perd sa traçabilité échoue.
   (Défaut réel rencontré : sans `export_extras=True`, Blender n'écrit pas les
   propriétés personnalisées — les 7 GLB étaient intraçables.)
3. **Aucune dimension physique revendiquée** — le manifeste est scanné : toute
   unité (`m`, `kg`, `cm`, `W`, `Wh`) fait échouer le contrôle.

## 4. Usage

```bash
# génération (nécessite numpy visible par Blender, voir §5)
export PYTHONPATH=$HOME/.local/lib/blender-py312
blender --background --python tools/assets/build_assets.py

# contrôle (échoue si écart modèle/assets, traçabilité absente, ou unité physique)
blender --background --python tools/assets/build_assets.py -- --check

# rendu de vérification + test falsifiable
blender --background --python tools/assets/render_preview.py
python3 tools/assets/test_preview.py assets/preview.png
```

## 5. Dépendance : numpy pour le Python de Blender

L'installation Blender du conteneur est **minimaliste** : le Python embarqué
(`/usr/bin/python3.12`) n'a pas de `site-packages`, et l'export glTF en dépend
(`numpy`). Blender n'a ni `pip` ni droits d'installation ; `apt` exige `sudo`.

Solution retenue, **sans sudo et sans modification du système** :

```bash
uv pip install --python /usr/bin/python3.12 \
    --target $HOME/.local/lib/blender-py312 numpy
```

Puis `PYTHONPATH=$HOME/.local/lib/blender-py312` au lancement de Blender.

L'alternative (export OBJ, natif sans numpy) a été écartée : format sans
matériaux PBR ni hiérarchie, et non consommable directement par Three.js, ce qui
aurait exigé un pipeline de conversion supplémentaire pour un résultat inférieur.

Autre limite de l'installation : le débruiteur Cycles (`OpenImageDenoise`) est
absent → `use_denoising = False` dans le script de rendu.

## 6. Preuve de rendu

`assets/preview.png` — planche des 7 assets, rendue avec Blender lui-même
(Cycles, 32 échantillons, 1600×920).

Le rendu est **mesuré**, pas supposé. `tools/assets/test_preview.py` échoue si
l'image est plate :

- chaque asset occupe sa case, cadrage calculé sur les **bornes réelles
  mesurées** après placement ;
- résultat : **67,2 % de pixels non-fond, 4862 couleurs distinctes** ;
- le test est **falsifiable** : vérifié contre une image uniforme → exit 1.

Un premier rendu produisait une image uniforme (6 couleurs, 97 % d'une seule
teinte) : la caméra était positionnée sur une grille *supposée* et non sur les
bornes *mesurées*. C'est ce défaut qui a motivé le critère chiffré — un PNG qui
existe ne prouve rien.

## 7. Limites assumées

- **Les formes sont des conventions visuelles**, pas des spécifications. Le
  modèle ne dit pas à quoi ressemble un `entUavF` ; le pipeline choisit une
  forme distinctive et l'assume comme telle.
- **Distinction visuelle** : `reference-mockup` est volontairement abstraite
  (structure cubique à montants) pour rester non confondable avec une
  plateforme opérationnelle — cohérent avec l'exigence de non-confusion portée
  par le modèle de qualité.
- **Aucun asset n'est encore chargé par le viewer** : la chaîne actuelle
  (viewer 2D/3D procédural) reste inchangée. L'intégration des GLB est une
  étape distincte, à décider séparément.
