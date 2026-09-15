# Décisions en attente — Essaim hétérogène 30 plateformes (Action 2)

Posture : ingénieur système, revue contradictoire. Date : 2026-09-15 (UTC).
Source de vérité du modèle : `/home/hermesagent/workspace/swarmdrones_likec4/backup_v5/architecture.c4`
(1029 lignes et 1440 lignes selon les copies : la copie active est `backup_v5/architecture.c4`,
modifiée 2026-09-15 05:03, qui contient les 16 angles morts et les 5 ADR au statut `acceptee`).

## Ce qui est constaté, littéralement, dans le modèle

Vérifié par inspection directe du fichier :

- 5 décisions `adr1..adr5`, toutes `metadata { statut 'acceptee' }` (5 occurrences).
- 0 décision au statut `ouverte` ou `en attente` (les seuls autres `statut` du fichier sont
  les 13 `couvrir` et 2 `surveiller` des angles morts, plus 1 `couvrir+accepter`).
- 16 angles morts `blindspotAM1..AM16`. Les 4 marqués `gravite 'critique'` :
  - `blindspotAM1` — AM-1 Arbitrage de licence non tranché (BSD-3 vs GPLv3)
  - `blindspotAM3` — AM-3 Budget radio à 30 agents non dimensionné
  - `blindspotAM5` — AM-5 Validation échelle 2-5-12-30 irréaliste en réel (`statut 'couvrir+accepter'`)
  - `blindspotAM7` — AM-7 Cybersécurité du lien montant et de l autopilote
- 15 risques `riskR1..R15`. Correspondances directes : R-1 ↔ AM-3, R-2 ↔ AM-7,
  R-3 ↔ AM-5, R-7 ↔ AM-1.

Le problème est donc confirmé : ces 4 trous de spécification ne sont portés par aucune
entité « décision ». Ils sont décrits comme des angles morts (trou reconnu) et non comme des
choix à arbitrer.

## Méthode suivie pour chaque fiche

Une fiche n est retenue comme décision que si elle satisfait trois conditions :
1. **plusieurs issues réelles et mutuellement exclusives** existent ;
2. le choix **change la conception** (chemins d implémentation divergents ensuite) ;
3. il existe **un porteur unique identifiables** pouvant dire « oui à l option X ».

Si une seule issue raisonnable existe, ou si l objet est de nature « produire un artefact
technique » (travail à faire) plutôt que « arbitrer entre des branches », je le déclare
travail à faire au lieu de forcer une fiche. Cela arrive pour **AM-3**, partiellement,
comme détaillé plus bas.

Étiquetage épistémique utilisé ci-dessous : `[FAIT]` (démontré / documenté en source
primaire), `[HYP]` (hypothèse de conception), `[EXTRAP]` (extrapolation depuis une autre
échelle ou un autre domaine), `Non vérifié` (rien d établi en source primaire).
Rappel de contexte : le corpus local
(`/home/hermesagent/swarmdrone-research/catalog.json`) compte 1011 entrées mais **2 seulement**
au stade `PRIMARY_SOURCE_VERIFIED` ; il ne peut donc pas servir de preuve au niveau
revendication (confirmé dans `quality-summary.json`). Les fiches ci-dessous reposent sur le
document d architecture et l annexe v1, pas sur le corpus comme preuve.

---

## Isse de décision retenues

Trois fiches de décision (AM-1, AM-5, AM-7) + un constat de travail à faire (AM-3),
motivé explicitement. Numérotation des IDs alignée sur le préfixe `DE-` et la convention
`blindspotAM<n>` du modèle.

---

DECISION-ATTENTE DE-01
titre : Socle de vol et régime de distribution du firmware
angle_mort : blindspotAM1
question : Faut-il baser le firmware embarqué sur un socle permissif (PX4, BSD-3) ou sur un socle copyleft (ArduPilot, GPLv3), et le livrable doit-il rester fermable ou non ?
options : PX4 BSD-3 comme socle unique et livrable fermé ; ArduPilot GPLv3 comme socle unique avec publication du code embarqué dérivé ; PX4 en socle avec compilateur compagnon partiellement propriétaire et publication sélective ; coexistence PX4 pour UAV et ArduPilot Rover pour USV avec stratégie de licence par domaine
criteres : conformité juridique du mode de distribution commerciale ; coût de refonte si le socle est changé tard ; maturité des modes autonomes par classe de plateforme ; capacité à fermer les composants à valeur ajoutée ; délai de mise en service
consequence_si_non_tranche : Choix implicite de fait par le premier développeur qui code l autopilote ; toute refonte ultérieure du socle touche onboard.autopilot, onboard.mission, onboard.safety et se répercute sur le HIL, les tests et la documentation ; risque de découvrir une exigence de fermeture après des mois de développement.
porteur : direction technique avec avis juridique (revue licences) — décision de niveau programme, pas ingénieur
echeance : avant le démarrage de la conception détaillée du socle embarqué, et avant tout choix d autopilote dans le HIL

Note de traçabilité : `onboard.autopilot -> AutopilotPX4 'implemente par (primaire)'` et
`-> ArduPilot 'alternative (secondaire)'` existent dans le modèle ; le risque associé est
`riskR7` (Conflit de licence bloquant la distribution). L annexe v1 (§A.1) établit PX4 en
BSD-3 `[FAIT — LICENSE PX4-Autopilot]` et ArduPilot en GPLv3 `[FAIT — ardupilot.org]`.
La difficulté propre aux USV (voie Rover, licence non figée) est signalée `Non vérifié`
dans l annexe — à lever dans la fiche.

---

DECISION-ATTENTE DE-02
titre : Plafond d échelle réelle et répartition des preuves par modalité
angle_mort : blindspotAM5
question : Jusqu à quelle taille d essaim valide-t-on en vol réel, et quels critères d acceptation sont déclarés prouvés uniquement en SIL/HIL/jumeau numérique ?
options : plafonner le réel à 5 plateformes et déclarer 12 et 30 comme preuves simulées ; plafonner le réel à 12 et déclarer 30 comme simulé ; viser 30 en réel en acceptant le coût calendaire et réglementaire ; renoncer au critère à 30 agents et redéfinir les critères d acceptation autour d un palier réel atteignable
criteres : coût et logistique d une campagne à 30 plateformes hétérogènes ; délai d obtention des autorisations BVLOS et zones ; valeur probante d une preuve simulée pour l acceptation client ; couverture réglementaire ; exposition au risque de critère jamais mesuré
consequence_si_non_tranche : Le critère d acceptation « à 30 agents » reste inscrit sans qu aucune modalité ne le produise ; soit il est implicitement contourné, soit il bloque la recette ; la valeur probante du dossier s effondre sans que personne ne l ait décidé.
porteur : responsable essais avec la direction technique (arbitrage coût / preuve / calendrier)
echeance : avant de figer le plan de campagne d essais et avant la première demande d autorisation de vol

Note de traçabilité : la recommandation de l annexe (§AM-5) est « couvrir + accepter » avec
un plafond réel réaliste de l ordre de 5 à 12 `[HYP]`. Le modèle porte déjà
`blindspotAM5 -> adr4 'deport du lourd conditionne la preuve d echelle'` et `riskR3`
(validation réelle à 30 agents non réalisable). Le modèle de déploiement de `backup_v5`
instancie bien 30 plateformes (18 UAV-R, 8 UAV-F, 4 USV) — c est l échelle cible, pas une
échelle validée.

---

DECISION-ATTENTE DE-03
titre : Modèle de menaces et stratégie de clés pour le lien montant et autopilote
angle_mort : blindspotAM7
question : Quel niveau d authentification et de gestion de clés impose-t-on au lien montant, au lien essaim et à l autopilote, et comment préserve-t-on la sûreté quand la sécurité est compromise ou indisponible ?
options : profil fort en conception — mTLS/DDS-Security partout, PKI embarquée avec rotation, ordres critiques signés obligatoires, red-team avant vol ; sécurité graduée par zone — forte sur le lien montant et le C2, allégée sur le bus interne autopilote au nom de la sûreté, avec quarantaine et refus des ordres non signés comme garde-fou ; sécurité différée — conception d abord fonctionnelle, durcissement reporté après le premier palier de vol, avec acceptation explicite du risque résiduel ; ségrégation stricte — canal de sûreté non chiffré mais isolé physiquement et logiquement, canal de sécurité chiffré en parallèle, sur le modèle de l ADR-3 déjà accepté
criteres : impact d une clé compromise sur l ensemble de la flotte ; conflit sûreté versus sécurité sur la voie de sûreté ; coût et complexité de la PKI embarquée et de la rotation ; latence ajoutée par le chiffrement sur les liens contraints ; effort de red-teaming ; conformité aux exigences attendues d une autorité
consequence_si_non_tranche : Un essaim est une cible à fort effet de levier : une clé compromise ou un ordre non authentifié peut atteindre la flotte entière. Sans décision, l implémentation par défaut (MAVLink et DDS non authentifiés, mentionnée comme surface d attaque dans l annexe) persiste, et le conflit sûreté/sécurité de l ADR-3 reste non résolu en conception.
porteur : architecte système sécurité avec le RSSI et un avis juridique sur les obligations — si aucun RSSI n est nommé, écrire explicitement « porteur à désigner » avant lancement
echeance : avant la conception détaillée des interfaces de communication et impérativement avant le premier vol avec lien montant actif

Note de traçabilité : le modèle pose `blindspotAM7 -> adr3 'arbitrage surete securite non
resolu en conception'` et `riskR2` (prise de contrôle via lien non authentifié). L ADR-3
« Canaux de sûreté et de sécurité séparés » est `statut 'acceptee'` : il tranche la
séparation des canaux, mais pas le modèle de menaces ni la gestion de clés, qui restent
ouverts. Une fiche d acceptation du risque résiduel est requise si l option « sécurité
différée » est retenue.

---

## AM-3 — Constat : travail à faire, avec un noyau de décision résiduel

AM-3 (budget radio à 30 agents non dimensionné) est **majoritairement un travail
d ingénierie, pas une décision binaire**. La raison est directe :

- La source (§8 du document d architecture) donne 1 à 10 Hz par agent, delta-compressé, et
  indique explicitement « budget lien total à dimensionner selon radios `[HYP]` ».
  Il n existe pas d arbitrage entre branches concurrentes : **il faut produire le budget**.
- Le livrable manquant est un **modèle de budget radio et une simulation de contention**
  (`[SIM]`), prérequis et non raffinement (recommandation de l annexe, §AM-3).
- Tant que ce modèle n existe pas, aucune option de dimensionnement n est comparable :
  choisir une architecture radio avant d avoir le budget serait un choix non informé.

Autrement dit : ce n est pas « quelle branche choisir ? » mais « produire la donnée qui
rendra un choix possible ». La recommandation est de créer une **tâche d ingénierie**
(porteur : architecte système communications ; échéance : avant la conception détaillée du
lien), avec livrables : budget de débit par criticité de flux, taux de charge du canal à 30,
nombre de créneaux ou de flux concurrents, latence p95, marge par mode dégradé.

Cela dit, **un noyau de décision résiduel réel** subsiste et mérite sa propre fiche, car il
ne sera pas résolu par le seul calcul : le choix de l architecture radio physique et du
mécanisme d accès au canal engage le programme. Je le porte donc comme décision distincte,
conditionnée à la disponibilité du budget ci-dessus.

DECISION-ATTENTE DE-04
titre : Architecture radio à 30 agents et mécanisme de priorité
angle_mort : blindspotAM3
question : Quelle architecture radio et quel mécanisme d accès priorisé retient-on pour soutenir 30 agents plus les noeuds Edge sans perdre les messages de sûreté, une fois le budget radio établi ?
options : maille autonome de type Zenoh en relais décentralisé avec priorité par criticité ; relais Edge centralisé en étoile avec QoS par classe de flux ; architecture hybride — maille pour l essaim et lien longue portée dédié vers le C2, avec priorisation stricte des messages de sûreté ; profil multi-radio par domaine, distinct pour UAV et USV, avec passerelle d interconnexion
criteres : débit utile disponible par canal à 30 agents ; taux de perte des messages critiques de sûreté ; latence p95 comparée au budget §8 ; coût matériel par plateforme et SWaP-C ; résistance au brouillage et à la coupure d un noeud ; effort d intégration avec les briques déjà choisies
consequence_si_non_tranche : À 30 agents, la contention est non linéaire ; sans décision, le premier palier de vol réel sature le canal, les messages de sûreté sont perdus en même temps que la télémétrie, et la dégradation devient en cascade et non maîtrisée. Le risque est déjà identifié comme `riskR1` (criticité critique) sans porteur de décision.
porteur : architecte système communications, arbitrage avec la direction technique sur le coût matériel
echeance : après la production du budget radio, avant la conception détaillée du lien embarqué et avant le palier réel de 12 plateformes

Note de traçabilité : `onboard.linkRadio -> Zenoh 'relais mesh decentralise'` et
`-> MosquittoMQTT 'mode store-and-forward degrade'` existent dans le modèle ;
`blindspotAM3 -> adr2 'priorisation des deltas depend du budget radio'` est déjà tracé, ce
qui confirme que ce noyau dépend d un arbitrage non couvert par l ADR-2. L annexe v1 (§A.2)
qualifie Zenoh de `[FAIT existence/licence ; MEDIUM sur perf]`, la performance comparative
reposant sur un preprint unique — à revérifier en source primaire avant de fonder la
décision sur cette brique.

---

## Récapitulatif

| ID décision | angle mort | nature | porteur | échéance |
|---|---|---|---|---|
| DE-01 | blindspotAM1 | décision réelle (juridique et programme) | direction technique + juriste | avant conception détaillée du socle |
| DE-02 | blindspotAM5 | décision réelle (coût / preuve / calendrier) | responsable essais + direction technique | avant plan de campagne d essais |
| DE-03 | blindspotAM7 | décision réelle (sûreté versus sécurité) | architecte système sécurité (ou à désigner) | avant conception des interfaces, et avant premier vol avec lien |
| DE-04 | blindspotAM3 | noyau de décision résiduel, conditionné au budget radio | architecte système communications | après budget radio, avant palier 12 |
| — | blindspotAM3 | travail à faire : produire budget radio + simulation de contention | architecte système communications | avant conception détaillée du lien |

## Limites et points non vérifiés

- Le corpus local ne fournit aucune preuve au niveau revendication (2 entrées
  `PRIMARY_SOURCE_VERIFIED` sur 1011). Les fiches ne s appuient donc pas sur lui comme
  preuve ; les affirmations de licence proviennent de l annexe v1 qui cite les sources
  primaires des projets.
- `Non vérifié` : la licence et l existence des autopilotes commerciaux certifiables, des
  solutions USV légères de type PyPilot, et la performance comparative de Zenoh, non
  reconfirmées dans la session courante.
- `Non vérifié` : la désignation effective d un RSSI dans l organisation. La fiche DE-03
  indique explicitement qu il faut le nommer ou écrire « à désigner ».
- Les valeurs chiffrées de §8 et les critères de §9 du document d architecture restent
  `[EXTRAP]`/`[HYP]` ; aucune campagne n a été exécutée.
- Le présent document est une revue de décisions, pas une validation d architecture ni une
  autorisation de déploiement.
