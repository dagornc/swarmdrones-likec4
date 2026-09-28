package 'SWARM3D::ALG_FAULT_TOLERANT_CONTROL_ALLOC' {
    doc /*
      Specification SysML v2 — ALG_FAULT_TOLERANT_CONTROL_ALLOC : Allocation de commande tolerante aux fautes.
      Source du modele : e20-audit-completeness.c4 :: algFaultTolerantControlAlloc.
      Composants d'accueil : onboard.autopilot, onboard.health.
      Objet : Maintenir la commande malgre une faute actionneur, sans reconfiguration de mission.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_FAILURE_NOTIFICATION {
        doc /* notification de defaillance (onboard.health -> CH_MESH + CH_CLOUD). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgFaultTolerantControlAllocInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_FAULT_TOLERANT_CONTROL_ALLOC. */
        in item msg_failure_notification : MSG_FAILURE_NOTIFICATION;
    }

    // ===== Part def : ALG_FAULT_TOLERANT_CONTROL_ALLOC comme partie du systeme =====
    part def AlgFaultTolerantControlAlloc {
        doc /* Maintenir la commande malgre une faute actionneur, sans reconfiguration de mission. */
        port exchange : AlgFaultTolerantControlAllocInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute matriceAllocation : ScalarValues::Real;
        attribute limitesSaturation : ScalarValues::Real;
        attribute prioritesActionneurs : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute commandMaintained : ScalarValues::Boolean;  // commande maintenue malgre la faute (purpose)
        attribute flightValidated : ScalarValues::Boolean;  // validation en vol d'essaim (contraintes)

        doc /* Hypotheses : La faute est detectee et qualifiee en amont (ALG_HEALTH_MONITORING). */
        doc /* Contraintes : Degradation de manoeuvrabilite si faute critique ; validation HITL, pas de vol essaim. */
        doc /* Etat : local */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgFaultTolerantControlAllocBehavior {
        in msg_failure_notification : MSG_FAILURE_NOTIFICATION;

        action readFault : ReadFault;
        action reallocate : Reallocate;
        action apply : Apply;

        first readFault;
        then reallocate then apply;
    }
    action def ReadFault {
        doc /* Etape : Lire l'etat de sante des actionneurs. */
    }
    action def Reallocate {
        doc /* Etape : Redistribuer l'effort de commande sur les actionneurs restants (gestion des saturations). */
    }
    action def Apply {
        doc /* Etape : Emettre les signaux actionneurs recalcules. */
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_FTC_MAINTAIN {
        doc /* Maintenir la commande malgre une faute actionneur (purpose). */
        subject alg : AlgFaultTolerantControlAlloc;
        require constraint { alg.commandMaintained == true }
    }

    requirement def REQ_FTC_HITL {
        doc /* Validation HITL uniquement ; pas de vol d'essaim (contraintes). */
        subject alg : AlgFaultTolerantControlAlloc;
        require constraint { alg.flightValidated == false }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_autopilot {
        doc /* Composant d'accueil principal : onboard.autopilot (secondaires : onboard.health). */
        perform action run_algFaultTolerantControlAlloc : AlgFaultTolerantControlAllocBehavior;
        satisfy REQ_FTC_MAINTAIN;
        satisfy REQ_FTC_HITL;
    }
}
