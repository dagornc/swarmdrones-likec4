# Narratif ciblé — Mise en valeur des compétences SwarmDrones

Date : 2026-10-07 · Auteur : Christophe Dagorn
Objet : trois angles de communication adaptés à trois types d'interlocuteurs.

---

## Principe directeur

Ne pas vendre « des algorithmes de drones ». Vendre une **méthode d'ingénierie
système outillée** qui produit de la traçabilité vérifiable de l'article
scientifique jusqu'au code testé. C'est rare, c'est mesurable, et c'est
exactement ce que l'industrie des systèmes autonomes critiques cherche.

**La phrase d'accroche unique** (à réutiliser partout) :

> « Je construis des chaînes d'ingénierie où chaque affirmation est adossée à un
> artefact exécutable, et chaque artefact à un test qui échoue quand la promesse
> est violée. »

---

## Angle A — Industriel drone / défense

**Cibles** : Exail, Kongsberg, Thales, Airbus D&S, Delair, Parrot Pro,
Safran Electronics, Naval Group, DGA Techniques.

**Leur douleur** : les essaims de drones sont un domaine où la certification
(SORA, DO-178C, STANAG) exige une traçabilité exigence → conception → code →
test. La plupart des équipes la reconstituent à la main, tard, mal, et sous
pression d'audit.

**Ce que tu apportes** : une chaîne **mécanisée** qui produit cette traçabilité
en continu — modèle d'architecture comme source de vérité, spécifications
SysML v2 générées, implémentations Rust à parité mesurée, garde-fous qui
détectent les régressions silencieuses.

**Message clé** :
> « Vous ne manquez pas d'algorithmes. Vous manquez de traçabilité entre ce que
> vous spécifiez et ce que votre code fait réellement. J'ai construit et
> outillé cette chaîne sur un essaim de 30 plateformes — 521 éléments
> d'architecture, 942 relations, 15 algorithmes spécifiés en SysML v2 et
> implémentés en Rust avec parité bit-à-bit vérifiée. »

**Preuves à montrer** :
- Le modèle servi : likec4.breizh.ai
- Un dépôt Rust avec tests verts : alg-formation-control
- Le rapport d'audit : 0 référence pendante, quality gate 99/100

**Ce qu'il faut éviter** : promettre un produit fini. Tu proposes une
**compétence d'ingénierie système**, pas un drone qui vole.

---

## Angle B — Laboratoire / équipe de recherche

**Cibles** : laboratoires robotique (LAAS-CNRS, ISIR, IRISA, Lab-STICC),
équipes multi-agents, ONERA, INRIA.

**Leur douleur** : la veille scientifique est chronophage et non traçable. Les
états de l'art vieillissent vite et personne ne sait quelle source fonde quel
choix d'implémentation.

**Ce que tu apportes** : un **corpus de veille outillé** de 2 609 entrées avec
inventaire de confiance explicite (1 308 candidats primaires, 420 non
vérifiées, 2 signalées suspectes), et un **rattachement mécanisé** entre chaque
algorithme canonique et ses sources fondatrices.

**Message clé** :
> « J'ai construit un pipeline de veille qui ne prétend pas que tout est
> fiable : il trace le niveau de confiance de chaque source et signale ce qui
> reste à vérifier. 2 609 entrées, 805 PDF, rattachées aux 15 algorithmes
> canoniques d'un essaim. »

**Preuves à montrer** :
- L'inventaire de confiance du corpus
- La traçabilité algorithme → sources (science.c4)
- La distinction explicite entre « parité vérifiée » et « validité scientifique »

**Ce qu'il faut éviter** : prétendre que le corpus est exhaustif ou que les
algorithmes sont scientifiquement validés. Ton honnêteté épistémique est un
atout en milieu académique.

---

## Angle C — Intégrateur / startup / ESN technique

**Cibles** : intégrateurs systèmes autonomes, startups drone, ESN avec
pratique Rust/embarqué, cabinets d'ingénierie système.

**Leur douleur** : les projets multi-composants deviennent impossibles à
reproduire. « Ça marchait la semaine dernière » est la phrase la plus chère de
l'industrie.

**Ce que tu apportes** : une **architecture reproductible** — orchestrateur
avec submodules épinglés à des commits précis, parité bit-à-bit mesurée,
quality gate automatisé, garde-fous de non-régression.

**Message clé** :
> « Cloner mon dépôt à une date donnée redonne exactement les mêmes versions de
> chaque composant. 15 algorithmes, chacun dans son dépôt, épinglés par commit,
> avec parité bit-à-bit vérifiée contre une référence Python. »

**Preuves à montrer** :
- SwarmDrones (orchestrateur + submodules)
- Le harnais de parité (200/200 identiques)
- Le quality gate (99/100) et l'integrity check (7/7)

**Ce qu'il faut éviter** : noyer dans les détails algorithmiques. L'acheteur
veut la reproductibilité et la maintenabilité, pas la dérivation mathématique.

---

## Matrice de sélection

| Critère | Angle A (industriel) | Angle B (labo) | Angle C (intégrateur) |
|---|---|---|---|
| Accroche | Traçabilité certification | Veille traçable | Reproductibilité |
| Preuve n°1 | Modèle LikeC4 servi | Corpus 2 609 entrées | Submodules épinglés |
| Preuve n°2 | Rust + tests verts | Rattachement sources | Parité bit-à-bit |
| Ton | Ingénierie système | Rigueur épistémique | Fiabilité opérationnelle |
| Risque | Sur-promesse produit | Sur-promesse scientifique | Sur-promesse maturité |

---

## Séquençage recommandé

1. **Semaine 1** — Publier la vitrine (déjà fait) + 1 post LinkedIn « la chaîne ».
2. **Semaine 2** — Post LinkedIn « le corpus » (angle B) + README soignés sur
   2-3 dépôts Rust phares.
3. **Semaine 3** — Post LinkedIn « la parité » (angle C) + démo reproductible.
4. **Semaine 4** — Contact direct : 5-10 cibles, un seul lien vers la vitrine.

**Règle d'or** : un post = une preuve = un lien. Pas de storytelling creux.
