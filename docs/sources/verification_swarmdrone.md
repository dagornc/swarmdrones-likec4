# Vérification du contenu généré — revue contradictoire (profil swarmdrone)

Posture : je suis l'auteur des propositions (Action 1 et Action 2) et je passe
vérificateur. J'ai cherché activement ce qui est FAUX, pas ce qui me donne
raison. Date : 2026-09-15 (UTC).

## Périmètre et méthode effective

Ce qui a été réellement vérifié par exécution, pas par relecture :

- Diff automatique proposition -> injection : les 101 relations des Parties A/B
  de `relations_swarmdrone.md`, extraites par regex, comparées ligne à ligne aux
  relations réellement présentes dans `/docker/likec4/workspace/architecture.c4`.
  Résultat : **101/101 présentes, 0 libellé modifié, 0 relation perdue**
  (multi-ensembles strictement égaux sur les libellés).
- Décomposition confirmée : **87 relations composant -> élément** et
  **14 relations élément -> hypothèse/ADR**, soit 101. Les compteurs déclarés
  dans le modèle (`// -- composant_vers_element (87)`, `// -- element_vers_reference (14)`)
  concordent exactement avec mes propositions : aucune relation n'a été
  silencieusement écartée à l'injection.
- Couverture : les **15 risques** et les **16 angles morts** ont chacun au moins
  une relation (min 2, max 3 par élément). Aucun élément orphelin.
- Placement structurel : contrôle d'équilibre des accolades par script. Les
  relations injectées et `de1..de4` sont bien dans le bloc `model { }` (ouvert
  ligne 289, fermé ligne 1548), au même niveau que les `adr1..adr5` préexistants.
  Pas d'imbrication illégale dans une boundary.
- Validation LikeC4 réelle : `npx likec4 validate` -> **✓ Valid (2 files)**.
  Le modèle compile. Ce n'est pas une affirmation de ma part, c'est la sortie
  de l'outil.
- Vérification de neutralisation des apostrophes : mes libellés d'origine
  étaient **déjà** sans apostrophe (contrainte de mission, respectée dès la
  rédaction). Le texte injecté est identique au texte proposé au caractère près.
  Aucune déformation par neutralisation. Ce point de la mission (Verification 1)
  est donc un **non-événement** : le risque était réel mais ne s'est pas matérialisé.

Réserves de méthode, à assumer :

- Je n'ai pas exécuté l'export des vues ni inspecté le rendu graphique. Je
  vérifie la présence et la sémantique des relations in abstracto ; qu'une
  relation sature ou non une vue donnée n'a été vérifié que par lecture des
  `include` de `views.c4`, pas par rendu.
- L'affirmation sur les COLREGs (règle d'évitement normative imposée aux USV)
  reste reprise du texte du modèle ; **je ne l'ai pas reconfirmée en source
  normative primaire** dans cette session.

---

## Synthèse

**Le contenu injecté est fidèle et correct pour l'Action 1 (OUI), et correct
dans son existence mais avec des réserves réelles pour l'Action 2 et les vues
(OUI AVEC RÉSERVES).**

Décompte des écarts trouvés :

| Gravité | Nombre | Objet |
|---|---|---|
| Bloquant | 2 | (B1) les 4 décisions sont invisibles dans les vues dédiées aux décisions ; (B2) 4 relations Action 2 affirment que les décisions *résolvent* les risques, ce qui est faux et contredit le statut « ouverte » |
| Majeur | 2 | (M1) libellés de conformité lisibles comme causalité ; (M2) le risque R14 / AM16 n'est relié à aucun acteur `operator`, pourtant présent dans le modèle |
| Mineur | 3 | (m1) 16 libellés à élision neutralisée deviennent ambigus ; (m2) un libellé dupliqué ; (m3) mon propre compte « 101 » n'explicite pas 87+14 |

Aucun écart de fidélité de conversion : **la conversion n'a trahi aucune de mes
propositions**. Les écarts qui existent sont des erreurs de conception qui
étaient **déjà dans mes propositions** (donc ma responsabilité d'auteur) ou des
choix d'intégration de l'orchestrateur (Action 2), pas des pertes de conversion.

---

## Écarts bloquants

### B1 — Les 4 décisions DE-01..DE-04 sont dans le modèle mais ABSENTES des vues qui doivent les rendre

C'est le défaut le plus sérieux et il n'est pas dans mon texte : il est dans
l'intégration.

`views.c4` ligne 534-535 :

```
    include adr1, adr2, adr3, adr4, adr5
    include adr1 -> *, adr2 -> *, adr3 -> *, adr4 -> *, adr5 -> *
```

et ligne 559 (`view tracabilite`) :

```
    include h1, h2, h3, h4, h5, adr1, adr2, adr3, adr4, adr5
```

La vue s'appelle littéralement
`title 'Decisions d architecture (ADR-1..ADR-5) et ce qu elles justifient'`
et son `description` promet « **Mémoire des choix** ». Or elle liste
explicitement `adr1..adr5` : `de1..de4` n'y figurent pas, et le
`include adr1 -> *` ne les tire pas transitivement puisque `de` n'est pas
atteignable depuis `adr*` (les relations injectées vont dans l'autre sens :
`blindspotAM* -> de*`, et `adr2` est cible et non source de `de`).

**Conséquence concrète :** les 4 décisions ouvertes — l'objet même de
l'Action 2 — sont invisibles dans la seule vue censée présenter les décisions,
et invisibles dans la vue de traçabilité. Le livrable existe dans le modèle,
mais l'utilisateur qui ouvre la vue « Décisions » ne les voit pas. Une décision
non vue est une décision non prise.

C'est d'autant plus trompeur que la vue de traçabilité est décrite comme le
« contrôle de couverture » ; elle affichera « couvert » alors que 4 décisions
ouvertes manquent.

### B2 — Les 4 relations `de* -> riskR*` affirment que les décisions résolvent les risques (FAUX)

Injecté lignes 1543-1546 :

```
  de1 -> riskR7 'leve le conflit de licence'
  de2 -> riskR3 'borne la validation d echelle'
  de3 -> riskR2 'reduit la surface de prise de controle'
  de4 -> riskR1 'traite la contention radio a 30 agents'
```

Cette formulation est **fausse** pour trois raisons qui se cumulent :

1. Les quatre décisions sont au statut `metadata { statut 'ouverte' }`. Une
   décision ouverte **ne lève rien**, **ne borne rien**, **ne réduit rien**,
   **ne traite rien**. Le libellé décrit un effet qui n'a pas eu lieu.
   `leve` (au présent, accompli) est une affirmation de résultat.
2. Cela contredit frontalement ma propre réserve de la Partie C de
   `relations_swarmdrone.md`, où j'ai écrit que ces sujets sont des
   « relations de conformité, pas de causalité technique ». Ici l'orchestrateur
   (ou moi, mais ce n'est pas dans mon fichier) a produit exactement la
   causalité technique que j'avais explicitement refusée.
3. Le registre de risque du modèle distingue mitigation (ce qui traite) et
   risque. Confondre une décision *en attente* avec sa mitigation inverse le
   sens de la traçabilité : on lit « R-1 est traité » alors que R-1 reste
   `criticite 'critique'` sans décision prise.

Le sens correct est l'inverse : le risque **appelle** une décision, il ne la
reçoit pas. La paire de relations Action 2 est donc en partie redondante et en
partie fausse — `blindspotAM3 -> de4` dit déjà correctement « appelez une
décision », et `de4 -> riskR1` déforme cela en « décision = remède appliqué ».

Nota : ce défaut est le seul écart où je dois être dur avec l'intégration, mais
je ne peux pas prouver que ce n'est pas moi : le fichier `decisions_swarmdrone.md`
ne contient **aucune** relation `de -> risque`. Ces 4 lignes ont donc été
introduites à l'injection. Je les signale comme à corriger sans désigner
unilatéralement la main.

---

## Écarts majeurs

### M1 — Les libellés de « conformité » sont lisibles comme de la causalité technique

Point demandé explicitement par la mission (Verification 3). Ma Partie C
distingue soigneusement quatre familles de relations non causales (programme,
juridique, réglementaire, spécification transverse, facteur humain). **Cette
distinction n'apparaît nulle part dans le libellé injecté.** Exemples où le
libellé est plus fort que ce que le modèle autorise :

- `c2.gcs -> riskR6 'configuration des zones soumise aux autorisations'` :
  la formulation est neutre et acceptable. Mais lue comme une arête de graphe
  typée `exposed-to`, elle suggère que `c2.gcs` *cause* le risque R6. La source
  du risque R6 est le cadre légal BVLOS/COLREGs, hors modèle. Rien dans le
  libellé ne signale « point de conformité, pas cause ».
- `edge.coordinator -> riskR6 'deconfliction locale sans regle normative'` :
  libellé décrivant une *absence* (absence de règle) reliée à un risque par une
  arête `exposed-to`. La lecture « le coordinateur est exposé parce qu'il lui
  manque une règle » est défendable ; mais la lecture « le coordinateur est
  exposé » est fausse : ce n'est pas lui qui subit, c'est l'exploitation. Un
  lecteur presse conclut à une cause technique.
- `onboard.autopilot -> riskR7 'socle de vol copyleft ou permissif'` : c'est
  une **description du choix**, pas une exposition. Un autopilote n'est pas
  « exposé » à un choix de licence : c'est le *programme* qui est exposé. Le
  composant est le siège de la contrainte, comme je l'avais écrit en Partie C.
- `cloud.replayStore -> riskR7 'stockage objet AGPLv3 impose une revue'` et
  `cloud.analytics -> riskR7 'chaines AGPL et source-available cote cloud'` :
  même problème. Ce sont des faits de brique (MinIO AGPLv3, Grafana
  AGPL-3.0-only, bus à caveat Confluent), pas des expositions de composants
  d'architecture.

Tous ces cas sont **techniquement défendables en tant que localisation**
(où la contrainte atterrit), mais le graphe les type tous en `exposed-to`
(`title 'Est expose a'`, ligne 259-264 de `architecture.c4`). Le libellé ne
peut donc pas rattraper le type : le type porte le sens. **Soit on assume que
la relation signifie « siège de la contrainte », soit il faut un type distinct.**
Aujourd'hui le modèle ne dit ni l'un ni l'autre, et un lecteur non averti lira
de la causalité.

Recommandation de fond (pas cosmétique) : soit renommer les 8 relations
juridiques/programmatiques/réglementaires avec un préfixe explicite
(`point de conformite : ...`, `siege de la contrainte : ...`), soit créer un
`relationship concerns` distinct de `exposed-to`. Je préconise la seconde,
parce qu'elle rend la distinction **requêtable** au lieu de la confier à la
lecture d'un libellé.

### M2 — Le risque R14 / AM16 n'est relié à aucun acteur humain, alors que l'acteur existe

Le modèle déclare un élément `operator` (ligne 924 de `architecture.c4`) :

```
  operator -> c2.gcs 'supervise et autorise les actions critiques' { ... autorite 'humaine (H5)' }
```

`operator` est un **acteur de premier plan**, safety-critical, porteur explicite
de H5. Or :

- R-14 est « Charge C2 humaine excessive sous incertitude ». La charge est
  portée *par l'opérateur*. Mes relations vont vers `c2.gcs` (le poste) et
  `c2.alerting` (les alarmes), jamais vers l'acteur qui subit la charge.
- J'avais écrit en Partie C, point 6, « l'opérateur lui même est un acteur, pas
  un composant d'architecture. Je n'ai pas créé de relation vers un composant
  d'adaptation de charge, car il n'en existe pas dans les 24 composants. »

Ce raisonnement est **partiellement faux** : la mission imposait de relier les
risques aux « 15 risques / 16 angles morts » *et*, pour R14, l'acteur
`operator` **existe déjà dans le modèle** — il n'était simplement pas dans la
liste des 24 composants qu'on m'a donnée. J'ai confondu « pas dans ma liste »
avec « n'existe pas ». C'est l'angle mort de ma propre analyse que je dois
reconnaître.

Conséquence : la relation la plus importante de R-14/AM16 — « l'autorité
humaine H5 est saturée à 30 agents » — est absente. `operator -> riskR14` et
`operator -> blindspotAM16` manquent.

---

## Écarts mineurs

### m1 — 16 libellés deviennent ambigus après neutralisation de l'élision

La mission (Verification 1) demande si un libellé a été *changé de sens* par
la suppression des apostrophes. Réponse : **non, aucune déformation**, parce
que mes libellés étaient déjà sans apostrophe. **Mais** cette contrainte de
rédaction a produit, de mon fait, 16 libellés qui se lisent mal en français
correct. Le pire cas :

- `onboard.perception -> riskR9 'detection d evitement in extremis'` : se lit
  naturellement « détection d'évitement » (= on a détecté un évitement, ce qui
  n'a pas de sens) alors que le sens visé est « détection **pour** l'évitement
  in extremis ». Le libellé est ambigu au point d'être trompeur.
- `onboard.taskAuction -> blindspotAM10 'transfert de tache sans regle d autorite'`
  et `onboard.taskAuction -> riskR15 'attribution sans regle d autorite inter domaines'` :
  « d autorite » se lit aussi bien « d'autorité » (correct) que « d'autorité »
  collé au mot suivant ; ambiguïté faible mais réelle.
- `c2.gcs -> blindspotAM16 'charge d un operateur sur 30 agents non evaluee'` :
  « d un » est laid et frôle la faute de lecture.

Famille complète des 16 cas (tokens `d X` / `l X` issus d'élision) :
`d echelle` (×2), `d evitement` (×2), `d un`, `l horloge`, `d energie` (×2),
`d autorite` (×2), `d horloge`, `l autopilote`, `l energie`, `d agent` (×2).
Gravité : cosmétique, sauf `detection d evitement in extremis` qui est
réellement trompeur.

### m2 — Un libellé dupliqué

`campagnes rejouables pour l echelle` apparaît deux fois, sur la même cible
`cloud.replayStore`, mais pour deux sources différentes (`riskR3` et
`blindspotAM5`). C'est cohérent sémantiquement (R-3 et AM-5 sont deux
formulations du même problème d'échelle), mais l'unicité locale des libellés
dans une vue n'est pas garantie — je l'avais moi-même signalé comme
`Non verifie` en Partie D, point 4. After vérification : la duplication **ne
casse pas** la validation LikeC4 (✓ Valid), donc ce n'est pas bloquant. À
garder par cohérence, ou à différencier si une future vue exige l'unicité.

### m3 — Mon propre décompte « 101 » n'explicitait pas 87 + 14

Le fichier annonce « 101 relations » sans dire qu'il s'agit de 87 relations
composant -> élément et 14 relations élément -> référence. L'orchestrateur a
retrouvé la décomposition exacte (les commentaires du modèle le prouvent), donc
**aucune perte** ; mais l'ambiguïté de mon décompte a coûté une vérification.
À documenter pour la prochaine itération.

---

## Corrections proposées (prêtes à injecter)

### C1 — Faire apparaître les 4 décisions dans les vues (corrige B1)

Dans `/docker/likec4/workspace/views.c4`, vue `decisions` (après ligne 534) :

```
    include adr1, adr2, adr3, adr4, adr5
    include adr1 -> *, adr2 -> *, adr3 -> *, adr4 -> *, adr5 -> *
    include de1, de2, de3, de4
    include blindspotAM1 -> de1, blindspotAM5 -> de2, blindspotAM7 -> de3, blindspotAM3 -> de4
```

et adapter le `title` / `description` pour annoncer aussi les décisions
**ouvertes** (ADR tranchées + DE en attente), par exemple :

```
    title 'Decisions d architecture : ADR-1..5 (tranchees) et DE-01..04 (ouvertes)'
```

Dans la vue `tracabilite` (ligne 559), ajouter `de1, de2, de3, de4` à la liste
des éléments tracés :

```
-    include h1, h2, h3, h4, h5, adr1, adr2, adr3, adr4, adr5
+    include h1, h2, h3, h4, h5, adr1, adr2, adr3, adr4, adr5, de1, de2, de3, de4
```

### C2 — Corriger les 4 relations Action 2 fausses (corrige B2)

Le sens « décision = remède appliqué » est faux. Deux options, je recommande la
seconde :

Option retenue si l'on garde le lien : reformuler au conditionnel et au futur,
sans accompli.

```
-  de1 -> riskR7 'leve le conflit de licence'
+  de1 -> riskR7 'conditionne la levee du conflit de licence'
-  de2 -> riskR3 'borne la validation d echelle'
+  de2 -> riskR3 'conditionne la borne de validation d echelle'
-  de3 -> riskR2 'reduit la surface de prise de controle'
+  de3 -> riskR2 'conditionne la reduction de la surface de prise de controle'
-  de4 -> riskR1 'traite la contention radio a 30 agents'
+  de4 -> riskR1 'conditionne le traitement de la contention radio a 30 agents'
```

Option préférée : **supprimer ces 4 relations source, car elles sont
redondantes**. La ligne `blindspotAM3 -> de4 'architecture radio a choisir apres budget'`
porte déjà correctement l'appel de décision. Une arête `de -> risk` inverse le
sens de la traçabilité (le risque n'est pas la cible d'un remède non appliqué).

```
-  de1 -> riskR7 'leve le conflit de licence'
-  de2 -> riskR3 'borne la validation d echelle'
-  de3 -> riskR2 'reduit la surface de prise de controle'
-  de4 -> riskR1 'traite la contention radio a 30 agents'
```

### C3 — Ajouter les relations manquantes vers `operator` (corrige M2)

Dans `/docker/likec4/workspace/architecture.c4`, section Action 1 :

```
+  operator -> riskR14 'charge humaine sous incertitude a 30 agents'
+  operator -> blindspotAM16 'autorite humaine non tenable a cette echelle'
```

Justification : `operator` est déclaré acteur du modèle, safety-critical, et
porteur de H5 (`operator -> h5 'autorite humaine sur les actions critiques'`).
La charge R-14/AM16 est portée par cet acteur. L'omettre laissait le risque le
plus « humain » sans acteur humain.

### C4 — Levez l'ambiguïté du libellé trompeur (corrige m1, cas unique grave)

```
-  onboard.perception -> riskR9 'detection d evitement in extremis'
+  onboard.perception -> riskR9 'detection pour evitement in extremis'

   (ou mieux : 'detection d urgence pour evitement' — à préférer si
    'pour evitement' heurte la lecture)
```

Les 15 autres cas d'élision sont cosmétiques : je ne propose pas de correction
de confort sur ceux-là, conformément à la consigne « uniquement ce qui est faux
ou trompeur ».

### C5 — Rendre la non-causalité requêtable (corrige M1)

Ce n'est pas un libellé faux à corriger mot à mot, c'est un défaut de type.
Recommandation structurante (à arbitrer, pas à appliquer d'office) : ajouter
dans `architecture.c4` un type de relation distinct, par exemple

```
  /** Le composant est le SIEGE d une contrainte juridique, programme ou
   *  reglementaire. La source du risque est hors du modele. A lire comme une
   *  localisation d implementation, pas comme une cause technique. */
  relationship concerns {
    title 'Concerne (conformite, pas causalite)'
    line dotted
    color sourceGray
  }
```

puis reclasser les 8 relations de conformité (R-6, R-7, AM-1, AM-2, AM-5, AM-8,
AM-11, AM-13) sous `concerns` plutôt que `exposed-to`. Si cette séparation n'est
pas souhaitée, la mention explicite « point de conformite : » en tête de
libellé est un moindre mal acceptable.

---

## Ce qui est correct (confirmé après vérification)

- **Fidélité de conversion : parfaite.** Les 101 relations proposées sont
  injectées au caractère près. Zéro relation perdue, zéro libellé altéré, zéro
  option de fiche tronquée. Vérifié par diff de multi-ensembles, pas par
  relecture.
- **Options des 4 fiches DE : intégralement conservées.** Les 4 options de
  DE-01, DE-02, DE-03 et de DE-04 sont présentes dans les `description` du
  modèle, sans troncature (vérifié : 4 options pour DE-01 et DE-02 et DE-03,
  4 pour DE-04, conformes à `decisions_swarmdrone.md`).
- **Aucune « option retenue » introduite.** Aucune des 4 fiches ne recommande
  une branche : elles listent les options, la question, les critères, la
  conséquence si non tranché, le porteur, l'échéance. Le statut est
  `'ouverte'` pour les quatre. Le critère « fiche ouverte » est satisfait.
- **Les 4 AM critiques sont bien les 4 couverts.** Vérifié dans le modèle :
  `gravite 'critique'` est porté par AM-1, AM-3, AM-5, AM-7 uniquement.
  DE-01←AM-1, DE-02←AM-5, DE-03←AM-7, DE-04←AM-3 : aucun AM critique oublié,
  aucune fiche créée sur un AM non critique. La correspondance AM↔DE est exacte.
- **Équilibre des accolades et placement des blocs : corrects.** `de1..de4` et
  toutes les relations sont dans `model { }`, au bon niveau. Le modèle est
  syntaxiquement valide (`✓ Valid (2 files)`).
- **Couverture complète :** 15/15 risques et 16/16 angles morts ont au moins
  une relation. Aucun élément de l'inventaire n'est orphelin.
- **Bonne conduite des « travaux à faire » vs « décisions ».** AM-3 est bien
  traité comme travail d'ingénierie *plus* noyau de décision résiduel, pas
  comme une fausse décision binaire. Le modèle conserve cette nuance dans la
  `description` de DE-04 (« Condition. Cette décision est conditionnée à la
  production préalable du budget radio (travail d ingénierie, pas arbitrage). »).
- **Les libellés respectent les contraintes :** tous ≤ 50 caractères, aucun
  dépassement.

---

## Corrections directement applicables

```
views.c4 : vue `decisions`, include : `include adr1..adr5 / include adr1 -> *...` -> ajouter `include de1, de2, de3, de4` et `include blindspotAM1 -> de1, blindspotAM5 -> de2, blindspotAM7 -> de3, blindspotAM3 -> de4`
views.c4 : vue `decisions`, title : 'Decisions d architecture (ADR-1..ADR-5) et ce qu elles justifient' -> 'Decisions d architecture : ADR-1..5 (tranchees) et DE-01..04 (ouvertes)'
views.c4 : vue `tracabilite`, include (ligne 559) : `include h1, h2, h3, h4, h5, adr1, adr2, adr3, adr4, adr5` -> `include h1, h2, h3, h4, h5, adr1, adr2, adr3, adr4, adr5, de1, de2, de3, de4`
architecture.c4 : relation `de1 -> riskR7` : 'leve le conflit de licence' -> SUPPRIMER (redondante et fausse ; l appel de decision est deja porte par blindspotAM1 -> de1) ; alternative : 'conditionne la levee du conflit de licence'
architecture.c4 : relation `de2 -> riskR3` : 'borne la validation d echelle' -> SUPPRIMER ; alternative : 'conditionne la borne de validation d echelle'
architecture.c4 : relation `de3 -> riskR2` : 'reduit la surface de prise de controle' -> SUPPRIMER ; alternative : 'conditionne la reduction de la surface de prise de controle'
architecture.c4 : relation `de4 -> riskR1` : 'traite la contention radio a 30 agents' -> SUPPRIMER ; alternative : 'conditionne le traitement de la contention radio a 30 agents'
architecture.c4 : relation `onboard.perception -> riskR9` : 'detection d evitement in extremis' -> 'detection pour evitement in extremis'
architecture.c4 : relation `operator -> riskR14` : ABSENTE -> AJOUTER 'charge humaine sous incertitude a 30 agents'
architecture.c4 : relation `operator -> blindspotAM16` : ABSENTE -> AJOUTER 'autorite humaine non tenable a cette echelle'
architecture.c4 : type de relation pour les 8 liens de conformite (R-6, R-7, AM-1, AM-2, AM-5, AM-8, AM-11, AM-13) : `exposed-to` -> arbitrer introduction d un type `concerns` (non causal) ou prefixe de libelle 'point de conformite :' (correction structurante, non appliquee d office)
```

---

## Limites de cette vérification (ce que je n'ai PAS pu établir)

1. **Rendu graphique non inspecté.** J'ai lu les `include` de `views.c4` ; je
   n'ai pas régénéré les images des vues. Une relation peut être présente mais
   illisible par surcharge. Non vérifié : lisibilité visuelle des vues enrichies.
2. **Source normative primaire COLREGs non consultée.** L'affirmation que les
   COLREGs imposent des règles d'évitement normatives aux USV reste reprise du
   texte du modèle. `Non vérifié` : référence normative primaire. Ce point
   conditionne la solidité de `onboard.mission -> riskR6` et
   `onboard.mission -> blindspotAM8`.
3. **Licences PX4 / ArduPilot / MinIO / Grafana non reconfirmées dans cette
   session.** Elles proviennent de l'annexe v1. `Non vérifié` : état courant des
   licences en amont.
4. **Pas de test d'unicité de libellé dans une vue.** La duplication constatée
   ne casse pas la validation actuelle ; je ne sais pas si un futur export exige
   l'unicité. Non vérifié.
5. **Je ne peux pas trancher l'attribution des 4 relations `de -> risk`.** Elles
   ne figurent dans aucun de mes deux fichiers ; elles apparaissent à
   l'injection. Je les signale comme à corriger, sans affirmer qui les a écrites.

---

## Références (sources réellement consultées)

- Modèle vérifié : `/docker/likec4/workspace/architecture.c4` (1626 lignes) et
  `/docker/likec4/workspace/views.c4` (658 lignes).
- Propositions : `/home/hermesagent/workspace/relations_swarmdrone.md` (386 l.)
  et `/home/hermesagent/workspace/decisions_swarmdrone.md` (183 l.).
- Texte injecté : `/tmp/verif_injecte.txt`.
- Validation outil : `npx likec4 validate` -> `✓ Valid (2 files)`, exécuté le
  2026-09-15 05:32 (UTC), workspace `/docker/likec4/workspace`.
- Scripts de vérification exécutés : `diff_relations.py`, `diff2.py`,
  `labels_check.py`, `count_check.py`, `brace_check.py` (dans
  `/home/hermesagent/workspace/`).

aucun article trouvé
