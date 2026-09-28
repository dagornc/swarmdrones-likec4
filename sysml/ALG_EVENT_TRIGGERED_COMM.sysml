package 'SWARM3D::ALG_EVENT_TRIGGERED_COMM' {
    doc /*
      Specification SysML v2 — ALG_EVENT_TRIGGERED_COMM : Communication declenchee par evenement.
      Source du modele : e20-audit-completeness.c4 :: algEventTriggeredComm.
      Composants d'accueil : onboard.linkRadio, edge.relay.
      Objet : Reduire le debit de coordination sans perdre la fraicheur des decisions critiques.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_CONSENSUS_VOTE {
        doc /* vote de consensus (onboard.taskAuction -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_DRONE_STATE {
        doc /* etat de drone (onboard.telemetry -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_LINK_QUALITY {
        doc /* qualite de lien / QoS (onboard.linkRadio -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgEventTriggeredCommInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_EVENT_TRIGGERED_COMM. */
        in item msg_link_quality : MSG_LINK_QUALITY;
        in item msg_drone_state : MSG_DRONE_STATE;
        in item msg_consensus_vote : MSG_CONSENSUS_VOTE;
        out item msg_drone_state : MSG_DRONE_STATE;
        out item msg_consensus_vote : MSG_CONSENSUS_VOTE;
    }

    // ===== Part def : ALG_EVENT_TRIGGERED_COMM comme partie du systeme =====
    part def AlgEventTriggeredComm {
        doc /* Reduire le debit de coordination sans perdre la fraicheur des decisions critiques. */
        port exchange : AlgEventTriggeredCommInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute seuilsDeclenchement : ScalarValues::Real;
        attribute periodeGarde : ScalarValues::Real;
        attribute hysteresis : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute debitReduced : ScalarValues::Boolean;  // debit de coordination reduit (purpose)
        attribute safetyDependent : ScalarValues::Boolean;  // surete dependante de ce canal (hypotheses)

        doc /* Hypotheses : La surete locale ne depend pas de ce canal ; les alertes critiques restent sur CH_LOCAL. */
        doc /* Contraintes : Sur-declenchement possible en regime turbulent ; borne de debit a 30 non chiffree. */
        doc /* Etat : local + compteurs de declenchement */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgEventTriggeredCommBehavior {
        in msg_link_quality : MSG_LINK_QUALITY;
        in msg_drone_state : MSG_DRONE_STATE;
        in msg_consensus_vote : MSG_CONSENSUS_VOTE;
        out msg_drone_state : MSG_DRONE_STATE;
        out msg_consensus_vote : MSG_CONSENSUS_VOTE;

        action observe : Observe;
        action evaluate : Evaluate;
        action emit : Emit;

        first observe;
        then evaluate then emit;
    }
    action def Observe {
        doc /* Etape : Observer l'etat local et la qualite de lien. */
    }
    action def Evaluate {
        doc /* Etape : Evaluer les seuils de declenchement (hysteresis, periode de garde). */
    }
    action def Emit {
        doc /* Etape : Decider d'emettre (quoi, quand, a qui) sur evenement. */
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_ETC_REDUCE {
        doc /* Reduire le debit de coordination sans perdre la fraicheur des decisions critiques (purpose). */
        subject alg : AlgEventTriggeredComm;
        require constraint { alg.debitReduced == true }
    }

    requirement def REQ_ETC_LOCAL_SAFETY {
        doc /* La surete locale ne doit pas dependre de ce canal (hypotheses). */
        subject alg : AlgEventTriggeredComm;
        require constraint { alg.safetyDependent == false }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_linkRadio {
        doc /* Composant d'accueil principal : onboard.linkRadio (secondaires : edge.relay). */
        perform action run_algEventTriggeredComm : AlgEventTriggeredCommBehavior;
        satisfy REQ_ETC_REDUCE;
        satisfy REQ_ETC_LOCAL_SAFETY;
    }
}
