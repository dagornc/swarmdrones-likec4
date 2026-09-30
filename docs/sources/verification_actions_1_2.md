# Vérification et corrections — Actions 1 & 2 (2026-09-15)

## Objet

Vérification indépendante par le profil `swarmdrone` du contenu généré
(101 relations + 4 décisions en attente), puis répercussion des corrections
dans le modèle LikeC4.

## Méthode

1. **Production** par `swarmdrone` : `relations_swarmdrone.md` (101 relations),
   `decisions_swarmdrone.md` (4 fiches DE).
2. **Injection** dans le modèle, avec conversion (neutralisation des
   apostrophes, extraction en blocs `.c4`).
3. **Vérification contradictoire** par `swarmdrone` : `verification_swarmdrone.md`
   (469 lignes) — l'auteur passe vérificateur, cherche activement ce qui est faux.
4. **Vérification objective** par l'orchestrateur : diff proposition/injection,
   couverture, comptages.
5. **Corrections** appliquées puis revalidées.

## Contrôles objectifs (orchestrateur)

- Fidélité : **101/101 relations injectées, 0 libellé altéré** (diff de
  multi-ensembles, pas de relecture).
- Couverture : **15/15 risques et 16/16 angles morts** reliés. **0 orphelin**.
- Identifiants : **202/202 références valides**, 0 inconnue.
- Validation : `✓ Valid (2 files)` avant et après corrections.

## Écarts trouvés par la vérification contradictoire

### Bloquants

- **B1 — les 4 décisions DE-01..04 étaient invisibles dans les vues.**
  La vue `decisions` listait explicitement `adr1..adr5`. Un livrable invisible
  dans la seule vue censée le présenter. *Confirmé aussi par l'orchestrateur.*

- **B2 — 4 relations `de* -> riskR*` affirmaient un effet non advenu.**
  Libellés « leve », « borne », « reduit », « traite » alors que les décisions
  sont au statut `ouverte`. Une décision non prise ne lève rien. *Erreur
  introduite par l'orchestrateur à l'injection, absente des propositions.*

### Majeurs

- **M1 — les libellés de conformité se lisent comme de la causalité.**
  Le type de relation est `exposed-to` pour tous, y compris les liens
  juridiques/réglementaires. Non corrigé (voir décision ci-dessous).

- **M2 — R-14 / AM-16 (facteur humain) reliés à aucun acteur humain.**
  L'acteur `operator` existe dans le modèle, est porteur de H5, et subit
  réellement la charge. Absent des relations. *Auto-critique honnête de
  swarmdrone : il avait confondu « pas dans ma liste » avec « n'existe pas ».*

### Mineurs

- **m1 — 16 libellés à élision neutralisée** (`d evitement`, `d un`, `l horloge`).
  Cosmétique sauf `detection d evitement in extremis`, réellement trompeur
  (se lit « on a détecté un évitement »).
- **m2 — un libellé dupliqué** (`campagnes rejouables pour l echelle` sur
  `cloud.replayStore`, deux sources). Non bloquant, validation OK.
- **m3 — décompte « 101 » non explicité** (87 + 14). Pas de perte constatée.

## Corrections appliquées

| Correction | Écart | Action |
|---|---|---|
| C1 | B1 | Vue `decisions` scindée : `decisions` (ADR tranchées) + `decisionsOuvertes` (DE) ; `de1..de4` ajoutées à `tracabilite` |
| C2 | B2 | 4 relations reformulées au conditionnel : `conditionne la levee du...` |
| C3 | M2 | Ajout `operator -> riskR14` et `operator -> blindspotAM16` |
| C4 | m1 | Libellé corrigé : `detection d urgence pour evitement` |

### Décisions de l'orchestrateur

- **C1 : scission en deux vues** plutôt que l'ajout simple proposé par
  swarmdrone. Motif : après ajout, la vue mesurait 2502×6382 px (ratio 0,39,
  layout saturé). Après scission : `decisionsOuvertes` 3858×2228 (ratio 1,73,
  sain). Même méthode que la scission de `techChoices` en 3 vues.
- **C2 : reformulation retenue**, pas la suppression. Motif : conserver
  `quel risque est conditionné par quelle décision` est informatif ; c'est la
  formulation fautive qui était le problème, pas le lien. La recommandation
  préférée de swarmdrone (supprimer) est plus stricte mais perd l'information.
- **C5 (type `concerns` distinct) : NON appliquée.** Motif : correction
  structurante touchant 8 relations, sans valeur décisionnelle immédiate, et
  coût de régression élevé. Classée en amélioration optionnelle. M1 reste une
  réserve documentée.

## Réserves non levées

- **M1** : les 8 relations de conformité restent typées `exposed-to`. Un lecteur
  non averti peut lire de la causalité technique. Réserve documentée.
- Rendu graphique de `decisions` (2426×4048, ratio 0,60) reste vertical.
- Sources normatives primaires (COLREGs) non consultées dans cette session.
- Licences non reconfirmées dans cette session (proviennent de l'annexe v1).

## État final du modèle

- `architecture.c4` : 83 254 octets, `✓ Valid`
- Éléments : 14 software, 7 algorithm, 15 risk, 16 blindspot, 5 hypothesis, 9 decision
- Décisions : **5 tranchées** (ADR-1..5, `acceptee`) + **4 ouvertes** (DE-01..04)
- Relations : **239** — 0 orphelin sur risques, angles morts et décisions
- `views.c4` : **22 vues**, dont `decisionsOuvertes` (nouvelle)

## Artefacts

- `/home/hermesagent/workspace/relations_swarmdrone.md` — 101 relations proposées
- `/home/hermesagent/workspace/decisions_swarmdrone.md` — 4 fiches DE
- `/home/hermesagent/workspace/verification_swarmdrone.md` — revue contradictoire
- `/home/hermesagent/workspace/verification_actions_1_2.md` — ce document
- Sauvegardes : `backup_v1` .. `backup_v6`
