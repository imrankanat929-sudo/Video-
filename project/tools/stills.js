// Render still frames at given times: node tools/stills.js out_dir lang t1 t2 ...
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const serve = require('./server');
(async () => {
  const [out, lang, ...times] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const srv = await serve(); const port = srv.address().port;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('console', m => console.log('[page]', m.text())); p.on('pageerror', e => console.log('[err]', e.message));
  await p.goto(`http://127.0.0.1:${port}/index.html?render=1&lang=${lang}`); await p.evaluate(() => window.bootDone);
  for (const t of times) {
    const f = Math.round(+t * 30);
    const url = await p.evaluate(f => { window.renderFrame(f); return window.grabFrame(0.9); }, f);
    fs.writeFileSync(path.join(out, `t${(+t).toFixed(2).padStart(6, '0')}.jpg`), Buffer.from(url.split(',')[1], 'base64'));
  }
  await b.close(); srv.close();
})();
