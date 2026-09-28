package 'SWARM3D::ALG_CONSENSUS' {
    doc /*
      Specification SysML v2 — ALG_CONSENSUS : Consensus distribue (CRDT semi-treillis).
      Source du modele : algorithms.c4 :: algConsensus.
      Composants d'accueil : onboard.taskAuction, edge.coordinator.
      Objet : Etablir un etat commun sans autorite centrale, tolerant aux partitions.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_CONSENSUS_VOTE {
        doc /* vote de consensus (onboard.taskAuction -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgConsensusInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_CONSENSUS. */
        in item msg_consensus_vote : MSG_CONSENSUS_VOTE;
        out item msg_consensus_vote : MSG_CONSENSUS_VOTE;
    }

    // ===== Part def : ALG_CONSENSUS comme partie du systeme =====
    part def AlgConsensus {
        doc /* Etablir un etat commun sans autorite centrale, tolerant aux partitions. */
        port exchange : AlgConsensusInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute gains : ScalarValues::Real;
        attribute periode : ScalarValues::Real;
        attribute seuilConvergence : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute centralAuthority : ScalarValues::Boolean;  // absence d'autorite centrale (purpose)
        attribute convergenceGuaranteed : ScalarValues::Boolean;  // convergence garantie sous partition (contraintes)
        attribute boundedDelay : ScalarValues::Boolean;  // delais bornes (hypotheses)

        doc /* Hypotheses : Graphe connexe a terme ; delais bornes. */
        doc /* Contraintes : Partition prolongee : convergence non garantie. */
        doc /* Etat : etat partage replique */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgConsensusBehavior {
        in msg_consensus_vote : MSG_CONSENSUS_VOTE;
        out msg_consensus_vote : MSG_CONSENSUS_VOTE;

        action readLocal : ReadLocal;
        action merge : Merge;
        action converge : Converge;
        action broadcast : Broadcast;

        first readLocal;
        then merge then converge then broadcast;
    }
    action def ReadLocal {
        doc /* Etape : Lire l'etat local replique. */
    }
    action def Merge {
        doc /* Etape : Fusionner les etats recus (semi-treillis CRDT LWW). */
    }
    action def Converge {
        doc /* Etape : Iterer jusqu'au seuil de convergence. */
    }
    action def Broadcast {
        doc /* Etape : Diffuser l'etat fusionne aux voisins. */
    }

    // ===== State def : etats internes =====
    state def AlgConsensusState {
        state converging { doc /* etat en cours de convergence */ }
        state converged { doc /* etat converge (ecart residuel sous seuil) */ }
        transition converging to converged;
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_CONSENSUS_DISTRIBUTED {
        doc /* Le consensus doit s'etablir sans autorite centrale (purpose). */
        subject alg : AlgConsensus;
        require constraint { alg.centralAuthority == false }
    }

    requirement def REQ_CONSENSUS_PARTITION {
        doc /* Sous partition prolongee, la convergence n'est pas garantie (contraintes). */
        subject alg : AlgConsensus;
        require constraint { alg.convergenceGuaranteed == false }
    }

    requirement def REQ_CONSENSUS_BOUNDED_DELAY {
        doc /* La convergence suppose des delais bornes (hypotheses). */
        subject alg : AlgConsensus;
        require constraint { alg.boundedDelay == true }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_taskAuction {
        doc /* Composant d'accueil principal : onboard.taskAuction (secondaires : edge.coordinator). */
        perform action run_algConsensus : AlgConsensusBehavior;
        satisfy REQ_CONSENSUS_DISTRIBUTED;
        satisfy REQ_CONSENSUS_PARTITION;
        satisfy REQ_CONSENSUS_BOUNDED_DELAY;
    }
}
