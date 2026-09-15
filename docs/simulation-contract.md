# Contrat de simulation

> Epic **E10** · Carte `t_6641b537` · Fichier : `simulation.c4`

## 1. Objet

Définir **ce que le modèle promet** à ses consommateurs et **sous quelles
conditions**. C'est l'interface entre :

- **Producteur** : ce modèle LikeC4 (source de vérité sémantique)
- **Consommateurs** : simulateur, Blender, moteur Web 3D, environnement
  pédagogique, jumeau numérique

Sans ce contrat, chaque consommateur réinvente son interprétation de la
mission — et ils divergent.

## 2. Frontière de responsabilité

**FOURNI par le modèle :**
- `providesSemantics` — identités, capacités, fonctions, algorithmes, messages, séquences causales
- `providesTopology` — liens de communication, domaines, zones, chaînes de déploiement. *Qui parle à qui, pas où.*
- `providesContracts` — invariants, conditions de dégradation, critères de succès, ancrages risque/angle mort

**LAISSÉ au consommateur :**
- `leftToConsumer` — coordonnées 3D, maillages, textures, cinématique, rendu
- `leftToConsumer2` — horloge de simulation, pas de temps, intégration physique. Le modèle fournit des **séquences**, pas des durées
- `leftToConsumer3` — bruit, turbulence, modèles de canal radio. Le modèle déclare **les cas**, le consommateur les réalise

Cette frontière est la traduction opérationnelle de la règle de mission :
**LikeC4 reste sémantique, il ne devient pas un moteur 3D.**

## 3. Les 5 invariants vérifiables

- **INV-1** — La mission s'accomplit **sans C2 ni cloud**. Si une animation exige le cloud pour aboutir, elle viole l'architecture.
- **INV-2** — La sûreté **ne dépend jamais du réseau**. Test : SCN-06 avec `CH_MESH` et `CH_COMMAND` coupés.
- **INV-3** — L'échelle cible est **30, non prouvée à 30**. Tout consommateur qui affiche 30 doit porter la limite apparente.
- **INV-4** — **Aucune donnée 3D** dans le modèle sémantique.
- **INV-5** — Une affirmation non sourcée **reste non sourcée**. Interdiction de promouvoir une HYP en fait ou de combler un TBD.

Ces invariants sont **vérifiables automatiquement** (tests `INV-1`..`INV-5`).

## 4. Lacune déclarée dans le contrat

`unknownCapability` — **DE-07 reste ouvert : la capacité batterie n'a jamais
été déterminée.** Conséquence : **SCN-08 (énergie critique) n'est pas
simulable fidèlement**. Un consommateur qui simule l'énergie **invente une
valeur**.

C'est une force, pas une faiblesse : le contrat interdit explicitement de
fabriquer la donnée manquante, au lieu de laisser chacun la deviner.

## 5. Conditions de dégradation

- **DEG-1** — Perte de lien acceptée. Ce n'est **pas** une défaillance du drone.
- **DEG-2** — GNSS dégradable (cas nominal, dérive non quantifiée, DE-08).
- **DEG-3** — Saturation du spectre **non dimensionnée** (AM3). Le consommateur ne doit pas simuler une limite qu'il invente.
- **DEG-4** — Fausses pistes en densité (R-8). Représenter la dégradation, pas la masquer.

Chaque dégradation est reliée à son **scénario** et à son **risque/hypothèse** source.

## 6. Consommateurs déclarés

`consSimulator`, `consBlender`, `consWeb3D`, `consPedago`, `consTwin` —
tous marqués **« À CONSTRUIRE »** sauf le jumeau (**partiellement défini**).

Ils sont dans le modèle pour que **la dépendance soit explicite** : ce
modèle est mesuré à ce qu'il permet de construire.

## 7. Vérification

- `likec4 validate` → **Valid (12 files)**
- 237 éléments, 473 relations
- **22 éléments de contrat, 0 orphelin**
- 5 invariants · 4 conditions de dégradation · 5 consommateurs
