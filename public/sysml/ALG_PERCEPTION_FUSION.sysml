package 'SWARM3D::ALG_PERCEPTION_FUSION' {
    doc /*
      Specification SysML v2 — ALG_PERCEPTION_FUSION : Fusion multi-capteurs (EKF/UKF).
      Source du modele : algorithms.c4 :: algPerceptionFusion.
      Composants d'accueil : onboard.perception, edge.fusion.
      Objet : Estimer l'etat de la plateforme et les pistes des voisins.
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
    interface def AlgPerceptionFusionInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_PERCEPTION_FUSION. */
        in item msg_position_update : MSG_POSITION_UPDATE;
        in item msg_neighbor_state : MSG_NEIGHBOR_STATE;
        out item msg_position_update : MSG_POSITION_UPDATE;
    }

    // ===== Part def : ALG_PERCEPTION_FUSION comme partie du systeme =====
    part def AlgPerceptionFusion {
        doc /* Estimer l'etat de la plateforme et les pistes des voisins. */
        port exchange : AlgPerceptionFusionInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute bruitProcessus : ScalarValues::Real;
        attribute bruitMesure : ScalarValues::Real;
        attribute seuilRejetOutlier : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute stateEstimated : ScalarValues::Boolean;  // etat estime (purpose)
        attribute outlierRejected : ScalarValues::Boolean;  // outliers filtres (contraintes)

        doc /* Hypotheses : Bruits gaussiens ; linearisation acceptable (EKF). */
        doc /* Contraintes : Divergence possible en cas d'outliers non filtres. */
        doc /* Etat : estime local */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgPerceptionFusionBehavior {
        in msg_position_update : MSG_POSITION_UPDATE;
        in msg_neighbor_state : MSG_NEIGHBOR_STATE;
        out msg_position_update : MSG_POSITION_UPDATE;

        action predict : Predict;
        action update : Update;
        action fuseTracks : FuseTracks;

        first predict;
        then update then fuseTracks;
    }
    action def Predict {
        doc /* Etape : Prediction de l'etat (modele dynamique). */
    }
    action def Update {
        doc /* Etape : Correction par les mesures (EKF/UKF) avec rejet d'outliers. */
    }
    action def FuseTracks {
        doc /* Etape : Fusion des pistes relatives des voisins. */
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_FUSION_ESTIMATE {
        doc /* Estimer position, vitesse, attitude et pistes des voisins (purpose). */
        subject alg : AlgPerceptionFusion;
        require constraint { alg.stateEstimated == true }
    }

    requirement def REQ_FUSION_OUTLIER {
        doc /* La divergence est possible si les outliers ne sont pas filtres (contraintes). */
        subject alg : AlgPerceptionFusion;
        require constraint { alg.outlierRejected == true }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_perception {
        doc /* Composant d'accueil principal : onboard.perception (secondaires : edge.fusion). */
        perform action run_algPerceptionFusion : AlgPerceptionFusionBehavior;
        satisfy REQ_FUSION_ESTIMATE;
        satisfy REQ_FUSION_OUTLIER;
    }
}
