const puppeteer = require('puppeteer');
(async ()=>{
  const url = process.argv[2] || 'http://localhost:8000/';
  const browser = await puppeteer.launch({args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  await page.setViewport({width:1280, height:900});
  await page.goto(url, {waitUntil:'networkidle2'});
  // ensure spin trigger is visible
  try{ await page.waitForSelector('#spinTrigger', {timeout:5000}); }catch(e){}
  // take full page screenshot
  const out = 'assets/screenshot-wheel.png';
  await page.screenshot({path: out, fullPage: true});
  console.log('saved', out);
  await browser.close();
})();
