# Rapport — Nettoyage des copies parasites de `specification/` et vérification du PDF système

- Date : 2026-09-28 17:31 UTC
- Dépôt : `dagornc/swarmdrones-likec4` (branche `master`)
- Carte : `t_6360fa9e` (SPEC-CLEANUP)
- HEAD de départ : `b6db44a`

## 1. Fichiers supprimés (copies parasites)

Trois fichiers **non suivis** (`git status` → `??`) traînaient dans
`specification/` depuis le 22/09/2026. Ils ont été supprimés (simple `rm`, car
non suivis par git — `git rm` inapplicable).

| Fichier | Taille (o) | sha256 | Verdict copie |
|---|---|---|---|
| `specification/render_pdf_v2.py` | 9 421 | `acd3834002d42eafc8fbe58c9644db094660cdd04b356f8500f1616c8cefaa23` | **Identique** à `spec_systeme_essaim/render_pdf_v2.py` |
| `specification/tri_propositions_37.md` | 3 920 | `1858ac8545244757b9417ad2107ab8ffa34a6d5c9de3fc775ba25b0101de10cb` | **Identique** à `spec_systeme_essaim/tri_propositions_37.md` |
| `specification/specification_v2.md` | 43 207 | `46a0c9a9d4742be4e25a89e4d848d8fca9728f1c5bfa6c07b04ede5ccdda9049` | **PÉRIMÉE et FAUSSE** — diffère de l'original |

Justification :
- Les deux premiers sont des **copies strictement identiques** (mêmes sha256)
  d'originaux versionnés dans `~/workspace/spec_systeme_essaim/` (dépôt git
  propre, HEAD `11cc582`). Aucune perte d'information à les supprimer.
- Le troisième (`specification_v2.md`) est une **copie périmée et fausse** de
  l'original `spec_systeme_essaim/specification_v2.md` (43 774 o, sha256
  `29bc7a1166e75cb3f17fa1c64d87c5930052cf3f38210a9c11a827e93295d42d`). L'original
  a été corrigé par le commit `11cc582` de `spec_systeme_essaim` ; la copie
  conservait l'affirmation erronée « ~5,5 Mo » (voir §2).
- Le modèle LikeC4 ne référence ces fichiers **nulle part** (`grep` sur tous les
  `*.c4` → 0 occurrence). Ils ne sont donc ni un artefact du modèle, ni un
  livrable : ce sont des doublons parasites.

Après suppression, `git status --short` ne montre plus aucune entrée `??` pour
`specification/`.

## 2. Comparaison du PDF système publié

Le PDF système publié dans `swarmdrones_likec4/specification/` a été comparé à
l'original de `spec_systeme_essaim/`.

| Fichier | Taille (o) | sha256 |
|---|---|---|
| `swarmdrones_likec4/specification/Specification_Systeme_Essaim_Drones_v2.pdf` (AVANT correction) | 226 611 | `1a1d9fb7250fe53d487cbaa84eb2fa70924ec7fc3e3cec35dc04eba8d84efb0e` |
| `spec_systeme_essaim/Specification_Systeme_Essaim_Drones_v2.pdf` (original corrigé) | 228 388 | `3c4e29a9ab609b10022206977ccae6d92357e50c97e37a667eceaf49030eb5b3` |
| `spec_systeme_essaim/Specification_Systeme_Essaim_Drones.pdf` (v1, pour référence) | 292 318 | `c88df8a7b59ccf1e9f01d43b6d9d1eb0d4804af6f3165d2a8b8bb5285a5ffb74` |

**Les deux PDF v2 diffèrent** (226 611 o vs 228 388 o ; sha256 différents).
Contenu comparé par `pdftotext` :

- Original corrigé (`spec_systeme_essaim`, 228 388 o) :
  > « l'API interne (`/@id/likec4:plugin/swarmdrones/model.js`) pèse **11 563 626 octets** après publication »

- Copie publiée (226 611 o) :
  > « l'API interne pèse **~5,5 Mo**. La mesure antérieure de 11 531 990 octets correspondait à un autre »

La copie publiée portait l'affirmation **périmée et fausse** « ~5,5 Mo »,
exactement le défaut corrigé par le commit `11cc582` de `spec_systeme_essaim`.
L'original a été modifié le 2026-09-22 13:27:46 (après la correction), la copie
le 2026-09-22 12:59:38 (avant la correction) — la copie est donc bien antérieure.

### Décision

**Republication de l'original corrigé** (228 388 o, sha256
`3c4e29a9ab609b10022206977ccae6d92357e50c97e37a667eceaf49030eb5b3`) dans
`swarmdrones_likec4/specification/Specification_Systeme_Essaim_Drones_v2.pdf`.

Vérification post-copie (relue sur disque) :
- `sha256sum` → `3c4e29a9ab609b10022206977ccae6d92357e50c97e37a667eceaf49030eb5b3` ✔
- `stat -c%s` → `228388` ✔
- `pdfinfo` → `Pages: 23`, `Producer: WeasyPrint 70.0`, `File size: 228388 bytes` ✔

## 3. Carte LikeC4 pointant vers le PDF système

Vérification demandée : « la carte LikeC4 correspondante pointe-t-elle vers ce
PDF ? ».

Résultat : **aucune carte LikeC4 ne référence `Specification_Systeme_Essaim_Drones_v2.pdf`**.
- `grep` sur tous les `*.c4` (20 fichiers actifs) → 0 occurrence.
- La seule occurrence du nom de fichier dans tout le dépôt était
  `specification/render_pdf_v2.py` (le script parasite, désormais supprimé).
- Le modèle référence bien 13 `specDoc` PDF **par algorithme** (dans
  `algorithms.c4`/`e20-audit-completeness.c4`) et 15 `specDoc` SysML v2
  (`sysml.c4`), mais **pas** le document de spécification système global.

C'est une **lacune de traçabilité**, pas une erreur introduite par cette carte.
Signalée ici, non corrigée : ajouter une telle carte toucherait un fichier `.c4`
hors périmètre (risque de collision avec les cartes `architecte` concurrentes sur
`algorithms.c4`/`architecture.c4`/`science.c4`). À arbitrer côté modèle.

## 4. Documentation du mécanisme de publication (« HMR inopérant »)

Le fait « HMR inopérant sur le modèle compilé, seul `docker restart likec4`
publie une modification `.c4` » était documenté **uniquement** dans :
- `sync_likec4.sh` (script opérationnel, nombreuses occurrences) ;
- `export_likec4.sh` (lignes 26 et 55) ;
- `sysml/VALIDATION_REPORT.md` (ligne 63).

Il était **absent** du `README.md` et de `docs/` (la documentation canonique).

Action : ajout d'une section **« Publication du modèle (serveur LikeC4) »** au
`README.md`, juste après « Démarrage rapide », décrivant :
- le service de `public/` depuis un **instantané pris au démarrage** du conteneur ;
- le **HMR inopérant** sur `model.js` ;
- la nécessité de `docker restart likec4` après toute modification `.c4` ;
- la détection d'écart via `./sync_likec4.sh --drift` (sortie code 1 si divergence) ;
- le cache transitoire Cloudflare (`max-age=14400`).

## 5. Validation `likec4 validate` sur clone propre

Exécutée sur **clone propre** (`git clone -q . /tmp/lc_cleanup_v2`), jamais en
local (les 162 fichiers des `backup_*` gitignorés faussent le comptage).

Sortie réelle :

```
=== clone HEAD ===
b6db44a
=== npx likec4 validate ===
17:30:35.648 INFO  likec4.lang layout wasm
17:30:35.658 INFO  likec4.lang workspace: /tmp/lc_cleanup_v2
17:30:35.680 INFO  likec4.server.projects add 'swarmdrones'
17:30:35.681 INFO  likec4.server.workspace loaded 1 projects
17:30:37.211 INFO  likec4.lang workspace: found 20 source files
17:30:40.657 INFO  likec4.c4:validate ✓ Valid (20 files)
17:30:40.658 INFO  likec4.c4:validate validate 5s
EXIT=0
```

Résultat : **`✓ Valid (20 files)`**, code de sortie **0**.

Note : le clone de validation est pris sur l'état commité (HEAD `b6db44a`). Les
modifications de cette carte ne touchent **que** `README.md` et le PDF système
(aucun fichier `.c4`) : les 20 fichiers `.c4` validés sont donc strictement
identiques à ceux de l'état final commité.

## 6. Confirmation — fichiers `.c4` protégés non touchés

Conformément à l'interdiction de la carte, les trois fichiers modifiés par les
cartes `architecte` concurrentes n'ont **pas** été touchés. sha256 relevés avant
toute opération et recontrôlés :

| Fichier | sha256 (avant = après) |
|---|---|
| `algorithms.c4` | `dc5f1b77d808dd40cec4871739a6be610bad48ce77478e895e7ac2a634cb09d7` |
| `architecture.c4` | `c3e5ec52e909d683ae520f7e6456718f59c6090daffceddfd352caa8a6ddeee2` |
| `science.c4` | `0587d961c8ed5c8f8d117c5dd3c6b6310e833a1f278ef0f3e4a4bb1117c62fba` |

`git diff --stat` ne montre qu'une seule modification :
```
 specification/Specification_Systeme_Essaim_Drones_v2.pdf | Bin 226611 -> 228388 bytes
 1 file changed, 0 insertions(+), 0 deletions(-)
```
(le `README.md` et ce rapport s'ajoutent au commit, les suppressions de fichiers
non suivis n'apparaissent pas dans `git diff`).

## 7. Bilan des mesures réelles

- 3 fichiers parasites supprimés de `specification/` (tailles : 9 421, 43 207, 3 920 o).
- PDF système republié : 226 611 o → **228 388 o** (sha256
  `3c4e29a9ab609b10022206977ccae6d92357e50c97e37a667eceaf49030eb5b3`).
- `likec4 validate` sur clone propre : **`✓ Valid (20 files)`**, exit 0.
- `algorithms.c4` / `architecture.c4` / `science.c4` : sha256 inchangés.
- Documentation du piège « HMR inopérant / docker restart requis » ajoutée au `README.md`.
