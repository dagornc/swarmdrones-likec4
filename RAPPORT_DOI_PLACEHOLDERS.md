# Rapport — Traitement des DOI placeholders (SPEC-13-DOI-FIX)

**Carte** : `t_0395e67e` (SPEC-13-DOI-FIX)
**Date** : 2026-09-28
**Périmètre** : 8 DOI placeholders non résolus dans 5 spécifications

---

## 1. Conclusion

Les **8 DOI placeholders** ont été traités. Aucun n'a pu être résolu en une référence réelle vérifiable : les articles correspondants n'étaient pas identifiables dans les journaux de recherche (`research_*.md`) ni dans le corpus documentaire.

**Décision appliquée** : conformément à la règle de mission du modèle (« si aucun article fiable n'est trouvé, écrire "aucun article trouvé" et NE PAS noter SUPPORTED »), chaque référence a été **annotée comme retirée** plutôt que supprimée silencieusement — la trace du placeholder est conservée pour auditabilité.

**Aucun DOI n'a été inventé.**

---

## 2. Traitement par placeholder

| Spec | DOI placeholder | Traitement |
|---|---|---|
| leader_election | `10.1109/TRO.2025.xxx` | Annoté « référence non vérifiée, retirée » |
| safety_rules | `10.1109/TRO.2024.xxx` | Annoté « référence non vérifiée, retirée » |
| health_monitoring | `10.1109/TR.2024.xxx` | Annoté « référence non vérifiée, retirée » |
| health_monitoring | `10.1016/j.jpowsour.2023.xxx` | Annoté « référence non vérifiée, retirée » |
| energy_aware | `10.1109/TRO.2025.xxx` | Annoté « référence non vérifiée, retirée » |
| energy_aware | `10.1016/j.jpowsour.2026.xxx` | Annoté « référence non vérifiée, retirée » |
| energy_aware | `10.1109/TIE.2023.xxx` | Annoté « référence non vérifiée, retirée » |
| event_triggered_comm | `10.1109/TSP.2024.xxx` | Annoté « référence non vérifiée, retirée » |

**Forme de l'annotation** (exemple) :
> Zhang et al. (2025), « Health-Aware Leader Election for Resilient UAV Swarms », IEEE Trans. Robotics — référence non vérifiée, retirée (DOI placeholder 10.1109/TRO.2025.xxx non résolu)

---

## 3. Artefacts régénérés

| Spec | DOCX | PDF |
|---|---|---|
| leader_election | 47 222 o | 240 923 o |
| safety_rules | 47 699 o | 236 218 o |
| health_monitoring | 47 341 o | 238 287 o |
| energy_aware | 46 744 o | 230 893 o |
| event_triggered_comm | 47 325 o | 237 276 o |

Générateurs modifiés : `make_<slug>_spec.py` (5 fichiers).

---

## 4. Réserve méthodologique

**Les placeholders restent visibles dans le texte** sous forme d'annotation. Un lecteur qui cherche `10.1109/TRO.2025.xxx` le trouvera — mais dans une phrase qui dit explicitement que la référence est retirée. C'est un choix délibéré d'auditabilité : masquer le placeholder aurait rendu la correction invérifiable.

**Alternative non retenue** : supprimer purement la ligne de référence. Plus propre visuellement, mais perd la trace de l'erreur d'origine.

---

## 5. Action orchestrateur complémentaire

Le worker a traité les 8 placeholders et régénéré les DOCX/PDF, mais n'a pas :
- produit ce rapport (créé par l'orchestrateur) ;
- republié les 5 PDF corrigés sur GitHub.

**Republication effectuée par l'orchestrateur** : les 5 PDF corrigés ont été copiés dans `specification/` et poussés sur `dagornc/swarmdrones-likec4` (master).
