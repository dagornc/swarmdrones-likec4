package 'SWARM3D::ALG_NAV_GNSS_DEGRADE' {
    doc /*
      Specification SysML v2 — ALG_NAV_GNSS_DEGRADE : Navigation sous GNSS degrade.
      Source du modele : algorithms.c4 :: algNavigationGNSSDegrade.
      Composants d'accueil : onboard.perception, onboard.safety, onboard.autopilot.
      Objet : Maintenir une navigation utilisable malgre la perte du GNSS.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_POSITION_UPDATE {
        doc /* mise a jour de position (onboard.perception -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgNavigationGNSSDegradeInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_NAV_GNSS_DEGRADE. */
        in item msg_position_update : MSG_POSITION_UPDATE;
        out item msg_position_update : MSG_POSITION_UPDATE;
    }

    // ===== Part def : ALG_NAV_GNSS_DEGRADE comme partie du systeme =====
    part def AlgNavigationGNSSDegrade {
        doc /* Maintenir une navigation utilisable malgre la perte du GNSS. */
        port exchange : AlgNavigationGNSSDegradeInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute seuilDerive : ScalarValues::Real;
        attribute seuilBasculeVIO : ScalarValues::Real;
        attribute zoneRepli : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute positionUsable : ScalarValues::Boolean;  // position utilisable (purpose)
        attribute rtlTriggered : ScalarValues::Boolean;  // repli RTL declenche (contraintes)

        doc /* Hypotheses : Derive bornee sur la duree de bascule. */
        doc /* Contraintes : Derive non bornee sans recalage : securite par RTL. */
        doc /* Etat : estime local + etat de bascule */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgNavigationGNSSDegradeBehavior {
        in msg_position_update : MSG_POSITION_UPDATE;
        out msg_position_update : MSG_POSITION_UPDATE;

        action monitorGnss : MonitorGnss;
        action switchVio : SwitchVio;
        action monitorDrift : MonitorDrift;

        first monitorGnss;
        then switchVio then monitorDrift;
    }
    action def MonitorGnss {
        doc /* Etape : Surveiller l'etat du GNSS (integrite, disponibilite). */
    }
    action def SwitchVio {
        doc /* Etape : Basculer EKF (IMU+odometrie+GNSS) vers VIO sur perte. */
    }
    action def MonitorDrift {
        doc /* Etape : Surveiller la derive ; declencher la reduction de zone puis RTL. */
    }

    // ===== State def : etats internes =====
    state def AlgNavigationGNSSDegradeState {
        state nominal { doc /* navigation GNSS nominale */ }
        state degraded { doc /* navigation degradee (VIO, derive bornee) */ }
        state rtl { doc /* repli (Return-To-Launch) sur seuil de derive */ }
        transition nominal to degraded;
        transition degraded to rtl;
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_NAV_CONTINUITY {
        doc /* Maintenir une navigation utilisable malgre la perte du GNSS (purpose). */
        subject alg : AlgNavigationGNSSDegrade;
        require constraint { alg.positionUsable == true }
    }

    requirement def REQ_NAV_RTL {
        doc /* Sans recalage, la derive n'est pas bornee : securite par RTL (contraintes). */
        subject alg : AlgNavigationGNSSDegrade;
        require constraint { alg.rtlTriggered == true }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_perception {
        doc /* Composant d'accueil principal : onboard.perception (secondaires : onboard.safety, onboard.autopilot). */
        perform action run_algNavigationGNSSDegrade : AlgNavigationGNSSDegradeBehavior;
        satisfy REQ_NAV_CONTINUITY;
        satisfy REQ_NAV_RTL;
    }
}
