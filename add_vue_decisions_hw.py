#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_vue_decisions_hw.py — SWARM-3D-ARCHITECTURE / LikeC4  (P2)

Ajoute une vue `decisionsMaterielles` qui rend visibles les 6 decisions
ouvertes DE-05..DE-10 (decisions_hw.c4), actuellement absentes de toute vue.

NE MODIFIE AUCUNE VUE EXISTANTE : insertion d'une nouvelle vue avant la
derniere accolade fermante de views.c4.

Idempotent : si la vue existe deja, ne fait rien.
"""

import os
import re
import subprocess
import sys

BASE = os.environ.get('LIKEC4_BASE', '/docker/likec4/workspace')
VIEWS = os.path.join(BASE, 'views.c4')

VIEW_ID = 'decisionsMaterielles'

BLOC = """
  /** DECISIONS MATERIELLES OUVERTES (DE-05..DE-10) : les arbitrages de
   *  conception materielle non tranches. Chaque decision conditionne un
   *  element de `refDrone` (hardware.c4) : tant qu'elle est ouverte, le
   *  choix correspondant reste un trou du modele.
   *
   *  Complement de `decisionsOuvertes` (DE-01..04, appelees par les angles
   *  morts critiques). Ici, l'amont est le composant materiel conditionne. */
  view decisionsMaterielles {
    title '01 · Gouvernance \\/ Decisions materielles : DE-05..10 et le composant conditionne'

    description '''
      **Arbitrages materiels non tranches.** Six decisions de conception
      (socle de vol, partition calcul, bande radio, energie, IMU, sense-and-avoid)
      n'ont pas ete prises. Chacune conditionne un composant de `refDrone`.

      Lire le sens ainsi : `decision -> composant` = **ce choix conditionne
      cet element** ; tant que la decision est ouverte, le composant porte
      une incertitude de conception.

      Detail complet : cliquer une decision affiche sa description (Markdown),
      ses options, son porteur et son critere de decision.
    '''
    include decVolSocle, decPartitionCalcul, decBandeRadio, decEnergie, decImu, decSae
    include decVolSocle -> refDrone.flightCtrl, decPartitionCalcul -> refDrone.companion
    include decBandeRadio -> refDrone.radioLnk, decBandeRadio -> refDrone.netMesh
    include decEnergie -> refDrone.power, decImu -> refDrone.imu
    include decSae -> refDrone.saeSensor
    global style criticite
    autoLayout LeftRight
  }
"""


def main():
    src = open(VIEWS, encoding='utf-8').read()

    if re.search(r'^\s*view\s+' + VIEW_ID + r'\s*\{', src, re.M):
        print(f'  vue {VIEW_ID} deja presente — rien a faire')
        return 0

    # inserer avant la derniere accolade fermante
    idx = src.rstrip().rfind('}')
    if idx < 0:
        print('  ERREUR: accolade fermante introuvable', file=sys.stderr)
        return 1

    new = src[:idx] + BLOC + '\n' + src[idx:]
    open(VIEWS, 'w', encoding='utf-8').write(new)
    print(f'  vue {VIEW_ID} inseree ({len(BLOC)} caracteres)')

    print('  validation likec4...')
    r = subprocess.run(['likec4', 'validate'], cwd=BASE,
                       capture_output=True, text=True)
    tail = (r.stdout + r.stderr).strip().split('\n')[-1]
    print(f'  {tail}')
    return 0 if r.returncode == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
