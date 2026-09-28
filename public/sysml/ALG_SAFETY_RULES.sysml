package 'SWARM3D::ALG_SAFETY_RULES' {
    doc /*
      Specification SysML v2 — ALG_SAFETY_RULES : Surete par regles pre-approuvees.
      Source du modele : algorithms.c4 :: algSafetyRules.
      Composants d'accueil : onboard.safety, onboard.autopilot.
      Objet : Garantir un comportement sur sans lien ni coordination.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_COLLISION_ALERT {
        doc /* alerte de collision (onboard.perception -> CH_LOCAL prioritaire). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_FAILURE_NOTIFICATION {
        doc /* notification de defaillance (onboard.health -> CH_MESH + CH_CLOUD). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgSafetyRulesInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_SAFETY_RULES. */
        in item msg_collision_alert : MSG_COLLISION_ALERT;
        in item msg_failure_notification : MSG_FAILURE_NOTIFICATION;
    }

    // ===== Part def : ALG_SAFETY_RULES comme partie du systeme =====
    part def AlgSafetyRules {
        doc /* Garantir un comportement sur sans lien ni coordination. */
        port exchange : AlgSafetyRulesInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute seuilsDerive : ScalarValues::Real;
        attribute frontiereGeographique : ScalarValues::Real;
        attribute seuilsEnergie : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute linkDependent : ScalarValues::Boolean;  // dependance au lien de communication (purpose)
        attribute adversarialValidated : ScalarValues::Boolean;  // validation Monte-Carlo adversarial realisee (contraintes)

        doc /* Hypotheses : Capteurs essentiels encore valides. */
        doc /* Contraintes : Validation Monte-Carlo adversarial (N>=1000) NON faite. */
        doc /* Etat : local, etat de securite */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgSafetyRulesBehavior {
        in msg_collision_alert : MSG_COLLISION_ALERT;
        in msg_failure_notification : MSG_FAILURE_NOTIFICATION;

        action guard : Guard;
        action decide : Decide;
        action enforce : Enforce;

        first guard;
        then decide then enforce;
    }
    action def Guard {
        doc /* Etape : Watchdog independant : evaluer les regles pre-approuvees. */
    }
    action def Decide {
        doc /* Etape : Decider RTL / atterrissage d'urgence / gel de manoeuvre. */
    }
    action def Enforce {
        doc /* Etape : Appliquer la decision via l'autopilote (CH_LOCAL). */
    }

    // ===== State def : etats internes =====
    state def AlgSafetyRulesState {
        state safe { doc /* comportement nominal */ }
        state guarded { doc /* regle de surete declenchee */ }
        transition safe to guarded;
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_SAFETY_OFFLINE {
        doc /* Fonctionner sans aucun lien de communication (purpose). */
        subject alg : AlgSafetyRules;
        require constraint { alg.linkDependent == false }
    }

    requirement def REQ_SAFETY_ADVERSARIAL {
        doc /* La validation Monte-Carlo adversarial (N>=1000) n'est pas faite (contraintes). */
        subject alg : AlgSafetyRules;
        require constraint { alg.adversarialValidated == false }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_safety {
        doc /* Composant d'accueil principal : onboard.safety (secondaires : onboard.autopilot). */
        perform action run_algSafetyRules : AlgSafetyRulesBehavior;
        satisfy REQ_SAFETY_OFFLINE;
        satisfy REQ_SAFETY_ADVERSARIAL;
    }
}
