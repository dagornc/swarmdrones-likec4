# Audit — Dossier « 03 · Architecture » (menu gauche vertical)

> Date : 2026-09-21 · Périmètre : les vues LikeC4 du dossier `03 · Architecture`
> Source de vérité : le modèle compilé (`likec4 validate` → ✓ Valid, 18 fichiers)
> Méthode : inventaire des vues du dossier, croisement avec les 4 dimensions
> d'architecture demandées (logicielle, fonctionnelle, applicative, matérielle).

## 0. Conclusion exécutive

Le dossier `03 · Architecture` contient **12 vues**. Il couvre correctement le
**contexte**, les **conteneurs**, les **zones** et la **communication**, mais il
est **incomplet sur 3 des 4 dimensions d'architecture** demandées :

- **Architecture logicielle** — *absente* en tant que vue dédiée.
- **Architecture applicative** — *absente* (le kind `application` n'est utilisé
  que pour les consommateurs du modèle ; le kind `service` est déclaré mais
  **jamais utilisé**).
- **Architecture matérielle** — *existante mais mal placée* : la vue
  `hardwareArchitecture` vit dans `99 · Compléments`, pas dans `03 · Architecture`.
- **Architecture fonctionnelle** — *partielle* : `capabilityMap` ne montre que
  les 8 capacités (liste plate), sans la décomposition capacité → fonction →
  composant qui existe pourtant dans `functional.c4`.

**Verdict** : 4 schémas manquants à produire, tous plaçables dans
`03 · Architecture` sans casser l'existant (ajout par surcouche, aucune
suppression, aucun renommage).

## 1. Inventaire des vues existantes du dossier

| # | id de vue | Titre | Dimension couverte |
|---|---|---|---|
| 1 | `contexte-amont` | Contexte amont — externes, Onboard, Edge | Contexte |
| 2 | `contexte-aval` | Contexte aval — Edge gateway, C2, Cloud | Contexte |
| 3 | `contexte` | Contexte (synthèse) | Contexte |
| 4 | `conteneurs` | Conteneurs (niveau 2) | Conteneurs |
| 5 | `zone-onboard` | Zone Onboard (x30) | Zone |
| 6 | `zone-edge` | Zone Edge | Zone |
| 7 | `zone-cloud` | Zone Cloud | Zone |
| 8 | `communicationArchitecture` | Architecture de communication — canaux | Communication |
| 9 | `messageArchitecture` | Architecture des messages — 13 messages | Communication |
| 10 | `criticalMessages` | Messages critiques | Communication |
| 11 | `capabilityMap` | Carte des capacités — 8 capacités, 19 fonctions | Fonctionnel (partiel) |
| 12 | `worldModelMap` | World Model — entités, zones, catégories | World Model |

**Remarque** : `zone-c2` existe mais est classée dans `02 · Parcours`
(« GCS — supervision et autorité humaine »). Ce n'est pas un défaut, mais cela
signifie que le dossier `03 · Architecture` ne contient que **3 des 4 zones**.

## 2. Matrice de couverture par dimension

| Dimension | Vue dédiée dans `03` | Éléments du modèle disponibles | Verdict |
|---|---|---|---|
| **Logicielle** | ❌ aucune | 24 `component`, 14 `software` | **MANQUANTE** |
| **Fonctionnelle** | ⚠️ `capabilityMap` (plate) | 8 `capability`, 19 `function` | **PARTIELLE** |
| **Applicative** | ❌ aucune | 5 `application` (consommateurs), 0 `service` | **MANQUANTE** |
| **Matérielle** | ❌ (vue en `99 · Compléments`) | 1 `drone`, 6 `sensor`, 2 `actuator`, 1 `flightController`, 1 `companionComputer`, 2 `networkDevice`, 1 `computeNode` | **MAL PLACÉE** |

## 3. Écarts détaillés

### G-1 — Architecture logicielle absente · SÉVÉRITÉ HAUTE

**Fait mesuré.** Aucune vue du dossier `03` ne montre la structure logicielle
(composants, couches, dépendances). Les composants n'apparaissent que
*incidemment* dans les vues de zone (`zone-onboard`, `zone-edge`, `zone-cloud`).

**Conséquence.** Un lecteur ne peut pas répondre à « comment le logiciel est-il
structuré ? » ni « quelles sont les dépendances entre composants ? » depuis le
dossier Architecture. La vue `conteneurs` s'arrête au niveau 2 (zones) ; le
niveau 3 (composants) n'a pas de vue d'ensemble.

**Proposition.** Créer `softwareArchitecture` : les 24 composants groupés par
zone, avec leurs dépendances typées (`flow`, `commands`, `runsOn`), et la
frontière safety/mission/best-effort visible.

### G-2 — Architecture applicative absente · SÉVÉRITÉ HAUTE

**Fait mesuré.** Le kind `application` est déclaré dans le métamodèle et utilisé
**5 fois** — mais uniquement pour les *consommateurs* du modèle
(`consSimulator`, `consBlender`, `consWeb3D`, `consPedago`, `consTwin` dans
`simulation.c4`). Le kind `service` est déclaré mais **jamais utilisé** (0
occurrence).

**Conséquence.** Il n'existe aucune vue de la couche applicative : quelles
applications composent le système, quels services elles exposent, comment elles
s'articulent. C'est pourtant la couche qui répond à « qu'est-ce qui tourne, où,
et avec quelle interface ? ».

**Proposition.** Créer `applicationArchitecture` : les applications du système
(consommateurs + les briques applicatives identifiables : GCS, planner,
twin, analytics, replay-store) et leurs interfaces. **Aucune application ne sera
inventée** : seules les briques déjà présentes dans le modèle seront
représentées, avec un statut explicite pour les trous.

### G-3 — Architecture matérielle mal placée · SÉVÉRITÉ MOYENNE

**Fait mesuré.** La vue `hardwareArchitecture` (titre
`99 · Compléments / Architecture materielle — drone de reference`) existe et est
complète (chaîne capteurs → calcul → actionneurs). Mais elle est classée dans
`99 · Compléments`, pas dans `03 · Architecture`.

**Conséquence.** Incohérence de navigation : une architecture matérielle n'est
pas un « complément », c'est une dimension d'architecture de premier rang. Le
lecteur qui cherche l'architecture matérielle dans `03` ne la trouve pas.

**Proposition.** Créer une vue `hardwareArchitecture` **dans** `03 · Architecture`
(la vue existante en `99` n'est pas supprimée — voir §4 sur la duplication).

### G-4 — Architecture fonctionnelle partielle · SÉVÉRITÉ MOYENNE

**Fait mesuré.** `capabilityMap` inclut les 8 capacités **sans leurs relations**
(la vue ne fait que `include capFly, capPerceive, ...`). Les 19 fonctions et les
relations `realizes` (capacité → fonction → composant) existent dans
`functional.c4` mais ne sont visibles dans **aucune** vue du dossier `03`.

**Conséquence.** La décomposition fonctionnelle — le cœur du « pourquoi / quoi »
— n'est pas lisible. La vue actuelle est une liste, pas un schéma.

**Proposition.** Créer `functionalArchitecture` : la chaîne complète
capacité → fonction → composant, avec les 8 capacités et leurs 19 fonctions.

## 4. Décisions de conception retenues

1. **Ajout par surcouche, aucune suppression.** Les 12 vues existantes restent
   intactes. Les 4 nouvelles vues sont ajoutées.
2. **Pas de duplication de la vue matérielle.** Plutôt que de dupliquer
   `hardwareArchitecture`, la nouvelle vue `03` est une **vue de synthèse**
   (`hardwareArchitectureOverview`) qui inclut le drone de référence et sa
   chaîne, avec `navigateTo` vers la vue détaillée existante en `99`.
3. **Aucun élément inventé.** Les 4 vues n'utilisent que des éléments déjà
   présents dans le modèle. Les trous (ex. absence de `service`) sont
   **nommés**, pas comblés par des objets fictifs.
4. **Nommage.** Les ids suivent la convention existante (camelCase descriptif,
   comme `communicationArchitecture`, `messageArchitecture`).
5. **Titres.** Préfixe `03 · Architecture \/` pour apparaître dans le bon
   dossier du menu gauche vertical.

## 5. Livrables

| Vue | id | Dimension | Statut | Contenu vérifié |
|---|---|---|---|---|
| Architecture logicielle — composants et dépendances | `softwareArchitecture` | Logicielle | ✅ créée | 28 nœuds, 43 arêtes |
| Architecture applicative — applications et interfaces | `applicationArchitecture` | Applicative | ✅ créée | 17 nœuds, 15 arêtes |
| Architecture fonctionnelle — capacités, fonctions, composants | `functionalArchitecture` | Fonctionnelle | ✅ créée | 47 nœuds, 67 arêtes |
| Architecture matérielle — synthèse (drone de référence) | `hardwareArchitectureOverview` | Matérielle | ✅ créée | 21 nœuds, 23 arêtes |

## 6. Vérification

- `likec4 validate /data` → **✓ Valid (18 fichiers, 0 erreur)**
- `likec4 export json` → les 4 vues sont présentes et **non vides**
  (nœuds/arêtes ci-dessus), toutes classées sous `03 · Architecture /`.
- `tools/qa/quality_gate.py` → **99/100, GATE: PASS** (66 vues, 0 vide,
  30 `navigateTo`).
- `git diff --stat` → `views.c4 | 174 +++++` (ajout seul, aucune suppression).

*Fin de l'audit.*
