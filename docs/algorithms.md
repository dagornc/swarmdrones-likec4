# Catalogue d'algorithmes

> Epic **E04** · Carte `t_83ae834a` · Fichier : `algorithms.c4`

## 1. Objet

Transformer chaque algorithme en **objet de première classe**, exploitable
par le simulateur et comparable entre variantes (V5 de la roadmap).

Avant E04 : 7 algorithmes existaient comme *familles* dans `architecture.c4`
(kind `algorithm`, reliés aux hypothèses, angles morts et risques). Utile
pour la traçabilité, insuffisant pour la simulation : aucun champ d'entrée,
de sortie, de paramètre, d'implémentation ou de métrique.

E04 **enrichit sans casser** : les 7 éléments d'origine restent en place,
inchangés. Le catalogue ajoute 11 fiches actionnables.

## 2. Schéma d'une fiche (15 champs)

Chaque algorithme porte :

- `category` / `purpose` — domaine et raison d'être ;
- `inputs` / `outputs` — interface algorithmique ;
- `parameters` — ce que le simulateur doit exposer ;
- `hypotheses` / `contraintes` — domaine de validité ;
- `state` — ce qui est local vs partagé ;
- `executionMode` — `conceptual` / `emulated` / `simulated` / `executable` ;
- `implementationStatus` — `idea` / `specified` / `prototype` / `implemented` / `tested` / `validated` ;
- `repository` / `sourcePath` / `version` — **le code ne vit pas dans LikeC4** ;
- `maturity` / `evidence` — repris du modèle existant quand il existait ;
- `metrics` — ce qui permet la comparaison de variantes ;
- `references` — lien vers le référentiel scientifique ;
- `relatedComponents` / `relatedMessages` — traçabilité croisée ;
- `variantes` — les alternatives comparables (support de V5).

## 3. Les 11 algorithmes

**Coordination / décision distribuée**
- `algTaskAllocation` — CBBA, encheres avec resolution de conflits
- `algConsensus` — consensus distribue (CRDT/LWW retenu par defaut)
- `algFormationControl` — geometrie relative maintenue
- `algLeaderElection` — reconfiguration apres perte du leader

**Perception / navigation / sûreté**
- `algPerceptionFusion` — EKF/UKF local + pistes Edge
- `algNavigationGNSSDegrade` — bascule VIO, RTL sur derive
- `algCollisionAvoidance` — CBF, couche non negociable
- `algSafetyRules` — regles pre-approuvees + watchdog
- `algPathPlanning` — waypoints + MPC court horizon

**Surveillance / énergie**
- `algHealthMonitoring` — detection de faute, qualification de degradation
- `algEnergyAware` — arbitrage endurance / couverture

## 4. État d'implémentation — déclaré, pas supposé

**Les 11 algorithmes sont en `implementationStatus = idea` et
`executionMode = conceptual`.** Ce n'est pas un défaut du modèle : c'est la
vérité. Aucun repository n'a été identifié, aucune version n'existe. Les
écrire `implemented` aurait été une invention.

`repository = TBD` sur les 11 fiches. C'est une information manquante, pas
une information omise.

## 5. Honnêteté scientifique

**Aucune source primaire n'a été vérifiée dans cette session.** Chaque fiche
porte `references = 'aucune source verifiee dans cette session'`.

Les champs `maturity` et `evidence` qui portent la mention *« repris du
modèle existant »* ne sont pas des validations nouvelles : ce sont les
valeurs qui figuraient déjà dans `architecture.c4`. Elles sont conservées
telles quelles pour ne pas effacer un travail antérieur, et signalées comme
telles pour ne pas les faire passer pour un résultat de E04.

Conséquence opérationnelle : **le catalogue est structurellement complet
mais scientifiquement vide.** Il doit être rempli par le profil SwarmDrone
avant tout usage de comparaison algorithmique. C'est l'objet de E08.

## 6. Angles morts explicitement conservés

Trois limites reprises du modèle et **non résolues** ici :

- convergence de CBBA à 30 agents sous partition — *non mesurée* ;
- preuve de non-collision CBF à 30 agents — *non établie* ;
- validation Monte-Carlo adversariale (N ≥ 1000) — *non faite*.

Ces trois points sont exactement ceux qui décideront de la crédibilité de la
comparaison de variantes. Ils deviennent des critères d'acceptation de E10.

## 7. Vérification

- `likec4 validate` → **Valid (6 files)**
- 139 éléments, 316 relations
- 11 fiches, **15+ champs chacune, aucun champ manquant**
- **0 algorithme orphelin** (contrôle sur le modèle compilé)

## 8. Ce que E04 rend possible

Pour la scène 3D et le simulateur : chaque algorithme expose désormais son
interface (entrées/sorties/paramètres) et ses métriques. Le moteur V5 peut
donc instancier deux variantes du même algorithme et **comparer leurs
métriques** — à condition que E08 ait rempli les références.
