# Déploiement statique — likec4.breizh.ai

Service statique pour le modèle d'architecture SwarmDrones, en remplacement du
dev server LikeC4 (`likec4 start`).

## État actuel (2026-10-08)

**Bascule effectuée.** `likec4.breizh.ai` est servi par `likec4-static`
(nginx:alpine, build statique de 21 Mo). Le dev server `likec4` est arrêté
(`Exited (143)`), son conteneur et son image sont conservés pour rollback.

Vérifié en production : HTTP 200, titre « SwarmDrones — Architecture »,
bundle `likec4-views.js` 5,1 Mo servi gzip (1,28 Mo transférés), assets
fingerprintés en `immutable` 1 an, `index.html` en `no-cache`.

## Pourquoi

Le dev server LikeC4 présentait trois fragilités structurelles :

1. **`--public-dir` lu une seule fois au démarrage** — un fichier ajouté dans
   `public/` après le démarrage n'est pas servi (l'URL renvoie le fallback SPA).
2. **HMR inopérant sur le modèle compilé** — un changement de `.c4` exige un
   `docker restart` manuel.
3. **Service de développement en production** — pas de cache, pas de
   compression, dépendance à un process Node.

Le site statique supprime ces trois problèmes : nginx sert des fichiers, le
build est reproductible, et la publication est atomique.

## Architecture

```
repo git (swarmdrones_likec4)
        │  likec4 build
        ▼
swarmdrones-deploy/site/   ← build statique (31 Mo)
        │  bind mount ro
        ▼
conteneur likec4-static (nginx:alpine)
        │  labels Traefik
        ▼
Traefik ──► likec4.breizh.ai
```

## Fichiers

- `build_static.sh` — compile le modèle et publie dans `site/` (atomique)
- `switch.sh` — bascule / rollback / état
- `docker-compose.yml` — service nginx + labels Traefik
- `nginx.conf` — config nginx (gzip, cache, SPA fallback)
- `site/` — build publié (généré, non versionné)

## Utilisation

```bash
./build_static.sh          # (re)construire le site
./switch.sh status         # qui sert le site actuellement ?
./switch.sh to-static      # bascule vers le statique
./switch.sh to-dev         # rollback vers le dev server
```

## Bascule et rollback

Les deux conteneurs (`likec4` et `likec4-static`) déclarent le même `Host`
Traefik. **Un seul doit tourner à la fois** — sinon Traefik route vers l'un ou
l'autre de façon non déterministe.

- **Bascule** : `docker stop likec4` puis `docker compose up -d`
- **Rollback** : `docker compose down` puis `docker start likec4`

Le rollback est immédiat : le conteneur `likec4` et son image sont conservés.

## Mise à jour du contenu

Après une modification du modèle :

```bash
cd /home/hermesagent/workspace/swarmdrones_likec4
git pull   # ou édition locale
cd /home/hermesagent/workspace/swarmdrones-deploy
./build_static.sh
```

Le conteneur nginx sert le nouveau contenu immédiatement (bind mount), sans
redémarrage.

## Notes

- Le build prend ~2 min 30 (compilation du modèle + bundling).
- Le titre est corrigé après build : `likec4 build --title` n'atteint pas le
  HTML statique en v1.59.2 (bug de la version).
- `--use-hash-history` : navigation en `/#/view`, pas de réécriture d'URL.
- **Mémoire** : le build est gourmand (Graphviz + bundling). Sur cet hôte
  (7,8 Go), `unflatten` peut être tué par SIGTERM si la machine est chargée.
  `build_static.sh` borne le conteneur à `--memory=3g` et il faut lancer le
  build quand la mémoire disponible est suffisante (vérifier `free -h`).

## Incident du 2026-10-08 (à connaître)

Pendant la préparation de la bascule, un `docker rm -f` filtré par
`ancestor=ghcr.io/likec4/likec4:1.59.2` a **supprimé le conteneur de
production `likec4`** (il utilise la même image que les conteneurs de build).
Le site a renvoyé 404 pendant ~3 minutes.

Restauration : recréation via `docker compose up -d --force-recreate` depuis
`/docker/likec4/`. Le conteneur est de nouveau géré par compose.

**Règle** : ne jamais supprimer de conteneur avec un filtre par image.
Toujours lister, vérifier, puis supprimer par nom explicite.
