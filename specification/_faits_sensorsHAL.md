# Faits consolidés — sensorsHAL (extraits du modèle LikeC4, 2026-10-01)

## Identité
- Identifiant : `sensorsHAL`
- Nom qualifié : `onboard.sensorsHAL`
- Libellé : 'Interfaces capteurs'
- Kind : `component`
- Parent : `onboard` (x30 instances)
- Tag : `#safety-critical` (ex-`#best-effort`, commit 3cec8f2)
- Icône : `bootstrap:cpu`
- Défini : `architecture.c4:504`
- Technologie : 'HAL — drivers bas niveau'
- Rôle : « Abstraction matérielle capteurs/actionneurs. Absorbe l'hétérogénéité des plateformes. »

## Métadonnées déclarées (architecture.c4:538-543)
- `criticite 'best-effort'`  ← **INCOHÉRENT avec le tag #safety-critical**
- `frequence 'selon capteur'`
- `principe 'abstraction obligatoire (HARDWARE)'`
- `source '§4.1 onboard.sensorsHAL'`

## Entrées (7)
| Source | Relation | Libellé | Fichier |
|---|---|---|---|
| `radios` | radio | capteurs / GNSS / liaisons physiques | architecture.c4:1435 |
| `refDrone.imu` | flow | etat inertiel | hardware.c4:243 |
| `refDrone.gnss` | flow | position absolue | hardware.c4:244 |
| `refDrone.odometry` | flow | vitesse / cap / altitude | hardware.c4:245 |
| `refDrone.perceptionRel` | flow | pistes relatives voisins | hardware.c4:246 |
| `refDrone.saeSensor` | flow | obstacles proches | hardware.c4:247 |
| `refDrone.healthSensor` | flow | etat materiel | hardware.c4:248 |

## Sorties (3)
| Cible | Relation | Libellé | Criticité | Fréquence |
|---|---|---|---|---|
| `onboard.perception` | flow | flux capteurs | safety-critical | 10-60 Hz |
| `onboard.health` | flow | sante capteurs | mission-critical | — |
| `onboard.autopilot` | flow | etat navigation | safety-critical | — |

## Déploiement
- `onboard.sensorsHAL -[runsOn]-> companion` — 'HAL executee sur le calcul de bord' (hardware.c4:250)
- `companion` = `HW_COMPANION`, SoC ARM64 Linux

## Implémentation
- `MicroXRCEDDS` (PRIMARY, Apache-2.0, réserve « not ready for production use ») — pont MCU <-> DDS
- `MAVLinkMAVSDK` (SECONDARY, MIT/BSD-3) — alternative MAVLink

## Fonction réalisée
- `fnSensorAcquisition` = `FN_SENSOR_ACQUISITION — Acquérir les mesures capteurs`
- `fnSensorAcquisition -[realizes]-> onboard.sensorsHAL` (functional.c4:253)
- Capacité : `CAP_PERCEIVE`
- Criticité : `safety-critical` (functional.c4:104)
- Description : « Lire IMU, GNSS, odometrie, barometre et les exposer normalisees aux algorithmes. »
- Source : `hardware.c4 sensorsHAL`

## Angle mort
- `onboard.sensorsHAL -[exposed-to]-> blindspotAM11` — 'frames et unites heterogenes a normaliser' (architecture.c4:2036)
- `blindspotAM11` = 'AM-11 Ontologie commune non specifiee', gravite 'majeur', statut 'couvrir'
- Conséquence : « Integrations ad hoc; dette technique; jumeau numerique divergent. Frames et unites non normalisees : erreurs silencieuses de facteur d echelle ou de repere. »

## Traçabilité externe (4 liens)
- Kongsberg PROTECTOR Remote Weapon Systems
- Mariner USV Technical Brochure
- Exail Iguana E Datasheet
- HUGIN 6000 Datasheet

## Vues
`zone-onboard`, `mission-nominale`, `perte-de-lien`, `techAutopilot`, `techComms`, `ux-parcours`

## Fréquences déclarées (contexte)
- `imu` : 100-400 Hz
- `gnss` : 5-20 Hz
- relation `sensorsHAL→perception` : 10-60 Hz
- Chaîne suspecte `400 Hz → 60 Hz → 400 Hz` — **non corrigée** (ordre utilisateur P2)

## Piège de nommage
- `onboard.sensors-hal` (kebab) **INVALIDE** ; `onboard.sensorsHAL` (camel) correct
- Source : `docs/sources/mapping_ids_annexe_v1.md:9`
