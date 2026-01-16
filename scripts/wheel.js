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
    // Use conic-gradient for nice looking colored wheel and add rotated labels
    wheelEl.innerHTML = '';
    const segCount = segments.length;
    const colors = ['#fff4e6','#fffbe6','#fff4f0','#fff0f6','#f0fff6','#e6fbff','#f0f7ff','#f7f0ff'];
    const colorList = [];
    for(let i=0;i<segCount;i++) colorList.push(colors[i % colors.length]);
    const stops = colorList.map((c,i)=> `${c} ${Math.round((i/segCount)*100)}% ${(Math.round(((i+1)/segCount)*100))}%`).join(', ');
    // build conic-gradient string
    const grad = `conic-gradient(${colorList.map((c,i)=> `${c} ${i*(360/segCount)}deg ${(i+1)*(360/segCount)}deg`).join(',')})`;
    wheelEl.style.background = grad;
    // create labels
    const segAngle = 360 / segCount;
    segments.forEach((s,i)=>{
      const lbl = document.createElement('div');
      lbl.className = 'label';
      const angle = i * segAngle;
      lbl.style.transform = `rotate(${angle}deg) translate(-100%, -100%)`;
      lbl.innerHTML = `<div style="transform: rotate(${segAngle}deg); padding:6px 8px; background:transparent;">${s.text}</div>`;
      wheelEl.appendChild(lbl);
    });
  }

  function randomChoiceWeighted(){
    // adjusted probabilities: favor 10 and 12, rare 20
    return [
      {pct:10, weight:40},
      {pct:12, weight:28},
      {pct:15, weight:16},
      {pct:18, weight:10},
      {pct:20, weight:6}
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
    return `TULUM${pct}`;
  }

  // Audio helpers using WebAudio API (runs in browser)
  function createAudioContext(){
    try{ return new (window.AudioContext || window.webkitAudioContext)(); }catch(e){ return null; }
  }
  function startSpinSound(ctx){
    if(!ctx) return null;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sawtooth';
    o.frequency.value = 120;
    g.gain.value = 0.0001;
    o.connect(g);
    g.connect(ctx.destination);
    o.start();
    // ramp up
    g.gain.exponentialRampToValueAtTime(0.02, ctx.currentTime + 0.25);
    // sweep frequency slowly
    o.frequency.exponentialRampToValueAtTime(600, ctx.currentTime + 4.5);
    return {osc:o,gain:g,ctx:ctx};
  }
  function stopSpinSound(handle){
    if(!handle) return;
    try{
      handle.gain.gain.exponentialRampToValueAtTime(0.0001, handle.ctx.currentTime + 0.8);
      setTimeout(()=>{ try{ handle.osc.stop(); handle.osc.disconnect(); }catch(e){} }, 900);
    }catch(e){}
  }
  function playSuccessChime(ctx){
    if(!ctx) return;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sine';
    o.frequency.value = 440;
    g.gain.value = 0.0001;
    o.connect(g); g.connect(ctx.destination);
    o.start();
    g.gain.exponentialRampToValueAtTime(0.08, ctx.currentTime + 0.02);
    o.frequency.linearRampToValueAtTime(660, ctx.currentTime + 0.18);
    setTimeout(()=>{ g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.45); try{ o.stop(); }catch(e){} }, 400);
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
    // more segments for a Temu-like wheel — repeat values to make 12 slices
    const base = [10,12,15,10,12,18,10,15,20,12,10,15];
    const segments = base.map(p=>({text: p + '%', pct: p}));
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
    let audioHandle = null;
    const audioCtx = createAudioContext();
    spinBtn.addEventListener('click', async ()=>{
      if(spinning) return;
      spinning = true;
      spinBtn.disabled = true;

      // Decide prize
      const pct = pickRandom();
      // find index in segments (use first match)
      // pick an index among segments that match desired pct (random among matches)
      const matching = segments.map((s,i)=> ({s,i})).filter(x=>x.s.pct===pct).map(x=>x.i);
      const idx = matching[Math.floor(Math.random()*matching.length)];
      const segCount = segments.length;
      const segAngle = 360 / segCount;
      // compute target rotation so that pointer at top lands on chosen segment
      // wheel rotation: rotate to large number + target
      const randomSpins = 5 + Math.floor(Math.random()*3); // 5-7 spins
      const variability = (segAngle*0.6);
      const targetAngle = 360*randomSpins + (360 - (idx * segAngle) - segAngle/2) + (Math.random()*variability - variability/2);
      // start audio
      audioHandle = startSpinSound(audioCtx);
      wheel.style.transition = 'transform 5s cubic-bezier(.16,.84,.24,1)';
      wheel.style.transform = `rotate(${targetAngle}deg)`;

      // wait for transition end
      wheel.addEventListener('transitionend', function onEnd(){
        wheel.removeEventListener('transitionend', onEnd);
        const code = generateCoupon(pct);
        // expiry: valid for next visit (30 days)
        const created = new Date();
        const expiry = new Date(created);
        expiry.setDate(expiry.getDate() + 30);
        const payload = {pct, code, created: created.toISOString(), expires: expiry.toISOString()};
        localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
        resultEl.innerHTML = `<strong>¡Ganaste ${pct}% de descuento!</strong><div style="margin-top:8px">Tu código: <code id="couponCode">${code}</code> <button id="copyCoupon" class="btn btn-small">Copiar</button></div><div style="margin-top:8px;font-size:13px;color:#666">Muestra este código en tu próxima visita.</div>`;
        const copyBtn = document.getElementById('copyCoupon');
        copyBtn && copyBtn.addEventListener('click', ()=>{ navigator.clipboard.writeText(code); alert('Código copiado'); });
        // stop audio and play chime
        stopSpinSound(audioHandle);
        playSuccessChime(audioCtx);
        // show terms modal with expiry
        showTermsModal(payload);
        spinBtn.disabled = false;
        spinning = false;
      });
    });

    closeBtn.addEventListener('click', ()=> modal.remove());
    modal.classList.add('open');
  }

  // Terms modal: shows expiry and basic terms, requires acknowledgment
  function showTermsModal(payload){
    // remove existing
    if(document.getElementById('termsModal')) document.getElementById('termsModal').remove();
    const div = document.createElement('div');
    div.className = 'terms-modal open';
    div.id = 'termsModal';
    const expiry = new Date(payload.expires);
    const expiryText = expiry.toLocaleDateString();
    div.innerHTML = `<div class="terms-dialog" role="dialog" aria-modal="true"><h4>Términos del cupón</h4><p>Has obtenido <strong>${payload.pct}%</strong> de descuento. Código: <strong>${payload.code}</strong>.</p><p>Válido para la próxima visita hasta el <strong>${expiryText}</strong>. Presenta este código en el local para aplicar el descuento. No acumulable con otras promociones.</p><div class="terms-actions"><button id="termsClose" class="btn btn-primary">Aceptar</button><button id="termsDismiss" class="btn btn-outline">Cerrar</button></div></div>`;
    document.body.appendChild(div);
    document.getElementById('termsClose').addEventListener('click', ()=>{ div.remove(); });
    document.getElementById('termsDismiss').addEventListener('click', ()=>{ div.remove(); });
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
