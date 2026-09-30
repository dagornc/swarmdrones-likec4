# E00 — Audit de l'architecture LikeC4 existante (SwarmDrones)

> Mission SWARM-3D-ARCHITECTURE · Board `swarm-3d-architecture` · Carte `t_5542ae1d`
> Date : 2026-09-15 · Profil : principal (audit contradictoire)
> Source de vérité de cet audit : **le modèle compilé par LikeC4 1.59.2**, pas les fichiers `.c4`.

## 0. Conclusion exécutive

L'existant est **de bonne qualité architecturale mais inexploitable comme base de connaissance machine**. Trois constats dominent :

1. **Aucune relation n'est typée.** La spécification déclare 14 kinds de relations ; **0 sont utilisées**. Les 239 arcs du modèle sont donc des `flow` implicites. C'est le défaut bloquant n°1 : sans typage, aucune extraction automatique de flux, de messages ou de dépendances n'est possible.
2. **Le modèle ne couvre que ~30 % du périmètre cible.** Il décrit correctement le déploiement (onboard/edge/C2/cloud) mais **il n'existe aucun objet de première classe** pour : `message`, `event`, `command`, `telemetry`, `topic`, `channel`, `protocol`, `interface`, `sensor`, `actuator`, `computeNode`, `function`, `capability`, `algorithm` (au sens catalogue complet), `scientificPaper`.
3. **Le modèle est plus riche que ce que le fichier local contient.** `point4/` (validé, exporté, actif) contient 97 éléments et 22 vues ; `architecture.c4` local n'en contenait que 41 éléments et 17 vues. **Régression silencieuse** : un lot complet (produits du marché, algorithmes, risques, angles morts, décisions ouvertes) avait été perdu côté fichier de travail.

> **MISE À JOUR 2026-09-30.** Constat n°3 périmé : la régression a été absorbée, le modèle racine est la tête de version (58 vues, 513 noms qualifiés), et `point4/` est supprimé (commit `72389f7`). Constats n°1 et n°2 : voir les mises à jour de P-01 et P-05.

**Verdict** : ne pas réécrire. **Consolider d'abord** (fait), puis **refonder la spécification** (kinds + relations typées), puis **étendre par lots traçables**. La structure logique existante (zones, composants, hypothèses, ADR) est saine et doit être préservée à l'identique.

**Score de qualité actuel : 31/100** (détail §6). Cible de clôture : ≥ 90/100.

---

## 1. Découverte — organisation réelle du projet

### 1.1 Où vit le modèle (fait établi)

Le **workspace actif** n'est pas le dossier de travail. Vérifié par `docker inspect` :

- Conteneur `likec4` (`ghcr.io/likec4/likec4:1.59.2`), **up**.
- Bind mount : `/docker/likec4/workspace` → `/data` (rw).
- `likec4 validate /data` → **✓ Valid (2 files)**, projet `swarmdrones`.

**Fait critique (état 2026-09-30)** : `/docker/likec4/workspace/*.c4` est **bit-à-bit identique à `point4/*.c4`**, et **diffère de 606 lignes** de `swarmdrones_likec4/architecture.c4`.

Interprétation : `point4/` est la **véritable tête de version**. Le fichier racine était une copie régressée.

> **MISE À JOUR 2026-09-30 — cette section est périmée.** La situation décrite ici a été résolue depuis : le fichier racine a été resynchronisé depuis `point4/`, puis enrichi (58 vues contre 22, 513 noms qualifiés). `point4/` a été **supprimé** (commit `72389f7`) : ses 8 `.md` sources ont été déplacés vers `docs/sources/`, ses 5 `.png` vers `export/point4_v1/`, ses `.c4` supprimés après vérification qu'ils étaient absorbés par le modèle racine. Le modèle actif est désormais la racine, et `likec4 validate` porte sur 20 fichiers source.

### 1.2 Arborescence utile

```
swarmdrones_likec4/
├── architecture.c4        2228 l.  ← modèle (spécification + logique + déploiement)
├── views.c4                        ← 58 vues
├── algorithms.c4                   ← catalogue des 15 algorithmes canoniques
├── hardware.c4                     ← architecture matérielle
├── likec4.config.json              ← projet "swarmdrones"
├── export_likec4.sh                ← procédure d'export (5 leçons capitalisées)
├── docs/sources/                   ← 8 .md sources (ex-point4/, déplacés le 2026-09-30)
├── archive/backups/                ← backup_v1..v21 (4,2 Mo, non versionnés)
├── drawio/ 16 fichiers              ← exports DrawIO
├── png/ 16 fichiers                 ← exports PNG
└── docs/                           ← LIVRABLES DE CETTE MISSION
```

L'historique `backup_v1 → v6 → point4` était **linéaire et non destructif** : chaque lot avait son backup. Les backups sont désormais regroupés dans `archive/backups/` (commit `eb59d0a`).

### 1.3 Conventions déjà en place (à préserver)

- **Identifiants** : `zone.composant` en **camelCase**, point comme séparateur (`onboard.sensorsHAL`, `edge.gateway`). **Stable, lisible, exploitable par machine.** ✔
  - ⚠️ **Piège** : la forme kebab-case (`onboard.sensors-hal`) est **invalide** comme référence LikeC4 — elle n'existe que dans les documents sources. Le libellé affiché peut être en kebab (`'Interfaces capteurs'`), mais l'identifiant technique reste camelCase. Voir `docs/sources/mapping_ids_annexe_v1.md`.
- **Organisation des fichiers** : spécification + modèle + déploiement dans `architecture.c4` ; vues dans `views.c4`. Séparation saine.
- **En-têtes de section** en commentaires ASCII, avec justification et renvoi de section du document source. Rare et précieux.
- **Traçabilité documentaire** : chaque composant porte `metadata.source = '§4.1 onboard.x'`, et il existe une **entité `docSource`** matérialisant le document dans le graphe. C'est un mécanisme de traçabilité réel, pas déclaratif.
- **Hypothèses et décisions comme entités** (H1..H5, ADR-1..5) avec relations d'impact requêtables. **Excellente pratique, à généraliser.**
- **Kinds de criticité** en tags (`safety-critical`, `mission-critical`, `best-effort`, `cloudOnly`) + `styleGroup criticite` produisant la légende native. ✔

---

## 2. Inventaire quantifié

Mesuré sur le **modèle compilé** (`docker exec likec4 likec4 export json`), par `tools/audit_inventory.py`.

### 2.1 Compteurs

- Éléments : **97**
- Relations : **239**
- Vues : **22** (16 élément, 3 dynamiques, 1 déploiement, 2 non exportées en PNG)
- Tags déclarés : **23** · Kinds d'éléments : **13** · Kinds de relations : **14**
- Nœuds de déploiement : `host` uniquement (1 kind, 4 usages)

### 2.2 Éléments par kind

- `component` : 24 — les composants logiciels réels
- `blindspot` : 16 — angles morts (lot 3)
- `risk` : 15 — risques (lot 3)
- `software` : 14 — produits du marché (lot 3)
- `decision` : 9 — 5 ADR tranchées + 4 décisions ouvertes (DE)
- `algorithm` : 7 — familles algorithmiques (lot 3)
- `hypothesis` : 5 — H1..H5
- `external` : 2 (`radios`, `docSource`)
- `operator`, `platform`, `edgeStation`, `c2System`, `cloudSystem` : 1 chacun

### 2.3 Répartition par zone

| Zone | Composants | Contenu |
|---|---|---|
| `onboard` (x30) | 13 | sensorsHAL, perception, autopilot, safety, mission, taskAuction, health, energy, telemetry, linkRadio |
| `edge` (1..N) | 5 | relay, fusion, coordinator, cache, gateway |
| `c2` | 6 | gcs, planner, auth, missionStore, alerting (+1) |
| `cloud` | 4 | twin, analytics, modelRegistry, replayStore |
| Hors zone | 69 | hypothèses, décisions, produits, algorithmes, risques, angles morts |

### 2.4 Vues existantes (22)

Elément : `index`, `contexte`, `contexte-amont`, `contexte-aval`, `paysage-criticite`, `zone-onboard`, `zone-edge`, `zone-c2`, `zone-cloud`, `hypotheses`, `decisions`, `decisionsOuvertes`, `tracabilite`, `techAutopilot`, `techComms`, `techData`, `riskMatrix`, `blindspotBySeverity`.
Dynamiques : `mission-nominale`, `perte-de-lien`, `perte-de-lien-c2-operateur`.
Déploiement : `deploiement-30-plateformes`.

Densité maximale : `deploiement-30-plateformes` (41 nœuds / 127 arêtes) — **illisible en statique**, ce qui est déjà documenté dans le fichier lui-même.

---

## 3. Problèmes identifiés, par criticité

### P-01 — Aucune relation n'est typée · CRITICITÉ BLOQUANTE

**Fait mesuré.** `specification { relationship sync ... flow ... radio ... command ... store ... async ... safety ... depend-on ... justifie ... derives-from ... implemented-by ... alternative-to ... exposed-to ... does-not-cover }` → **14 kinds déclarés, 0 utilisés**.

Les 239 arcs du modèle compilé ont tous `kind: undefined`. Exemple réel :

```c4
onboard.sensorsHAL -> onboard.perception 'flux capteurs' { technology 'Bus capteur' }
```

Le sens réel (flux de données ? commande ? voie de sûreté ?) est **encodé dans une chaîne libre**. Aucun outil ne peut distinguer :
- un appel synchrone d'un ordre préemptif,
- une dépendance de sûreté d'un simple flux de données,
- un `publishes` d'un `subscribes`.

**Conséquence sur l'objectif de mission** : impossible de générer la vue des messages animés (étape 6), impossible de calculer les dépendances logiques, impossible de détecter un cycle, impossible de colorer les flux par criticité de façon automatique.

**Proposition** : rendre le typage **obligatoire** via une passe mécanique sur les 239 arcs (le libellé de l'arc est déjà discriminant dans ~95 % des cas), puis vérification par échantillonnage humain. Fait partie de E01/E03.

### P-02 — Kinds cibles absents du métamodèle · CRITICITÉ BLOQUANTE

**Fait mesuré.** `grep -c 'scientificPaper\|element message\|element sensor' architecture.c4` → 0.

Le métamodèle actuel (13 kinds) **ne peut pas représenter** les objets exigés par la cible :

| Catégorie cible | Kinds requis | Présents |
|---|---|---|
| Système | `system`, `subsystem`, `capability`, `mission` | Non (1 seul `platform`) |
| Fonctionnel | `function`, `process`, `responsibility` | Non |
| Logiciel | `application`, `service`, `component`, `agent`, `module`, `API` | Partiel (`component` seul) |
| Algorithmique | `algorithm`, `strategy`, `policy`, `optimizer`, `planner`, `controller` | Partiel (`algorithm` seul, sans champs) |
| Données | `message`, `event`, `command`, `telemetry`, `state`, `dataset` | **Aucun** |
| Communication | `topic`, `channel`, `protocol`, `interface` | **Aucun** |
| Matériel | `drone`, `sensor`, `actuator`, `computeNode`, `networkDevice`, `groundStation`, `server` | **Aucun** |
| Infrastructure | `host`, `container`, `network`, `runtime`, `middleware` | Partiel (`host` seul) |
| Documentation | `scientificPaper`, `specification`, `standard`, `sourceCode`, `test`, `experiment` | **Aucun** |

**Conséquence** : la communication inter-composants n'existe que comme texte dans les libellés d'arcs. Aucun message n'est un objet. La simulation ne pourra recevoir ni noms de messages, ni fréquences, ni producteurs/consommateurs, ni QoS.

**Proposition** : E01 refond la spécification en 9 familles, E06 crée les objets message/protocole.

### P-03 — Régression silencieuse du fichier de travail · CRITICITÉ HAUTE (corrigée)

**Fait mesuré (état d'origine).** `diff point4/architecture.c4 architecture.c4` → 606 lignes de différence. 56 éléments présents dans `point4` **absents** du fichier racine : 14 produits du marché, 7 algorithmes, 16 angles morts, 15 risques, 4 décisions ouvertes. Idem pour `views.c4` (5 vues, dont `decisionsOuvertes`, `techAutopilot`, `techComms`, `techData`, `riskMatrix`, `blindspotBySeverity`).

**Cause probable** : un profil a patché le fichier racine depuis un état antérieur (backup_v3, 1029 lignes) sans resynchroniser depuis le workspace actif. `architecture.c4.bak` (261 octets) et `architecture.c4.bak_point4` (47 ko) témoignent de manipulations manuelles.

**Risque** : tout travail futur démarrant sur le fichier racine **reperdait un lot entier**. Sans vérification par `diff` contre le mount Docker, la perte serait passée inaperçue (le fichier restait *valide* pour LikeC4).

**Action prise** : état régressé préservé dans `backup_v7_regression/`, puis `architecture.c4` et `views.c4` restaurés depuis `point4/`. **Vérifié identique au workspace actif.**

**Règle à inscrire au mode opératoire** : *toujours comparer le fichier de travail au mount Docker avant de patcher ; toujours valider puis prouver l'identité (`diff`) après écriture.*

> **MISE À JOUR 2026-09-30 — résolu et clos.** La régression a été absorbée : le modèle racine compte désormais **58 vues** (contre 22) et **513 noms qualifiés**, et couvre les 56 éléments autrefois manquants. Les 7 familles algorithmiques de `point4/` ont été remplacées par les objets de catalogue `algXxx` de `algorithms.c4` (correspondance 1:1, métadonnées plus riches : DOI, repository, `executionMode`, `evidenceLevel`). `point4/` est supprimé (commit `72389f7`). La règle de comparaison au mount Docker reste valable.

### P-04 — Aucune source scientifique dans le modèle · CRITICITÉ HAUTE

**Fait mesuré.** `grep -cP '(doi|DOI|arxiv|RFC\s+\d{3,})'` → 5 occurrences, **toutes dans du texte de description**, aucune dans une métadonnée citable. Aucun kind `scientificPaper`. Aucun `link` externe (`grep -cP '^\s*link\s'` → 0). Aucune URL (`grep -c 'https\?://'` → 0).

Pourtant le modèle s'appuie sur des affirmations scientifiques fortes, présentes en prose :
- CBBA (5 mentions) — convergence **non revendiquée sous partition**
- CBF (8 mentions) — évitement de collision
- CRDT/LWW (8 mentions) — coordination sous partition
- DTN / RFC 9171 — store-and-forward (dans `ALR-SWARM30.md`, pas dans le modèle)

**Conséquence** : la « scientific knowledge base » exigée est absente. Aucune affirmation n'est rattachable à une source *depuis le graphe*. Violation directe de la règle « toute affirmation scientifique importante doit pouvoir être reliée à une source ».

**Proposition** : E08, sur production du profil SwarmDrone. **Aucune source ne sera inventée** : les entrées non vérifiables porteront `evidence: unknown` + carte Kanban.

### P-05 — Pas d'architecture matérielle ni de drone de référence · CRITICITÉ HAUTE

**Fait mesuré.** Le kind `platform` est une **frontière de zone** (`onboard = platform 'Plateformes onboard (x30)'`), pas un objet matériel. Il n'existe **aucun** `sensor`, `actuator`, `computeNode`, `flightController`, `companionComputer`.

Les capteurs et actionneurs sont des **phrases** dans `radios` (`external 'Radios / GNSS / Capteurs'`) et dans la description de `onboard.sensorsHAL`.

> **MISE À JOUR 2026-09-30 — traité.** `hardware.c4` existe désormais : il déclare les capteurs (`imu`, `gnss`, `odometry`, `perceptionRel`, `saeSensor`, `healthSensor`), les actionneurs (`propulsion`, `servos`), les nœuds de calcul (`companion`, `flightCtrl`) et les relations matérielles (`hardware.c4:243-254`).

**Conséquence** : l'étape 8 (« modéliser le drone de référence » avec Flight Controller, Companion Computer, Navigation, Perception, Safety Manager, Sensors, Actuators) est **irréalisable** sur le métamodèle actuel. Or c'est la base des 30 instances et des assets Blender.

**Proposition** : E05 crée l'architecture matérielle ; E07 la raccorde en deployment.

### P-06 — Vues dynamiques trop peu nombreuses · CRITICITÉ MOYENNE

**Fait mesuré.** 3 vues dynamiques : `mission-nominale`, `perte-de-lien`, `perte-de-lien-c2-operateur`. La cible en exige **10** (SCN-01..SCN-10).

Manquent intégralement : démarrage de l'essaim, découverte des voisins, création de formation, allocation distribuée, évitement de collision, perte d'un drone, réallocation, perte temporaire de com, retour de com, reconfiguration.

Note : `perte-de-lien` couvre partiellement SCN-08/09 mais **ne montre pas** le comportement de l'essaim (« acteur → message → composant → algorithme → décision → effet sur l'essaim ») : il n'y a **pas d'algorithmes** dans la boucle dynamique, puisque les algorithmes du lot 3 ne sont rattachés à aucun composant de façon exécutable.

**Proposition** : E09 étend les 3 vues existantes (aucune n'est supprimée) et en crée 7 nouvelles.

### P-07 — Nomenclature des identifiants non homogène · CRITICITÉ MOYENNE

**Fait mesuré.** Trois régimes coexistent :

1. **Minuscules pointées** — `onboard.sensorsHAL`, `edge.gateway`, `c2.planner` : **72 éléments, convention à conserver**.
2. **CamelCase préfixé, sans séparateur** — `AlgorithmsTaskAllocationCBBA`, `AutopilotPX4`, `PostgreSQLPostGIS`, `blindspotAM1`, `riskR1` : **52 éléments**. Lisible par un humain, **ambigu pour une machine** (`AlgorithmsPerceptionFusionEKFUKF` : où finit la catégorie, où commence le sujet ?).
3. **Préfixes courts non alignés** — `h1..h5`, `adr1..adr5`, `de1..de4`, `docSource`, `radios`, `n10..n30`.

Aucun identifiant ne respecte le format cible `SYS_ / SUBSYS_ / ALG_ / MSG_ / SW_ / HW_ / PROTO_`. **Et aucune convention n'est écrite.**

**Conséquence** : un consommateur externe (World Model, simulateur) ne peut pas dériver le type d'un objet depuis son identifiant. Les collisions de nommage ne sont pas détectables.

**Risque de migration** : changer les identifiants casse les 239 arcs et 22 vues. **Recommandation : ne pas renommer les identifiants existants** (ils sont déjà stables et référencés) ; **ajouter un champ `metadata.id` normalisé au format cible**, qui devient l'identifiant d'export. Le nom technique LikeC4 reste stable. C'est la seule approche qui respecte « *un changement de nom visible ne doit pas casser l'identifiant technique* ».

### P-08 — Métadonnées hétérogènes et non typées · CRITICITÉ MOYENNE

**Fait mesuré.** 44 clés de métadonnées distinctes, sans schéma : `criticite` (39), `source` (28), `statut` (25), `evidence` (21), `alerte` (16), `gravite` (16), `consequence` (16), `categorie` (15), `probabilite` (15), `impact` (15 — collision avec `impact_si_faux` des hypothèses), `mitigation` (15), `licence` (14), `role` (15), `zone` (14), `frequence` (11), `maturite` (7), `fonction` (7), `robustesse_lien` (7), etc.

Problèmes : `impact` est utilisé avec **deux sens** (gravité d'un risque / impact d'une hypothèse) ; `evidence` mélange valeurs (`HIGH`, `MEDIUM`, `HIGH-existence_LOW-perf`) ; `statut` porte 25 valeurs sur des kinds différents ; aucune clé n'est contrainte par kind.

**Conséquence** : un consommateur ne peut pas valider le modèle automatiquement. Les règles de cohérence (E18) sont inapplicables.

**Proposition** : E01 définit un **schéma de métadonnées par kind** (`docs/metamodel.md`), avec clés réservées et valeurs énumérées. Aucune clé existante n'est supprimée ; les non conformes sont conservées sous un préfixe `x_` (extension libre).

### P-09 — Pas de hiérarchie fonctionnelle ni de capacités · CRITICITÉ MOYENNE

`onboard`, `edge`, `c2`, `cloud` sont des **zones de déploiement**, pas des sous-systèmes fonctionnels. Il n'existe aucun `capability` (ex. « allouer une tâche », « maintenir une formation »), aucun `function`, aucun `mission` objet.

Résultat : le modèle décrit **où les choses tournent**, pas **ce que le système sait faire**. Or le Digital Twin pédagogique a besoin de la couche capacité pour expliquer le comportement.

**Proposition** : E02 crée la couche fonctionnelle **en surcouche** (relations `implements` vers les composants existants, sans déplacer ni renommer quoi que ce soit).

### P-10 — Pas de contrat avec le simulateur, ni World Model, ni métriques · CRITICITÉ MOYENNE

Rien n'existe hors LikeC4 pour : le contrat d'interface simulation (E10), le World Model intermédiaire (E11), les métriques comparables entre algorithmes (E17).

Les 7 algorithmes du lot 3 portent `maturite` et `robustesse_lien`, mais **aucune métrique**, **aucune entrée/sortie**, **aucun paramètre**, **aucun mode d'exécution** (`conceptual`/`emulated`/`simulated`/`executable`), **aucun statut d'implémentation**.

**Proposition** : E04 (champs algorithmes), E10 (contrat), E11 (World Model), E17 (métriques, planifié dans E04/E10).

### P-11 — Vues non exportées et liens de navigation incomplets · CRITICITÉ FAIBLE

- `decisionsOuvertes`, `techAutopilot/Comms/Data`, `riskMatrix`, `blindspotBySeverity` : présentes dans certaines sorties d'export, **absentes de la procédure `export_likec4.sh`** (16 PNG/DrawIO pour 22 vues). Cinq vues ne sont donc jamais exportées par le script officiel.
- 12 `navigateTo` seulement, concentrés sur `zone-*` et `contexte`. Les vues `techAutopilot/Comms/Data`, `riskMatrix`, `blindspotBySeverity` ne sont **atteignables depuis aucune autre vue** : ce sont des feuilles mortes de la navigation.
- `deploiement-30-plateformes` fait 41 nœuds / 127 arêtes, non exploitable en statique (déjà documenté par l'auteur).

**Proposition** : E13 met à jour la procédure d'export ; une carte dédiée ajoute la navigation depuis `index`.

### P-12 — Dette méthodologique : dix-huit scripts ad hoc à la racine · CRITICITÉ FAIBLE

`probe2.py`, `probe3.py`, `probe4.py`, `probe5.py`, `pb.py`, `pb4.py`, `pb12.py`, `diff2.py`, `read_verif.py`, `count_check.py`, `labels_check.py`, `brace_check.py`, `diff_relations.py`, `binom_check.py`, `affectation.py`… Ces scripts de vérification ponctuelle **ne sont pas conservés dans le projet LikeC4** ; ils attestent d'une pratique de vérification réelle (bon signe) mais non capitalisée.

**Proposition** : E12 rassemble les vérifications en une suite `tools/qa/` exécutable et rejouable. Les scripts ad hoc d'origine ne sont pas supprimés du workspace.

---

## 4. Matrice de criticité

Format : impact (I) × probabilité (P) → priorité.

- **P-01** relations non typées — I : bloquant · P : certaine → **P0, traiter en premier**
- **P-02** kinds cibles absents — I : bloquant · P : certaine → **P0**
- **P-03** régression silencieuse — I : haut · P : déjà survenue → **P0, corrigée**
- **P-04** aucune source scientifique — I : haut · P : certaine → **P1**
- **P-05** pas d'architecture matérielle — I : haut · P : certaine → **P1**
- **P-09** pas de couche fonctionnelle — I : moyen · P : certaine → **P1**
- **P-10** pas de contrat simulateur/World Model — I : moyen · P : certaine → **P1**
- **P-08** métadonnées non typées — I : moyen · P : certaine → **P2**
- **P-07** nomenclature non homogène — I : moyen · P : certaine → **P2** (à traiter sans renommage)
- **P-06** seulement 3 vues dynamiques — I : moyen · P : certaine → **P2**
- **P-11** vues non exportées — I : faible · P : certaine → **P3**
- **P-12** scripts ad hoc — I : faible · P : certaine → **P3**

Conclusion : **le modèle n'est pas « à refaire », il est « à typer, compléter et instrumenter »**. La structure en zones, la traçabilité par `metadata.source`, les hypothèses et décisions comme entités, et les tags de criticité sont de vrais actifs à ne pas perdre. Ce qui manque est **le squelette sémantique** (kinds + relations typées) et **les objets non-logiciels** (messages, matériel, algorithmes détaillés, sources).

## 5. Score de qualité détaillé — 31/100

| Critère | Poids | Note | Justification |
|---|---|---|---|
| Validité syntaxique | 10 | **10** | `likec4 validate` → ✓ Valid, 2 fichiers |
| Identifiants uniques | 10 | **8** | 97 éléments, 0 doublon détecté ; format non homogène |
| Type des éléments | 10 | **5** | 13 kinds, mais aucune famille données/com/télécom/matériel |
| Type des relations | 15 | **0** | 14 kinds déclarés, **0 utilisés** — 239 arcs non typés |
| Complétude documentaire | 10 | **7** | descriptions riches + `metadata.source` ; 0 lien externe, 0 source citable |
| Couverture algorithmique | 10 | **2** | 7 familles nommées ; 0 entrée/sortie/paramètre/métrique |
| Couverture messages | 10 | **0** | aucun message objet |
| Couverture matérielle | 10 | **0** | aucun capteur/actionneur/nœud de calcul |
| Couverture déploiement | 10 | **6** | vue 30 plateformes présente ; `host` seul kind, illisible |
| Vues et navigation | 5 | **4** | 22 vues, 12 `navigateTo`, 5 vues feuilles mortes |
| Traçabilité / preuves | 10 | **4** | `metadata.source` et H/ADR réels ; aucune source scientifique |
| **Total pondéré** | **110** | **31/100** | (note ramenée sur 100) |

Objectif de clôture : **≥ 90/100**, mesuré par `tools/qa/quality_gate.py` (E12/E18).

## 6. Ordre de migration retenu

Principe : **rien n'est supprimé, tout est ajouté par surcouche traçable**. Chaque lot est validé par `likec4 validate` + `diff` contre le mount Docker + export PNG de contrôle.

1. **E01 — Métamodèle** : refondre `specification{}` en 9 familles de kinds + 21 relations typées. Aucun élément touché. Réversible.
2. **E03 — Typage des relations** : passe mécanique sur les 239 arcs vers les kinds E01. Gain sémantique immédiat, sans ajout d'objet.
3. **E02 — Architecture fonctionnelle** : capacités et fonctions en surcouche, reliées aux composants par `implements`.
4. **E05 — Architecture matérielle** + **E07 — Deployment** : drone de référence, capteurs, actionneurs, nœuds de calcul, raccordement au déploiement.
5. **E04 — Algorithmes** : enrichissement des 7 existants (entrées/sorties/paramètres/métriques/mode) + ajout des algorithmes manquants (leader election, path planning, réallocation).
6. **E06 — Messages** : 14 messages objets + protocoles + topics + QoS + criticité.
7. E08 (scientifique) · E09 (scénarios) · E10 (contrat) · E11 (World Model) · E13 (doc) · E12 (validation globale).

Justification de cet ordre : E01 débloque tout (sans kinds, on ne peut pas créer de message ni de capteur) ; E03 est le meilleur rapport valeur/risque ; E02/E05/E07 posent la structure que E04/E06 viennent remplir ; E08 alimente les affirmations de E04/E06.

## 7. Écarts avec l'architecture cible, par étape de la mission

- Étape 2 (métamodèle) : **0 % → cible E01**. Bloquant.
- Étape 3 (identifiants) : convention appliquée sur 74 % des éléments, **non documentée**. À formaliser sans renommer.
- Étape 4 (enrichissement scientifique) : **0 %**. Rien à récupérer dans le modèle.
- Étape 5 (algorithmes objets) : ~20 %. 7 familles nommées, aucun champ exploitable.
- Étape 6 (messages) : **0 %**. Bloquant pour la simulation.
- Étape 7 (logique/physique) : ~50 %. Zones séparées, deployment présent, mais **pas de matériel**.
- Étape 8 (drone de référence) : **0 %**.
- Étape 9 (30 instances) : ~40 %. Vue de déploiement à 30 plateformes, pas de génération paramétrique.
- Étape 10 (vues hiérarchiques) : ~70 %. 22 vues en place, navigation incomplète.
- Étape 11 (vues dynamiques) : **30 %**. 3 sur 10.
- Étape 12 (références scientifiques) : **0 %**.
- Étape 13 (contrat simulateur) : **0 %**.
- Étape 14 (World Model) : **0 %**.
- Étape 15 (métadonnées 3D) : **0 %** (catégories absentes) — à apporter par E01/E11.
- Étape 16 (modification d'algorithmes A/B/C) : **0 %**.
- Étape 17 (métriques) : **0 %**.
- Étape 18 (QA) : outils `probe*.py` ad hoc, **non capitalisés**.

**Avancement global estimé : 22 %** de l'architecture cible, avec des fondations saines mais un squelette sémantique manquant.

---

*Fin du rapport E00. Carte `t_5542ae1d` → REVIEW puis DONE après validation du plan de migration par le board.*
