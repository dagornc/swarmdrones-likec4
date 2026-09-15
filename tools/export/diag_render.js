// Diagnostic de rendu reel de viewer/index.html via Playwright (conteneur).
// Expose l'etat REEL : console, erreurs, geometrie DOM, verdict des controles.
const { chromium } = require('/usr/lib/node_modules/@playwright/mcp/node_modules/playwright-core');

const PAGE = 'http://172.16.1.1:8931/index.html';
const EXE = '/ms-playwright/chromium-1200/chrome-linux64/chrome';

(async () => {
  const browser = await chromium.launch({
    executablePath: EXE, headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });

  const logs = [], errs = [];
  page.on('console', m => logs.push(m.type() + ': ' + m.text()));
  page.on('pageerror', e => errs.push(String(e)));

  await page.goto(PAGE, { waitUntil: 'load', timeout: 30000 });
  // laisser le boot asynchrone (loadThree 9s max) se terminer
  await page.waitForTimeout(11000);

  const state = await page.evaluate(() => {
    const g = id => { const e = document.getElementById(id); return e; };
    const box = e => { if (!e) return null; const r = e.getBoundingClientRect();
      return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }; };
    const cv = g('c');
    const out = {
      mode: (typeof mode !== 'undefined') ? mode : 'UNDEF',
      threeLoaded: (typeof window.THREE !== 'undefined') ? !!window.THREE : false,
      hasScene: (typeof SCENE !== 'undefined') ? !!SCENE : false,
      counts: (typeof SCENE !== 'undefined' && SCENE.counts) ? SCENE.counts : null,
      checks: (typeof window.__CHECKS !== 'undefined') ? window.__CHECKS : null,
      canvas: cv ? { box: box(cv), width: cv.width, height: cv.height,
                     clientW: cv.clientWidth, clientH: cv.clientHeight } : null,
      stage: box(g('stage')), hud: box(g('hud')), scenebar: box(g('scenebar')),
      scenebarHTML: g('scenebar') ? g('scenebar').children.length : -1,
      legend: box(g('legend')),
      bannerShown: g('banner') ? g('banner').className : null,
      bannerText: g('banner') ? (g('banner').textContent || '').slice(0, 120) : null,
      checksHTMLlen: g('checks') ? g('checks').innerHTML.length : -1,
      kpisHTMLlen: g('kpis') ? g('kpis').innerHTML.length : -1,
      bodyLen: document.body.innerHTML.length,
    };
    return out;
  });

  console.log('===== ETAT REEL DE LA PAGE =====');
  console.log(JSON.stringify(state, null, 2));
  console.log('\n===== ERREURS JS (' + errs.length + ') =====');
  errs.forEach(e => console.log('  ' + e.slice(0, 300)));
  console.log('\n===== CONSOLE (' + logs.length + ') =====');
  logs.slice(0, 30).forEach(l => console.log('  ' + l.slice(0, 300)));

  await page.screenshot({ path: '/tmp/diag.png', fullPage: false });
  console.log('\nscreenshot -> /tmp/diag.png');
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
