package 'SWARM3D::ALG_LEADER_ELECTION' {
    doc /*
      Specification SysML v2 — ALG_LEADER_ELECTION : Election de leader (reconfiguration apres perte).
      Source du modele : algorithms.c4 :: algLeaderElection.
      Composants d'accueil : onboard.mission, edge.coordinator.
      Objet : Restaurer une autorite de coordination apres perte.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_CONSENSUS_VOTE {
        doc /* vote de consensus (onboard.taskAuction -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_FAILURE_NOTIFICATION {
        doc /* notification de defaillance (onboard.health -> CH_MESH + CH_CLOUD). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_HEARTBEAT {
        doc /* battement de vivacite (onboard.health -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgLeaderElectionInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_LEADER_ELECTION. */
        in item msg_heartbeat : MSG_HEARTBEAT;
        in item msg_failure_notification : MSG_FAILURE_NOTIFICATION;
        out item msg_consensus_vote : MSG_CONSENSUS_VOTE;
    }

    // ===== Part def : ALG_LEADER_ELECTION comme partie du systeme =====
    part def AlgLeaderElection {
        doc /* Restaurer une autorite de coordination apres perte. */
        port exchange : AlgLeaderElectionInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute seuilDetectionPerte : ScalarValues::Real;
        attribute priorite : ScalarValues::Real;
        attribute timeout : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute leaderAssigned : ScalarValues::Boolean;  // leader designe (purpose)
        attribute singleLeaderGuaranteed : ScalarValues::Boolean;  // unicite du leader garantie (contraintes)

        doc /* Hypotheses : Detection fiable de la perte du leader. */
        doc /* Contraintes : Risque de double leader sous partition. */
        doc /* Etat : partage */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgLeaderElectionBehavior {
        in msg_heartbeat : MSG_HEARTBEAT;
        in msg_failure_notification : MSG_FAILURE_NOTIFICATION;
        out msg_consensus_vote : MSG_CONSENSUS_VOTE;

        action detectLoss : DetectLoss;
        action vote : Vote;
        action assert : Assert;

        first detectLoss;
        then vote then assert;
    }
    action def DetectLoss {
        doc /* Etape : Detecter la perte du leader courant (expiration heartbeat). */
    }
    action def Vote {
        doc /* Etape : Election distribuee par vote (MSG_CONSENSUS_VOTE). */
    }
    action def Assert {
        doc /* Etape : Designer le leader retenu selon priorite et timeout. */
    }

    // ===== State def : etats internes =====
    state def AlgLeaderElectionState {
        state follower { doc /* aucun leader local, attente */ }
        state electing { doc /* election en cours */ }
        state leader { doc /* agent designe coordinateur temporaire */ }
        transition follower to electing;
        transition electing to leader;
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_ELECTION_RESTORE {
        doc /* Restaurer une autorite de coordination apres perte (purpose). */
        subject alg : AlgLeaderElection;
        require constraint { alg.leaderAssigned == true }
    }

    requirement def REQ_ELECTION_NO_DOUBLE {
        doc /* Sous partition, le risque de double leader demeure (contraintes). */
        subject alg : AlgLeaderElection;
        require constraint { alg.singleLeaderGuaranteed == false }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_mission {
        doc /* Composant d'accueil principal : onboard.mission (secondaires : edge.coordinator). */
        perform action run_algLeaderElection : AlgLeaderElectionBehavior;
        satisfy REQ_ELECTION_RESTORE;
        satisfy REQ_ELECTION_NO_DOUBLE;
    }
}
