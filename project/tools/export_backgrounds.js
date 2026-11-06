// Export background plates as PNG: node tools/export_backgrounds.js
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const serve = require('./server');
(async () => {
  const out = path.resolve(__dirname, '../assets/backgrounds');
  const srv = await serve(); const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('[err]', e.message));
  await p.goto(`http://127.0.0.1:${srv.address().port}/index.html?render=1&lang=ru`); await p.evaluate(() => window.bootDone);
  for (const n of await p.evaluate(() => window.plateNames())) {
    const url = await p.evaluate(n => window.renderPlate(n), n);
    fs.writeFileSync(path.join(out, `bg_${n}.png`), Buffer.from(url.split(',')[1], 'base64'));
    console.log('bg_' + n + '.png');
  }
  await b.close(); srv.close();
})();
