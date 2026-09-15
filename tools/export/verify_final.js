// Verification finale du rendu : screenshot + mesure objective de l'image.
// Produit la preuve : nombre de pixels non-noirs, couleurs distinctes,
// et le verdict des 8 controles de contrat.
const { chromium } = require('/usr/lib/node_modules/@playwright/mcp/node_modules/playwright-core');
const EXE = '/ms-playwright/chromium-1200/chrome-linux64/chrome';

(async () => {
  const browser = await chromium.launch({
    executablePath: EXE, headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));

  await page.goto('http://172.16.1.1:8931/index.html', { waitUntil: 'load' });
  await page.waitForTimeout(11000);

  // mesure objective directement dans le framebuffer du canvas principal
  const metrics = await page.evaluate(() => {
    const cv = document.getElementById('c');
    const gl = cv.getContext('webgl2') || cv.getContext('webgl');
    if (!gl) return { error: 'no-gl' };
    if (typeof draw === 'function') draw();      // repeupler le buffer
    const w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
    const buf = new Uint8Array(w * h * 4);
    gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, buf);
    let nonBlack = 0; const colors = new Set();
    for (let i = 0; i < buf.length; i += 4) {
      const r = buf[i], g = buf[i + 1], b = buf[i + 2];
      if (r + g + b > 30) nonBlack++;
      colors.add((r >> 4) + ',' + (g >> 4) + ',' + (b >> 4));
    }
    return {
      canvas: w + 'x' + h,
      nonBlackPixels: nonBlack,
      pctNonBlack: +(nonBlack / (w * h) * 100).toFixed(1),
      distinctColors: colors.size,
      checks: window.__CHECKS ? { total: window.__CHECKS.total, fail: window.__CHECKS.fail } : null,
      mode: typeof mode !== 'undefined' ? mode : 'UNDEF',
      scenebar: document.getElementById('scenebar').children.length,
    };
  });

  console.log(JSON.stringify(metrics, null, 2));
  console.log('erreurs JS:', errs.length);

  await page.screenshot({ path: '/tmp/final.png' });
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
