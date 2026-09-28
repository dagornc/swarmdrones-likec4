package 'SWARM3D::ALG_TASK_ALLOCATION' {
    doc /*
      Specification SysML v2 — ALG_TASK_ALLOCATION : Allocation de taches distribuee (CBBA v3).
      Source du modele : algorithms.c4 :: algTaskAllocation.
      Composants d'accueil : onboard.taskAuction, edge.coordinator.
      Objet : Repartir un ensemble de taches entre agents heterogenes sans autorite centrale.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_CONSENSUS_VOTE {
        doc /* vote de consensus (onboard.taskAuction -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_HEARTBEAT {
        doc /* battement de vivacite (onboard.health -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_TASK_ASSIGNMENT {
        doc /* attribution de tache (onboard.taskAuction -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_TASK_BID {
        doc /* enchere de tache (onboard.taskAuction -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgTaskAllocationInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_TASK_ALLOCATION. */
        in item msg_task_bid : MSG_TASK_BID;
        in item msg_heartbeat : MSG_HEARTBEAT;
        out item msg_task_assignment : MSG_TASK_ASSIGNMENT;
        out item msg_consensus_vote : MSG_CONSENSUS_VOTE;
    }

    // ===== Part def : ALG_TASK_ALLOCATION comme partie du systeme =====
    part def AlgTaskAllocation {
        doc /* Repartir un ensemble de taches entre agents heterogenes sans autorite centrale. */
        port exchange : AlgTaskAllocationInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute neighborCount : ScalarValues::Real;
        attribute bidValue : ScalarValues::Real;
        attribute conflictWindow : ScalarValues::Real;
        attribute timeout : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute centralAuthority : ScalarValues::Boolean;  // absence d'autorite centrale (purpose)
        attribute convergenceScope : ScalarValues::String;  // portee de convergence garantie (contraintes)
        attribute eventDriven : ScalarValues::Boolean;  // communication evenementielle ED-CBBA (hypotheses)

        doc /* Hypotheses : Communication evenementielle (ED-CBBA) ; couts additifs ; agents cooperatifs ; partition detectable par heartbeat. */
        doc /* Contraintes : Convergence globale non garantie sous partition persistante (garantie locale) ; optimalite 50% pire-cas ; budget radio. */
        doc /* Etat : local par agent + etat partage des encheres + etat de partition */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgTaskAllocationBehavior {
        in msg_task_bid : MSG_TASK_BID;
        in msg_heartbeat : MSG_HEARTBEAT;
        out msg_task_assignment : MSG_TASK_ASSIGNMENT;
        out msg_consensus_vote : MSG_CONSENSUS_VOTE;

        action buildBundle : BuildBundle;
        action publishBids : PublishBids;
        action resolveConflicts : ResolveConflicts;
        action announce : Announce;

        first buildBundle;
        then publishBids then resolveConflicts then announce;
    }
    action def BuildBundle {
        doc /* Etape : Construire le faisceau local : ordonner les taches par score d'enchere. */
    }
    action def PublishBids {
        doc /* Etape : Emettre les encheres vers les voisins (sur evenement, ED-CBBA). */
    }
    action def ResolveConflicts {
        doc /* Etape : Resolution de conflits : consensus des encheres, re-attribution en cas d'egalite. */
    }
    action def Announce {
        doc /* Etape : Annoncer l'attribution retenue (MSG_TASK_ASSIGNMENT). */
    }

    // ===== State def : etats internes =====
    state def AlgTaskAllocationState {
        state idle { doc /* aucune tache ouverte */ }
        state bidding { doc /* encheres en cours */ }
        state consensus { doc /* resolution de conflits en cours */ }
        transition idle to bidding;
        transition bidding to consensus;
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_ALLOC_DISTRIBUTED {
        doc /* L'allocation doit s'operer sans autorite centrale (purpose). */
        subject alg : AlgTaskAllocation;
        require constraint { alg.centralAuthority == false }
    }

    requirement def REQ_ALLOC_LOCAL_CONVERGENCE {
        doc /* Sous partition persistante, seule la convergence locale est garantie (contraintes). */
        subject alg : AlgTaskAllocation;
        require constraint { alg.convergenceScope == 'local' }
    }

    requirement def REQ_ALLOC_EVENT_DRIVEN {
        doc /* La communication doit etre evenementielle (ED-CBBA) pour respecter le budget radio (hypotheses). */
        subject alg : AlgTaskAllocation;
        require constraint { alg.eventDriven == true }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_taskAuction {
        doc /* Composant d'accueil principal : onboard.taskAuction (secondaires : edge.coordinator). */
        perform action run_algTaskAllocation : AlgTaskAllocationBehavior;
        satisfy REQ_ALLOC_DISTRIBUTED;
        satisfy REQ_ALLOC_LOCAL_CONVERGENCE;
        satisfy REQ_ALLOC_EVENT_DRIVEN;
    }
}
