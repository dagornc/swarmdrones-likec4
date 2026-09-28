package 'SWARM3D::ALG_PATH_PLANNING' {
    doc /*
      Specification SysML v2 — ALG_PATH_PLANNING : Planification de trajectoire (waypoints + MPC).
      Source du modele : algorithms.c4 :: algPathPlanning.
      Composants d'accueil : onboard.mission, c2.planner, edge.coordinator.
      Objet : Produire et maintenir une trajectoire faisable vers l'objectif.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_TRAJECTORY_PROPOSAL {
        doc /* proposition de trajectoire (onboard.taskAuction -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_TRAJECTORY_UPDATE {
        doc /* trajectoire retenue (onboard.mission -> CH_LOCAL + CH_MESH). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgPathPlanningInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_PATH_PLANNING. */
        in item msg_trajectory_proposal : MSG_TRAJECTORY_PROPOSAL;
        out item msg_trajectory_proposal : MSG_TRAJECTORY_PROPOSAL;
        out item msg_trajectory_update : MSG_TRAJECTORY_UPDATE;
    }

    // ===== Part def : ALG_PATH_PLANNING comme partie du systeme =====
    part def AlgPathPlanning {
        doc /* Produire et maintenir une trajectoire faisable vers l'objectif. */
        port exchange : AlgPathPlanningInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute horizonMPC : ScalarValues::Real;
        attribute couts : ScalarValues::Real;
        attribute poidsContraintes : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute feasible : ScalarValues::Boolean;  // trajectoire faisable (purpose)
        attribute centralReoptConditional : ScalarValues::Boolean;  // re-optimisation centralisee conditionnee au lien (contraintes)

        doc /* Hypotheses : Modele dynamique suffisamment fidele. */
        doc /* Contraintes : Re-optimisation centralisee seulement si le lien le permet. */
        doc /* Etat : plan local versionne */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgPathPlanningBehavior {
        in msg_trajectory_proposal : MSG_TRAJECTORY_PROPOSAL;
        out msg_trajectory_proposal : MSG_TRAJECTORY_PROPOSAL;
        out msg_trajectory_update : MSG_TRAJECTORY_UPDATE;

        action plan : Plan;
        action optimize : Optimize;
        action commit : Commit;

        first plan;
        then optimize then commit;
    }
    action def Plan {
        doc /* Etape : Produire le plan embarque versionne (waypoints par defaut). */
    }
    action def Optimize {
        doc /* Etape : MPC court horizon (Edge) si la ressource le permet. */
    }
    action def Commit {
        doc /* Etape : Publier la trajectoire retenue (MSG_TRAJECTORY_UPDATE). */
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_PLAN_FEASIBLE {
        doc /* Produire et maintenir une trajectoire faisable (purpose). */
        subject alg : AlgPathPlanning;
        require constraint { alg.feasible == true }
    }

    requirement def REQ_PLAN_LINK {
        doc /* La re-optimisation centralisee n'a lieu que si le lien le permet (contraintes). */
        subject alg : AlgPathPlanning;
        require constraint { alg.centralReoptConditional == true }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_mission {
        doc /* Composant d'accueil principal : onboard.mission (secondaires : c2.planner, edge.coordinator). */
        perform action run_algPathPlanning : AlgPathPlanningBehavior;
        satisfy REQ_PLAN_FEASIBLE;
        satisfy REQ_PLAN_LINK;
    }
}
