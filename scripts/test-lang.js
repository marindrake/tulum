const puppeteer = require('puppeteer');

(async () => {
  console.log('test-lang: starting');
  const url = process.argv[2] || 'http://localhost:8000/';
  let browser;
  try{
    console.log('test-lang: launching browser');
    browser = await puppeteer.launch({args: ['--no-sandbox','--disable-setuid-sandbox']});
    console.log('test-lang: browser launched');
  }catch(err){
    console.error('launch error', err && err.message);
    process.exit(1);
  }
  const page = await browser.newPage();
  page.setDefaultTimeout(15000);
  await page.goto(url, { waitUntil: 'networkidle2' });
  console.log('test-lang: page loaded');
  console.log('test-lang: waiting for translations (best-effort)');

  // helper to read first 3 menu item names
  async function readMenuItems(){
    // wait up to 20s for menu items to appear
    try{
      await page.waitForSelector('#menuColumns .menu-col ul li .item', {timeout: 20000});
    }catch(e){
      // continue and attempt to read whatever is present
    }
    return page.evaluate(() => {
      const nodes = Array.from(document.querySelectorAll('#menuColumns .menu-col ul li .item'));
      return nodes.slice(0,6).map(n => n.textContent.trim());
    });
  }

  // ensure translations loaded (best-effort)
  await page.waitForFunction(() => window.TRANSLATIONS !== null, {timeout: 5000}).catch(()=>{});
  // give extra time for menu fetch and render
  await new Promise(r => setTimeout(r, 500));

  const results = { url };
  console.log('test-lang: evaluating initial language');
  // capture initial (detected or saved) language
  results.initial_lang = await page.evaluate(() => window.LANG || localStorage.getItem('tulum_lang') || null);
  console.log('test-lang: initial_lang ->', results.initial_lang);
  results.before = await readMenuItems();
  console.log('test-lang: captured before items', results.before);

  // click EN
  await page.evaluate(() => { if(window.setLang) setLang('en'); });
  console.log('test-lang: setLang en');
  await new Promise(r => setTimeout(r, 400));
  results.en = await readMenuItems();

  // click FR
  await page.evaluate(() => { if(window.setLang) setLang('fr'); });
  console.log('test-lang: setLang fr');
  await new Promise(r => setTimeout(r, 400));
  results.fr = await readMenuItems();

  // click ES
  await page.evaluate(() => { if(window.setLang) setLang('es'); });
  console.log('test-lang: setLang es');
  await new Promise(r => setTimeout(r, 400));
  results.es = await readMenuItems();

  const out = JSON.stringify(results, null, 2);
  const fs = require('fs');
  try{ fs.writeFileSync('scripts/lang-result.json', out); }catch(e){ /* ignore */ }
  console.log('test-lang: finished', out);
  await browser.close();
})();
process.on('unhandledRejection', (e) => { console.error('UnhandledRejection', e && e.message); process.exit(1); });