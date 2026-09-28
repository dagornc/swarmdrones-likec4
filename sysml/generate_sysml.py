#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_sysml.py — Emission des 15 specifications SysML v2 du catalogue SWARM-3D.

Carte kanban : SYSML-15 (t_d671a500). Profil : architecte.

OBJET : transformer les fiches algorithmes du modele LikeC4 en fichiers `.sysml`
reels (syntaxe textuelle SysML v2 / KerML, notation OMG), un fichier par
algorithme, dans sysml/.

REGLE D'HONNETETE (invariant INV-5 du modele) :
  - chaque champ de ce script est une TRANSCRIPTION d'un champ du modele
    LikeC4 (algorithms.c4 / e20-audit-completeness.c4 / messages.c4) ;
  - aucune valeur numerique n'est inventee : les parametres sans valeur au
    modele sont declares comme attributs SANS initialiseur (TBD) ;
  - les attributs derives (`attrs`) et les expressions `require constraint`
    sont des transcriptions QUALITATIVES des champs `purpose`/`contraintes`/
    `hypotheses` ; elles ne sont pas executables et ne pretendent pas l'etre.

Ce script est la TABLE DE TRACABILITE machine-readable : algorithme -> source
LikeC4 -> fichier .sysml emis.

Usage :
  python3 generate_sysml.py            # re-emet les 15 fichiers sysml/*.sysml
  python3 generate_sysml.py --manifest # affiche la table de tracabilite (TSV)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# MESSAGES (cf messages.c4) — item def SysML par message consomme/produit.
# ---------------------------------------------------------------------------
MESSAGES = {
    "msgTaskBid":             ("MSG_TASK_BID",             "enchere de tache (onboard.taskAuction -> CH_MESH)"),
    "msgTaskAssignment":      ("MSG_TASK_ASSIGNMENT",      "attribution de tache (onboard.taskAuction -> CH_MESH)"),
    "msgConsensusVote":       ("MSG_CONSENSUS_VOTE",       "vote de consensus (onboard.taskAuction -> CH_MESH)"),
    "msgHeartbeat":           ("MSG_HEARTBEAT",            "battement de vivacite (onboard.health -> CH_MESH)"),
    "msgFormationState":      ("MSG_FORMATION_STATE",      "etat de la formation (onboard.mission -> CH_MESH)"),
    "msgPositionUpdate":      ("MSG_POSITION_UPDATE",      "mise a jour de position (onboard.perception -> CH_MESH)"),
    "msgNeighborState":       ("MSG_NEIGHBOR_STATE",       "etat de voisinage (onboard.perception -> CH_MESH)"),
    "msgCollisionAlert":      ("MSG_COLLISION_ALERT",      "alerte de collision (onboard.perception -> CH_LOCAL prioritaire)"),
    "msgMissionCommand":      ("MSG_MISSION_COMMAND",      "commande de mission (c2.gcs -> CH_CMD)"),
    "msgTrajectoryProposal":  ("MSG_TRAJECTORY_PROPOSAL",  "proposition de trajectoire (onboard.taskAuction -> CH_MESH)"),
    "msgTrajectoryUpdate":    ("MSG_TRAJECTORY_UPDATE",    "trajectoire retenue (onboard.mission -> CH_LOCAL + CH_MESH)"),
    "msgFailureNotification": ("MSG_FAILURE_NOTIFICATION", "notification de defaillance (onboard.health -> CH_MESH + CH_CLOUD)"),
    "msgLinkQuality":         ("MSG_LINK_QUALITY",         "qualite de lien / QoS (onboard.linkRadio -> CH_MESH)"),
    "msgDroneState":          ("MSG_DRONE_STATE",          "etat de drone (onboard.telemetry -> CH_MESH)"),
}

# ---------------------------------------------------------------------------
# ALGORITHMES — 15 entrees. Chaque champ provient d'une fiche LikeC4.
#   attrs : attributs derives (nom, type, doc) references par les contraintes.
#   reqs  : (id, texte, contrainte) — la contrainte reference `alg.<attr>`.
# ---------------------------------------------------------------------------
ALGORITHMS = [
    {
        "alg_id": "ALG_TASK_ALLOCATION",
        "likec4_id": "algTaskAllocation",
        "source": "algorithms.c4 :: algTaskAllocation",
        "title": "Allocation de taches distribuee (CBBA v3)",
        "purpose": "Repartir un ensemble de taches entre agents heterogenes sans autorite centrale.",
        "params": ["neighborCount", "bidValue", "conflictWindow", "timeout"],
        "hypotheses": "Communication evenementielle (ED-CBBA) ; couts additifs ; agents cooperatifs ; partition detectable par heartbeat.",
        "contraintes": "Convergence globale non garantie sous partition persistante (garantie locale) ; optimalite 50% pire-cas ; budget radio.",
        "state_field": "local par agent + etat partage des encheres + etat de partition",
        "hosts": ["onboard.taskAuction", "edge.coordinator"],
        "msgs_in": ["msgTaskBid", "msgHeartbeat"],
        "msgs_out": ["msgTaskAssignment", "msgConsensusVote"],
        "attrs": [
            ("centralAuthority", "Boolean", "absence d'autorite centrale (purpose)"),
            ("convergenceScope", "String",  "portee de convergence garantie (contraintes)"),
            ("eventDriven",      "Boolean", "communication evenementielle ED-CBBA (hypotheses)"),
        ],
        "steps": [
            ("buildBundle",      "Construire le faisceau local : ordonner les taches par score d'enchere."),
            ("publishBids",      "Emettre les encheres vers les voisins (sur evenement, ED-CBBA)."),
            ("resolveConflicts", "Resolution de conflits : consensus des encheres, re-attribution en cas d'egalite."),
            ("announce",         "Annoncer l'attribution retenue (MSG_TASK_ASSIGNMENT)."),
        ],
        "states": [("idle", "aucune tache ouverte"), ("bidding", "encheres en cours"), ("consensus", "resolution de conflits en cours")],
        "reqs": [
            ("REQ_ALLOC_DISTRIBUTED", "L'allocation doit s'operer sans autorite centrale (purpose).", "alg.centralAuthority == false"),
            ("REQ_ALLOC_LOCAL_CONVERGENCE", "Sous partition persistante, seule la convergence locale est garantie (contraintes).", "alg.convergenceScope == 'local'"),
            ("REQ_ALLOC_EVENT_DRIVEN", "La communication doit etre evenementielle (ED-CBBA) pour respecter le budget radio (hypotheses).", "alg.eventDriven == true"),
        ],
    },
    {
        "alg_id": "ALG_CONSENSUS",
        "likec4_id": "algConsensus",
        "source": "algorithms.c4 :: algConsensus",
        "title": "Consensus distribue (CRDT semi-treillis)",
        "purpose": "Etablir un etat commun sans autorite centrale, tolerant aux partitions.",
        "params": ["gains", "periode", "seuilConvergence"],
        "hypotheses": "Graphe connexe a terme ; delais bornes.",
        "contraintes": "Partition prolongee : convergence non garantie.",
        "state_field": "etat partage replique",
        "hosts": ["onboard.taskAuction", "edge.coordinator"],
        "msgs_in": ["msgConsensusVote"],
        "msgs_out": ["msgConsensusVote"],
        "attrs": [
            ("centralAuthority",       "Boolean", "absence d'autorite centrale (purpose)"),
            ("convergenceGuaranteed",  "Boolean", "convergence garantie sous partition (contraintes)"),
            ("boundedDelay",           "Boolean", "delais bornes (hypotheses)"),
        ],
        "steps": [
            ("readLocal", "Lire l'etat local replique."),
            ("merge",     "Fusionner les etats recus (semi-treillis CRDT LWW)."),
            ("converge",  "Iterer jusqu'au seuil de convergence."),
            ("broadcast", "Diffuser l'etat fusionne aux voisins."),
        ],
        "states": [("converging", "etat en cours de convergence"), ("converged", "etat converge (ecart residuel sous seuil)")],
        "reqs": [
            ("REQ_CONSENSUS_DISTRIBUTED", "Le consensus doit s'etablir sans autorite centrale (purpose).", "alg.centralAuthority == false"),
            ("REQ_CONSENSUS_PARTITION", "Sous partition prolongee, la convergence n'est pas garantie (contraintes).", "alg.convergenceGuaranteed == false"),
            ("REQ_CONSENSUS_BOUNDED_DELAY", "La convergence suppose des delais bornes (hypotheses).", "alg.boundedDelay == true"),
        ],
    },
    {
        "alg_id": "ALG_FORMATION_CONTROL",
        "likec4_id": "algFormationControl",
        "source": "algorithms.c4 :: algFormationControl",
        "title": "Controle de formation",
        "purpose": "Maintenir une formation geometrique malgre les perturbations.",
        "params": ["geometrieCible", "gains", "distanceSeparationNominale"],
        "hypotheses": "Acces a une estimation relative fiable.",
        "contraintes": "Depend de la qualite de la perception relative.",
        "state_field": "local",
        "hosts": ["onboard.mission", "onboard.perception"],
        "msgs_in": ["msgPositionUpdate", "msgFormationState"],
        "msgs_out": ["msgFormationState"],
        "attrs": [
            ("error",                   "Real",    "erreur de formation (TBD, non chiffree au modele)"),
            ("tolerance",               "Real",    "tolerance de formation (TBD, non chiffree au modele)"),
            ("relativeEstimateReliable","Boolean", "fiabilite de l'estimation relative (hypotheses)"),
        ],
        "steps": [
            ("estimateRelative", "Estimer les positions relatives des voisins."),
            ("computeError",     "Calculer l'erreur par rapport a la geometrie cible."),
            ("correct",          "Emettre les consignes de correction de trajectoire."),
        ],
        "states": [("holding", "formation maintenue dans les tolerances"), ("correcting", "formation en correction (hors tolerance)")],
        "reqs": [
            ("REQ_FORMATION_HOLD", "Maintenir la geometrie cible malgre les perturbations (purpose).", "alg.error <= alg.tolerance"),
            ("REQ_FORMATION_PERCEPTION", "La qualite depend de la perception relative (contraintes).", "alg.relativeEstimateReliable == true"),
        ],
    },
    {
        "alg_id": "ALG_LEADER_ELECTION",
        "likec4_id": "algLeaderElection",
        "source": "algorithms.c4 :: algLeaderElection",
        "title": "Election de leader (reconfiguration apres perte)",
        "purpose": "Restaurer une autorite de coordination apres perte.",
        "params": ["seuilDetectionPerte", "priorite", "timeout"],
        "hypotheses": "Detection fiable de la perte du leader.",
        "contraintes": "Risque de double leader sous partition.",
        "state_field": "partage",
        "hosts": ["onboard.mission", "edge.coordinator"],
        "msgs_in": ["msgHeartbeat", "msgFailureNotification"],
        "msgs_out": ["msgConsensusVote"],
        "attrs": [
            ("leaderAssigned",         "Boolean", "leader designe (purpose)"),
            ("singleLeaderGuaranteed", "Boolean", "unicite du leader garantie (contraintes)"),
        ],
        "steps": [
            ("detectLoss", "Detecter la perte du leader courant (expiration heartbeat)."),
            ("vote",       "Election distribuee par vote (MSG_CONSENSUS_VOTE)."),
            ("assert",     "Designer le leader retenu selon priorite et timeout."),
        ],
        "states": [("follower", "aucun leader local, attente"), ("electing", "election en cours"), ("leader", "agent designe coordinateur temporaire")],
        "reqs": [
            ("REQ_ELECTION_RESTORE", "Restaurer une autorite de coordination apres perte (purpose).", "alg.leaderAssigned == true"),
            ("REQ_ELECTION_NO_DOUBLE", "Sous partition, le risque de double leader demeure (contraintes).", "alg.singleLeaderGuaranteed == false"),
        ],
    },
    {
        "alg_id": "ALG_PERCEPTION_FUSION",
        "likec4_id": "algPerceptionFusion",
        "source": "algorithms.c4 :: algPerceptionFusion",
        "title": "Fusion multi-capteurs (EKF/UKF)",
        "purpose": "Estimer l'etat de la plateforme et les pistes des voisins.",
        "params": ["bruitProcessus", "bruitMesure", "seuilRejetOutlier"],
        "hypotheses": "Bruits gaussiens ; linearisation acceptable (EKF).",
        "contraintes": "Divergence possible en cas d'outliers non filtres.",
        "state_field": "estime local",
        "hosts": ["onboard.perception", "edge.fusion"],
        "msgs_in": ["msgPositionUpdate", "msgNeighborState"],
        "msgs_out": ["msgPositionUpdate"],
        "attrs": [
            ("stateEstimated",  "Boolean", "etat estime (purpose)"),
            ("outlierRejected", "Boolean", "outliers filtres (contraintes)"),
        ],
        "steps": [
            ("predict",    "Prediction de l'etat (modele dynamique)."),
            ("update",     "Correction par les mesures (EKF/UKF) avec rejet d'outliers."),
            ("fuseTracks", "Fusion des pistes relatives des voisins."),
        ],
        "states": [],
        "reqs": [
            ("REQ_FUSION_ESTIMATE", "Estimer position, vitesse, attitude et pistes des voisins (purpose).", "alg.stateEstimated == true"),
            ("REQ_FUSION_OUTLIER", "La divergence est possible si les outliers ne sont pas filtres (contraintes).", "alg.outlierRejected == true"),
        ],
    },
    {
        "alg_id": "ALG_NAV_GNSS_DEGRADE",
        "likec4_id": "algNavigationGNSSDegrade",
        "source": "algorithms.c4 :: algNavigationGNSSDegrade",
        "title": "Navigation sous GNSS degrade",
        "purpose": "Maintenir une navigation utilisable malgre la perte du GNSS.",
        "params": ["seuilDerive", "seuilBasculeVIO", "zoneRepli"],
        "hypotheses": "Derive bornee sur la duree de bascule.",
        "contraintes": "Derive non bornee sans recalage : securite par RTL.",
        "state_field": "estime local + etat de bascule",
        "hosts": ["onboard.perception", "onboard.safety", "onboard.autopilot"],
        "msgs_in": ["msgPositionUpdate"],
        "msgs_out": ["msgPositionUpdate"],
        "attrs": [
            ("positionUsable", "Boolean", "position utilisable (purpose)"),
            ("rtlTriggered",   "Boolean", "repli RTL declenche (contraintes)"),
        ],
        "steps": [
            ("monitorGnss",  "Surveiller l'etat du GNSS (integrite, disponibilite)."),
            ("switchVio",    "Basculer EKF (IMU+odometrie+GNSS) vers VIO sur perte."),
            ("monitorDrift", "Surveiller la derive ; declencher la reduction de zone puis RTL."),
        ],
        "states": [("nominal", "navigation GNSS nominale"), ("degraded", "navigation degradee (VIO, derive bornee)"), ("rtl", "repli (Return-To-Launch) sur seuil de derive")],
        "reqs": [
            ("REQ_NAV_CONTINUITY", "Maintenir une navigation utilisable malgre la perte du GNSS (purpose).", "alg.positionUsable == true"),
            ("REQ_NAV_RTL", "Sans recalage, la derive n'est pas bornee : securite par RTL (contraintes).", "alg.rtlTriggered == true"),
        ],
    },
    {
        "alg_id": "ALG_COLLISION_AVOIDANCE",
        "likec4_id": "algCollisionAvoidance",
        "source": "algorithms.c4 :: algCollisionAvoidance",
        "title": "Evitement de collision (Control Barrier Functions)",
        "purpose": "Garantir la non-collision locale sans dependre du reseau.",
        "params": ["distanceMinimale", "horizon", "parametresBarriere"],
        "hypotheses": "Contraintes differentiellement realisables ; dynamique connue.",
        "contraintes": "Corrige E08 (SCI-2) : N=30 uniquement en simulation ; materiel reel = 5 robots ; violations residuelles 5,1 par essai a N=30.",
        "state_field": "local, sans etat partage",
        "hosts": ["onboard.safety", "onboard.perception", "onboard.autopilot"],
        "msgs_in": ["msgCollisionAlert", "msgPositionUpdate"],
        "msgs_out": [],
        "attrs": [
            ("linkDependent",  "Boolean", "dependance au reseau (purpose)"),
            ("provenAtScale30","Boolean", "preuve a N=30 (contraintes)"),
        ],
        "steps": [
            ("sense",   "Mesurer les positions et vitesses relatives."),
            ("barrier", "Evaluer la fonction de barriere de controle (CBF)."),
            ("correct", "Emettre la correction de consigne minimale preservant la securite (CH_LOCAL)."),
        ],
        "states": [],
        "reqs": [
            ("REQ_CA_LOCAL", "La non-collision doit etre garantie sans dependre du reseau (purpose).", "alg.linkDependent == false"),
            ("REQ_CA_SCALE", "A N=30, la preuve est uniquement en simulation ; le materiel reel est a 5 robots (contraintes).", "alg.provenAtScale30 == false"),
        ],
    },
    {
        "alg_id": "ALG_SAFETY_RULES",
        "likec4_id": "algSafetyRules",
        "source": "algorithms.c4 :: algSafetyRules",
        "title": "Surete par regles pre-approuvees",
        "purpose": "Garantir un comportement sur sans lien ni coordination.",
        "params": ["seuilsDerive", "frontiereGeographique", "seuilsEnergie"],
        "hypotheses": "Capteurs essentiels encore valides.",
        "contraintes": "Validation Monte-Carlo adversarial (N>=1000) NON faite.",
        "state_field": "local, etat de securite",
        "hosts": ["onboard.safety", "onboard.autopilot"],
        "msgs_in": ["msgCollisionAlert", "msgFailureNotification"],
        "msgs_out": [],
        "attrs": [
            ("linkDependent",        "Boolean", "dependance au lien de communication (purpose)"),
            ("adversarialValidated", "Boolean", "validation Monte-Carlo adversarial realisee (contraintes)"),
        ],
        "steps": [
            ("guard",   "Watchdog independant : evaluer les regles pre-approuvees."),
            ("decide",  "Decider RTL / atterrissage d'urgence / gel de manoeuvre."),
            ("enforce", "Appliquer la decision via l'autopilote (CH_LOCAL)."),
        ],
        "states": [("safe", "comportement nominal"), ("guarded", "regle de surete declenchee")],
        "reqs": [
            ("REQ_SAFETY_OFFLINE", "Fonctionner sans aucun lien de communication (purpose).", "alg.linkDependent == false"),
            ("REQ_SAFETY_ADVERSARIAL", "La validation Monte-Carlo adversarial (N>=1000) n'est pas faite (contraintes).", "alg.adversarialValidated == false"),
        ],
    },
    {
        "alg_id": "ALG_PATH_PLANNING",
        "likec4_id": "algPathPlanning",
        "source": "algorithms.c4 :: algPathPlanning",
        "title": "Planification de trajectoire (waypoints + MPC)",
        "purpose": "Produire et maintenir une trajectoire faisable vers l'objectif.",
        "params": ["horizonMPC", "couts", "poidsContraintes"],
        "hypotheses": "Modele dynamique suffisamment fidele.",
        "contraintes": "Re-optimisation centralisee seulement si le lien le permet.",
        "state_field": "plan local versionne",
        "hosts": ["onboard.mission", "c2.planner", "edge.coordinator"],
        "msgs_in": ["msgTrajectoryProposal"],
        "msgs_out": ["msgTrajectoryProposal", "msgTrajectoryUpdate"],
        "attrs": [
            ("feasible",                "Boolean", "trajectoire faisable (purpose)"),
            ("centralReoptConditional", "Boolean", "re-optimisation centralisee conditionnee au lien (contraintes)"),
        ],
        "steps": [
            ("plan",     "Produire le plan embarque versionne (waypoints par defaut)."),
            ("optimize", "MPC court horizon (Edge) si la ressource le permet."),
            ("commit",   "Publier la trajectoire retenue (MSG_TRAJECTORY_UPDATE)."),
        ],
        "states": [],
        "reqs": [
            ("REQ_PLAN_FEASIBLE", "Produire et maintenir une trajectoire faisable (purpose).", "alg.feasible == true"),
            ("REQ_PLAN_LINK", "La re-optimisation centralisee n'a lieu que si le lien le permet (contraintes).", "alg.centralReoptConditional == true"),
        ],
    },
    {
        "alg_id": "ALG_HEALTH_MONITORING",
        "likec4_id": "algHealthMonitoring",
        "source": "algorithms.c4 :: algHealthMonitoring",
        "title": "Surveillance d'etat et detection de faute",
        "purpose": "Detecter une faute et qualifier la degradation avant qu'elle ne devienne critique.",
        "params": ["seuilsDetection", "fenetresTemporelles", "hysteresis"],
        "hypotheses": "Les indicateurs internes sont observables.",
        "contraintes": "Faux positifs et faux negatifs non caracterises.",
        "state_field": "etat de sante local + agregat Edge",
        "hosts": ["onboard.health", "edge.coordinator"],
        "msgs_in": ["msgHeartbeat", "msgFailureNotification"],
        "msgs_out": ["msgFailureNotification"],
        "attrs": [
            ("earlyDetection",     "Boolean", "detection precoce de la degradation (purpose)"),
            ("fpFnCharacterized",  "Boolean", "faux positifs/negatifs caracterises (contraintes)"),
        ],
        "steps": [
            ("collect", "Collecter telemetrie interne, heartbeats voisins, indicateurs capteurs."),
            ("detect",  "Detecter l'anomalie (seuils, fenetres, hysteresis)."),
            ("qualify", "Qualifier la degradation (gravite, cause)."),
            ("notify",  "Emettre l'alarme / notification de defaillance."),
        ],
        "states": [("nominal", "sante nominale"), ("degraded", "degradation qualifiee"), ("faulted", "faute detectee")],
        "reqs": [
            ("REQ_HEALTH_EARLY", "Detecter et qualifier la degradation avant qu'elle ne devienne critique (purpose).", "alg.earlyDetection == true"),
            ("REQ_HEALTH_FP", "Faux positifs et faux negatifs non caracterises (contraintes).", "alg.fpFnCharacterized == false"),
        ],
    },
    {
        "alg_id": "ALG_ENERGY_AWARE",
        "likec4_id": "algEnergyAware",
        "source": "algorithms.c4 :: algEnergyAware",
        "title": "Planification sensible a l'energie",
        "purpose": "Maximiser la valeur de mission sous contrainte d'energie residuelle.",
        "params": ["margeSecurite", "seuilsRetour", "coutsEnergetiques"],
        "hypotheses": "Consommation previsible a court terme.",
        "contraintes": "Modele energetique a calibrer.",
        "state_field": "local",
        "hosts": ["onboard.mission", "onboard.autopilot"],
        "msgs_in": ["msgMissionCommand"],
        "msgs_out": [],
        "attrs": [
            ("missionValueMaximized", "Boolean", "valeur de mission maximisee (purpose)"),
            ("modelCalibrated",       "Boolean", "modele energetique calibre (contraintes)"),
        ],
        "steps": [
            ("assess",  "Evaluer l'energie residuelle et la consommation estimee."),
            ("tradeoff","Arbitrer couverture / duree / marge de repli."),
            ("replan",  "Planifier le repli si la marge franchit le seuil."),
        ],
        "states": [],
        "reqs": [
            ("REQ_ENERGY_VALUE", "Maximiser la valeur de mission sous contrainte d'energie residuelle (purpose).", "alg.missionValueMaximized == true"),
            ("REQ_ENERGY_CALIBRATION", "Le modele energetique reste a calibrer (contraintes).", "alg.modelCalibrated == false"),
        ],
    },
    {
        "alg_id": "ALG_EVENT_TRIGGERED_COMM",
        "likec4_id": "algEventTriggeredComm",
        "source": "e20-audit-completeness.c4 :: algEventTriggeredComm",
        "title": "Communication declenchee par evenement",
        "purpose": "Reduire le debit de coordination sans perdre la fraicheur des decisions critiques.",
        "params": ["seuilsDeclenchement", "periodeGarde", "hysteresis"],
        "hypotheses": "La surete locale ne depend pas de ce canal ; les alertes critiques restent sur CH_LOCAL.",
        "contraintes": "Sur-declenchement possible en regime turbulent ; borne de debit a 30 non chiffree.",
        "state_field": "local + compteurs de declenchement",
        "hosts": ["onboard.linkRadio", "edge.relay"],
        "msgs_in": ["msgLinkQuality", "msgDroneState", "msgConsensusVote"],
        "msgs_out": ["msgDroneState", "msgConsensusVote"],
        "attrs": [
            ("debitReduced",    "Boolean", "debit de coordination reduit (purpose)"),
            ("safetyDependent", "Boolean", "surete dependante de ce canal (hypotheses)"),
        ],
        "steps": [
            ("observe",  "Observer l'etat local et la qualite de lien."),
            ("evaluate", "Evaluer les seuils de declenchement (hysteresis, periode de garde)."),
            ("emit",     "Decider d'emettre (quoi, quand, a qui) sur evenement."),
        ],
        "states": [],
        "reqs": [
            ("REQ_ETC_REDUCE", "Reduire le debit de coordination sans perdre la fraicheur des decisions critiques (purpose).", "alg.debitReduced == true"),
            ("REQ_ETC_LOCAL_SAFETY", "La surete locale ne doit pas dependre de ce canal (hypotheses).", "alg.safetyDependent == false"),
        ],
    },
    {
        "alg_id": "ALG_COOPERATIVE_LOCALIZATION",
        "likec4_id": "algCooperativeLocalization",
        "source": "e20-audit-completeness.c4 :: algCooperativeLocalization",
        "title": "Localisation cooperative inter-agents",
        "purpose": "Fournir une estimation relative fiable sans dependre du GNSS ni d'une infrastructure.",
        "params": ["topologieVoisinage", "gainsConsensus", "bruitsMesure"],
        "hypotheses": "Graphe de voisinage suffisamment connexe ; horloges approximativement alignees.",
        "contraintes": "Degrade en partition profonde ; derive sans recalage absolu.",
        "state_field": "partage (consensus) + local",
        "hosts": ["onboard.perception", "edge.fusion"],
        "msgs_in": ["msgPositionUpdate", "msgNeighborState"],
        "msgs_out": ["msgPositionUpdate"],
        "attrs": [
            ("infrastructureDependent", "Boolean", "dependance a une infrastructure (purpose)"),
            ("partitionRobust",         "Boolean", "robustesse a la partition profonde (contraintes)"),
        ],
        "steps": [
            ("range",    "Acquerir les mesures relatives (UWB/ranging, odometrie, IMU)."),
            ("exchange", "Echanger les etats avec les voisins."),
            ("fuse",     "Fusionner par consensus pour estimer positions relatives et incertitudes."),
        ],
        "states": [("converging", "estimation relative en cours de convergence"), ("tracking", "estimation relative convergee (suivi)")],
        "reqs": [
            ("REQ_COOPLOC_INFRA_FREE", "Estimation relative fiable sans GNSS ni infrastructure (purpose).", "alg.infrastructureDependent == false"),
            ("REQ_COOPLOC_PARTITION", "Degradation en partition profonde ; derive sans recalage absolu (contraintes).", "alg.partitionRobust == false"),
        ],
    },
    {
        "alg_id": "ALG_FAULT_TOLERANT_CONTROL_ALLOC",
        "likec4_id": "algFaultTolerantControlAlloc",
        "source": "e20-audit-completeness.c4 :: algFaultTolerantControlAlloc",
        "title": "Allocation de commande tolerante aux fautes",
        "purpose": "Maintenir la commande malgre une faute actionneur, sans reconfiguration de mission.",
        "params": ["matriceAllocation", "limitesSaturation", "prioritesActionneurs"],
        "hypotheses": "La faute est detectee et qualifiee en amont (ALG_HEALTH_MONITORING).",
        "contraintes": "Degradation de manoeuvrabilite si faute critique ; validation HITL, pas de vol essaim.",
        "state_field": "local",
        "hosts": ["onboard.autopilot", "onboard.health"],
        "msgs_in": ["msgFailureNotification"],
        "msgs_out": [],
        "attrs": [
            ("commandMaintained", "Boolean", "commande maintenue malgre la faute (purpose)"),
            ("flightValidated",   "Boolean", "validation en vol d'essaim (contraintes)"),
        ],
        "steps": [
            ("readFault",  "Lire l'etat de sante des actionneurs."),
            ("reallocate", "Redistribuer l'effort de commande sur les actionneurs restants (gestion des saturations)."),
            ("apply",      "Emettre les signaux actionneurs recalcules."),
        ],
        "states": [],
        "reqs": [
            ("REQ_FTC_MAINTAIN", "Maintenir la commande malgre une faute actionneur (purpose).", "alg.commandMaintained == true"),
            ("REQ_FTC_HITL", "Validation HITL uniquement ; pas de vol d'essaim (contraintes).", "alg.flightValidated == false"),
        ],
    },
    {
        "alg_id": "ALG_JAMMING_RESILIENT_MODE",
        "likec4_id": "algJammingResilientMode",
        "source": "e20-audit-completeness.c4 :: algJammingResilientMode",
        "title": "Mode double cooperatif/autonome sous brouillage",
        "purpose": "Rester operationnel quand le canal de coordination est brouille ou degrade.",
        "params": ["seuilBascule", "hysteresis", "dwellTimeMinimal"],
        "hypotheses": "La surete locale (HOCBF/regles) reste active quel que soit le mode.",
        "contraintes": "Deux modes peuvent diverger sur la decision de mission ; reconvergence a la restauration du lien. (Seuil de bascule ~40% de pertes constate dans ADMOS.)",
        "state_field": "superviseur local + etat partage degrade",
        "hosts": ["onboard.mission", "onboard.perception", "edge.coordinator"],
        "msgs_in": ["msgLinkQuality", "msgDroneState"],
        "msgs_out": [],
        "attrs": [
            ("operational",      "Boolean", "reste operationnel sous brouillage (purpose)"),
            ("localSafetyActive","Boolean", "surete locale active quel que soit le mode (hypotheses)"),
        ],
        "steps": [
            ("monitorLink","Surveiller le taux de perte de paquets et la qualite de lien."),
            ("supervise",  "Basculer cooperative/autonome (hysteresis + dwell time minimal)."),
            ("applyMode",  "Appliquer le mode courant ; la surete locale reste active."),
        ],
        "states": [("cooperative", "fonctionnement cooperatif (consensus)"), ("autonomous", "fonctionnement autonome (plan embarque)")],
        "reqs": [
            ("REQ_JAM_OPERATIONAL", "Rester operationnel quand le canal de coordination est brouille (purpose).", "alg.operational == true"),
            ("REQ_JAM_SAFETY", "La surete locale reste active quel que soit le mode (hypotheses).", "alg.localSafetyActive == true"),
        ],
    },
]

assert len(ALGORITHMS) == 15, "il faut exactement 15 algorithmes"


def render(alg):
    L = []
    pkg = "SWARM3D::" + alg["alg_id"]
    item_in = [MESSAGES[k] for k in alg["msgs_in"]]
    item_out = [MESSAGES[k] for k in alg["msgs_out"]]
    part = alg["likec4_id"][0].upper() + alg["likec4_id"][1:]
    iface = part + "Interface"
    act = part + "Behavior"

    L.append(f"package '{pkg}' {{")
    L.append("    doc /*")
    L.append(f"      Specification SysML v2 — {alg['alg_id']} : {alg['title']}.")
    L.append(f"      Source du modele : {alg['source']}.")
    L.append(f"      Composants d'accueil : {', '.join(alg['hosts'])}.")
    L.append(f"      Objet : {alg['purpose']}")
    L.append("    */")
    L.append("")
    L.append("    import ScalarValues::*;")
    L.append("")

    # --- Donnees (messages) ---
    L.append("    // ===== Donnees : messages consommes / produits (cf messages.c4) =====")
    seen = {}
    for name, desc in item_in + item_out:
        seen[name] = desc
    for name in sorted(seen):
        L.append(f"    item def {name} {{")
        L.append(f"        doc /* {seen[name]}. Schema TBD (messages.c4) — non invente. */")
        L.append("    }")
    L.append("")

    # --- Interface ---
    L.append("    // ===== Interface : echanges de l'algorithme =====")
    L.append(f"    interface def {iface} {{")
    L.append(f"        doc /* Messages consommes (in) et produits (out) par {alg['alg_id']}. */")
    for name, _desc in item_in:
        L.append(f"        in item {name.lower()} : {name};")
    for name, _desc in item_out:
        L.append(f"        out item {name.lower()} : {name};")
    L.append("    }")
    L.append("")

    # --- Part def ---
    L.append(f"    // ===== Part def : {alg['alg_id']} comme partie du systeme =====")
    L.append(f"    part def {part} {{")
    L.append(f"        doc /* {alg['purpose']} */")
    L.append(f"        port exchange : {iface};")
    L.append("")
    L.append("        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.")
    for p in alg["params"]:
        L.append(f"        attribute {p} : ScalarValues::Real;")
    L.append("")
    L.append("        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).")
    for aname, atype, adoc in alg["attrs"]:
        L.append(f"        attribute {aname} : ScalarValues::{atype};  // {adoc}")
    L.append("")
    L.append(f"        doc /* Hypotheses : {alg['hypotheses']} */")
    L.append(f"        doc /* Contraintes : {alg['contraintes']} */")
    L.append(f"        doc /* Etat : {alg['state_field']} */")
    L.append("    }")
    L.append("")

    # --- Action def ---
    L.append("    // ===== Action def : comportement algorithmique =====")
    L.append(f"    action def {act} {{")
    for name, _desc in item_in:
        L.append(f"        in {name.lower()} : {name};")
    for name, _desc in item_out:
        L.append(f"        out {name.lower()} : {name};")
    L.append("")
    for sname, _sdoc in alg["steps"]:
        L.append(f"        action {sname} : {sname[0].upper()}{sname[1:]};")
    L.append("")
    if alg["steps"]:
        first = alg["steps"][0][0]
        rest = alg["steps"][1:]
        L.append(f"        first {first};")
        if rest:
            L.append(f"        then {' then '.join(s[0] for s in rest)};")
    L.append("    }")
    for sname, sdoc in alg["steps"]:
        L.append(f"    action def {sname[0].upper()}{sname[1:]} {{")
        L.append(f"        doc /* Etape : {sdoc} */")
        L.append("    }")
    L.append("")

    # --- State def (si pertinent) ---
    if alg["states"]:
        L.append("    // ===== State def : etats internes =====")
        L.append(f"    state def {part}State {{")
        for sname, sdoc in alg["states"]:
            L.append(f"        state {sname} {{ doc /* {sdoc} */ }}")
        for i in range(len(alg["states"]) - 1):
            L.append(f"        transition {alg['states'][i][0]} to {alg['states'][i+1][0]};")
        L.append("    }")
        L.append("")

    # --- Requirement def ---
    L.append("    // ===== Requirement def : exigences tracees =====")
    for rid, rdoc, rcons in alg["reqs"]:
        L.append(f"    requirement def {rid} {{")
        L.append(f"        doc /* {rdoc} */")
        L.append(f"        subject alg : {part};")
        L.append(f"        require constraint {{ {rcons} }}")
        L.append("    }")
        L.append("")

    # --- Tracabilite composant d'accueil ---
    host0 = "Host_" + alg["hosts"][0].replace(".", "_")
    others = alg["hosts"][1:] or ["aucun"]
    L.append("    // ===== Tracabilite : composant d'accueil =====")
    L.append(f"    part def {host0} {{")
    L.append(f"        doc /* Composant d'accueil principal : {alg['hosts'][0]} (secondaires : {', '.join(others)}). */")
    L.append(f"        perform action run_{alg['likec4_id']} : {act};")
    for rid, _rdoc, _rcons in alg["reqs"]:
        L.append(f"        satisfy {rid};")
    L.append("    }")
    L.append("}")

    return "\n".join(L) + "\n"


def render_likec4():
    """Emet ../sysml.c4 : elements specDoc + relations documentedBy + vue."""
    def c4s(s):
        # LikeC4 : les apostrophes terminent les chaines '...'. Le repo les
        # evite (style "d un", "l etat"). On remplace par une espace.
        return s.replace("'", " ")

    L = []
    L.append("// =============================================================================")
    L.append("//  SYSML-15 — SPECIFICATIONS SysML v2 DES 15 ALGORITHMES (carte t_d671a500)")
    L.append("//")
    L.append("//  Fichier purement ADDITIF : aucun identifiant, relation ni vue existant")
    L.append("//  n'est modifie. Les fiches `algorithm` (les 15) ne sont PAS touchees.")
    L.append("//")
    L.append("//  Decision de conception (orchestrateur) : LikeC4 n'est PAS SysML v2.")
    L.append("//  Les specs SysML v2 vivent dans des fichiers .sysml reels (dossier sysml/),")
    L.append("//  un par algorithme. LikeC4 les REFERENCE via des elements specDoc + une")
    L.append("//  relation `documentedBy`, et expose la tracabilite dans la vue")
    L.append("//  `algorithmSysmlTraceability`.")
    L.append("//")
    L.append("//  Validation (honnete) :")
    L.append("//    - syntaxe LikeC4 : docker exec likec4 likec4 validate /data -> Valid")
    L.append("//    - syntaxe SysML v2 : parseur structurel maison (sysml/validate_sysml.py),")
    L.append("//      15/15. AUCUN validateur OMG SysML v2 n'est installe (documente).")
    L.append("// =============================================================================")
    L.append("")
    L.append("model {")
    L.append("")
    L.append("  // ===========================================================================")
    L.append("  //  specDoc SysML v2 — un element par algorithme, pointant vers le fichier")
    L.append("  //  .sysml correspondant (depot dagornc/swarmdrones-likec4, dossier sysml/).")
    L.append("  // ===========================================================================")
    L.append("")
    for alg in ALGORITHMS:
        spec_id = "sysml" + alg["likec4_id"][3:]
        L.append(f"  {spec_id} = specDoc 'Specification SysML v2 — {alg['alg_id']}' {{")
        L.append("    #source-doc")
        L.append(f"    link https://github.com/dagornc/swarmdrones-likec4/blob/master/sysml/{alg['alg_id']}.sysml \"Source SysML v2 (sysml/{alg['alg_id']}.sysml)\"")
        L.append(f"    description 'Specification SysML v2 (notation textuelle OMG) — {c4s(alg['title'])}. Constructeurs : part def, action def, requirement def, interface def. Transcrite de {c4s(alg['source'])}.'")
        L.append("    metadata {")
        L.append(f"      algorithme '{alg['alg_id']}'")
        L.append("      format 'SysML v2 (OMG, notation textuelle)'")
        L.append(f"      fichier 'sysml/{alg['alg_id']}.sysml'")
        L.append("      validation 'structurelle maison (sysml/validate_sysml.py) — aucun validateur OMG installe'")
        L.append("    }")
        L.append("  }")
        L.append("")
    L.append("  // ===========================================================================")
    L.append("  //  Relations : algorithme -[documentedBy]-> specification SysML v2")
    L.append("  // ===========================================================================")
    L.append("")
    for alg in ALGORITHMS:
        spec_id = "sysml" + alg["likec4_id"][3:]
        L.append(f"  {alg['likec4_id']} -[documentedBy]-> {spec_id} 'specification SysML v2'")
    L.append("")
    L.append("}")
    L.append("")
    L.append("views {")
    L.append("")
    L.append("  // ===========================================================================")
    L.append("  //  SYSML-15 — TRACABILITE ALGORITHME -> SPECIFICATION SysML v2")
    L.append("  //  Projection (sens reel du metamodele) : algorithm -[documentedBy]-> specDoc")
    L.append("  //  Aucun arc n'est invente : seules les relations ci-dessus sont projetees.")
    L.append("  //  ETAT : 15/15 algorithmes references par une spec SysML v2.")
    L.append("  // ===========================================================================")
    L.append("")
    L.append("  view algorithmSysmlTraceability {")
    L.append("    title '04 · Algorithmique \\/ Traçabilite algorithme -> specification SysML v2'")
    L.append("    description '''")
    L.append("      Lecture : « ou est la specification SysML v2 de cet algorithme ? »")
    L.append("")
    L.append("      Chemin projete (sens reel du metamodele) :")
    L.append("        chaque algorithme est documente par sa specDoc SysML v2 (documentedBy).")
    L.append("")
    L.append("      Chaque specDoc reference le fichier sysml/<ALG_ID>.sysml du depot")
    L.append("      dagornc/swarmdrones-likec4 (notation textuelle OMG).")
    L.append("")
    L.append("      ETAT MESURE : 15/15 algorithmes portent une specification SysML v2.")
    L.append("      VALIDATION : syntaxe LikeC4 = likec4 validate (outil reel) ; syntaxe")
    L.append("      SysML v2 = parseur structurel maison uniquement (aucun validateur OMG")
    L.append("      installe — la conformite OMG reste a etablir avec SysIDE).")
    L.append("")
    L.append("      Complement : algorithmSpecTraceability (specifications PDF detaillees).")
    L.append("    '''")
    for alg in ALGORITHMS:
        L.append(f"    include {alg['likec4_id']}")
    for alg in ALGORITHMS:
        spec_id = "sysml" + alg["likec4_id"][3:]
        L.append(f"    include {spec_id}")
    L.append("    global style lectureZones")
    L.append("    autoLayout LeftRight")
    L.append("  }")
    L.append("}")
    return "\n".join(L) + "\n"


def main():
    manifest = []
    for alg in ALGORITHMS:
        fname = f"{alg['alg_id']}.sysml"
        path = os.path.join(HERE, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(alg))
        manifest.append((alg["alg_id"], alg["likec4_id"], alg["source"], fname))

    # Emission du fichier LikeC4 de tracabilite (sysml.c4 a la racine du depot)
    lc_path = os.path.join(os.path.dirname(HERE), "sysml.c4")
    with open(lc_path, "w", encoding="utf-8") as f:
        f.write(render_likec4())
    print("  ecrit sysml.c4 (racine du depot)")

    if "--manifest" in sys.argv:
        print("# TABLE DE TRACABILITE (TSV)")
        print("alg_id\tlikec4_id\tsource\tfichier")
        for alg_id, lc, src, fn in manifest:
            print(f"{alg_id}\t{lc}\t{src}\t{fn}")

    print(f"{len(ALGORITHMS)}/15 specifications SysML v2 emises dans sysml/.")


if __name__ == "__main__":
    main()
