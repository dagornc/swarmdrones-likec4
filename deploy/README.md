# Déploiement statique — likec4.breizh.ai

Service statique pour le modèle d'architecture SwarmDrones, en remplacement du
dev server LikeC4 (`likec4 start`).

## État actuel (2026-10-10)

**Bascule effectuée.** `likec4.breizh.ai` est servi par `likec4-static`
(nginx:alpine, build statique de 23 Mo). Le dev server `likec4` est arrêté
(`Exited (143)`), son conteneur et son image sont conservés pour rollback.

Vérifié en production : HTTP 200, titre « SwarmDrones — Architecture »,
bundle `likec4-views.js` 5,1 Mo servi gzip (1,28 Mo transférés), assets
fingerprintés en `immutable` 1 an, `index.html` en `no-cache`.

**Rendu vérifié au navigateur (Playwright, 2026-10-10)** : 62 vues sur 62
rendues correctement, 0 erreur JS, 0 requête réseau échouée.

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
swarmdrones_likec4/deploy/site/   ← build statique (23 Mo, non versionné)
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
- `nginx.conf` — config nginx (gzip, cache, 404 réel)
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
cd deploy
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
- **`robots.txt`** : LikeC4 génère `Disallow: /` (site entier interdit aux
  moteurs) et écrase celui de `public/`. `build_static.sh` le remplace après
  build par `Allow: /`.
- **404** : pas de fallback SPA (inutile en hash-history). Un chemin inexistant
  renvoie un vrai HTTP 404.
- **Cache Cloudflare** : le site est derrière Cloudflare. Après un changement
  de `robots.txt` ou d'un fichier non fingerprinté, l'ancienne version peut
  rester servie jusqu'à 4 h (`max-age=14400`). Purger le cache si besoin.

## Pièges de publication (rencontrés le 2026-10-10)

`build_static.sh` publie **en place, depuis un conteneur root**. Deux pièges
rendent le site inaccessible (403/404 sur tout) si on publie naïvement :

1. **Remplacer le répertoire monté** (`mv`/`rm -rf` puis recréation) invalide
   le bind mount Docker : le conteneur pointe vers l'inode supprimé. Publier
   en place (vider le contenu, pas le répertoire).
2. **Permissions** : les fichiers produits par le conteneur appartiennent à
   `root`. Un `cp`/`rm` depuis l'hôte échoue, et le répertoire `site/` doit
   rester traversable (`755`) sinon nginx (autre UID) renvoie 403.

La publication passe donc par un conteneur `alpine` qui vide, copie et
normalise les permissions (`chmod 755` + `chmod -R a+rX`).

## Incident du 2026-10-08 (à connaître)

Pendant la préparation de la bascule, un `docker rm -f` filtré par
`ancestor=ghcr.io/likec4/likec4:1.59.2` a **supprimé le conteneur de
production `likec4`** (il utilise la même image que les conteneurs de build).
Le site a renvoyé 404 pendant ~3 minutes.

Restauration : recréation via `docker compose up -d --force-recreate` depuis
`/docker/likec4/`. Le conteneur est de nouveau géré par compose.

**Règle** : ne jamais supprimer de conteneur avec un filtre par image.
Toujours lister, vérifier, puis supprimer par nom explicite.
