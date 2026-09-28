# Rapport de validation — SYSML-15 (t_d671a500)

Date : 2026-09-28 · Profil : architecte · Dépôt : dagornc/swarmdrones-likec4

## Verdict

Les livrables sont produits et vérifiés de première main, avec une réserve
explicite : **la syntaxe SysML v2 n'est pas validée par un outil OMG** (aucun
disponible dans l'environnement). La réserve est documentée, pas dissimulée.

## 1. Ce qui est VÉRIFIÉ (preuve de première main)

### 1.1 Spécifications SysML v2 — 15/15 fichiers
15 fichiers `.sysml` présents dans `sysml/`, un par algorithme du périmètre
figé. Chaque fichier contient les constructeurs exigés par la carte :
`part def`, `attribute`, `action def`, `requirement def`, `interface def`
(+ `state def` quand la fiche source nomme un automate), et la traçabilité vers
le composant d'accueil (`perform` / `satisfy`).

### 1.2 Contrôle syntaxique structurel maison — 15/15
`python3 sysml/validate_sysml.py` → **15/15 fichiers conformes** au contrôle
structurel (délimiteurs équilibrés, package en tête, constructeurs attendus,
nommage, terminaison des instructions). Voir limites en section 2.

### 1.3 Modèle LikeC4 — validation outil réel
`docker exec likec4 likec4 validate /data` → **✓ Valid (20 files)**.
- Baseline avant changement : ✓ Valid (19 files).
- Après ajout de `sysml.c4` : ✓ Valid (20 files).
- Aucune fiche `algorithm` existante modifiée, aucune relation/vue existante
  supprimée (fichier purement additif, conformément à la consigne opérateur).

### 1.4 Traçabilité — 15/15
`sysml.c4` ajoute 15 éléments `specDoc` (`sysml*`), 15 relations
`algorithm -[documentedBy]-> specDoc`, et la vue `algorithmSysmlTraceability`.
Les 15 références d'algorithmes existants résolvent (sinon `likec4 validate`
échouerait en « not resolved »).

### 1.5 Aucune invention de contenu
Chaque champ des `.sysml` est une transcription d'un champ LikeC4
(`purpose`, `parameters`, `hypotheses`, `contraintes`, `relatedComponents`,
`relatedMessages`, `state`). Les paramètres sans valeur sont déclarés sans
initialiseur. La table de traçabilité machine-readable est
`sysml/generate_sysml.py` (manifeste `--manifest`).

## 2. Ce qui n'est PAS vérifié (réserve honnête)

### 2.1 Conformité OMG de la syntaxe SysML v2
**Non vérifiée.** Aucun validateur SysML v2 conforme OMG n'est installé :
- `java` absent (prérequis de SysIDE / SysML v2 Pilot Implementation) ;
- `syside` / `sysml` absents ;
- `pip index versions sysml2` → « No matching distribution found » ;
- `npm view sysml2|sysml|@omg/sysml` → « 404 Not Found ».

Le parseur maison vérifie la **structure lexicale**, pas la grammaire OMG, ni la
sémantique, ni la résolvabilité des types (`ScalarValues::Real`, etc.).

### 2.2 État initial des machines d'états
Les `state def` ne marquent pas l'état initial (`entry`) : simplification
documentée, à affiner sous SysIDE.

### 2.3 Publication sur likec4.breizh.ai (service web)
Le modèle **servi** ne reflète pas encore la nouvelle vue : le serveur Vite ne
recharge pas le modèle compilé, un `docker restart likec4` est requis — acte
manuel soumis à l'autorisation explicite de Christophe (service en production).
Hors périmètre des critères d'acceptation de la carte (qui demandent
`validate` + publication GitHub).

## 3. Action recommandée

Faire valider les 15 `.sysml` par un outil OMG réel (SysIDE ou SysML v2 Pilot
Implementation, Java 17+) en intégration continue, puis corriger les éventuels
écarts de grammaire. Le parseur maison reste utile comme garde-fou de
régression rapide.

## 4. Commandes de re-vérification

```sh
cd /home/hermesagent/workspace/swarmdrones_likec4
python3 sysml/validate_sysml.py
docker exec likec4 likec4 validate /data
```
