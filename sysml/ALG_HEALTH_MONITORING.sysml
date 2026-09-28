package 'SWARM3D::ALG_HEALTH_MONITORING' {
    doc /*
      Specification SysML v2 — ALG_HEALTH_MONITORING : Surveillance d'etat et detection de faute.
      Source du modele : algorithms.c4 :: algHealthMonitoring.
      Composants d'accueil : onboard.health, edge.coordinator.
      Objet : Detecter une faute et qualifier la degradation avant qu'elle ne devienne critique.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_FAILURE_NOTIFICATION {
        doc /* notification de defaillance (onboard.health -> CH_MESH + CH_CLOUD). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_HEARTBEAT {
        doc /* battement de vivacite (onboard.health -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgHealthMonitoringInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_HEALTH_MONITORING. */
        in item msg_heartbeat : MSG_HEARTBEAT;
        in item msg_failure_notification : MSG_FAILURE_NOTIFICATION;
        out item msg_failure_notification : MSG_FAILURE_NOTIFICATION;
    }

    // ===== Part def : ALG_HEALTH_MONITORING comme partie du systeme =====
    part def AlgHealthMonitoring {
        doc /* Detecter une faute et qualifier la degradation avant qu'elle ne devienne critique. */
        port exchange : AlgHealthMonitoringInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute seuilsDetection : ScalarValues::Real;
        attribute fenetresTemporelles : ScalarValues::Real;
        attribute hysteresis : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute earlyDetection : ScalarValues::Boolean;  // detection precoce de la degradation (purpose)
        attribute fpFnCharacterized : ScalarValues::Boolean;  // faux positifs/negatifs caracterises (contraintes)

        doc /* Hypotheses : Les indicateurs internes sont observables. */
        doc /* Contraintes : Faux positifs et faux negatifs non caracterises. */
        doc /* Etat : etat de sante local + agregat Edge */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgHealthMonitoringBehavior {
        in msg_heartbeat : MSG_HEARTBEAT;
        in msg_failure_notification : MSG_FAILURE_NOTIFICATION;
        out msg_failure_notification : MSG_FAILURE_NOTIFICATION;

        action collect : Collect;
        action detect : Detect;
        action qualify : Qualify;
        action notify : Notify;

        first collect;
        then detect then qualify then notify;
    }
    action def Collect {
        doc /* Etape : Collecter telemetrie interne, heartbeats voisins, indicateurs capteurs. */
    }
    action def Detect {
        doc /* Etape : Detecter l'anomalie (seuils, fenetres, hysteresis). */
    }
    action def Qualify {
        doc /* Etape : Qualifier la degradation (gravite, cause). */
    }
    action def Notify {
        doc /* Etape : Emettre l'alarme / notification de defaillance. */
    }

    // ===== State def : etats internes =====
    state def AlgHealthMonitoringState {
        state nominal { doc /* sante nominale */ }
        state degraded { doc /* degradation qualifiee */ }
        state faulted { doc /* faute detectee */ }
        transition nominal to degraded;
        transition degraded to faulted;
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_HEALTH_EARLY {
        doc /* Detecter et qualifier la degradation avant qu'elle ne devienne critique (purpose). */
        subject alg : AlgHealthMonitoring;
        require constraint { alg.earlyDetection == true }
    }

    requirement def REQ_HEALTH_FP {
        doc /* Faux positifs et faux negatifs non caracterises (contraintes). */
        subject alg : AlgHealthMonitoring;
        require constraint { alg.fpFnCharacterized == false }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_health {
        doc /* Composant d'accueil principal : onboard.health (secondaires : edge.coordinator). */
        perform action run_algHealthMonitoring : AlgHealthMonitoringBehavior;
        satisfy REQ_HEALTH_EARLY;
        satisfy REQ_HEALTH_FP;
    }
}
