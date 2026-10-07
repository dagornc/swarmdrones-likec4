# Corpus SwarmDrone — version publiable

Métadonnées bibliographiques d'un corpus de veille scientifique sur les
**essaims de drones** et les systèmes autonomes multi-agents.

**2 609 entrées** — titres, sources, DOI, identifiants arXiv, niveau de
confiance et périmètre.

> **Ce qui est publié ici** : uniquement des **faits bibliographiques publics**
> (titre, URL source, DOI, arXiv, hôte, classification).
>
> **Ce qui n'est PAS publié** : les PDF, le contenu des articles, les chemins
> locaux, les empreintes de fichiers. Le corpus complet (6,3 Go, 805 PDF) reste
> privé — les documents sont soumis au droit d'auteur de leurs éditeurs.

## Fichiers

- [`statistiques.md`](statistiques.md) — tableau de bord du corpus
- [`index.md`](index.md) — index complet des 2 609 entrées
- [`corpus.json`](corpus.json) — métadonnées structurées (exploitable par script)

## Ce que ce corpus démontre

Un pipeline de veille qui **ne prétend pas que tout est fiable** : il trace le
niveau de confiance de chaque entrée et signale ce qui reste à vérifier.

- **1 308** candidats primaires (`A-primary-candidate`)
- **797** documents d'artefacts (`B-artifact-documentation`)
- **420** non vérifiées (`unverified`)
- **48** découvertes (`D-discovery`)
- **34** sources officielles (`B-official`)
- **2** signalées suspectes (`suspicious`)

Les dates revendiquées ne sont pas des preuves : la métadonnée décisive est
résolue contre la source primaire.

## Rattachement aux algorithmes

Chaque algorithme canonique du modèle LikeC4 est rattaché à ses sources
fondatrices. Voir le dépôt principal :
[`dagornc/swarmdrones-likec4`](https://github.com/dagornc/swarmdrones-likec4).

## Régénération

Ce dossier est **généré** depuis le catalogue privé. Ne pas éditer à la main.

## Licence

Les métadonnées bibliographiques sont des faits publics. Les documents sources
restent la propriété de leurs éditeurs respectifs.
