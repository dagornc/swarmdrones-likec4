package 'SWARM3D::ALG_COLLISION_AVOIDANCE' {
    doc /*
      Specification SysML v2 — ALG_COLLISION_AVOIDANCE : Evitement de collision (Control Barrier Functions).
      Source du modele : algorithms.c4 :: algCollisionAvoidance.
      Composants d'accueil : onboard.safety, onboard.perception, onboard.autopilot.
      Objet : Garantir la non-collision locale sans dependre du reseau.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_COLLISION_ALERT {
        doc /* alerte de collision (onboard.perception -> CH_LOCAL prioritaire). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_POSITION_UPDATE {
        doc /* mise a jour de position (onboard.perception -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgCollisionAvoidanceInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_COLLISION_AVOIDANCE. */
        in item msg_collision_alert : MSG_COLLISION_ALERT;
        in item msg_position_update : MSG_POSITION_UPDATE;
    }

    // ===== Part def : ALG_COLLISION_AVOIDANCE comme partie du systeme =====
    part def AlgCollisionAvoidance {
        doc /* Garantir la non-collision locale sans dependre du reseau. */
        port exchange : AlgCollisionAvoidanceInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute distanceMinimale : ScalarValues::Real;
        attribute horizon : ScalarValues::Real;
        attribute parametresBarriere : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute linkDependent : ScalarValues::Boolean;  // dependance au reseau (purpose)
        attribute provenAtScale30 : ScalarValues::Boolean;  // preuve a N=30 (contraintes)

        doc /* Hypotheses : Contraintes differentiellement realisables ; dynamique connue. */
        doc /* Contraintes : Corrige E08 (SCI-2) : N=30 uniquement en simulation ; materiel reel = 5 robots ; violations residuelles 5,1 par essai a N=30. */
        doc /* Etat : local, sans etat partage */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgCollisionAvoidanceBehavior {
        in msg_collision_alert : MSG_COLLISION_ALERT;
        in msg_position_update : MSG_POSITION_UPDATE;

        action sense : Sense;
        action barrier : Barrier;
        action correct : Correct;

        first sense;
        then barrier then correct;
    }
    action def Sense {
        doc /* Etape : Mesurer les positions et vitesses relatives. */
    }
    action def Barrier {
        doc /* Etape : Evaluer la fonction de barriere de controle (CBF). */
    }
    action def Correct {
        doc /* Etape : Emettre la correction de consigne minimale preservant la securite (CH_LOCAL). */
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_CA_LOCAL {
        doc /* La non-collision doit etre garantie sans dependre du reseau (purpose). */
        subject alg : AlgCollisionAvoidance;
        require constraint { alg.linkDependent == false }
    }

    requirement def REQ_CA_SCALE {
        doc /* A N=30, la preuve est uniquement en simulation ; le materiel reel est a 5 robots (contraintes). */
        subject alg : AlgCollisionAvoidance;
        require constraint { alg.provenAtScale30 == false }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_safety {
        doc /* Composant d'accueil principal : onboard.safety (secondaires : onboard.perception, onboard.autopilot). */
        perform action run_algCollisionAvoidance : AlgCollisionAvoidanceBehavior;
        satisfy REQ_CA_LOCAL;
        satisfy REQ_CA_SCALE;
    }
}
