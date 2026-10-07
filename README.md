# SWARM-3D — De l'article scientifique au code vérifié

**Une chaîne d'ingénierie système complète et falsifiable** : veille scientifique
automatisée → modèle d'architecture sémantique → spécifications SysML v2 →
implémentations Rust → parité bit-à-bit mesurée.

> Ce dépôt n'est pas une maquette. Chaque affirmation qu'il porte est adossée à
> un artefact exécutable, et chaque artefact à un test qui **échoue** quand la
> promesse est violée.

---

## Le problème

Concevoir un essaim de plateformes autonomes (26 aériennes + 4 de surface) qui
maintient une **décision d'état partagée sans coordinateur central** exige de
tenir ensemble quatre choses que l'industrie traite habituellement séparément :

- la **littérature scientifique** qui fonde chaque choix algorithmique ;
- l'**architecture** du système et ses dépendances ;
- les **spécifications formelles** exigibles en certification ;
- le **code** qui implémente réellement, et la preuve qu'il fait ce qu'il dit.

La plupart des projets perdent la traçabilité entre ces quatre couches. Ici,
elle est **mécanisée**.

---

## La chaîne, en cinq étapes

```
  ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
  │  1. VEILLE      │   │  2. MODÈLE       │   │  3. SPÉCIFICATION│
  │  SCIENTIFIQUE   │──▶│  SÉMANTIQUE      │──▶│  FORMELLE        │
  │  2 609 entrées  │   │  LikeC4          │   │  SysML v2        │
  │  805 PDF        │   │  521 éléments    │   │  15 fichiers     │
  │  confiance      │   │  942 relations   │   │  traçables       │
  │  tracée         │   │  0 référence     │   │                  │
  │                 │   │  pendante        │   │                  │
  └─────────────────┘   └──────────────────┘   └─────────────────┘
                                                       │
                                                       ▼
  ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
  │  5. PREUVE      │   │  4. IMPLÉMENTATION│  │                 │
  │  Parité         │◀──│  Rust            │◀─┘                 │
  │  bit-à-bit      │   │  15 dépôts       │                    │
  │  200/200        │   │  publics         │                    │
  │  identiques     │   │  tests verts     │                    │
  └─────────────────┘   └──────────────────┘
```

### 1. Veille scientifique traçable

Un corpus de **2 609 entrées** (805 PDF) collecté et maintenu par un pipeline
automatisé, avec un **inventaire de confiance explicite** :

- 1 308 candidats primaires (A-primary-candidate)
- 797 documents d'artefacts (B-artifact-documentation)
- 34 sources officielles (B-official)
- 420 non vérifiées, 48 découvertes, 2 signalées suspectes

Le corpus **ne prétend pas** que tout est fiable : il **trace** le niveau de
confiance de chaque entrée et signale ce qui reste à vérifier. Les dates
revendiquées ne sont pas des preuves — la métadonnée décisive est résolue
contre la source primaire.

### 2. Modèle d'architecture sémantique (LikeC4)

Le modèle est la **source de vérité sémantique** : il décrit *ce qui existe, ce
que ça fait, et ce qui est prouvé*. Il ne contient **aucune coordonnée 3D** —
la spatialisation appartient aux consommateurs (Blender, moteur Web).

- **20 fichiers** `.c4`, **521 éléments**, **942 relations**, **70 vues**
- **0 référence pendante** (aucune cible fantôme)
- `likec4 validate` → **✓ Valid (20 files)**
- Quality gate : **99/100** (11 critères calculés)
- Contrôle d'intégrité : **7/7** (contrôles que la syntaxe ne voit pas)

### 3. Spécifications SysML v2

**15 fichiers** `.sysml`, un par algorithme canonique, générés depuis le modèle
avec traçabilité vers le composant d'accueil (`perform` / `satisfy`).

Réserve assumée : la syntaxe n'est pas validée par un outil OMG (aucun
disponible dans l'environnement). Le contrôle structurel maison passe 15/15.
**La réserve est documentée, pas dissimulée.**

### 4. Implémentations Rust

**15 dépôts publics** `alg-*`, un par algorithme, chacun avec son code, ses
tests, sa référence Python normative et son harnais de parité.

Exemple vérifié de première main (`alg-formation-control`) :

```
cargo build --release   →  succès
cargo test              →  5/5 tests passés, 0 échec
verify_parite_rust.py   →  200/200 comparaisons identiques, 0 écart
                           PARITÉ BIT-À-BIT VÉRIFIÉE
```

### 5. Preuve de parité

La parité Rust ↔ Python est mesurée sur 50 graines × 4 scénarios (nominal,
perte de liens, perturbation, formation à 12 agents), après conversion des
flottants en représentation IEEE 754 binaire.

**Ce que la parité prouve** : les deux simulateurs calculent exactement la même
chose.
**Ce qu'elle ne prouve pas** : la validité scientifique de la loi de commande,
sa stabilité formelle, ou son aptitude au vol réel. Cette distinction est
maintenue partout dans le dépôt.

---

## Reproductibilité

L'orchestrateur [`SwarmDrones`](https://github.com/dagornc/SwarmDrones) agrège
les 15 algorithmes et les protocoles en **git submodules épinglés à des commits
précis** — pas des branches flottantes. Cloner le dépôt à une date donnée
redonne exactement les mêmes versions.

```bash
git clone --recurse-submodules https://github.com/dagornc/SwarmDrones.git
```

---

## Vérifier soi-même

**Le plus rapide** — une commande, tout est vérifié :

```bash
git clone https://github.com/dagornc/SwarmDrones.git && cd SwarmDrones && ./demo.sh
```

Le script clone la solution complète, compile et teste les 15 algorithmes Rust,
vérifie la parité bit-à-bit et affiche les points d'entrée publics.
(`./demo.sh --quick` pour un seul algorithme.)

**Étape par étape** :

```bash
# Modèle : validation outil réel
docker exec likec4 likec4 validate /data        # attendu : ✓ Valid (20 files)

# Qualité : 11 critères, score /100
python3 tools/qa/quality_gate.py                # attendu : 99/100 — GATE: PASS

# Intégrité : 7 contrôles que la syntaxe ne voit pas
python3 tools/qa/integrity_check.py             # attendu : 7/7 OK

# Cohérence modèle <-> code
python3 tools/qa/check_model_code_consistency.py  # attendu : 15/15, FAIL=0

# Un algorithme, de bout en bout
git clone https://github.com/dagornc/alg-formation-control.git
cd alg-formation-control && cargo test && python3 verify_parite_rust.py
```

**Audit d'exécution complet** (2026-10-07) : les 15 dépôts Rust clonés depuis
GitHub compilent, passent **209 tests (0 échec)** et vérifient **4 100
comparaisons de parité (0 écart)**. Détail :
[`docs/RAPPORT_AUDIT_EXECUTION_RUST.md`](docs/RAPPORT_AUDIT_EXECUTION_RUST.md).

---

## Explorer le modèle

Le modèle est servi publiquement : **[likec4.breizh.ai](https://likec4.breizh.ai)**

Les 15 spécifications détaillées (PDF) et les 15 fichiers SysML y sont
également accessibles.

---

## Ce que ce dépôt refuse d'affirmer

L'honnêteté épistémique est une propriété du système, pas une posture :

- Aucune **valeur chiffrée non sourcée** (contrôle automatisé I-6).
- Aucune **coordonnée 3D** dans le modèle sémantique.
- Aucun algorithme marqué `validé` tant qu'il reste `idea` / `conceptual` /
  `evidenceLevel NONE` dans le modèle.
- Les **2 DOI morts** identifiés sont signalés, pas remplacés par une source
  inventée.
- Les **11 sources orphelines** sont listées comme telles, pas rattachées
  d'autorité.

---

## Limites assumées

Ce dépôt est un **démonstrateur d'ingénierie**, pas un outil opérationnel :

- Les simulateurs sont **cinématiques en 2D** — aucune dynamique de vol,
  aucun modèle aérodynamique, aucun délai continu, aucune saturation
  d'actionneur.
- La parité prouve la **cohérence d'implémentation**, pas la validité
  scientifique.
- Aucun essai matériel n'est inclus.

Ces limites sont écrites dans le dépôt, pas cachées dans une annexe.

---

## Documentation

- [`docs/README_TECHNIQUE.md`](docs/README_TECHNIQUE.md) — documentation
  technique complète (garde-fous, synchronisation, invariants, outils)
- [`GOUVERNANCE.md`](GOUVERNANCE.md) — protection contre les régressions
  silencieuses
- [`RAPPORT_AUDIT_FINAL_LIKEC4.md`](RAPPORT_AUDIT_FINAL_LIKEC4.md) — audit de
  cohérence et d'intégrité des liens
- [`sysml/VALIDATION_REPORT.md`](sysml/VALIDATION_REPORT.md) — validation SysML
- [`docs/traceability.md`](docs/traceability.md) — traçabilité

---

## Auteur

**Christophe Dagorn** — ingénieur informatique (INSA Rennes).

Licence MIT.
