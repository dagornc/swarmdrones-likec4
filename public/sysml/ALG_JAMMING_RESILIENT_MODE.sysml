package 'SWARM3D::ALG_JAMMING_RESILIENT_MODE' {
    doc /*
      Specification SysML v2 — ALG_JAMMING_RESILIENT_MODE : Mode double cooperatif/autonome sous brouillage.
      Source du modele : e20-audit-completeness.c4 :: algJammingResilientMode.
      Composants d'accueil : onboard.mission, onboard.perception, edge.coordinator.
      Objet : Rester operationnel quand le canal de coordination est brouille ou degrade.
    */

    import ScalarValues::*;

    // ===== Donnees : messages consommes / produits (cf messages.c4) =====
    item def MSG_DRONE_STATE {
        doc /* etat de drone (onboard.telemetry -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }
    item def MSG_LINK_QUALITY {
        doc /* qualite de lien / QoS (onboard.linkRadio -> CH_MESH). Schema TBD (messages.c4) — non invente. */
    }

    // ===== Interface : echanges de l'algorithme =====
    interface def AlgJammingResilientModeInterface {
        doc /* Messages consommes (in) et produits (out) par ALG_JAMMING_RESILIENT_MODE. */
        in item msg_link_quality : MSG_LINK_QUALITY;
        in item msg_drone_state : MSG_DRONE_STATE;
    }

    // ===== Part def : ALG_JAMMING_RESILIENT_MODE comme partie du systeme =====
    part def AlgJammingResilientMode {
        doc /* Rester operationnel quand le canal de coordination est brouille ou degrade. */
        port exchange : AlgJammingResilientModeInterface;

        // Parametres (repris de metadata.parameters) — sans valeur : TBD au modele.
        attribute seuilBascule : ScalarValues::Real;
        attribute hysteresis : ScalarValues::Real;
        attribute dwellTimeMinimal : ScalarValues::Real;

        // Attributs derives (transcription qualitative de purpose/hypotheses/contraintes).
        attribute operational : ScalarValues::Boolean;  // reste operationnel sous brouillage (purpose)
        attribute localSafetyActive : ScalarValues::Boolean;  // surete locale active quel que soit le mode (hypotheses)

        doc /* Hypotheses : La surete locale (HOCBF/regles) reste active quel que soit le mode. */
        doc /* Contraintes : Deux modes peuvent diverger sur la decision de mission ; reconvergence a la restauration du lien. (Seuil de bascule ~40% de pertes constate dans ADMOS.) */
        doc /* Etat : superviseur local + etat partage degrade */
    }

    // ===== Action def : comportement algorithmique =====
    action def AlgJammingResilientModeBehavior {
        in msg_link_quality : MSG_LINK_QUALITY;
        in msg_drone_state : MSG_DRONE_STATE;

        action monitorLink : MonitorLink;
        action supervise : Supervise;
        action applyMode : ApplyMode;

        first monitorLink;
        then supervise then applyMode;
    }
    action def MonitorLink {
        doc /* Etape : Surveiller le taux de perte de paquets et la qualite de lien. */
    }
    action def Supervise {
        doc /* Etape : Basculer cooperative/autonome (hysteresis + dwell time minimal). */
    }
    action def ApplyMode {
        doc /* Etape : Appliquer le mode courant ; la surete locale reste active. */
    }

    // ===== State def : etats internes =====
    state def AlgJammingResilientModeState {
        state cooperative { doc /* fonctionnement cooperatif (consensus) */ }
        state autonomous { doc /* fonctionnement autonome (plan embarque) */ }
        transition cooperative to autonomous;
    }

    // ===== Requirement def : exigences tracees =====
    requirement def REQ_JAM_OPERATIONAL {
        doc /* Rester operationnel quand le canal de coordination est brouille (purpose). */
        subject alg : AlgJammingResilientMode;
        require constraint { alg.operational == true }
    }

    requirement def REQ_JAM_SAFETY {
        doc /* La surete locale reste active quel que soit le mode (hypotheses). */
        subject alg : AlgJammingResilientMode;
        require constraint { alg.localSafetyActive == true }
    }

    // ===== Tracabilite : composant d'accueil =====
    part def Host_onboard_mission {
        doc /* Composant d'accueil principal : onboard.mission (secondaires : onboard.perception, edge.coordinator). */
        perform action run_algJammingResilientMode : AlgJammingResilientModeBehavior;
        satisfy REQ_JAM_OPERATIONAL;
        satisfy REQ_JAM_SAFETY;
    }
}
