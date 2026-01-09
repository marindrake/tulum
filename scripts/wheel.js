(function(){
  // Spin wheel feature: one spin per visitor (stored in localStorage)
  const TRIGGER_ID = 'spinTrigger';
  const STORAGE_KEY = 'tulum_coupon';
  const modalHtml = `
  <div class="wheel-modal" id="wheelModal" role="dialog" aria-modal="true" aria-label="Gira y gana">
    <div class="wheel-dialog">
      <h3>Gira la rueda y gana un descuento</h3>
      <div class="wheel-canvas">
        <div class="wheel-pointer" aria-hidden="true"></div>
        <div class="wheel" id="wheel">
        </div>
      </div>
      <div class="wheel-result" id="wheelResult"></div>
      <div style="margin-top:12px">
        <button id="spinBtn" class="btn btn-primary btn-small">Girar</button>
        <button id="closeWheel" class="btn btn-outline btn-small">Cerrar</button>
      </div>
    </div>
  </div>`;

  function createSegments(wheelEl, segments){
    wheelEl.innerHTML = '';
    const segAngle = 360 / segments.length;
    segments.forEach((s, i)=>{
      const div = document.createElement('div');
      div.className = 'segment';
      const angle = i * segAngle;
      const color = i%2===0 ? '#fff8f3' : '#fff';
      div.style.transform = `rotate(${angle}deg) translate(-100%, -100%)`;
      div.innerHTML = `<div style="transform:rotate(${segAngle}deg);background:${color};padding:12px 10px;border-radius:6px;border:1px solid rgba(0,0,0,0.04);font-weight:700;">${s.text}</div>`;
      wheelEl.appendChild(div);
    });
  }

  function randomChoiceWeighted(){
    // define possible results and weights (more chance for 10-15)
    return [
      {pct:10, weight:30},
      {pct:12, weight:25},
      {pct:15, weight:20},
      {pct:18, weight:15},
      {pct:20, weight:10}
    ];
  }

  function pickRandom(){
    const items = randomChoiceWeighted();
    const sum = items.reduce((a,b)=>a+b.weight,0);
    let r = Math.random()*sum;
    for(const it of items){
      if(r < it.weight) return it.pct;
      r -= it.weight;
    }
    return items[0].pct;
  }

  function generateCoupon(pct){
    const t = Date.now().toString(36).toUpperCase();
    const r = Math.random().toString(36).slice(2,8).toUpperCase();
    return `TULUM${pct}-${t}-${r}`;
  }

  function showModal(){
    if(document.getElementById('wheelModal')) return;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('wheelModal');
    const wheel = document.getElementById('wheel');
    const spinBtn = document.getElementById('spinBtn');
    const closeBtn = document.getElementById('closeWheel');
    const resultEl = document.getElementById('wheelResult');

    // build visible segments for the wheel
    const segments = [10,12,15,18,20].map(p=>({text:p+"%", pct:p}));
    createSegments(wheel, segments);

    // if user already has coupon, show it
    const saved = localStorage.getItem(STORAGE_KEY);
    if(saved){
      const data = JSON.parse(saved);
      resultEl.innerHTML = `<strong>Ya ganaste: ${data.pct}%</strong><div style="margin-top:8px">Código: <code>${data.code}</code> <button id="copyCoupon" class="btn btn-small">Copiar</button></div>`;
      modal.classList.add('open');
      const copyBtn = document.getElementById('copyCoupon');
      copyBtn && copyBtn.addEventListener('click', ()=>{ navigator.clipboard.writeText(data.code); alert('Código copiado'); });
      closeBtn.addEventListener('click', ()=> modal.remove());
      return;
    }

    let spinning = false;
    spinBtn.addEventListener('click', async ()=>{
      if(spinning) return;
      spinning = true;
      spinBtn.disabled = true;

      // Decide prize
      const pct = pickRandom();
      // find index in segments (use first match)
      const idx = segments.findIndex(s=>s.pct===pct);
      const segCount = segments.length;
      const segAngle = 360 / segCount;
      // compute target rotation so that pointer at top lands on chosen segment
      // wheel rotation: rotate to large number + target
      const randomSpins = 5 + Math.floor(Math.random()*3); // 5-7 spins
      const targetAngle = 360*randomSpins + (360 - (idx * segAngle) - segAngle/2) + (Math.random()* (segAngle/2) - segAngle/4);
      wheel.style.transition = 'transform 4s cubic-bezier(.12,.8,.25,1)';
      wheel.style.transform = `rotate(${targetAngle}deg)`;

      // wait for transition end
      wheel.addEventListener('transitionend', function onEnd(){
        wheel.removeEventListener('transitionend', onEnd);
        const code = generateCoupon(pct);
        const payload = {pct, code, created: new Date().toISOString()};
        localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
        resultEl.innerHTML = `<strong>¡Ganaste ${pct}% de descuento!</strong><div style="margin-top:8px">Tu código: <code id="couponCode">${code}</code> <button id="copyCoupon" class="btn btn-small">Copiar</button></div><div style="margin-top:8px;font-size:13px;color:#666">Muestra este código en tu próxima visita.</div>`;
        const copyBtn = document.getElementById('copyCoupon');
        copyBtn && copyBtn.addEventListener('click', ()=>{ navigator.clipboard.writeText(code); alert('Código copiado'); });
        spinBtn.disabled = false;
        spinning = false;
      });
    });

    closeBtn.addEventListener('click', ()=> modal.remove());
    modal.classList.add('open');
  }

  // wire trigger
  document.addEventListener('DOMContentLoaded', ()=>{
    const trigger = document.getElementById(TRIGGER_ID);
    if(!trigger) return;
    trigger.addEventListener('click', (e)=>{
      e.preventDefault();
      showModal();
    });
  });
})();
