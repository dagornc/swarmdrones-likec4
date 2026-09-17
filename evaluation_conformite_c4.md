# Évaluation de la conformité C4 — SwarmDrones

> Date : 2026-09-17 · Modèle : `/docker/likec4/workspace` (copie active, servie par le conteneur LikeC4 1.59.2)
> Référentiel : *The C4 model for visualising software architecture* (Simon Brown) — approche de modélisation, pas une norme ISO formelle.
> Méthode : lecture intégrale des sources `.c4` + validation par compilation réelle (`likec4 validate`) + inspection du modèle compilé (JSON).

---

## 0. Conclusion exécutive

Le modèle SwarmDrones **respecte l'esprit et la structure du C4**, avec un écart structurel historique (niveau 2 « conteneurs » fusionné avec le niveau 3 « composants ») **désormais corrigé** par l'ajout d'une vue `conteneurs` dédiée et d'une déclaration de granularité explicite dans la source de vérité.

**Verdict : conforme C4, avec deux réserves assumées** (niveau 4 non couvert — optionnel ; métamodèle étendu au-delà du C4 canonique — choix légitime documenté).

---

## 1. Rappel : ce qu'est le C4

Le C4 (Simon Brown) organise la description d'une architecture en **4 niveaux hiérarchiques de zoom** :

- **N1 — Contexte** : le système dans son environnement (acteurs, systèmes externes).
- **N2 — Conteneurs** : décomposition en unités exécutables/déployables (process, app, data store) et leurs communications.
- **N3 — Composants** : décomposition de chaque conteneur en composants.
- **N4 — Code** : décomposition de chaque composant en classes/modules (optionnel, souvent généré).

Plus des **vues supplémentaires** : System Landscape, Dynamic, Deployment.

Le C4 est une **approche** avec des principes (hiérarchie de zoom, vues par public, une vue = une question), pas une norme avec des critères de validation formels. On évalue donc une **adhésion aux principes**, pas un audit normatif.

---

## 2. Matrice de conformité par niveau

| Niveau C4 | Statut | Éléments du modèle | Vues |
|---|---|---|---|
| **N1 — Contexte** | ✅ Conforme | `operator` (acteur), `radios` (externe), `docSource` | `contexte`, `contexte-amont`, `contexte-aval` |
| **N2 — Conteneurs** | ✅ Conforme *(corrigé)* | Les 4 zones `onboard` / `edge` / `c2` / `cloud` = conteneurs | `conteneurs` *(nouvelle)* |
| **N3 — Composants** | ✅ Conforme | `onboard.*`, `edge.*`, `c2.*`, `cloud.*` (29 composants) | `zone-onboard`, `zone-edge`, `zone-c2`, `zone-cloud` |
| **N4 — Code** | ⚠️ Non couvert (optionnel) | Métamodèle définit `module`, `sourceCode` | aucune (acceptable) |
| **Vues dynamiques** | ✅ Conforme | — | `mission-nominale`, `perte-de-lien`, `perte-de-lien-c2-operateur` |
| **Vue déploiement** | ✅ Conforme | `deployment` (x30, runtimes, zones) | `deploiement-30-plateformes`, `deploymentChain`, `deploymentZones` |
| **Vues transversales** | ✅ Au-delà du C4 | hypothèses, ADR, risques, angles morts, choix technos | `hypotheses`, `decisions`, `riskMatrix`, `blindspotBySeverity`, `tech*` |

---

## 3. Détail par niveau

### N1 — Contexte : conforme
- Le système est situé dans son environnement : acteur humain (`operator`), systèmes externes (`radios`/GNSS/capteurs), document source (`docSource`).
- Les vues de contexte répondent à la question C4 « qui interagit avec le système ? ».
- Bonne pratique : chaque vue documente son **public** et sa **question** (ADR-001 « une vue = une question = un public »).

### N2 — Conteneurs : conforme (corrigé le 2026-09-17)
- **État antérieur** : les 4 zones étaient des frontières (`platform`, `edgeStation`, `c2System`, `cloudSystem`) contenant directement des composants, **sans vue ni déclaration de niveau 2**. Le niveau 2 était fusionné avec le niveau 3.
- **Correction apportée** :
  1. Vue `conteneurs` ajoutée (6 nœuds, 8 relations inter-zones) — vérifiée par compilation et inspection du modèle compilé.
  2. Déclaration de granularité C4 ajoutée dans l'en-tête du `model {` de `architecture.c4` : « les 4 zones SONT les conteneurs du niveau 2 ; les composants sont le niveau 3 ».
- **Vérification** : la vue `conteneurs` expose exactement les 8 relations inter-zones attendues (radios→onboard, onboard↔edge, operator→c2, edge↔c2, edge→cloud, cloud→c2).

### N3 — Composants : conforme et riche
- 29 composants détaillés (technologie, criticité, fréquence, latence, source documentaire).
- Relations typées et exhaustives (sync, flow, radio, command, store, async, safety).
- C'est le niveau le plus abouti du modèle.

### N4 — Code : non couvert (acceptable)
- Le C4 rend ce niveau **optionnel** (souvent généré depuis le code).
- Le métamodèle définit `module` et `sourceCode`, mais aucune vue de niveau code. Non bloquant.

---

## 4. Écarts restants et recommandations

### Écart 1 — Métamodèle étendu au-delà du C4 canonique (assumé)
Le C4 canonique a 4 kinds (person, software system, container, component). Le métamodèle SwarmDrones en a **plus de 40** (system, capability, mission, function, message, drone, sensor, runtime, scientificPaper, etc.).

- **Nature** : extension légitime pour un projet d'ingénierie système multi-domaines (essaim de drones), pas une violation.
- **Recommandation** : documenter explicitement que le C4 est la **colonne vertébrale** (N1-N4) et que les kinds supplémentaires sont des **extensions de qualification** (hypothèses, décisions, risques, matériel, science, world model). La déclaration de granularité ajoutée dans `architecture.c4` le précise déjà pour les kinds qualificateurs.

### Écart 2 — Niveau 4 (code) non couvert
- **Recommandation** : le laisser non couvert tant que le code n'existe pas ; le générer depuis le code quand l'implémentation avancera.

### Écart 3 — Redondance vue `index` / vue `conteneurs`
- Les deux vues ont la même structure (6 nœuds, 8 edges). C'est cohérent avec le C4 (System Landscape vs Conteneurs), mais la distinction est conceptuelle (question posée), pas structurelle.
- **Recommandation** : enrichir la vue `conteneurs` avec les **technologies** des flux (ex. « MQTT/broker » pour edge↔c2) pour la différencier de `index`. Optionnel.

---

## 5. Preuves de vérification (exécution réelle)

| Vérification | Commande | Résultat |
|---|---|---|
| Compilation | `docker exec likec4 likec4 validate /data` | `✓ Valid (17 files)` |
| Rendu vue conteneurs | `likec4 export png -f conteneurs` | `conteneurs.png` généré (464 Ko) |
| Contenu de la vue | inspection du JSON compilé | 6 nœuds, 8 relations inter-zones correctes |

---

## 6. Conclusion

Le modèle SwarmDrones est **conforme au modèle C4** sur les niveaux 1, 2 (corrigé) et 3, avec des vues dynamiques et de déploiement conformes. Les deux réserves (niveau 4 optionnel, métamodèle étendu) sont des choix assumés et documentés, pas des défauts.

**Niveau de confiance de cette évaluation : élevé** (lecture intégrale des sources + validation par compilation réelle + inspection du modèle compilé).
