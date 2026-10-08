# Rapport d'audit d'exécution — 15 dépôts Rust

Date : 2026-10-07 · Auteur : Christophe Dagorn
Méthode : clone `--depth 1` de chaque dépôt public, `cargo build --release`,
`cargo test`, `python3 verify_parite_rust.py`. Exécution réelle, résultats bruts.

## Verdict

**15/15 dépôts compilent. 0 échec de test. Parité bit-à-bit vérifiée partout.**

- **209 tests passés**, 0 échec.
- **4 900 comparaisons de parité**, 0 écart.

## Résultats détaillés

| Dépôt | Build | Tests | Parité |
|---|---|---|---|
| alg-formation-control | OK | 10/0 | 200/200 identiques |
| alg-consensus | OK | 18/0 | 900 graines, 0 écart |
| alg-task-allocation | OK | 37/0 | 300/300 identiques |
| alg-collision-avoidance | OK | 10/0 | 150/150 identiques |
| alg-cooperative-localization | OK | 15/0 | 200/200 identiques |
| alg-energy-aware | OK | 7/0 | 300/300 identiques |
| alg-event-triggered-comm | OK | 13/0 | 200/200 identiques |
| alg-fault-tolerant-control-alloc | OK | 12/0 | 250/250 identiques |
| alg-health-monitoring | OK | 13/0 | 250/250 identiques |
| alg-jamming-resilient-mode | OK | 14/0 | 250/250 identiques |
| alg-leader-election | OK | 9/0 | 300/300 identiques |
| alg-nav-gnss-degrade | OK | 13/0 | 250/250 identiques |
| alg-path-planning | OK | 13/0 | 250/250 identiques |
| alg-perception-fusion | OK | 12/0 | 200/200 identiques |
| alg-safety-rules | OK | 13/0 | 900/900 identiques |

## Ce que cet audit prouve

- Les 15 dépôts sont **réellement exécutables** depuis un clone public frais.
- Aucun dépôt n'est un stub : tous compilent et passent leurs tests.
- La parité Rust ↔ Python est **mesurée**, pas revendiquée.

## Ce que cet audit ne prouve pas

- La **validité scientifique** des lois de commande (la parité prouve la
  cohérence d'implémentation, pas la correction mathématique).
- L'aptitude au **vol réel** (simulateurs cinématiques 2D, pas de dynamique).
- La **couverture** des tests (nombre de tests ≠ qualité des tests).

## Reproductibilité

```bash
for r in alg-formation-control alg-consensus alg-task-allocation \
         alg-collision-avoidance alg-cooperative-localization alg-energy-aware \
         alg-event-triggered-comm alg-fault-tolerant-control-alloc \
         alg-health-monitoring alg-jamming-resilient-mode alg-leader-election \
         alg-nav-gnss-degrade alg-path-planning alg-perception-fusion alg-safety-rules; do
  git clone --depth 1 "https://github.com/dagornc/$r.git" "/tmp/$r"
  (cd "/tmp/$r" && cargo test && python3 verify_parite_rust.py)
done
```
