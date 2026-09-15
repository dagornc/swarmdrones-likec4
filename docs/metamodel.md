# Métamodèle SwarmDrone

> Epic **E01** · Carte `t_b6b0fb55` · Fichier source : `metamodel.c4`
> État : **validé** par `likec4 validate` → `✓ Valid (3 files)`

## 1. Principe directeur

LikeC4 est la **source de vérité sémantique** de l'architecture. Il décrit la structure, les responsabilités et les échanges. Il ne décrit **ni le rendu, ni l'espace 3D** : aucune coordonnée graphique n'est autorisée dans le modèle. Le placement spatial appartient au moteur Web 3D.

Le métamodèle est régi par quatre règles :

1. **Aucun identifiant existant n'est renommé.** Les 97 éléments et 239 relations historiques sont conservés à l'identique — prouvé : les compteurs sont inchangés après E01.
2. **Ajout par surcouche.** Les 56 kinds côtoient les 13 kinds historiques sans les invalider.
3. **Sémantique explicite.** Une relation dont le sens n'est pas établi porte `unknown` et génère une carte Kanban. Jamais de kind choisi par défaut.
4. **Le code n'est pas dans LikeC4.** Le kind `sourceCode` référence un dépôt Git ; il ne contient pas d'implémentation.

## 2. Les 9 familles d'éléments (56 kinds)

### Famille 1 — Système (4 kinds)
`system`, `subsystem`, `capability`, `mission`
La capacité est l'objet qui répond à « que sait faire le système ? », indépendamment de son implémentation. Elle relie mission et fonction.

### Famille 2 — Fonctionnel (3 kinds)
`function`, `process`, `responsibility`
La responsabilité distingue explicitement l'autorité humaine de l'autonomie embarquée — distinction structurante ici, où l'opérateur « n'agit jamais dans la boucle de contrôle temps réel ».

### Famille 3 — Logiciel (6 kinds)
`application`, `service`, `component`, `agent`, `module`, `apiContract`
`agent` est le kind central de l'essaim : entité logicielle autonome avec état, objectifs et décision locale. `component` reste le kind des 24 composants historiques.

### Famille 4 — Algorithmique (7 kinds)
`algorithm`, `strategy`, `policy`, `optimizer`, `planner`, `controller`
`algorithm` (historique) désigne une famille ; `strategy` désigne une variante interchangeable — c'est le **niveau B** de modification (E16).

### Famille 5 — Données (6 kinds)
`message`, `event`, `command`, `telemetry`, `state`, `dataset`
C'est la famille qui rend les communications **explicitement observables**. Sans elle, aucune visualisation de flux animés n'est possible.

### Famille 6 — Communication (3 kinds)
`topic`, `protocol`, `interface`
Le topic nommé explicitement permet au simulateur de router les messages sans deviner.

### Famille 7 — Matériel (7 kinds)
`drone`, `sensor`, `actuator`, `computeNode`, `networkDevice`, `groundStation`, `server`
Base du drone de référence (E05) et des assets Blender. `drone` porte la description des 30 instances.

### Famille 8 — Infrastructure (5 kinds)
`container`, `network`, `runtime`, `middleware`
Chaîne de déploiement : `Algorithm → Component → Service → Runtime → ComputeNode → Drone`.

### Famille 9 — Documentation et preuves (7 kinds)
`scientificPaper`, `specDoc`, `standard`, `sourceCode`, `test`, `experiment`
Permet `Algorithm → supportedBy → scientificPaper` et `scientificPaper → evaluates → algorithm` (E08/E12).

> **Note technique** : le kind `specification` a dû être nommé `specDoc`. `specification` est un **mot réservé** du langage LikeC4 (bloc racine `specification {}`) et provoque une erreur de syntaxe.

## 3. Les 37 relations

### 21 relations exigées par la mission (toutes présentes)
Structure : `contains`, `derivedFrom`
Exécution : `implements`, `runsOn`, `deployedOn`
Messages : `publishes`, `subscribes`, `sends`, `receives`
Autorité : `commands`, `observes`, `controls`
Dépendances : `dependsOn`, `calls`
Données : `produces`, `consumes`, `uses`
Preuve : `validates`, `documentedBy`, `supportedBy`, `measuredBy`

### 14 relations historiques (préservées)
`sync`, `flow`, `radio`, `command`, `store`, `async`, `safety`, `depend-on`, `justifie`, `derives-from`, `implemented-by`, `alternative-to`, `exposed-to`, `does-not-cover`

### 1 relation de sécurité méthodologique
`unknown` — pour tout arc dont le sens n'est pas établi. Son usage est **tracé** et doit tendre vers zéro avant clôture.

> **Collision de nommage** : `command` existe en kind d'élément (commande) et en kind de relation (ordre). LikeC4 les distingue par espace de nommes, mais c'est une source de confusion pour un lecteur humain. À noter, pas à corriger (renommer casserait l'existant).

## 4. Tags de criticité (conservés)

`safety-critical`, `mission-critical`, `best-effort`, `cloudOnly` — cœur de la sémantique visuelle. Légende native produite par `styleGroup criticite`.

## 5. Convention sémantique des attributions

**Attribution de criticité au flux, pas à l'élément.** Un composant `safety-critical` peut émettre un message `best-effort`. La criticité se lit sur l'arc, pas sur le nœud.

**Un message a un producteur et au moins un consommateur.** Un message sans producteur ou sans consommateur est une erreur détectée par E12.

**Un algorithme a des entrées et des sorties.** Un algorithme sans entrée/sortie est une erreur détectée par E12.

## 6. Preuve de non-régression

| Mesure | Avant E01 | Après E01 | Verdict |
|---|---|---|---|
| Kinds d'éléments | 13 | 56 | +43 |
| Kinds de relations | 14 (0 utilisés) | 37 | +23 |
| Éléments du modèle | 97 | **97** | inchangé ✔ |
| Relations du modèle | 239 | **239** | inchangé ✔ |
| Vues | 22 | **22** | inchangé ✔ |
| `likec4 validate` | Valid (2 files) | **Valid (3 files)** | ✔ |

## 7. Suite

- **E03** : typer les 239 arcs existants (les kinds sont prêts).
- **E02** : couche fonctionnelle (capabilities, functions) en surcouche.
- **E04** : enrichir les 7 algorithmes avec entrées/sorties/paramètres/métriques.
- **E06** : créer les 14 messages objets + protocoles + topics.

## 8. Réserve

Les 56 kinds sont **déclarés**, pas **peuplés**. Les familles 1, 2, 5, 6, 7, 8, 9 comptent aujourd'hui 0 instance. E01 est un gain de *capacité de représentation*, pas de contenu. La note de qualité ne progresse qu'à mesure que les epics suivants peuplent ces kinds.
