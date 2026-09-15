# World Model — spécification pour la consommation 3D

> Epic **E11** · Carte `t_ab3002bd` · Fichier : `worldmodel.c4`
> Carte de conception : `docs/world-model-spec.md`

## 1. Objet

Préparer la consommation du modèle par **Blender** et le **moteur Web 3D**,
sans introduire de 3D dans LikeC4.

Le World Model est un modèle **indépendant et dérivé** :
- il ne contient **aucune coordonnée, aucun maillage, aucune texture** ;
- il déclare les **entités simulables**, leurs **zones** et leurs **catégories** ;
- il est la **couche de correspondance** entre sémantique et rendu.

## 2. Schéma de dérivation

```
id_likec4 (stable) → role_scene → categorie_visuelle → population
```

L'`id_likec4` est la **clé étrangère**. Le consommateur 3D ne doit **jamais**
inventer un identifiant : il prend ceux du World Model.

## 3. Population réelle (vérifiée sur le modèle compilé)

- **UAV-R ×18** — reconnaissance, voilure fixe → `ZONE_AIR`
- **UAV-F ×8** — multirotor → `ZONE_AIR`
- **USV ×4** — surface maritime → `ZONE_SURFACE`
- **= 30 plateformes opérationnelles** (26 aériens + 4 surface)
- **Drone de référence ×1** — maquette, **hors des 30**, visuellement distincte
- Infrastructure : GCS ×1, Edge ×1, jumeau ×1

⚠️ **Total du fichier = 34 entités**, dont **30 opérationnelles**. La maquette
de référence et l'infrastructure ne se comptent pas dans l'essaim.

## 4. Les 6 zones sémantiques

`ZONE_AIR`, `ZONE_SURFACE`, `ZONE_ALLOCATION`, `ZONE_COMMS`, `ZONE_COMMAND`,
`ZONE_CLOUD`. Ce sont des **domaines abstraits**, pas des emprises : le
consommateur les spatialise.

## 5. Les 10 états d'apparence

Chaque état **dérive d'un scénario E09**. Le rendu représente des **états**,
pas seulement des objets : nominal, lien C2 perdu, agent perdu, partition,
GNSS dégradé, risque de collision, spectre saturé, énergie critique,
densité élevée, leader perdu à N=30.

## 6. Les 6 règles de représentation (garde-fous)

Ce sont les règles qui **protègent la vérité du modèle** :

- **REG-1** — Ne jamais inventer d'identifiant (tout id vient de la table de correspondance)
- **REG-2** — **Ne pas afficher de valeur d'énergie** (DE-07 ouvert)
- **REG-3** — **Ne pas afficher de portée radio chiffrée** (annonces commerciales non vérifiées)
- **REG-4** — **Porter la limite N=30** (validation réelle plafonne à 26)
- **REG-5** — 30 opérationnels + 1 référence distincte
- **REG-6** — Aucune position issue du modèle sémantique (INV-4)

Ces règles sont **vérifiables** : chacune porte un test.

## 7. Ce qui n'est PAS dans le World Model

- Aucune coordonnée, aucun maillage, aucune texture
- Aucun comportement ni dynamique (c'est le rôle des scénarios E09)
- Aucune valeur chiffrée non sourcée (énergie, portée)
- Aucune durée ni horloge

## 8. Vérification

- `likec4 validate` → **Valid (14 files)**
- 285 éléments, 544 relations
- **33 éléments #world, 0 orphelin**
- **INV-4 confirmé par scan** : aucune coordonnée x/y/z dans les 14 fichiers `.c4`
  (les 2 seules correspondances de l'expression régulière sont des échelles
  d'agents `{10,20,30}` dans `science.c4` — faux positifs)
- Population : 18 + 8 + 4 = **30 opérationnels**, +1 maquette distincte

## 9. Nature des entités — clarification post-export

Chaque entité porte un champ `nature`, qui distingue **trois populations** :

- `plateforme_essaim` — les **30** plateformes opérationnelles (UAV-R, UAV-F, USV)
- `maquette_reference` — le drone de référence, **hors essaim**, distinct au rendu
- `infrastructure` — GCS, Edge, jumeau numérique : **ne volent pas**, ce ne sont
  pas des plateformes

Cette distinction a été **révélée par le test d'export** : le premier essai
comptait 33 « opérationnels » parce que GCS, Edge et Twin étaient agrégés aux
plateformes. Le contrôle a échoué (`FAIL: 33 operationnels (attendu 30)`), la
cause a été corrigée **dans le modèle**, pas dans le test.

## 10. Artefact d'export

`tools/export/export_scene.py` produit `export/scene.json` — la **seule porte
de sortie** vers la 3D :

- **34 instances** nommées (`UAV-R-01`..`UAV-R-18`, `UAV-F-01`.., `USV-01`..)
- **`transform: null` partout** — INV-4 : le consommateur spatialise
- 6 `consumer_obligations` explicites (interdictions d'inventer)
- Auto-vérification : `python3 tools/export/export_scene.py --check`
