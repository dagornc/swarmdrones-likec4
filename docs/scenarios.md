# Scénarios dynamiques

> Epic **E09** · Carte `t_361b3beb` · Fichier : `scenarios.c4`

## 1. Objet

Décrire le système **en mouvement**. Les scénarios sont la matière première
de trois consommateurs :

- les **guided tours** navigables (E13) — on explique en déroulant une séquence ;
- les **animations 3D** (E11) — un scénario devient une timeline ;
- les **cas de test** du simulateur (E10) — un scénario devient un test.

## 2. Principe de non-fiction

Un scénario n'est **pas** de la fiction. Chaque étape référence des
éléments, messages ou algorithmes **réellement présents** dans le modèle.

Le contrôle qualité a vérifié : **0 référence morte, 0 étape isolée,
0 scénario orphelin** sur le modèle compilé.

## 3. Règle de mission respectée : aucune coordonnée 3D

Un scénario décrit une **séquence causale** (« qui déclenche quoi »),
**pas un chemin dans l'espace**. Le placement spatial appartient au
World Model (E11). Cette séparation est la garantie que LikeC4 reste
sémantique.

## 4. Les 10 scénarios

**Nominal**
- **SCN-01 — Mission nominale sans C2 ni cloud.** Le scénario de référence :
  il valide que la mission s'accomplit avec C2 et cloud indisponibles du
  début à la fin. N'active que des capacités `sans_lien = oui`.

**Dégradations de lien et d'acteurs**
- **SCN-02 — Perte du lien de commandement.** Mission poursuivie sur plan embarqué ; re-optimisation *différée*, pas perdue.
- **SCN-03 — Perte d'un agent et reconfiguration.** Détection, réélection, redistribution de charge.
- **SCN-04 — Partition du réseau.** Deux groupes qui ne communiquent plus ; pas de quorum global.
- **SCN-10 — Perte du leader à N=30.** Le scénario qui teste précisément ce qui **n'est pas mesuré**.

**Dégradations capteurs et physique**
- **SCN-05 — GNSS dégradé / denied.** Bascule VIO, puis repli sur seuil de dérive.
- **SCN-06 — Évitement de collision.** Couche de sûreté embarque, sans réseau ni allocation.
- **SCN-09 — Charge dense et perception dégradée.** Fausses pistes (R-8), dégradation propre.

**Ressources**
- **SCN-07 — Saturation du spectre.** Coordination dégradée, **sûreté intacte**.
- **SCN-08 — Énergie critique.** Arbitrage valeur de mission vs marge de repli.

## 5. Déroulé détaillé

Quatre scénarios structurants ont un **déroulé en 4 étapes** avec chaîne
causale explicite (`triggers`) :

- **SCN-01** : décollage sur plan embarqué → perception locale → sûreté armée → mission terminée
- **SCN-03** : perte détectée → alerte propagée → leader réélu → charge redistribuée
- **SCN-06** : convergence détectée → seuil franchi → correction minimale → séparation rétablie
- **SCN-10** : leader perdu à N=30 → élection distribuée → sûreté maintenue → nouveau leader

## 6. Ancrage épistémique

Chaque scénario est relié (`exposes`) au **risque ou à l'angle mort qu'il
teste**. C'est ce lien qui rend un scénario utile en QA (E12) :

- SCN-03 / SCN-04 → `riskR4` (split-brain)
- SCN-05 → `riskR5` (dérive GNSS-degradé)
- SCN-06 → `riskR9` (collision en urgence)
- SCN-07 → `blindspotAM3` (budget radio) + `riskR1` (contention à 30)
- SCN-09 → `riskR8` (fausses pistes)
- SCN-10 → `riskR3` (validation réelle à 30 non réalisable)

## 7. Limite déclarée

Ces scénarios ne sont **pas** des données de vol. **Aucun n'a été exécuté**,
ni en simulation ni en vol. Ils décrivent la séquence *attendue d'après
l'architecture*. Tous portent le tag `#hypothese`.

SCN-10 nécessite le simulateur (E10) : c'est précisément sa raison d'être.

## 8. Vérification

- `likec4 validate` → **Valid (11 files)**
- 215 éléments, 435 relations
- **10 scénarios · 16 étapes · 0 orphelin · 0 référence morte**
