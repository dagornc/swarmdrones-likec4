package 'SWARM3D::ALG_COOPERATIVE_LOCALIZATION' {
    doc /*
      Specification SysML v2 — ALG_COOPERATIVE_LOCALIZATION : Localisation cooperative inter-agents.
      Source du modele : e20-audit-completeness.c4 :: algCooperativeLocalization.
      Composants d'accueil : onboard.perception, edge.fusion.
      Objet : Fournir une estimation relative fiable sans dependre du GNSS ni d'une infrastructure.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_NEIGHBOR_STATE {
        doc /* etat de voisinage (onboard.perception -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_POSITION_UPDATE {
        doc /* mise a jour de position (onboard.perception -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgCooperativeLocalizationInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_COOPERATIVE_LOCALIZATION. */
        in item msg_position_update : MSG_POSITION_UPDATE;
        in item msg_neighbor_state : MSG_NEIGHBOR_STATE;
        out item msg_position_update : MSG_POSITION_UPDATE;
    }

    // ===== Part def : ALG_COOPERATIVE_LOCALIZATION comme partie du systeme =====
    part def AlgCooperativeLocalization {
        doc /* Fournir une estimation relative fiable sans dependre du GNSS ni d'une infrastructure. */
        port exchange : AlgCooperativeLocalizationInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute topologieVoisinage : ScalarValues::Real;
        attribute gainsConsensus : ScalarValues::Real;
        attribute bruitsMesure : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute infrastructureDependent : ScalarValues::Boolean;  // dependance a une infrastructure (purpose)
        attribute partitionRobust : ScalarValues::Boolean;  // robustesse a la partition profonde (contraintes)

        doc /* Hypotheses : Graphe de voisinage suffisamment connexe ; horloges approximativement alignees. */
        doc /* Contraintes : Degrade en partition profonde ; derive sans recalage absolu. */
        doc /* Etat : partage (consensus) + local */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgCooperativeLocalizationBehavior {
        in msg_position_update : MSG_POSITION_UPDATE;
        in msg_neighbor_state : MSG_NEIGHBOR_STATE;
        out msg_position_update : MSG_POSITION_UPDATE;

        action range : Range;
        action exchange : Exchange;
        action fuse : Fuse;

        first range;
        then exchange then fuse;
    }
    action def Range {
        doc /* Etape : Acquerir les mesures relatives (UWB/ranging, odometrie, IMU). */
    }
    action def Exchange {
        doc /* Etape : Echanger les etats avec les voisins. */
    }
    action def Fuse {
        doc /* Etape : Fusionner par consensus pour estimer positions relatives et incertitudes. */
    }

    // ===== State def : etats internes =====
    state def AlgCooperativeLocalizationState {
        state converging { doc /* estimation relative en cours de convergence */ }
        state tracking { doc /* estimation relative convergee (suivi) */ }
        transition converging to tracking;
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_COOPLOC_INFRA_FREE {
        doc /* Estimation relative fiable sans GNSS ni infrastructure (purpose). */
        subject alg : AlgCooperativeLocalization;
        require constraint { alg.infrastructureDependent == false }
    }

    requirement def REQ_COOPLOC_PARTITION {
        doc /* Degradation en partition profonde ; derive sans recalage absolu (contraintes). */
        subject alg : AlgCooperativeLocalization;
        require constraint { alg.partitionRobust == false }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_perception {
        doc /* Composant d'accueil principal : onboard.perception (secondaires : edge.fusion). */
        perform action run_algCooperativeLocalization : AlgCooperativeLocalizationBehavior;
        satisfy REQ_COOPLOC_INFRA_FREE;
        satisfy REQ_COOPLOC_PARTITION;
    }
}
