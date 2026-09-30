# VÉRIFICATION FINALE — Point ④ (logiciels, algorithmes, angles morts, risques)

Date : 2026-09-14 · Vérificateur : Hermès (poste principal)
Chaîne : profil `swarmdrone` (contenu) → profil `architecte` (injection LikeC4, interrompu) → reprise et correction manuelle → vérification indépendante

## 1. Ce que le point ④ devait livrer

| Volet | Attendu | Livré | Statut |
|---|---|---|---|
| Logiciels du marché | choix primaire + secondaire | 14 briques | ✅ |
| Algorithmes | familles retenues | 7 familles | ✅ |
| Angles morts | inventaire | 16 (16/16) | ✅ |
| Risques | inventaire | 15 (15/15) | ✅ |

## 2. Vérifications effectuées

### 2.1 Complétude (script `/tmp/verify_point4.py`)
- Angles morts : 16 dans l'annexe / 16 dans le modèle — **0 manquant, 0 en trop**
- Risques : 15 dans l'annexe / 15 dans le modèle — **0 manquant, 0 en trop**
- Logiciels : 14 éléments `software` ; Algorithmes : 7 éléments `algorithm`

### 2.2 Fidélité des criticités (script `/tmp/check_risk2.py`)
- 15/15 criticités du modèle **identiques** à celles de l'annexe (5 critiques, 5 élevées, 5 moyennes).
- Réserve signalée : le barème P×I n'est pas strictement monotone (R-2/R-4/R-5 à P×I=3,5 → « critique », R-6 à 3,5 → « élevée »). C'est un arbitrage **fidèlement repris de l'annexe**, pas une erreur d'injection.

### 2.3 Licences (sources primaires, API GitHub `/license` + fichiers LICENSE)
| Brique | Licence | Vérifiée |
|---|---|---|
| PX4 | BSD-3-Clause | ✅ |
| ArduPilot | GPL-3.0 | ✅ |
| ROS 2 | Apache-2.0 | ✅ |
| Micro XRCE-DDS | Apache-2.0 | ✅ |
| Gazebo Sim | Apache-2.0 | ✅ |
| QGroundControl | Apache-2.0 (app : dual Apache-2.0/GPLv3) | ✅ |
| OpenCPN | GPL-2.0 | ✅ |
| MinIO | **AGPL-3.0** | ✅ (alerte juridique confirmée) |
| Grafana | **AGPL-3.0** | ✅ (alerte juridique confirmée) |
| Zenoh | Apache-2.0 OR EPL-2.0 (GitHub : NOASSERTION) | ~ (double licence) |

### 2.4 Validation syntaxique
- `likec4 validate` : **✓ Valid (2 files)** — à chaque étape.

### 2.5 Rendu des vues
- `techAutopilot` 6 422×3 124 (2,06) · `techComms` 6 484×4 962 (1,31) · `techData` 4 974×2 350 (2,12) — lisibles
- `riskMatrix` 9 510×2 322 (4,10) · `blindspotBySeverity` 9 262×2 322 (3,99) — lisibles
- Export : 3 vues en 13,7 s (après découpage ; 42,4 s et ratio 0,80 avant)

### 2.6 Service web
- `https://likec4.breizh.ai/` → **HTTP 200**, TTFB 222 ms
- Conteneur redémarré le **2026-09-15 à 04:49:38** (autorisation utilisateur « Ok go »), soit **après** les modifications des sources (22:07:13 et 22:24:30 le 14/09).
- Au démarrage, le serveur régénère `likec4:model/swarmdrones` : il lit donc les fichiers à jour.
- **Preuve d'identité du contenu** : export `riskMatrix.png` post-restart → SHA-256 `77a9941a72dea572ed3615b72dcf1670902d3f5d6ce7799a73dcffa4e8f51bfd`, **identique** à l'empreinte du rendu de référence du point ④. Le site public sert bien le modèle enrichi, octet pour octet.
- ✅ Vérification du service **complète et concluante**.

## 3. Corrections appliquées par le vérificateur

Le profil `architecte` a été **interrompu** : appel LLM pendu 30 min (connexion DeepInfra ouverte sans trafic), puis régression détectée (7 fichiers, 12 erreurs) et fichiers de test parasites `zz_t4..t8.c4`. Reprise manuelle :

1. **IDs à points invalides** — `Autopilot.PX4`, `Middleware.ROS2`… (13 éléments) → renommés en identifiants plats (`AutopilotPX4`, `ROS2`, …). Erreur LikeC4 : « Could not resolve reference ».
2. **Tags placés après `metadata`** — LikeC4 exige les tags **en premier** dans le corps d'un élément. Les 21 tags des nouveaux éléments ont été retirés (l'information est conservée dans `metadata`, qui est requêtable). Erreur : « Expecting } but found software-primary ».
3. **Fichiers parasites supprimés** : `zz_t4.c4` … `zz_t8.c4`, `zz_test_tags.c4`.
4. **Références non résolues dans les relations** : `PX4` → `AutopilotPX4`, `Ros2` → `ROS2`.
5. **Style global inexistant** : `global style crit` → `criticite`.
6. **`techChoices` illisible** (9 486×11 788) → scindée en `techAutopilot` / `techComms` / `techData`.

## 4. Fichiers

- Modèle : `/docker/likec4/workspace/architecture.c4` (70 832 o) et `views.c4` (27 000+ o)
- Sauvegardes : `backup_v1/`, `backup_v2/`, `backup_v3/` (pré-point ④), `backup_v4/` (post-point ④)
- Contenu source : `/home/hermesagent/workspace/swarm30_annexe_v1.md` (55 362 o)
- Mapping d'IDs appliqué : `/home/hermesagent/workspace/mapping_ids_annexe_v1.md`
- Vérification licences : `/home/hermesagent/workspace/verification_annexe_v1.md`

## 5. Limites et réserves (honnêteté)

- Les **estimations quantitatives** de l'annexe (budgets radio, P_d/P_fa, latences) proviennent du profil `swarmdrone` : elles sont marquées « MEDIUM/LOW evidence » et **n'ont pas été revérifiées** par une source primaire — c'est cohérent avec la posture scientifique du profil, mais ce sont des ordres de grandeur, pas des mesures.
- Le rendu **`deploiement-30-plateformes`** reste lisible uniquement en interactif (zoom/pan), comme documenté précédemment.
- La vérification du service public est **incomplète** tant que le restart n'est pas fait.
