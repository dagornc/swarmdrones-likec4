# Mise à jour dynamique du corpus public

Ce document décrit le dispositif qui maintient le dossier
[`corpus-public/`](.) synchronisé avec la veille scientifique.

## Principe

Le corpus public est **régénéré automatiquement** à chaque exécution du
pipeline hebdomadaire de veille. Aucune intervention manuelle n'est requise.

```
cron (lundi 08:00)
  └─ swarmdrone-corpus-update.sh
       └─ weekly_corpus_update.py
            ├─ 1. arxiv              (rattrapage par tranches de 7 jours)
            ├─ 2. crossref_openalex
            ├─ 3. huggingface
            ├─ 4. catalog_rebuild
            ├─ 5. bibliographic_quality
            ├─ 6. impact_analysis
            ├─ 7. verify_corpus_links
            ├─ 8. generate_descriptions   (extraction, puis LLM local)
            └─ 9. publish_public_corpus   (régénère + commit + push)
```

## Ce qui est publié

Uniquement des **faits bibliographiques publics** :

- titre de l'article
- URL directe vers la source
- DOI et identifiant arXiv
- hôte, type de ressource, niveau de confiance, périmètre
- **description courte** (≤ 15 mots)
- **date de publication** revendiquée (non prouvée)

## Ce qui n'est jamais publié

- les PDF et le contenu des articles (droit d'auteur)
- les chemins locaux
- les empreintes de fichiers (`sha256`)
- toute donnée de credential

## Format de `index.md`

Chaque ligne contient exactement ce qui est demandé :

```
| # | Date | Description | Titre (lien direct) | Confiance |
```

- **lien direct** : le titre est un lien cliquable vers la source
- **description** : ≤ 15 mots, extraite de l'article ou générée localement
- **date de publication** : revendiquée par la source, `—` si absente

## Date de dernière mise à jour

Elle est écrite dans :

- `README.md` — ligne `**Dernière mise à jour : AAAA-MM-JJ HH:MM UTC**`
- `index.md` — même ligne en tête de fichier
- `statistiques.md` — même ligne en tête de fichier

## Génération des descriptions

`catalog.json` ne contient **aucun champ `abstract` ni `description`**.
Les descriptions sont donc produites par `generate_descriptions.py` :

1. **extraction** depuis le Markdown archivé localement (≈ 83 % des cas) :
   meta description, sinon meilleure phrase informative (scoring heuristique
   qui écarte navigation, cookies, menus et fragments) ;
2. **LLM local** (Ollama `qwen2.5:3b`, ≈ 16 % des cas) quand l'extraction
   échoue ;
3. **rejet** si la description ne partage aucun mot significatif avec le
   titre — mieux vaut pas de description qu'une description fausse.

Le résultat est mis en cache dans `descriptions.json` (clé = numéro d'entrée),
donc les entrées déjà traitées ne sont jamais recalculées.

## Robustesse

- **Tranches arXiv** : `arxiv_windowed_update.py` découpe la fenêtre en
  tranches de 7 jours. Sans cela, un watermark en retard produit une fenêtre
  dépassant le plafond de pagination arXiv (2 000 résultats), le run échoue
  et le watermark n'avance pas — cercle vicieux.
- **Étapes non critiques** : `generate_descriptions` et
  `publish_public_corpus` sont marquées non critiques. Un échec de
  publication ne remet pas en cause la validité de la veille.
- **Verrou de run** : deux pipelines ne peuvent pas tourner simultanément.

## Vérifier

```bash
# état du dernier run
cat /home/hermesagent/swarmdrone-research/last-update-status.json

# relancer la publication seule (sans push)
python3 scripts/publish_public_corpus.py --no-push

# rattraper un retard arXiv
python3 scripts/arxiv_windowed_update.py --dry-run
```
