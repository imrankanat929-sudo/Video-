// YouTube thumbnail: node tools/thumbnail.js [lang] -> output/thumbnail_<lang>.png (1280x720) + _1080.png
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const serve = require('./server');
(async () => {
  const lang = process.argv[2] || 'ru';
  const out = path.resolve(__dirname, '../../output');
  const srv = await serve(); const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('[err]', e.message));
  await p.goto(`http://127.0.0.1:${srv.address().port}/index.html?render=1&lang=${lang}`); await p.evaluate(() => window.bootDone);
  const url = await p.evaluate(() => window.renderThumb());
  const big = path.join(out, `thumbnail_${lang}_1080.png`);
  fs.writeFileSync(big, Buffer.from(url.split(',')[1], 'base64'));
  execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-i', big, '-vf', 'scale=1280:720:flags=lanczos', path.join(out, `thumbnail_${lang}.png`)]);
  const v = await p.evaluate(() => window.renderThumbV());
  fs.writeFileSync(path.join(out, `thumbnail_${lang}_9x16.png`), Buffer.from(v.split(',')[1], 'base64'));
  console.log('ok'); await b.close(); srv.close();
})();
