# Typage sémantique des relations

> Epic **E03** · Carte `t_5f46d5aa` · Outils : `tools/arc_classify.py`, `tools/arc_apply.py`

## 1. Problème résolu (P-01 de l'audit)

Avant E03 : **14 kinds de relations déclarés dans la spécification, 0 utilisé**. Les 239 arcs du modèle portaient leur sémantique dans une chaîne libre — 227 libellés distincts pour 239 arcs. Aucun outil ne pouvait distinguer une voie de sûreté d'un flux de données.

Après E03 : **239 relations, 0 non typée**.

## 2. Méthode

Deux outils séparés, pour que la décision et l'écriture soient auditables indépendamment :

- **`arc_classify.py`** — classifieur déterministe. Produit une proposition dans `/tmp/typage.json`. N'écrit jamais dans le modèle.
- **`arc_apply.py`** — applique la proposition. Idempotent, préserve libellés, options et indentation à l'identique. Supporte `--dry-run`.

**Priorité des règles** (la première qui matche gagne) :

1. `safety` — mots-clés de voie de sûreté dans le **libellé seulement**
2. `derives-from` — traçabilité documentaire
3. `command` — ordres, setpoints, consignes
4. `radio` — lien radio, GNSS, liaison physique
5. `store` — persistance, cache, replay
6. `async` — différé, store-and-forward, CRDT, consensus
7. `sync` — appel synchrone, requête
8. `depend-on` — hypothèse (kind historique réutilisé)
9. `justifie` — décision (kind historique réutilisé)
10. `exposed-to` — risque, angle mort (kind historique réutilisé)
11. `implemented-by` — brique logicielle du marché (kind historique réutilisé)
12. `alternative-to` — substitution
13. `flow` — **défaut**, flux de données

## 3. Trois erreurs de classifieur détectées et corrigées

Le classifieur a d'abord produit un résultat plausible mais **faux sur des cas réels**. Détectées par revue par échantillonnage, pas par confiance dans le chiffre.

- `onboard.perception -> onboard.safety 'detection d'evitement'` classé `safety` → **corrigé en `flow`**. Un arc qui *vise* le composant de sûreté est un flux d'entrée, pas une voie de sûreté. La règle initiale déclenchait sur le mot `safety` présent dans le **nom de l'élément cible**.
- `onboard.telemetry -> onboard.linkRadio 'telemetrie priorisee'` classé `radio` → **corrigé en `flow`**. Un trafic qui *transite* par la radio est un flux de données.
- `onboard -> docSource 'decrit en §4.1'` classé `sync` → **corrigé en `derives-from`**. Règle de traçabilité documentaire remontée en priorité 2.

**Leçon** : un classifieur par mots-clés doit être validé sur échantillon réel, pas sur son taux de couverture. Le taux était de 100 %, la qualité de 3 cas sur 239 était fausse.

## 4. Distribution obtenue

- `exposed-to` — 83 (composants et briques exposés à des risques / angles morts)
- `flow` — 31 (flux de données internes, cœur du onboard et du edge)
- `justifie` — 25 (décisions motivant des choix de conception)
- `depend-on` — 18 (composants dépendant d'hypothèses)
- `implemented-by` — 18 (composants implémentés par une brique du marché)
- `radio` — 16 (liens intermittents)
- `store` — 16 (persistance)
- `sync` — 9 (invocations)
- `command` — 7 (ordres, setpoints)
- `safety` — 6 (voies de sûreté, RTL, geofence)
- `async` — 6 (différé, CRDT)
- `derives-from` — 4 (traçabilité vers le document source)

## 5. Preuve de non-régression et d'effet

| Mesure | Avant E03 | Après E03 |
|---|---|---|
| Éléments | 97 | **97** |
| Relations | 239 | **239** |
| Vues | 22 | **22** |
| Relations non typées | 239 | **0** |
| `likec4 validate` | Valid (3 files) | **Valid (3 files)** |

Aucun arc ajouté, supprimé, ni déplacé : seul le préfixe `-[kind]->` a été inséré. Le libellé, les blocs d'options et l'indentation sont inchangés.

## 6. Ce que cela débloque

Le typage rend possible, sans intervention humaine :

- le **filtrage des flux** par nature (`radio` vs `flow` vs `command`) ;
- la **détection de cycles** sur `dependsOn` seul, sans être pollué par les arcs de traçabilité ;
- la **coloration automatique** des arcs par criticité de flux ;
- l'extraction du **graphe de messages** : les arcs `radio` + les futurs kinds `publishes`/`subscribes` composeront la vue des flux animés (E06) ;
- le calcul de la **matrice d'exposition aux risques** sans heuristique de nommage.

## 7. Réserve

12 kinds sur 37 sont utilisés. Les 25 autres (`contains`, `implements`, `runsOn`, `deployedOn`, `publishes`, `subscribes`, `sends`, `receives`, `commands`, `observes`, `controls`, `calls`, `produces`, `consumes`, `uses`, `validates`, `documentedBy`, `supportedBy`, `measuredBy`, `evaluates`, `unknown`, ...) attendent leurs objets : ils seront peuplés par E02 (fonctionnel), E04 (algorithmes), E05 (matériel), E06 (messages), E07 (deployment), E08 (scientifique).

Le kind `unknown` compte **0 usage**. C'est le résultat attendu : chaque arc a pu être qualifié avec un motif explicite. Il reste disponible comme filet de sécurité pour les lots à venir.
