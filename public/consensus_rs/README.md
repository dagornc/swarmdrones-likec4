# consensus_rs — ALG_CONSENSUS en Rust

Implémentation Rust de référence de l'algorithme **ALG_CONSENSUS**
(CRDT semi-treillis + gossip), portage fidèle du simulateur Python
`sim_consensus.py` de la spécification v5 (§4.7.1).

## Résultat vérifié

- **Parité bit-à-bit** avec la référence Python : **9 000 comparaisons**
  (9 tests × 1 000 graines), **0 écart**.
- **18/18 tests** unitaires et d'intégration passent.
- **13× plus rapide** que Python : 9 000 simulations en **1,29 s**
  (6 977 sim/s) contre 535 sim/s en Python.
- **0 warning** de compilation.

## Modèle

- **Topologie** : grille 2D 6×5 (N = 30), voisinage 4-connexe, fanout f = 6.
- **État par agent** : couple `(valeur, horloge_logique)`.
- **Fusion** : semi-treillis — `max` sur le couple. L'opération est
  commutative, associative et idempotente, ce qui garantit la convergence
  **indépendamment de l'ordre d'arrivée des messages**.
- **Perturbations** : perte i.i.d. par message, latence, duplication,
  partition gauche/droite, retrait d'agents.

## Pourquoi la parité est difficile

Le point délicat n'est pas l'algorithme — c'est le **générateur
pseudo-aléatoire**. Pour obtenir les mêmes résultats, il ne suffit pas
d'utiliser « un bon RNG » : il faut reproduire *exactement* la séquence de
CPython. `src/rng.rs` embarque donc :

- **MT19937** avec l'initialisation `init_by_array` de CPython ;
- `random()` — combinaison de deux tirages 32 bits (53 bits de mantisse) ;
- `randint()` → `_randbelow()` par rejet avec `getrandbits(k)` ;
- `sample()` — algorithme exact de `Lib/random.py`, y compris le calcul de
  `setsize` et **l'ordre de sélection** (CPython ne trie pas).

Les tests `tests/parite.rs` comparent les sorties aux valeurs de référence
produites par CPython.

## Utilisation

```bash
cargo build --release

# Un test, 100 graines
./target/release/consensus_rs --test T1 --seeds 1001-1100 --out resultats.csv

# Tous les tests, 1000 graines
./target/release/consensus_rs --all --seeds 1001-2000 --out resultats.csv
```

Sortie CSV :
`test,seed,periode_convergence,accord,messages,taille_etat,periode_refusion,divergence_reelle`

## Vérification

```bash
cargo test --release                      # 18 tests
python3 verify_parite_rust.py --seeds 1001-1100   # parité vs Python
```

## Tests du harnais

- **T1** — convergence sans perte.
- **T3** — perte 25 % par message.
- **T4** — duplication ×2.
- **T5** — partition gauche/droite.
- **T5D** — partition avec divergence forcée (mesure du temps de re-fusion).
- **T8** — retrait de 3 agents à t = 3.
- **T9** — partition (variante).

## Structure

```
src/
  lib.rs    — racine du crate, ré-exports
  rng.rs    — MT19937 compatible CPython (random, randint, sample)
  sim.rs    — simulateur : état, fusion semi-treillis, gossip, tests
  main.rs   — CLI compatible avec sim_consensus.py
tests/
  parite.rs — tests de parité avec CPython
verify_parite_rust.py — comparaison automatique Rust vs Python
```
