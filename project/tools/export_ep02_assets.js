// EP02 package: character sheet, scene illustrations, 9:16 thumbnails.  node tools/export_ep02_assets.js
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const serve = require('./server');
const ROOT = path.resolve(__dirname, '..'), OUT = path.resolve(ROOT, '..', 'output');
const save = (url, file) => { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64')); };
(async () => {
  const srv = await serve(); const b = await chromium.launch(); const port = srv.address().port;
  for (const lang of ['ru', 'en']) {
    const p = await b.newPage(); p.on('pageerror', e => console.log('[err]', e.message));
    await p.goto(`http://127.0.0.1:${port}/index.html?render=1&lang=ep02_${lang}`); await p.evaluate(() => window.bootDone);
    const T = JSON.parse(fs.readFileSync(path.join(ROOT, `config/timeline.ep02_${lang}.json`)));
    if (lang === 'ru' && !process.argv.includes('--thumbs')) {
      // character reference
      save(await p.evaluate(() => window.renderCharacterSheet('MAIN CHARACTER — REFERENCE', [
        'Teen, 15–16. Messy black hair, dark sweater. Shown from the back, in profile or as a silhouette.',
        'Same design, proportions and colours in every scene of every episode.',
        'Lit by rim light: phone / monitor / TV (cold blue), morning window (warm), alerts (red).'])), path.join(ROOT, 'assets/character/hero_reference.png'));
      // illustrations: 3 key frames per scene
      for (const s of T.shots) for (const [k, f] of [[1, 0.15], [2, 0.55], [3, 0.92]]) {
        const t = s.start + (s.end - s.start) * f;
        const url = await p.evaluate(fr => { window.renderFrame(fr); return MAIN.toDataURL('image/jpeg', 0.92); }, Math.round(t * T.fps));
        save(url, path.join(ROOT, `assets/illustrations/ep02/scene_${s.id}_${k}.jpg`));
      }
      console.log('illustrations ok');
    }
    const S = JSON.parse(fs.readFileSync(path.join(ROOT, `config/strings.${lang}.json`)));
    const t = lang === 'ru' ? ['ВОДА ИСЧЕЗЛА', 'СО ВСЕЙ ПЛАНЕТЫ', 'НЕ ПЫТАЙТЕСЬ ВЕРНУТЬ ВОДУ'] : ['WATER IS GONE', 'FROM THE WHOLE PLANET', 'DO NOT TRY TO BRING THE WATER BACK'];
    save(await p.evaluate(a => window.renderThumbCine(...a), t), path.join(OUT, `thumbnail_EP02_${lang}_9x16.png`));
    await p.close();
  }
  await b.close(); srv.close(); console.log('done');
})();
