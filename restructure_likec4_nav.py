#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
restructure_likec4_nav.py — Restructure l'arborescence de navigation LikeC4
(volet gauche) en 6 dossiers thématiques, SANS modifier le contenu des vues.

Mécanisme : LikeC4 construit l'arbre de navigation à partir du `title` de
chaque vue, en découpant sur ' / '. On réécrit donc uniquement le préfixe
de chemin (les segments avant le dernier ' / '), en conservant le libellé
terminal de chaque vue à l'identique.

Sécurité : sauvegarde .bak, vérification post-écriture, validate LikeC4.
"""
import re, shutil, sys, os

BASE = os.environ.get('LIKEC4_BASE', '/docker/likec4/workspace')

# ---------------------------------------------------------------------------
# Cartographie : view_id -> nouveau chemin de navigation (segments)
# Le dernier segment = libellé terminal (repris de l'arborescence cible).
# ---------------------------------------------------------------------------
NEW_PATH = {
    # ===== 01 - Gouvernance & Stratégie (Executive View) =====
    'contexte':            ['01 - Gouvernance & Stratégie (Executive View)', "Contexte (synthese) — vue d'ensemble des zones"],
    'system-context':      ['01 - Gouvernance & Stratégie (Executive View)', '01 Contexte systeme (C4 L1) — Essaim SwarmDrones et son environnement'],
    'consumerMap':         ['01 - Gouvernance & Stratégie (Executive View)', 'Consommateurs du modele — 5 cibles'],
    'simulationBoundary':  ['01 - Gouvernance & Stratégie (Executive View)', 'Consommateurs du modele — ce que le modele fournit et ne fournit pas'],
    'decisions':           ['01 - Gouvernance & Stratégie (Executive View)', "Decisions tranchees : ADR-1..5 et ce qu'elles justifient"],
    'decisionsOuvertes':   ['01 - Gouvernance & Stratégie (Executive View)', 'Decisions ouvertes : DE-01..04 appelees par les angles morts'],
    'blindspotBySeverity': ['01 - Gouvernance & Stratégie (Executive View)', 'Angles morts — 16 lacunes de specification (§C)'],
    'riskMatrix':          ['01 - Gouvernance & Stratégie (Executive View)', 'Matrice de risques — 15 risques (§D)'],
    'hypotheses':          ['01 - Gouvernance & Stratégie (Executive View)', 'Hypotheses et impact — si une hypothese tombe, quoi revoir'],

    # ===== 02 - Parcours & Opérations (Business & Scenarios) =====
    'scenarioCatalogue':   ['02 - Parcours & Opérations (Business & Scenarios)', 'Catalogue des scenarios — 10 scenarios'],
    'scenarioNominal':     ['02 - Parcours & Opérations (Business & Scenarios)', 'Mission nominale — INIT -> READY -> LAUNCH -> EXECUTE'],
    'mission-nominale':    ['02 - Parcours & Opérations (Business & Scenarios)', 'Mission nominale — INIT -> READY -> LAUNCH -> EXECUTE'],
    'scenarioScaleChallenge': ['02 - Parcours & Opérations (Business & Scenarios)', 'SCN-10 — Perte du leader a N=30'],
    'perte-de-lien':       ['02 - Parcours & Opérations (Business & Scenarios)', 'Scenario degrade — perte de lien C2 + GNSS degrade'],
    'perte-de-lien-c2-operateur': ['02 - Parcours & Opérations (Business & Scenarios)', 'Perte de lien C2 — vue operateur (brief de quart)'],
    'apprendre-capteur':   ['02 - Parcours & Opérations (Business & Scenarios)', 'UX Parcours', 'Chaînes de valeur', '1 — Du capteur à l’action'],
    'apprendre-mission':   ['02 - Parcours & Opérations (Business & Scenarios)', 'UX Parcours', 'Chaînes de valeur', '2 — De l’intention au plan embarqué'],
    'apprendre-telemetrie':['02 - Parcours & Opérations (Business & Scenarios)', 'UX Parcours', 'Chaînes de valeur', '3 — De la télémétrie à l’analyse'],
    'zone-c2':             ['02 - Parcours & Opérations (Business & Scenarios)', 'GCS — supervision et autorite humaine'],

    # ===== 03 - Architecture Logique & Flux (C4 Containers & Interactions) =====
    'conteneurs':          ['03 - Architecture Logique & Flux (C4 Containers & Interactions)', 'Conteneurs (niveau 2) — les 4 zones et leurs echanges'],
    'zone-onboard':        ['03 - Architecture Logique & Flux (C4 Containers & Interactions)', 'Détail des Zones (Contexte amont / aval)', 'Zone Onboard (x30) — surete, mission et lien'],
    'zone-edge':           ['03 - Architecture Logique & Flux (C4 Containers & Interactions)', 'Détail des Zones (Contexte amont / aval)', 'Zone Edge — relais, fusion, coordination (1..N)'],
    'zone-cloud':          ['03 - Architecture Logique & Flux (C4 Containers & Interactions)', 'Détail des Zones (Contexte amont / aval)', 'Zone Cloud — hors boucle de controle'],
    'communicationArchitecture': ['03 - Architecture Logique & Flux (C4 Containers & Interactions)', 'Architecture de communication — canaux'],
    'messageArchitecture': ['03 - Architecture Logique & Flux (C4 Containers & Interactions)', 'Architecture des messages — 13 messages, 0 orphelin'],
    'criticalMessages':    ['03 - Architecture Logique & Flux (C4 Containers & Interactions)', 'Messages critiques — voie de surete locale'],
    'worldModelMap':       ['03 - Architecture Logique & Flux (C4 Containers & Interactions)', 'World Model — entites, zones et categories (AUCUNE 3D)'],

    # ===== 04 - Algorithmique & Capacités (Components) =====
    'capabilityMap':       ['04 - Algorithmique & Capacités (Components)', 'Carte des capacites — 8 capacites, 19 fonctions'],
    'algorithmCatalog':    ['04 - Algorithmique & Capacités (Components)', 'Catalogue algorithmique — 11 algorithmes'],
    'techAutopilot':       ['04 - Algorithmique & Capacités (Components)', 'Vues thématiques (§A)', '3 — autopilotage & perception'],
    'techComms':           ['04 - Algorithmique & Capacités (Components)', 'Vues thématiques (§A)', '3 — communication & coordination'],
    'techData':            ['04 - Algorithmique & Capacités (Components)', 'Vues thématiques (§A)', '3 — données, observabilité & jumeau'],
    'observeChain':        ['04 - Algorithmique & Capacités (Components)', 'Chaînes algorithmiques', "Chaine d'observation — du drone au jumeau numerique"],
    'algorithmCoordination':['04 - Algorithmique & Capacités (Components)', 'Chaînes algorithmiques', 'Chaine de coordination — algorithmes dependants du lien'],
    'algorithmSafety':     ['04 - Algorithmique & Capacités (Components)', 'Chaînes algorithmiques', 'Chaine de surete — algorithmes embarquables sans lien'],

    # ===== 05 - Physique & Déploiement (Infrastructure) =====
    'index':               ['05 - Physique & Déploiement (Infrastructure)', 'SwarmDrones — Paysage des zones de deploiement'],
    'deploiement-30-plateformes': ['05 - Physique & Déploiement (Infrastructure)', 'Deploiement — 30 plateformes, N stations Edge, 1 C2, 1 cloud'],
    'deploymentChain':     ['05 - Physique & Déploiement (Infrastructure)', 'Chaine de deploiement — Algorithm -> Component -> Runtime'],
    'droneInternal':       ['05 - Physique & Déploiement (Infrastructure)', 'Drone de reference — vue interne (Architecture materielle)'],

    # ===== 06 - Sûreté, Vérification & Recherche =====
    'invariantsView':      ['06 - Sûreté, Vérification & Recherche', '5 invariants verifiables du contrat'],
    'renderRules':         ['06 - Sûreté, Vérification & Recherche', '6 regles de representation — garde-fous verifiables'],
    'worldStates':         ['06 - Sûreté, Vérification & Recherche', "10 etats d'apparence — le rendu represente des ETATS"],
    'tracabilite':         ['06 - Sûreté, Vérification & Recherche', 'Tracabilite — couverture documentaire par zone'],
    'scienceVerdicts':     ['06 - Sûreté, Vérification & Recherche', 'Verdicts scientifiques — 4 affirmations decisives'],
    'benchmarkGaps':       ['06 - Sûreté, Vérification & Recherche', 'Trous de benchmark — ce qui n est PAS prouve'],
}

# Vues conservées hors arborescence cible (non citées par l'utilisateur) :
# on les laisse dans un dossier « 99 - Vues complémentaires » pour ne rien perdre.
KEEP_EXTRA = {
    'contexte-amont':      ['99 - Vues complémentaires', 'Contexte amont — externes, Onboard (x30), Edge (1..N)'],
    'contexte-aval':       ['99 - Vues complémentaires', 'Contexte aval — Edge gateway, C2, Cloud (hors boucle de controle)'],
    'paysage-criticite':   ['99 - Vues complémentaires', 'Paysage par criticite — safety / mission / best-effort / cloud'],
    'scenarioRiskMapping': ['99 - Vues complémentaires', 'Scenarios x risques — ce que chaque scenario teste'],
    'survivabilitySplit':  ['99 - Vues complémentaires', 'Frontiere avec lien / sans lien — ce qui vole sans reseau'],
    'deploymentZones':     ['99 - Vues complémentaires', 'Zones de deploiement — embarque vs sol vs distant'],
    'hardwareArchitecture':['99 - Vues complémentaires', 'Architecture materielle — drone de reference'],
    'scienceToAlgorithms': ['99 - Vues complémentaires', 'Sources -> verdicts -> algorithmes concernes'],
    'lecture-surete':      ['99 - Vues complémentaires', '1 — Qui protège localement la plateforme ?'],
    'lecture-autorisation':['99 - Vues complémentaires', '2 — Qui autorise et qui garde la trace ?'],
    'lecture-autonomie':   ['99 - Vues complémentaires', '3 — Que reste-t-il sans liaison C2 ?'],
}

ALL = {**NEW_PATH, **KEEP_EXTRA}

def esc(s):
    """Échappe une apostrophe et les '/' internes pour la syntaxe LikeC4.

    LikeC4 découpe le title sur ' / ' pour construire l'arborescence de
    navigation. Un '/' qui doit rester dans le libellé doit être échappé
    avec un backslash (\\/), sinon il crée un dossier parasite.
    """
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("/", "\\/")

def main():
    files = ['views.c4', 'ux-parcours.c4', 'e19-system-context.c4']
    total = 0
    for f in files:
        path = os.path.join(BASE, f)
        src = open(path, encoding='utf-8').read()
        shutil.copy2(path, path + '.bak')

        def repl(m):
            nonlocal total
            kind, vid, body = m.group(1) or '', m.group(2), m.group(3)
            if vid not in ALL:
                return m.group(0)
            new_title = ' / '.join(esc(s) for s in ALL[vid])
            # remplace uniquement la ligne title '...' dans le corps de la vue
            # (gère les apostrophes échappées \' à l'intérieur du titre)
            def sub_title(tm):
                nonlocal total
                total += 1
                return f"title '{esc(new_title)}'"
            new_body = re.sub(r"title '(?:[^'\\]|\\.)*'", sub_title, body, count=1)
            return f"{kind}view {vid} {{{new_body}\n  }}"

        # capture le corps de chaque vue (jusqu'à l'accolade fermante en début de ligne)
        pattern = re.compile(
            r"(dynamic |deployment )?view ([a-zA-Z0-9_-]+) \{(.*?)\n  \}",
            re.S)
        out = pattern.sub(repl, src)
        open(path, 'w', encoding='utf-8').write(out)
        print(f"{f}: {total} titres traités (cumul)")
    print(f"TOTAL titres réécrits: {total}")

if __name__ == '__main__':
    main()
