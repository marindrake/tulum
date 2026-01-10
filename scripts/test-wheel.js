const puppeteer = require('puppeteer');
(async ()=>{
  const url = process.argv[2] || 'http://localhost:8000/';
  const browser = await puppeteer.launch({args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  page.on('console', msg => { try{ console.log('PAGE LOG:', msg.text()); }catch(e){} });
  page.on('pageerror', err => { console.error('PAGE ERROR:', err.message); });
  page.setDefaultTimeout(30000);
  await page.goto(url, {waitUntil:'networkidle2'});
  // open wheel
  await page.waitForSelector('#spinTrigger', {timeout:10000});
  await page.click('#spinTrigger');
  await page.waitForSelector('#wheelModal', {timeout:10000});
  console.log('modal present');
  const hasWheel = await page.$('#wheel') !== null;
  console.log('has #wheel?', hasWheel);
  // if coupon already exists, read it
  let existing = await page.evaluate(()=> localStorage.getItem('tulum_coupon'));
  if(existing){
    console.log('existing', existing);
    await browser.close();
    process.exit(0);
  }
  // click spin
  await page.waitForSelector('#spinBtn', {timeout:10000});
  console.log('found #spinBtn, clicking');
  await page.evaluate(()=> document.getElementById('spinBtn').click());
  // wait until localStorage has tulum_coupon
  const result = await page.waitForFunction(()=> !!localStorage.getItem('tulum_coupon'), {polling:200, timeout:20000}).then(()=>{
    return page.evaluate(()=> localStorage.getItem('tulum_coupon'));
  }).catch(()=>null);

  if(result){
    try{
      const parsed = JSON.parse(result);
      console.log(JSON.stringify({ok:true, coupon: parsed}, null, 2));
    }catch(e){
      console.log('raw', result);
    }
  } else {
    console.error('timeout waiting for coupon');
  }
  await browser.close();
})();