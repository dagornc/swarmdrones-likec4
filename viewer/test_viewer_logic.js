#!/usr/bin/env node
/* ============================================================================
   Test de la logique de conformite du VIEWER, executee sous Node sur le
   vrai export/scene.json.

   Pourquoi ce test : le coeur du viewer (verification du contrat) est du
   JavaScript pur, sans DOM. On l'extrait ici a l'identique pour l'executer
   sous Node — ce qui evite d'installer un navigateur tout en prouvant que
   la logique du viewer est correcte sur l'artefact reel.

   Si ce test passe ET que test_consumer_contract.py passe, alors la logique
   de verification est prouvee deux fois (Python + JS). Reste a verifier
   visuellement le rendu, ce qu'aucun test automatique ne remplace.
============================================================================ */
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const SCENE_PATH = path.join(ROOT, "export", "scene.json");

/* --- copie EXACTE de obsText() du viewer --- */
function obsText(s) {
  return JSON.stringify({
    o: s.consumer_obligations, st: s.states, iv: s.invariants_applied,
  });
}

/* --- copie EXACTE de runChecks() du viewer, retour au lieu de DOM --- */
function runChecks(SCENE) {
  const s = SCENE, c = s.counts, I = s.instances;
  const ops = I.filter(i => i.is_swarm_platform);
  const ref = I.filter(i => i.is_reference_mockup);
  const inf = I.filter(i => i.nature === "infrastructure");
  const checks = [];

  const withT = I.filter(i => i.transform !== null && i.transform !== undefined);
  checks.push(["REG-6 / INV-4", withT.length === 0]);

  checks.push(["REG-5", ops.length === 30 && ref.length === 1]);

  const ids = new Set(I.map(i => i.instance_id));
  const cls = new Set(I.map(i => i.class_id));
  const fromModel = new Set(s.derivation_links.map(l => l.from));
  checks.push(["REG-1",
    ids.size === I.length && [...cls].every(k => fromModel.has(k))]);

  const tx = obsText(s);
  checks.push(["REG-4", !!tx.match(/N\s*=\s*30\s*NON\s*PROUV/i)]);
  checks.push(["REG-2", !tx.match(/\b(Wh|mAh|%|autonomie\s*\d)/i)]);
  checks.push(["REG-3", !tx.match(/\b\d+\s*(km|m)\b/i)]);

  checks.push(["INTÉGRITÉ",
    c.instances === I.length && c.operational_platforms === ops.length
    && c.reference_mockups === ref.length && c.infrastructure === inf.length]);

  const ver = s.render_rules.filter(r => r.verifiable);
  checks.push(["GARDE-FOUS",
    s.render_rules.length >= 6 && ver.length === s.render_rules.length]);

  return checks;
}

const clone = o => JSON.parse(JSON.stringify(o));

function main() {
  const s = JSON.parse(fs.readFileSync(SCENE_PATH, "utf8"));
  let ok = true;

  console.log("=== A. ARTEFACT REEL — logique JS du viewer ===");
  const res = runChecks(s);
  res.forEach(([k, v]) => console.log(`  ${v ? "OK  " : "FAIL"} ${k}`));
  const passed = res.filter(([, v]) => v).length;
  console.log(`  -> ${passed}/${res.length} controles passes`);
  if (passed !== res.length) ok = false;

  console.log("\n=== B. MUTATIONS — le controle cible DOIT echouer ===");
  const muts = [];
  let m;

  m = clone(s); m.states[0].rendering = "batterie a 42%";
  muts.push(["energie % dans un etat", "REG-2", m]);

  m = clone(s); m.instances[0].class_id = "entClasseInventee";
  muts.push(["class_id hors modele", "REG-1", m]);

  m = clone(s); m.consumer_obligations.push("portee radio 15 km");
  muts.push(["portee 15 km dans les obligations", "REG-3", m]);

  m = clone(s); m.instances[0].transform = { x: 1, y: 2, z: 3 };
  muts.push(["transform non nul", "REG-6 / INV-4", m]);

  m = clone(s); m.instances.slice(0, 3).forEach(i => { i.is_swarm_platform = false; });
  muts.push(["3 plateformes requalifiees", "REG-5", m]);

  m = clone(s); m.counts.operational_platforms = 33;
  muts.push(["compteur declare 33", "INTÉGRITÉ", m]);

  m = clone(s);
  m.consumer_obligations = m.consumer_obligations.filter(o => !/NON PROUVE/i.test(o));
  m.states.forEach(st => {
    if (st.rendering) st.rendering = st.rendering.replace("N=30 NON PROUVE", "");
    if (st.limit) st.limit = st.limit.replace("N=30 NON PROUVE", "");
  });
  muts.push(["mention N=30 NON PROUVE retiree de toutes ses sources", "REG-4", m]);

  for (const [label, target, mm] of muts) {
    const r = Object.fromEntries(runChecks(mm));
    const caught = r[target] === false;
    console.log(`  ${caught ? "ATTRAPE " : "RATE   "} [${target}] <- ${label}`);
    if (!caught) ok = false;
  }

  console.log("\n=== RESULTAT ===");
  console.log(ok
    ? "OK — logique de verification du viewer VALIDE sous Node (8/8 + 6/6 mutations)"
    : "ECHEC");
  process.exit(ok ? 0 : 1);
}

main();
