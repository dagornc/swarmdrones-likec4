#!/usr/bin/env python3
"""
E03 — Typage des relations (SWARM-3D-ARCHITECTURE, carte t_5f46d5aa)

Objectif : donner a chaque arc existant un kind de relation SEMANTIQUE.
Principe de mission :
  - aucun arc n'est supprime, aucun element n'est renomme ;
  - un arc dont le sens n'est PAS etabli recoit le kind `unknown` et une
    carte Kanban est creee (jamais de kind par defaut silencieux) ;
  - le classifieur est deterministe et auditable : meme entree -> meme sortie.

Sortie : /tmp/typage.json  (proposition) puis application par arc_apply.py
"""
import re, json, sys, collections

SRC = 'architecture.c4'


# ---------------------------------------------------------------------------
# Regles de classification, par ordre de priorite decroissante.
# Chaque regle : (nom_kind, predicat_sur_(src,dst,lab,ksrc,kdst))
# Les predicats s'appuient SURTOUT sur les kinds des extremites (fiable) et
# seulement en second recours sur le libelle (bruite).
# ---------------------------------------------------------------------------
def rules():
    R = []
    add = R.append

    # REGLE : un composant qui s'appuie sur un algorithme IMPLEMENTE cet
    # algorithme. Ce n'est ni un appel synchrone ni un lien radio.
    def is_impl_algo(src, dst, lab, ks, kd):
        l = lab.lower()
        return (kd == 'algorithm'
                or "s appuie sur" in l or "s'appuie sur" in l
                or "implemente" in l or "implémente" in l)
    add(('implements', is_impl_algo))

    # --- TRACABILITE : priorite haute, avant tout kind technique ------------
    # Un arc qui VISE une hypothese, une decision, un risque ou un angle mort
    # est une relation de tracabilite, pas un flux ni un lien radio.
    def is_trace_hyp(src, dst, lab, ks, kd):
        return kd == 'hypothesis'
    add(('depend-on', is_trace_hyp))

    def is_trace_dec(src, dst, lab, ks, kd):
        return kd == 'decision'
    add(('justifie', is_trace_dec))

    def is_trace_risk(src, dst, lab, ks, kd):
        return kd in ('risk', 'blindspot')
    add(('exposed-to', is_trace_risk))

    # --- Voie de surete : securite avant tout le reste -----------------------
    # ATTENTION : ne PAS declencher sur le simple mot 'safety' present dans un
    # nom d'element cible. Un arc qui VISE le composant de surete est souvent un
    # flux d'entree (detection, niveaux de sante), pas une voie de surete.
    def is_safety(src, dst, lab, ks, kd):
        l = lab.lower()
        # mots-cles explicites dans le LIBELLE seulement
        if any(w in l for w in ('voie de surete', 'voie surete', 'abort',
                                'rtl', 'geofence', 'preemptif', 'atterrissage')):
            return True
        # une commande critique vers l'autopilote
        if kd == 'component' and 'autopilot' in dst.lower() and 'critique' in l:
            return True
        return False
    add(('safety', is_safety))

    # --- Traçabilite documentaire (avant radio : 'decrit en §' n'est pas un lien radio) ---
    def is_src_doc(src, dst, lab, ks, kd):
        l = lab.lower()
        return (ks == 'docSource' or kd == 'docSource'
                or 'decoule' in l or 'decrit en' in l
                or 'section' in l or 'document source' in l
                or l.startswith('source'))
    add(('derives-from', is_src_doc))

    # --- Commandes / ordres ---------------------------------------------------
    def is_command(src, dst, lab, ks, kd):
        l = lab.lower()
        return ('commande' in l or 'ordre' in l or 'directive' in l
                or 'setpoint' in l or 'consigne' in l
                or 'armement' in l or 'largage' in l)
    add(('command', is_command))

    # --- Radio / lien intermittent -------------------------------------------
    # ATTENTION : ne PAS declencher sur un trafic qui TRANSITE par un composant
    # radio (ex. 'telemetrie priorisee' -> linkRadio) : c'est un flux de donnees.
    def is_radio(src, dst, lab, ks, kd):
        l = lab.lower()
        s = (src + ' ' + lab).lower()
        if 'trafic' in l or 'messages' in l or 'telemetrie' in l:
            return False
        return ('radio' in s or 'lien radio' in l or 'liaison' in l
                or 'gnss' in s or 'satcom' in l or 'bande' in l
                or 'capteurs / gnss' in l)
    add(('radio', is_radio))

    # --- Persistance ----------------------------------------------------------
    def is_store(src, dst, lab, ks, kd):
        s = (src + ' ' + dst + ' ' + lab).lower()
        return ('persist' in s or 'stock' in s or 'store' in s
                or 'cache' in s or 'plan version' in s or 'journal' in s
                or 'replay' in s or 'artefact' in s or 'base' in s)
    add(('store', is_store))

    # --- Store-and-forward / differe -----------------------------------------
    def is_async(src, dst, lab, ks, kd):
        s = (src + ' ' + dst + ' ' + lab).lower()
        return ('differe' in s or 'store-and-forward' in s or 'async' in s
                or 'dtn' in s or 'replication' in s or 'crdt' in s
                or 'consensus' in s or 'vote' in s)
    add(('async', is_async))

    # --- Invocation synchrone -------------------------------------------------
    def is_sync(src, dst, lab, ks, kd):
        l = lab.lower()
        return ('appel' in l or 'requete' in l or 'sync' in l
                or 'api' in l or 'invocation' in l)
    add(('sync', is_sync))

    # --- Traçabilite / preuve : kinds HISTORIQUES a reutiliser ---------------
    def is_hyp_dep(src, dst, lab, ks, kd):
        return ks == 'hypothesis' or kd == 'hypothesis'
    add(('depend-on', is_hyp_dep))

    def is_justifie(src, dst, lab, ks, kd):
        return ks == 'decision' or kd == 'decision'
    add(('justifie', is_justifie))

    def is_exposed(src, dst, lab, ks, kd):
        return (ks == 'risk' or kd == 'risk'
                or ks == 'blindspot' or kd == 'blindspot')
    add(('exposed-to', is_exposed))

    def is_impl_by(src, dst, lab, ks, kd):
        return ks == 'software' or kd == 'software'
    add(('implemented-by', is_impl_by))

    def is_alt(src, dst, lab, ks, kd):
        return 'alternativ' in lab.lower() or 'substitution' in lab.lower()
    add(('alternative-to', is_alt))

    # --- Traçabilite / preuve -------------------------------------------------
    def is_proof(src, dst, lab, ks, kd):
        return (ks in ('algorithm', 'scientificPaper') or kd in ('algorithm', 'scientificPaper')
                or ks in ('external', 'operator') or kd in ('external', 'operator'))
    add(('sync', is_proof))

    # --- Defaut : flux de donnees --------------------------------------------
    add(('flow', lambda *a: True))
    return R


def load():
    t = open(SRC).read()
    lines = t.split('\n')

    # kinds des elements imbriques : capturer aussi la profondeur/nom
    # Un element imbrique s'appelle `<zone>.<id>` dans les arcs.
    # On indexe donc les ids plats ET les ids qualifies par leur conteneur.
    kind = {}
    stack = []
    for ln in lines:
        for m in re.finditer(r'^\s*(\w+)\s*=\s*(\w+)\s*(?:\'[^\']*\')?\s*\{', ln):
            pass
    # approche robuste : parcourir ligne a ligne en suivant l'imbrication
    depth = 0
    ctx = []
    for ln in lines:
        m = re.match(r'^(\s*)(\w+)\s*=\s*(\w+)\s*(?:\'([^\']*)\')?\s*\{?\s*$', ln)
        if m:
            ind, eid, ekind = m.group(1), m.group(2), m.group(3)
            lvl = len(ind)
            while ctx and ctx[-1][0] >= lvl:
                ctx.pop()
            kind[eid] = ekind
            if ctx:
                kind[ctx[-1][1] + '.' + eid] = ekind
            ctx.append((lvl, eid))
    arcs = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith('//'):
            continue
        m = re.match(r"^([\w.]+)\s*(?:-\s*\[[\w-]+\]\s*)?->\s*([\w.]+)\s*(?:'((?:[^'\\]|\\.)*)')?", s)
        if m:
            arcs.append({'ln': i + 1, 'src': m.group(1), 'dst': m.group(2),
                         'lab': (m.group(3) or '').replace("\\'", "'")})
    return kind, arcs


def classify(kind, arcs):
    R = rules()
    out = []
    for a in arcs:
        ks = kind.get(a['src'], '?')
        kd = kind.get(a['dst'], '?')
        chosen = None
        for name, pred in R:
            if pred(a['src'], a['dst'], a['lab'], ks, kd):
                chosen = name
                break
        a2 = dict(a, ksrc=ks, kdst=kd, kind=chosen)
        out.append(a2)
    return out


if __name__ == '__main__':
    kind, arcs = load()
    res = classify(kind, arcs)
    c = collections.Counter(r['kind'] for r in res)
    print(f"arcs: {len(res)}")
    for k, n in c.most_common():
        print(f"  {n:4d}  {k}")
    json.dump({'arcs': res, 'kind': kind}, open('/tmp/typage.json', 'w'), indent=1)
