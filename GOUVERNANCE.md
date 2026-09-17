# Gouvernance du modèle SwarmDrones (LikeC4)

> Date : 2026-09-17 · Script : `gouvernance_swarmdrones.py`

## Objectif

Protéger le modèle LikeC4 contre les **régressions silencieuses** (perte d'éléments, de relations ou de vues) et **rappeler l'état de divergence** entre les copies. C'est le garde-fou de gouvernance recommandé après l'audit C4.

## Les 3 contrôles

1. **Validation** — `likec4 validate` (compilation réelle du modèle). Bloquant.
2. **Non-régression** — comparaison des compteurs (éléments/relations/vues par kind) avec une baseline. Toute **baisse** = échec. Bloquant.
3. **Divergence** — comparaison des fichiers `.c4` entre la copie active (`/docker/likec4/workspace`, servie par le conteneur) et la copie git (`/home/hermesagent/workspace/swarmdrones_likec4`). **Avertissement non bloquant** (la copie active est la référence).

## Usage

```bash
cd /docker/likec4/workspace

python3 gouvernance_swarmdrones.py            # contrôle complet (3/3)
python3 gouvernance_swarmdrones.py --init     # (re)établit la baseline
python3 gouvernance_swarmdrones.py --validate # validation seule
python3 gouvernance_swarmdrones.py --baseline # non-régression seule
python3 gouvernance_swarmdrones.py --divergence # divergence seule
```

**Code de sortie** : `0` = OK, `1` = au moins un contrôle bloquant a échoué.

## Conventions de référence

- **Copie active (référence)** : `/docker/likec4/workspace` — montée dans le conteneur `likec4`, servie à `https://likec4.breizh.ai`.
- **Copie git (historique)** : `/home/hermesagent/workspace/swarmdrones_likec4` — dépôt git, **en retard** par rapport à la copie active.
- **Baseline** : `gov_baseline.json` — établie le 2026-09-17 (312 éléments, 626 relations, 56 vues, 2 déploiements).

## Quand relancer

- **Après chaque modification** d'un fichier `.c4` : `python3 gouvernance_swarmdrones.py`.
- **Après un ajout volontaire** d'éléments/vues : relancer avec `--init` pour mettre à jour la baseline (sinon les hausses seront signalées comme « à vérifier »).
- **Avant un lot important** : contrôle complet pour détecter toute régression.

## Note sur la divergence

La divergence entre les deux copies est **connue et assumée** (la copie active est la référence). Le script la signale comme avertissement. Si la copie git doit redevenir la référence de versionnement, il faut la resynchroniser depuis la copie active.
