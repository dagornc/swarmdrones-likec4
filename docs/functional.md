# Architecture fonctionnelle

> Epic **E02** · Carte `t_4e4ec60b` · Fichier : `functional.c4`

## 1. Objet

Ajouter la couche **capability → function → component**, qui manquait
entièrement. C'est le niveau « pourquoi / quoi », au-dessus du « comment ».

Cette couche sert directement trois objectifs de la mission :
- **documentation pédagogique navigable** — on explique le système par
  ce qu'il *sait faire*, pas par ses composants ;
- **scénarios dynamiques** (E09) — un scénario raconte l'activation
  d'une capacité ;
- **comparaison de variantes** (V5) — on compare des fonctions, pas
  des fichiers.

## 2. Méthode — dérivé, pas inventé

Chaque fonction est **dérivée de la description d'un composant existant**
d'`architecture.c4`. La référence d'origine est portée dans le champ
`metadata.source` de chaque fonction. Exemple :

- `fnHealthMonitoring` ← *« Diagnostic interne (batterie, moteurs,
  capteurs, températures), prédiction de défaillance, marge d'énergie »*
  (description réelle d'`onboard.health`).

Aucune fonction n'a été inventée. Quand la description source était trop
vague, la fonction porte un `tbd` explicite au lieu d'être devinée.

## 3. Les 8 capacités

- `capFly` — voler et se maintenir en vol (1 fonction)
- `capPerceive` — percevoir et se situer (**4 fonctions**)
- `capDecide` — décider et réagir (**3 fonctions**)
- `capCooperate` — coopérer en essaim (**4 fonctions**)
- `capCommunicate` — communiquer (1 fonction)
- `capSurvive` — survivre aux pannes (**3 fonctions**)
- `capObserve` — être observé et expliqué (**3 fonctions**)
- `capCommand` — être commandé (1 fonction)

**19 fonctions au total.**

## 4. Distinction structurante : avec lien / sans lien

Chaque capacité porte `metadata.sans_lien`. Le résultat :

**Fonctionnent SANS aucun réseau :**
`capFly`, `capPerceive`, `capDecide`, `capSurvive` (repli local).

**Dépendent du réseau :**
`capCooperate`, `capCommunicate` (maillage), `capCommand`.

**Non requises pour voler :**
`capObserve` — c'est la capacité qui sert le projet pédagogique et le
Digital Twin 3D, pas la sécurité du vol.

Cette frontière recoupe exactement celle démontrée en E07 (chaîne de
sûreté `rtFlight` vs coordination `rtCompanion`), par un chemin
indépendant. **Deux méthodes différentes aboutissent à la même
séparation** — c'est un renforcement, pas une redondance.

## 5. Traçabilité descendante

Chaque fonction porte `metadata.algo` quand un algorithme du catalogue
E04 la réalise. La chaîne complète devient donc :

```
CAPACITE -> FONCTION -> ALGORITHME -> COMPOSANT -> RUNTIME -> NOEUD
```

Exemple :
`capDecide` → `fnCollisionAvoidance` → `algCollisionAvoidance` →
`onboard.safety` → `rtFlight` → `refDrone.flightCtrl`

C'est cette chaîne unique qui permet d'expliquer, à un public non
technique, *pourquoi* un composant existe.

## 6. TBD conservés

Trois fonctions portent une dépendance ouverte, **non comblée** :

- `fnRelativeEstimation` — technologie dépend de **DE-08** (IMU/perception) ;
- `fnMeshCommunication` — bande et protocole dépendent de **DE-06** ;
- `fnEnergyManagement` — capacité batterie = **DE-07**, seul TBD réellement ouvert.

## 7. Vérification

- `likec4 validate` → **Valid (10 files)**
- 189 éléments, 396 relations
- **8 capacités · 19 fonctions**
- **0 capacité sans fonction · 0 fonction sans composant réalisateur**
