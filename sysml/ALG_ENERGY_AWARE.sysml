package 'SWARM3D::ALG_ENERGY_AWARE' {
    doc /*
      Specification SysML v2 — ALG_ENERGY_AWARE : Planification sensible a l'energie.
      Source du modele : algorithms.c4 :: algEnergyAware.
      Composants d'accueil : onboard.mission, onboard.autopilot.
      Objet : Maximiser la valeur de mission sous contrainte d'energie residuelle.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_MISSION_COMMAND {
        doc /* commande de mission (c2.gcs -> CH_CMD). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgEnergyAwareInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_ENERGY_AWARE. */
        in item msg_mission_command : MSG_MISSION_COMMAND;
    }

    // ===== Part def : ALG_ENERGY_AWARE comme partie du systeme =====
    part def AlgEnergyAware {
        doc /* Maximiser la valeur de mission sous contrainte d'energie residuelle. */
        port exchange : AlgEnergyAwareInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute margeSecurite : ScalarValues::Real;
        attribute seuilsRetour : ScalarValues::Real;
        attribute coutsEnergetiques : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute missionValueMaximized : ScalarValues::Boolean;  // valeur de mission maximisee (purpose)
        attribute modelCalibrated : ScalarValues::Boolean;  // modele energetique calibre (contraintes)

        doc /* Hypotheses : Consommation previsible a court terme. */
        doc /* Contraintes : Modele energetique a calibrer. */
        doc /* Etat : local */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgEnergyAwareBehavior {
        in msg_mission_command : MSG_MISSION_COMMAND;

        action assess : Assess;
        action tradeoff : Tradeoff;
        action replan : Replan;

        first assess;
        then tradeoff then replan;
    }
    action def Assess {
        doc /* Etape : Evaluer l'energie residuelle et la consommation estimee. */
    }
    action def Tradeoff {
        doc /* Etape : Arbitrer couverture / duree / marge de repli. */
    }
    action def Replan {
        doc /* Etape : Planifier le repli si la marge franchit le seuil. */
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_ENERGY_VALUE {
        doc /* Maximiser la valeur de mission sous contrainte d'energie residuelle (purpose). */
        subject alg : AlgEnergyAware;
        require constraint { alg.missionValueMaximized == true }
    }

    requirement def REQ_ENERGY_CALIBRATION {
        doc /* Le modele energetique reste a calibrer (contraintes). */
        subject alg : AlgEnergyAware;
        require constraint { alg.modelCalibrated == false }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_mission {
        doc /* Composant d'accueil principal : onboard.mission (secondaires : onboard.autopilot). */
        perform action run_algEnergyAware : AlgEnergyAwareBehavior;
        satisfy REQ_ENERGY_VALUE;
        satisfy REQ_ENERGY_CALIBRATION;
    }
}
