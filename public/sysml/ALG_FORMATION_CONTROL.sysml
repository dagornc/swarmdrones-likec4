package 'SWARM3D::ALG_FORMATION_CONTROL' {
    doc /*
      Specification SysML v2 — ALG_FORMATION_CONTROL : Controle de formation.
      Source du modele : algorithms.c4 :: algFormationControl.
      Composants d'accueil : onboard.mission, onboard.perception.
      Objet : Maintenir une formation geometrique malgre les perturbations.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_FORMATION_STATE {
        doc /* etat de la formation (onboard.mission -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_POSITION_UPDATE {
        doc /* mise a jour de position (onboard.perception -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgFormationControlInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_FORMATION_CONTROL. */
        in item msg_position_update : MSG_POSITION_UPDATE;
        in item msg_formation_state : MSG_FORMATION_STATE;
        out item msg_formation_state : MSG_FORMATION_STATE;
    }

    // ===== Part def : ALG_FORMATION_CONTROL comme partie du systeme =====
    part def AlgFormationControl {
        doc /* Maintenir une formation geometrique malgre les perturbations. */
        port exchange : AlgFormationControlInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute geometrieCible : ScalarValues::Real;
        attribute gains : ScalarValues::Real;
        attribute distanceSeparationNominale : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute error : ScalarValues::Real;  // erreur de formation (TBD, non chiffree au modele)
        attribute tolerance : ScalarValues::Real;  // tolerance de formation (TBD, non chiffree au modele)
        attribute relativeEstimateReliable : ScalarValues::Boolean;  // fiabilite de l'estimation relative (hypotheses)

        doc /* Hypotheses : Acces a une estimation relative fiable. */
        doc /* Contraintes : Depend de la qualite de la perception relative. */
        doc /* Etat : local */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgFormationControlBehavior {
        in msg_position_update : MSG_POSITION_UPDATE;
        in msg_formation_state : MSG_FORMATION_STATE;
        out msg_formation_state : MSG_FORMATION_STATE;

        action estimateRelative : EstimateRelative;
        action computeError : ComputeError;
        action correct : Correct;

        first estimateRelative;
        then computeError then correct;
    }
    action def EstimateRelative {
        doc /* Etape : Estimer les positions relatives des voisins. */
    }
    action def ComputeError {
        doc /* Etape : Calculer l'erreur par rapport a la geometrie cible. */
    }
    action def Correct {
        doc /* Etape : Emettre les consignes de correction de trajectoire. */
    }

    // ===== State def : etats internes =====
    state def AlgFormationControlState {
        state holding { doc /* formation maintenue dans les tolerances */ }
        state correcting { doc /* formation en correction (hors tolerance) */ }
        transition holding to correcting;
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_FORMATION_HOLD {
        doc /* Maintenir la geometrie cible malgre les perturbations (purpose). */
        subject alg : AlgFormationControl;
        require constraint { alg.error <= alg.tolerance }
    }

    requirement def REQ_FORMATION_PERCEPTION {
        doc /* La qualite depend de la perception relative (contraintes). */
        subject alg : AlgFormationControl;
        require constraint { alg.relativeEstimateReliable == true }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_mission {
        doc /* Composant d'accueil principal : onboard.mission (secondaires : onboard.perception). */
        perform action run_algFormationControl : AlgFormationControlBehavior;
        satisfy REQ_FORMATION_HOLD;
        satisfy REQ_FORMATION_PERCEPTION;
    }
}
