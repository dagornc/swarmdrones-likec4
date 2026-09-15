# Notes de versionnement

## Ce qui est versionné

Le **savoir** : sources du modèle, code de vérification, documentation, scripts.

- `*.c4` — le modèle LikeC4 (source de vérité)
- `tools/` — pipeline d'export, contrats exécutables, générateur d'assets
- `viewer/` — le consommateur 3D et son test de logique
- `docs/` — spécifications et documentation
- `export_likec4.sh` — script d'export, porteur des leçons apprises
- `point4/` — analyses (le markdown porte le raisonnement)

## Ce qui n'est PAS versionné

Le **produit régénérable** : tout ce qu'un script peut recalculer.

- `backup_v*/` — 22 sauvegardes manuelles antérieures à git (4,2 Mo de doublons)
- `png/*.png`, `point4/*.png`, `*.drawio` — exports d'images LikeC4 (~25 Mo)
- `export/scene.json`, `viewer/scene.json` + empreintes
- `assets/glb/*.glb`, `assets/assets.json`, `assets/preview.png`

### Pourquoi exclure les sorties du pipeline

Un artefact versionné peut **mentir** sur ce que le code produit réellement : le
fichier commité peut dater d'une exécution antérieure au code. C'est un risque de
divergence silencieuse, déjà rencontré une fois sur ce projet (la copie manuelle
`viewer/scene.json`, devenue désynchronisée).

Chaque sortie est **vérifiable par recalcul** :

```bash
python3 tools/export/export_scene.py --check          # coherence scene.json
blender --background --python tools/assets/build_assets.py -- --check
python3 tools/assets/test_preview.py assets/preview.png
```

Le contrôle est plus fort qu'un versionnement : il **refuse** une sortie périmée.

## Détail technique

Le dépôt contenait initialement 27 Mo d'objets git : des fichiers lourds
(PNG) avaient été indexés avant d'être exclus par `.gitignore`. Un
`git reflog expire --expire=now --all && git gc --prune=now` a ramené `.git`
à **1,2 Mo** sans toucher au commit.

## Limites

- Pas de dépôt distant : ce dépôt est local. Le travail est protégé contre la
  perte accidentelle de fichiers, **pas** contre la perte de la machine.
  Un `git remote add` vers un hébergement est une décision à prendre
  séparément (implique de publier — attention si le contenu devient sensible).
- Un seul commit : l'historique commence maintenant. Il ne raconte pas les
  versions antérieures, qui sont figées dans `backup_v*/`.
