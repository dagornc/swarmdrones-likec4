# Relations de tracabilite manquantes — essaim 30 plateformes heterogenes

Mission : Action 1. Posture scientifique stricte : aucune relation inventee.
Source de verite : /home/hermesagent/workspace/swarmdrones_likec4/architecture.c4,
/home/hermesagent/workspace/point4_toolkit/block_risk.c4,
/home/hermesagent/workspace/point4_toolkit/block_blindspot.c4,
/home/hermesagent/workspace/point4_toolkit/block_relations.c4,
/home/hermesagent/workspace/swarmdrones_likec4/point4/mapping_ids_annexe_v1.md.

Regle appliquee : une relation n'est proposee que si elle est fondee sur le
texte du modele ou sur la definition meme du risque/angle mort. Chaque libelle
est court (<= 50 car.), sans apostrophe. Les observations issues du modele sont
des FAITS DE MODELE ; leur validite theorique plus large n'est pas revendiquee.

Note de convention : la mission impose le sens `<SOURCE> -> <CIBLE>`.
Pour la lisibilite « par quoi est ce expose / cause », j'emploie la convention
suivante et je la signale : `<composant> -> riskR<n> 'comment il est expose'`
et `<composant> -> blindspotAM<n> 'ce qui manque dans ce composant'`.
C'est la convention deja utilisee dans block_relations.c4 (brique -> risque).

---

## PARTIE A — Risques vers composants (et hypotheses / ADR)

riskR1 (contention radio a 30 agents) — criticite critique
- onboard.linkRadio -> riskR1 'point unique de saturation radio a 30 agents'
  (justif : linkRadio est le seul element qui porte tout le trafic essaim, mesh et store-and-forward selon sa description)
- edge.relay -> riskR1 'relais agregateur soumis a la contention'
  (justif : edge.relay relaie le trafic inter-plateformes et vers le C2, il concentre donc la contention)
- onboard.telemetry -> riskR1 'volume de telemetrie non budgete'
  (justif : telemetry produit le flux 1-10 Hz delta-compresse qui alimente la radio)
- riskR1 -> h2 'contention aggravee par le lien intermittent'
  (justif : H2 impose store-and-forward, qui augmente le volume et les rafales sur coupure)

riskR2 (prise de controle via lien non authentifie)
- onboard.linkRadio -> riskR2 'surface d attaque du lien montant'
  (justif : linkRadio gere decouverte de voisins, mesh et chiffrement, donc l interface non authentifiee)
- onboard.autopilot -> riskR2 'commands non signes atteignent la boucle de vol'
  (justif : les ordres de mission arrivent a l autopilote via linkRadio puis mission, sans authentification par defaut)
- c2.auth -> riskR2 'emission et signature des ordres critiques'
  (justif : c2.auth emet les jetons et garantit authorization_ref sur action critique)
- riskR2 -> adr3 'canaux surete et securite separes a tenir'
  (justif : ADR-3 separe la voie de surete de la couche crypto, ce qui conditionne la reponse au risque)

riskR3 (validation reelle a 30 agents non realisable)
- cloud.twin -> riskR3 'validation d echelle reportee sur le jumeau'
  (justif : cloud.twin porte rejeu et simulation, seul moyen de prouver l echelle a cout constant)
- cloud.replayStore -> riskR3 'campagnes rejouables pour l echelle'
  (justif : replayStore stocke les journaux pour Monte-Carlo et non-regression)
- riskR3 -> adr4 'deport du lourd hors boucle a justifier'
  (justif : ADR-4 place le traitement lourd hors boucle, donc la validation depend du differe)

riskR4 (perte de coherence sous partition / split brain)
- onboard.taskAuction -> riskR4 'allocation decentralisee sous partition'
  (justif : taskAuction fonctionne en encheres decentralisees a 0.2-1 Hz, expose au split brain)
- edge.coordinator -> riskR4 'coordination locale divergente de la vue C2'
  (justif : edge.coordinator prend le relais de l allocation quand le lien C2 tombe)
- edge.fusion -> riskR4 'vues tactiques divergentes entre zones'
  (justif : edge.fusion consolide les pistes localement, donc peut diverger d une zone a l autre)
- riskR4 -> adr5 'robustesse sous partition arbitree'
  (justif : ADR-5 choisit la robustesse et refuse le consensus global dur, ce qui definit la tolerance au split brain)

riskR5 (derive en GNSS degrade)
- onboard.perception -> riskR5 'estimation de position derivee sans GNSS'
  (justif : perception porte la redondance GNSS + INS + odometrie + relative et l alerte sense-and-avoid)
- onboard.safety -> riskR5 'RTL sur seuil de derive'
  (justif : safety declenche RTL et atterrissage d urgence selon la derive)
- onboard.mission -> riskR5 'mission nominale sans recalage GNSS'
  (justif : mission doit executer sans lien ni GNSS garanti, avec ses etats DEGRADED et RTL/RECOVER)
- riskR5 -> h3 'hypothese GNSS degradable directement teste'
  (justif : R5 est la materialisation de H3, marquee a-valider avec probabilite locale inconnue)

riskR6 (non conformite reglementaire BVLOS COLREGs)
- edge.coordinator -> riskR6 'deconfliction locale sans regle normative'
  (justif : coordinator resout les conflits d espace localement sans reference aux regles d evitement maritimes)
- onboard.mission -> riskR6 'navigation marine des 4 USV a conformer'
  (justif : mission porte la navigation des USV, soumise aux COLREGs selon la description du risque)
- c2.gcs -> riskR6 'configuration des zones soumise aux autorisations'
  (justif : c2.gcs est le poste de commandement qui fixe zones et supervision, donc le point de conformite operationnelle)

riskR7 (conflit de licence bloquant la distribution)
- cloud.replayStore -> riskR7 'stockage objet AGPLv3 impose une revue'
  (justif : replayStore est associe a MinIO AGPLv3 avec reserve revue juridique requise)
- cloud.analytics -> riskR7 'chaines AGPL et source-available cote cloud'
  (justif : analytics s appuie sur Grafana AGPL-3.0-only et un bus a caveat Confluent)
- onboard.autopilot -> riskR7 'socle de vol copyleft ou permissif'
  (justif : l autopilote choisit PX4 BSD-3 ou ArduPilot GPLv3, arbitrage structurant)

riskR8 (fusion degradee en scenario dense)
- edge.fusion -> riskR8 'fausses pistes et latence de fusion'
  (justif : edge.fusion produit les pistes consolidees et la carte locale a 1-10 Hz en scenario dense)
- onboard.perception -> riskR8 'cibles P_d et P_fa non fixees en source'
  (justif : perception alimente la fusion, mais aucune valeur cible de detection n y est definie)
- cloud.replayStore -> riskR8 'mesure de fausses pistes rejouable'
  (justif : seul un rejeu deterministe permet de comparer les taux de fausses pistes entre scenarios)

riskR9 (collision en scenario d urgence)
- onboard.safety -> riskR9 'barriere de surete independante du lien'
  (justif : safety porte les garde-fous et l ABORT local selon regles pre-approuvees)
- onboard.perception -> riskR9 'detection d evitement in extremis'
  (justif : perception fournit la detection d evitement avec l alerte sense-and-avoid)
- edge.fusion -> riskR9 'detection de la perte d un agent'
  (justif : edge.fusion detecte explicitement la perte d un agent, prealable a la zone d exclusion)
- riskR9 -> adr3 'voie de surete a maintenir non bloquee'
  (justif : ADR-3 garantit que la voie de surete reste fonctionnelle sans lien et sans crypto)

riskR10 (desynchronisation d horloge, donnees perimees)
- onboard.telemetry -> riskR10 't_publish et t_valid reposent sur l horloge locale'
  (justif : telemetry porte les deux horodatages et suppose une horloge source coherente)
- edge.fusion -> riskR10 'fusion de pistes fondee sur des horodatages'
  (justif : edge.fusion consolide des pistes horodatees, donc sensible a la derive d horloge)
- riskR10 -> adr2 'fraicheur explicite suppose un temps fiable'
  (justif : ADR-2 repose sur la fraicheur explicite, ce qui n a de sens que si le temps reste coherent)

riskR11 (fidelite du jumeau numerique insuffisante)
- cloud.twin -> riskR11 'jumeau non mesure contre le reel'
  (justif : cloud.twin porte le jumeau et la prediction de derive sans procedure de fidelite)
- cloud.analytics -> riskR11 'ecart sim contre reel non instrumente'
  (justif : analytics calcule les metriques post-mission, mais aucune metrique d ecart sim-reel n est definie)

riskR12 (taches orphelines par non prise en compte de l energie)
- onboard.energy -> riskR12 'budget de retour non integre a l allocation'
  (justif : energy gere le budget de retour mais n alimente pas le cout d enchere)
- onboard.taskAuction -> riskR12 'encheres sans ponderation energetique'
  (justif : taskAuction alloue a 0.2-1 Hz sans contrainte d energie par defaut)
- onboard.health -> riskR12 'marge d energie a exposer a l allocation'
  (justif : health fournit diagnostic et marge d energie par plateforme)
- riskR12 -> adr5 'allocation robuste a ponderer energie'
  (justif : ADR-5 fait des encheres decentralisees le mecanisme par defaut, donc le lieu naturel du correctif)

riskR13 (effort de R and D sous estime sur la fusion multi agents)
- edge.fusion -> riskR13 'brique de fusion non specifiee'
  (justif : edge.fusion est decrit fonctionnellement sans algorithme, critere ni jeu de donnees)
- onboard.perception -> riskR13 'chaine de perception essaim a construire'
  (justif : perception est decrit par fonction sans metrique cible associee)
- cloud.modelRegistry -> riskR13 'voie de gestion de modeles non tranchee'
  (justif : modelRegistry est marque Non verifie et sans processus etabli)

riskR14 (charge C2 humaine excessive sous incertitude)
- c2.gcs -> riskR14 'goulot humain sur 30 agents'
  (justif : c2.gcs est le seul chemin d autorisation humaine pour superviser 30 plateformes)
- c2.alerting -> riskR14 'agregation d alarmes non calibree a la charge'
  (justif : alerting est en best-effort et agrege des alarmes sans mesure de charge cognitive)
- riskR14 -> h5 'autorite humaine a rendre tenable a l echelle'
  (justif : H5 pose l autorite humaine sur les actions critiques, que R14 met sous tension)

riskR15 (handoff inter domaines ambigu)
- edge.gateway -> riskR15 'frontiere de confiance et normalisation du handoff'
  (justif : gateway est la passerelle et frontiere de confiance entre essaim, C2 et cloud)
- onboard.taskAuction -> riskR15 'attribution sans regle d autorite inter domaines'
  (justif : taskAuction attribue des taches sans definir qui detient l autorite lors d un transfert UAV vers USV)
- onboard.mission -> riskR15 'execution de la tache transferee non identifiee'
  (justif : mission execute le plan embarque, donc une tache transferee doit y etre desambiguisee)

---

## PARTIE B — Angles morts vers composants (et hypotheses / ADR)

blindspotAM1 (arbitrage de licence non tranche)
- onboard.autopilot -> blindspotAM1 'socle de vol non fige dans le modele'
  (justif : l autopilote porte a la fois PX4 primaire et ArduPilot en repli, ce qui materialise l arbitrage ouvert)
- c2.gcs -> blindspotAM1 'GCS dual licence non tranchee'
  (justif : c2.gcs est associe a QGroundControl en licence dual Apache-2.0 ou GPLv3)
- onboard.mission -> blindspotAM1 'voie USV sous licence non etablie'
  (justif : mission s appuie sur OpenCPN GPLv2 et une piste PyPilot Non verifie)

blindspotAM2 (exposition AGPLv3 dans le Cloud)
- cloud.replayStore -> blindspotAM2 'stockage AGPL expose en reseau'
  (justif : replayStore est associe a MinIO AGPLv3 avec reserve revue juridique requise)
- cloud.analytics -> blindspotAM2 'tableaux de bord AGPL-3.0'
  (justif : analytics s appuie sur Grafana AGPL-3.0-only)
- cloud.modelRegistry -> blindspotAM2 'pipeline a caveat Confluent non OSI'
  (justif : la chaine cloud secondaire inclut un bus d evenements a caveat Confluent)

blindspotAM3 (budget radio a 30 agents non dimensionne)
- onboard.linkRadio -> blindspotAM3 'aucun budget radio total dans le composant'
  (justif : linkRadio decrit un mesh et une file priorisee mais sans budget agregе a 30 agents)
- onboard.telemetry -> blindspotAM3 'debit de telemetrie non chiffre globalement'
  (justif : telemetry fixe 1-10 Hz par agent en delta compresse sans dimensionnement collectif)
- edge.relay -> blindspotAM3 'agregation a 30 agents plus Edge non dimensionnee'
  (justif : edge.relay concentre le trafic des plateformes, point ou la contention se materialise)
- blindspotAM3 -> adr2 'priorisation des deltas depend du budget radio'
  (justif : ADR-2 fait transporter le delta avec priorisation par linkRadio, donc suppose un budget)

blindspotAM4 (perception d essaim sans brique ni metrique)
- onboard.perception -> blindspotAM4 'pas de metrique cible de fusion essaim'
  (justif : perception est decrit fonctionnellement sans algorithme ni critere associe)
- edge.fusion -> blindspotAM4 'fusion multi agents sans brique identifiee'
  (justif : edge.fusion est decrit sans algorithme et sans COTS identifie pour la fusion)
- cloud.replayStore -> blindspotAM4 'aucun jeu de donnees de test associe'
  (justif : replayStore existe pour la non-regression mais aucun jeu de donnees n est specifie)

blindspotAM5 (validation d echelle 2 5 12 30 irrealiste en reel)
- cloud.twin -> blindspotAM5 'prouver l echelle en simulation faute de reel'
  (justif : cloud.twin est le moyen de valider une echelle de 30 plateformes non realisable en vol)
- cloud.replayStore -> blindspotAM5 'campagnes rejouables pour l echelle'
  (justif : replayStore porte les journaux rejouables pour les campagnes Monte-Carlo)
- blindspotAM5 -> adr4 'deport du lourd conditionne la preuve d echelle'
  (justif : ADR-4 place le traitement lourd hors boucle, ce qui plafonne la modalite de preuve admise)

blindspotAM6 (desynchronisation d horloge non specifiee)
- onboard.telemetry -> blindspotAM6 'aucune source de temps declaree'
  (justif : telemetry porte t_publish et t_valid mais la source de temps n est pas specifiee)
- edge.fusion -> blindspotAM6 'fusion horodatee sans garde fou de derive'
  (justif : edge.fusion consolide des pistes horodatees sans comportement defini en perte de GNSS)
- onboard.health -> blindspotAM6 'derive d horloge non surveillee'
  (justif : health surveille batterie, moteurs, capteurs et temperatures mais pas la coherence temporelle)
- blindspotAM6 -> adr2 'fraicheur explicite sans specification du temps'
  (justif : ADR-2 rejette l horloge globale synchronisee mais ne specifie pas de substitut)

blindspotAM7 (cybersecurite du lien montant et de l autopilote)
- onboard.linkRadio -> blindspotAM7 'lien montant sans modele de menaces'
  (justif : linkRadio gere le chiffrement mais sans modele de menaces ni gestion de cles embarquees)
- onboard.autopilot -> blindspotAM7 'surface d attaque de l autopilote'
  (justif : l autopilote est atteignable par ordres via mission et linkRadio)
- c2.auth -> blindspotAM7 'rotation et revocation non etablies'
  (justif : c2.auth emet les jetons mais la PKI et la revocation embarquees sont marquees Non verifie)
- blindspotAM7 -> adr3 'arbitrage surete securite non resolu en conception'
  (justif : ADR-3 reconnait le conflit en le separant mais ne le resout pas cote securite)

blindspotAM8 (cadre reglementaire BVLOS et COLREGs)
- onboard.safety -> blindspotAM8 'regles d evitement non normatives a ce stade'
  (justif : safety porte les garde-fous et RTL sans integration des regles d evitement maritimes)
- onboard.mission -> blindspotAM8 'comportement USV a conformer aux COLREGs'
  (justif : mission porte la navigation des 4 USV, soumise aux COLREGs)
- c2.planner -> blindspotAM8 'plans de zone a contrainte reglementaire'
  (justif : planner genere les plans embarques dans des zones soumises a autorisation)

blindspotAM9 (gestion energetique heterogene non globale)
- onboard.energy -> blindspotAM9 'budget de retour par plateforme seulement'
  (justif : energy gere l energie et le budget de retour a l echelle locale par plateforme)
- onboard.taskAuction -> blindspotAM9 'allocation sans contrainte energetique globale'
  (justif : taskAuction n integre pas le cout d energie dans l enchere par defaut)
- onboard.health -> blindspotAM9 'marge d energie non exposee globalement'
  (justif : health calcule la marge d energie mais sans vue globale inter plateformes)
- blindspotAM9 -> adr5 'allocation robuste a pondere par l energie'
  (justif : ADR-5 fait de l enchere decentralisee le mecanisme par defaut, lieu du correctif energie)

blindspotAM10 (handover inter domaines mal defini UAV USV)
- edge.gateway -> blindspotAM10 'frontiere de confiance inter domaines'
  (justif : gateway est la frontiere de confiance et la normalisation entre essaim, C2 et cloud)
- onboard.taskAuction -> blindspotAM10 'transfert de tache sans regle d autorite'
  (justif : taskAuction attribue des taches sans definir l autorite lors d un transfert inter domaines)
- onboard.sensorsHAL -> blindspotAM10 'frames et unites heterogenes a normaliser'
  (justif : sensorsHAL absorbe l heterogeneite des plateformes, donc des reperes et des unites)

blindspotAM11 (ontologie commune non specifiee)
- cloud.twin -> blindspotAM11 'schema commun non fixe pour le jumeau'
  (justif : aucun schema commun d unites et de semantique n est fixe pour le jumeau)
- edge.fusion -> blindspotAM11 'vocabulaire de pistes non normalise'
  (justif : edge.fusion echange des pistes entre classes de plateformes sans schema commun)
- cloud.modelRegistry -> blindspotAM11 'versionnement de schema non defini'
  (justif : modelRegistry versionne modeles et configurations sans schema de donnees versionne)

blindspotAM12 (comportement en cas d agent defaillant non traite)
- edge.fusion -> blindspotAM12 'perte d agent detectee sans suite definie'
  (justif : edge.fusion detecte la perte d un agent mais la reaction n est pas definie)
- onboard.health -> blindspotAM12 'detection de defaillance sans reallocation'
  (justif : health fait la prediction de defaillance mais sans protocole de retrait et reintegration)
- onboard.taskAuction -> blindspotAM12 'tache orpheline apres perte d agent'
  (justif : taskAuction alloue des taches dont le titulaire peut disparaitre)

blindspotAM13 (observabilite et rejeu non contractuels)
- cloud.replayStore -> blindspotAM13 'contrat de trace non specifie'
  (justif : replayStore existe sans definir quoi enregistrer pour un rejeu deterministe)
- onboard.telemetry -> blindspotAM13 'entrees et alea absents de la trace'
  (justif : telemetry formate et priorise mais ne definit pas un contrat de trace rejouable)
- c2.auth -> blindspotAM13 'journalisation d audit non liee au rejeu'
  (justif : c2.auth journalise les decisions pour l audit sans lien avec la rejouabilite technique)

blindspotAM14 (bruit et fausses detections non quantifies)
- onboard.perception -> blindspotAM14 'aucune cible P_d et P_fa'
  (justif : perception porte la detection sans valeur cible de detection ni de fausse alarme)
- edge.fusion -> blindspotAM14 'fusion sans cible de fausses pistes'
  (justif : edge.fusion produit des pistes consolidees sans cible de taux de fausses pistes)

blindspotAM15 (fidelite du jumeau numerique non procedee)
- cloud.twin -> blindspotAM15 'procedure de fidelite absente'
  (justif : cloud.twin est le jumeau pour valider mais aucune procedure de fidelite n est prevue)
- cloud.analytics -> blindspotAM15 'metrique d ecart sim reel absente'
  (justif : analytics mesure la performance post-mission sans metrique d ecart sim contre reel)
- cloud.replayStore -> blindspotAM15 'campagne de recalibration non definie'
  (justif : replayStore permet le rejeu mais la recalibration du jumeau n est pas proceduree)

blindspotAM16 (facteur humain et charge du C2)
- c2.gcs -> blindspotAM16 'charge d un operateur sur 30 agents non evaluee'
  (justif : c2.gcs est le chemin d autorisation humaine, expose a la charge cognitive)
- c2.alerting -> blindspotAM16 'escalades en rafale non mesurees'
  (justif : alerting agrege et notifie les alarmes sans mesure du taux d escalade)
- c2.planner -> blindspotAM16 'replanification sous incertitude a charge humaine'
  (justif : planner produit des plans valides par l operateur sous incertitude)

---

## PARTIE C — Cas ou je ne force PAS de relation composant

Regle : un sujet de programme, juridique ou epistemique ne se rattache pas a un
composant technique. Je ne cree pas de lien artificiel.

1. riskR3 (validation reelle a 30 agents non realisable)
   Nature : programme et budget. Je rattache cloud.twin et cloud.replayStore
   comme MOYENS de preuve, mais le risque lui meme n est pas cause par un
   composant : c est une limite de faisabilite de campagne. Le lien composant
   est donc indirect (modalite de preuve), pas causal. A lire comme tel.

2. riskR7 / blindspotAM1 / blindspotAM2 (licences)
   Nature : juridique et programmatique. Les liens vers onboard.autopilot,
   cloud.replayStore et cloud.analytics sont MOTIVES par les briques
   associees (PX4, ArduPilot, MinIO, Grafana), pas par la logique du
   composant. Le composant est le SIEGE de la contrainte, pas sa cause.

3. blindspotAM5 (validation d echelle 2 5 12 30 en vol reel)
   Nature : programme et reglementation. Les liens vers cloud.twin et
   cloud.replayStore indiquent la modalite de preuve substitutive. Aucun lien
   causal vers un composant d execution.

4. riskR6 / blindspotAM8 (reglementation BVLOS et COLREGs)
   Nature : reglementaire. J ai rattache edge.coordinator, onboard.mission,
   onboard.safety et c2.planner comme POINTS DE CONFORMITE (la ou une regle
   devra etre implementee), mais je signale que le risque trouve sa source
   dans le cadre legal, hors perimetre du modele. Relation de conformite,
   pas de causalite technique.

5. blindspotAM11 (ontologie commune) et blindspotAM13 (contrat de trace)
   Nature : specification transverse. Les liens pointent les composants qui
   MANIPULENT le schema ou la trace (edge.fusion, cloud.twin, telemetry,
   replayStore). Ce sont des lieux d implementation, pas des causes. Un
   couplage vers cloud.modelRegistry pour AM13 serait possible mais moins
   direct que replayStore : je le mentionne sans le retenir.

6. riskR14 / blindspotAM16 (facteur humain)
   Nature : facteur humain. Les liens vers c2.gcs et c2.alerting sont
   solides pour l IHM, mais l operateur lui meme est un acteur, pas un
   composant d architecture. Je n ai pas cree de relation vers un composant
   d adaptation de charge, car il n en existe pas dans les 24 composants.

7. Relations vers h1 a h5 et adr1 a adr5
   Je n en propose QUE la ou l enonce de l hypothese ou de l ADR nomme
   explicitement le sujet du risque ou de l angle mort (voir A et B). Je n ai
   pas cree de lien systematique risque vers H5 ni vers ADR-1 pour chaque
   element, car ce serait de la decoration, pas de la tracabilite.

---

## PARTIE D — Ce que je ne sais pas / limites

1. Le nombre exact de relations deja presentes. La mission annonce 7 sur 15
   risques et 7 sur 16 angles morts. Dans block_relations.c4, je compte des
   liens brique vers risque et brique vers angle mort, plus des liens
   risque vers angle mort et angle mort vers document source. Je ne sais pas
   quelle metrique precise produit le compte 7 sur 15 et 7 sur 16, donc je ne
   garantis pas que mes ajouts portent le total a un chiffre exact.
   `Non verifie` : le total cible apres ajout.

2. Nature du kind cible. block_risk.c4 et block_blindspot.c4 declarent des
   elements risk et blindspot, mais je n ai pas trouve leur declaration de
   kind dans le contenu que j ai lu. Les kinds hypotheses et decisions
   existent dans architecture.c4. La compatibilite des relations que je
   propose avec le kind reellement declare doit etre verifiee avant
   injection. `Non verifie` : declaration de kind de risk et blindspot.

3. Sens de relation autorise. Le modele interdit parent vers enfant au sein
   d une boundary. Mes relations composant vers risque et composant vers
   angle mort traversent des boundaries : je suppose qu elles sont autorisees
   comme le sont brique vers risque dans block_relations.c4. A verifier sur
   un cas avant de tout injecter.

4. Unicite des libelles. Plusieurs relations reutilisent des libelles
   proches. Je ne sais pas si le generateur de vues exige l unicite locale
   des libelles dans une vue donnee.

5. Fondements normatifs. Pour riskR6 et blindspotAM8, l affirmation que les
   COLREGs imposent des regles d evitement normatives aux USV est reprise du
   texte du modele, pas d une source que j ai verifiee ici. `Non verifie` :
   reference normative primaire.

6. Ensure des composants non rattaches. Composants sans aucune relation
   proposee dans A et B : edge.cache, c2.missionStore, onboard.taskAuction
   est bien couvert, mais edge.cache et c2.missionStore ne le sont pas. Je
   n ai pas trouve de risque ou d angle mort dont ils sont le siege direct.
   `Non verifie` : il n existe peut etre pas de lien fonde pour eux, et je
   prefere le silence a une relation inventee.

7. Sauvegarde. Mes propositions ne sont pas fondees comme une revue
   documentaire exhaustive : je n ai lu que les fichiers cites en tete. Si
   une annexe ou un document de reference contredit un enonce, il primerait.
