# Diffusion — Posts LinkedIn et messages de contact

Date : 2026-10-07 · Auteur : Christophe Dagorn

Règle d'or : **un post = une preuve = un lien**. Pas de storytelling creux.
Chaque chiffre cité est vérifié et reproductible.

---

## Post 1 — La chaîne (angle industriel)

> Un essaim de 30 drones autonomes doit maintenir une décision d'état partagée
> sans coordinateur central. Ce n'est pas un problème d'algorithme. C'est un
> problème de traçabilité.
>
> Entre l'article scientifique qui fonde un choix et le code qui l'exécute,
> il y a quatre couches que la plupart des projets perdent en route :
> la littérature, l'architecture, la spécification formelle, le code.
>
> J'ai construit et outillé cette chaîne de bout en bout :
>
> → 3 647 entrées de veille scientifique, avec niveau de confiance tracé
> → un modèle d'architecture LikeC4 : 521 éléments, 942 relations, 0 référence pendante
> → 15 spécifications SysML v2 générées depuis le modèle
> → 15 implémentations Rust, parité bit-à-bit vérifiée
>
> Le tout est public et reproductible. Une commande clone, compile, teste et
> vérifie la parité :
>
> git clone https://github.com/dagornc/SwarmDrones.git && cd SwarmDrones && ./demo.sh
>
> Le modèle : https://likec4.breizh.ai
>
> #SystemsEngineering #MBSE #Rust #Drones #SysML

---

## Post 2 — Le corpus (angle recherche)

> La veille scientifique est chronophage et rarement traçable. Personne ne sait
> quelle source fonde quel choix d'implémentation.
>
> J'ai construit un pipeline qui ne prétend pas que tout est fiable : il **trace**
> le niveau de confiance de chaque entrée et signale ce qui reste à vérifier.
>
> 3 647 entrées exploitables (3 677 collectées, 30 sources inaccessibles listées à part) :
> → 2 307 candidats primaires
> → 864 documents d'artefacts
> → 410 non vérifiées
> → 4 signalées suspectes
>
> Chaque algorithme canonique est rattaché à ses sources fondatrices. Les dates
> revendiquées ne sont pas des preuves — la métadonnée décisive est résolue
> contre la source primaire.
>
> L'honnêteté épistémique n'est pas une posture ici : c'est un contrôle
> automatisé. Le dépôt refuse d'affirmer une valeur chiffrée non sourcée.
>
> Les métadonnées des 3 647 entrées sont publiques (titres, sources, DOI,
> arXiv, niveau de confiance) — sans les PDF, qui restent soumis au droit
> d'auteur de leurs éditeurs.
>
> https://github.com/dagornc/swarmdrones-likec4/tree/master/corpus-public
>
> #Recherche #VeilleScientifique #IA #Drones

---

## Post 3 — La parité (angle intégrateur)

> « Ça marchait la semaine dernière » est la phrase la plus chère de l'industrie.
>
> J'ai audité mes 15 dépôts Rust depuis un clone public frais :
>
> → 15/15 compilent
> → 209 tests passés, 0 échec
> → 4 900 comparaisons de parité Rust ↔ Python, 0 écart
>
> La parité est mesurée après conversion des flottants en IEEE 754 binaire.
> Elle prouve que les deux simulateurs calculent exactement la même chose.
> Elle ne prouve pas la validité scientifique de la loi de commande — et je
> l'écris noir sur blanc dans le dépôt.
>
> L'architecture est reproductible : chaque algorithme vit dans son dépôt,
> épinglé par commit précis, pas par branche flottante. Cloner à une date donnée
> redonne exactement les mêmes versions.
>
> https://github.com/dagornc/SwarmDrones
>
> #Rust #IngénierieLogicielle #Reproductibilité #Drones

---

## Post 4 — La méthode (synthèse)

> Ce que je sais faire, en une phrase :
>
> Construire des chaînes d'ingénierie où chaque affirmation est adossée à un
> artefact exécutable, et chaque artefact à un test qui échoue quand la promesse
> est violée.
>
> Concrètement, sur un système d'essaim de drones :
> → de l'article scientifique au code Rust, traçabilité mécanisée
> → spécifications SysML v2 générées depuis un modèle d'architecture
> → garde-fous qui détectent les régressions silencieuses
> → parité bit-à-bit mesurée, pas revendiquée
>
> Tout est public. Tout est reproductible. Rien n'est sur-vendu.
>
> https://github.com/dagornc/swarmdrones-likec4
>
> #SystemsEngineering #MBSE #Rust #Drones #Ingénierie

---

## Message de contact direct (à personnaliser par cible)

**Objet** : Traçabilité article → code sur un essaim de 30 plateformes

> Bonjour [Nom],
>
> Je travaille sur l'ingénierie système des essaims de drones autonomes, avec
> un angle précis : la traçabilité mécanisée entre la littérature scientifique,
> l'architecture, les spécifications formelles et le code.
>
> J'ai construit une chaîne complète et publique sur un essaim de 30 plateformes :
> modèle d'architecture LikeC4 (521 éléments, 942 relations), 15 spécifications
> SysML v2, 15 implémentations Rust à parité bit-à-bit vérifiée (209 tests,
> 0 échec).
>
> Tout est reproductible en une commande :
> https://github.com/dagornc/SwarmDrones
>
> Je serais ravi d'échanger sur la façon dont cette approche pourrait s'appliquer
> à [contexte de la cible].
>
> Bien cordialement,
> Christophe Dagorn

---

## Calendrier de diffusion

| Semaine | Action | Angle |
|---|---|---|
| 1 | Post 1 « la chaîne » | Industriel |
| 2 | Post 2 « le corpus » + README 2-3 dépôts Rust | Recherche |
| 3 | Post 3 « la parité » + démo | Intégrateur |
| 4 | Post 4 « la méthode » + contact direct 5-10 cibles | Synthèse |

## Cibles de contact direct

**Industriels drone / défense** : Exail, Kongsberg, Thales, Airbus D&S, Delair,
Parrot Pro, Safran Electronics, Naval Group.

**Laboratoires** : LAAS-CNRS, ISIR, IRISA, Lab-STICC, ONERA, INRIA.

**Intégrateurs / startups** : intégrateurs systèmes autonomes, startups drone,
ESN avec pratique Rust/embarqué.
