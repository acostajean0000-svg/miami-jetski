const {JSDOM,VirtualConsole}=require('jsdom'), fs=require('fs'), path=require('path');
const ROOT='/sessions/serene-affectionate-euler/mnt/miami-jetski-main';
const files=JSON.parse(fs.readFileSync('/tmp/sample.json','utf8'));
const SKIP=/matchMedia|IntersectionObserver|ResizeObserver|Not implemented|scrollTo|createObjectURL|requestIdleCallback/i;
process.on('unhandledRejection',()=>{});
process.on('uncaughtException',e=>{ if(!/Cannot read|not a function|Not implemented|primitive/.test(String(e&&e.message))) console.log('UNCAUGHT:',String(e&&e.message).slice(0,120)); });
const out=[];
function poly(w,errs){
  w.matchMedia=q=>({matches:false,media:q,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){},onchange:null});
  class IO{constructor(cb){this.cb=cb}observe(){}unobserve(){}disconnect(){}takeRecords(){return[]}}
  w.IntersectionObserver=IO; w.ResizeObserver=IO;
  w.scrollTo=()=>{}; w.requestIdleCallback=cb=>setTimeout(cb,0);
  w.dataLayer=w.dataLayer||[]; w.gtag=function(){w.dataLayer.push(arguments)};
  const mk=()=>new Proxy(function(){},{
    get:(t,p)=>{ if(p==='then')return undefined;
      if(p===Symbol.toPrimitive||p==='toString')return ()=>'stub';
      if(p==='length')return 0; if(p==='getCenter'||p==='getBounds')return ()=>mk();
      return mk(); },
    apply:()=>mk(), construct:()=>mk(),
    has:()=>true, set:()=>true });
  w.L=mk(); w.Chart=mk(); w.Swiper=mk();
  w.fetch=(u)=>{let p=String(u).replace(/^https?:\/\/[^/]+/,'').replace(/^\//,'').split('?')[0];
    const fp=require('path').join(ROOT,p);
    if(require('fs').existsSync(fp))return Promise.resolve({ok:true,status:200,json:()=>Promise.resolve(JSON.parse(require('fs').readFileSync(fp,'utf8'))),text:()=>Promise.resolve(require('fs').readFileSync(fp,'utf8'))});
    errs.push('FETCH 404: /'+p); return Promise.reject(new Error('404'));};
}
(async()=>{
for(const rel of files){
  const errs=[];
  const vc=new VirtualConsole();
  vc.on('jsdomError',e=>errs.push('ERROR: '+(e.message||'').slice(0,170)));
  vc.on('error',(...a)=>errs.push('console.error: '+String(a[0]).slice(0,170)));
  let dom;
  try{
    dom=new JSDOM(fs.readFileSync(path.join(ROOT,rel),'utf8'),{
      runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,
      url:'https://miamijetskiboatrentals.com/'+rel.replace(/\.html$/,''),
      beforeParse(w){ poly(w,errs); }});
    const w=dom.window;
    w.matchMedia=q=>({matches:false,media:q,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){},onchange:null});
    class IO{constructor(cb){this.cb=cb}observe(){}unobserve(){}disconnect(){}takeRecords(){return[]}}
    w.IntersectionObserver=IO; w.ResizeObserver=IO;
    w.scrollTo=()=>{}; w.requestIdleCallback=cb=>setTimeout(cb,0);
    w.dataLayer=w.dataLayer||[]; if(!w.gtag) w.gtag=function(){w.dataLayer.push(arguments)};
    w.L=w.L||new Proxy(function(){},{get:()=>new Proxy(function(){},{get:()=>()=>({})  ,apply:()=>({on(){},addTo(){return this},setView(){return this},remove(){}})}),apply:()=>({on(){},addTo(){return this},setView(){return this}})});
    const mk=()=>new Proxy(function(){},{
    get:(t,p)=>{ if(p==='then')return undefined;
      if(p===Symbol.toPrimitive||p==='toString')return ()=>'stub';
      if(p==='length')return 0; if(p==='getCenter'||p==='getBounds')return ()=>mk();
      return mk(); },
    apply:()=>mk(), construct:()=>mk(),
    has:()=>true, set:()=>true });
  w.L=mk(); w.Chart=mk(); w.Swiper=mk();
  w.fetch=(u)=>{let p=String(u).replace(/^https?:\/\/[^/]+/,'').replace(/^\//,'').split('?')[0];
      const fp=path.join(ROOT,p);
      if(fs.existsSync(fp))return Promise.resolve({ok:true,status:200,json:()=>Promise.resolve(JSON.parse(fs.readFileSync(fp,'utf8'))),text:()=>Promise.resolve(fs.readFileSync(fp,'utf8'))});
      errs.push('FETCH 404: /'+p); return Promise.reject(new Error('404'));
    };
    w.document.dispatchEvent(new w.Event('DOMContentLoaded',{bubbles:true}));
    w.dispatchEvent(new w.Event('load'));
    await new Promise(r=>setTimeout(r,160));
    // ---- prueba de conversión: clic en el primer botón de reserva ----
    try{
      const btn=[...w.document.querySelectorAll('a[onclick*="trackBookNow"]')][0]
                || [...w.document.querySelectorAll('a[href*="fareharbor.com/embeds/book/"]')][0];
      if(btn){
        const before=w.dataLayer.length;
        btn.dispatchEvent(new w.MouseEvent('click',{bubbles:true,cancelable:true}));
        const ev=w.dataLayer.slice(before).map(a=>Array.prototype.slice.call(a));
        const conv=ev.find(a=>a[0]==='event'&&a[1]==='conversion');
        const nconv=ev.filter(a=>a[0]==='event'&&a[1]==='conversion').length;
        if(nconv>1) errs.push('DOBLE: un clic disparó '+nconv+' conversiones');
        if(!conv) errs.push('CONV: el clic NO disparó ninguna conversión');
        else{
          const p=conv[2]||{};
          if(!p.send_to) errs.push('CONV: conversión sin send_to');
          else if(!/^AW-16509204378\//.test(p.send_to)) errs.push('CONV: send_to inesperado '+p.send_to);
          if(!(parseFloat(p.value)>0)) errs.push('CONV: valor '+JSON.stringify(p.value));
        }
        const href=btn.getAttribute('href')||'';
        if(href && !/^https:\/\/fareharbor\.com\//.test(href)) errs.push('LINK: el botón no apunta a FareHarbor -> '+href.slice(0,60));
      } else if(w.document.querySelector('a[href*="fareharbor.com"]')) errs.push('CONV: enlace FH sin ningún botón pulsable');
    }catch(e){ errs.push('CONV THROW: '+String(e.message).slice(0,120)); }
    const cards=w.document.querySelector('#cards,#grid,.op-grid,.cards');
    if(cards && cards.children.length===0) errs.push('VACIO: contenedor de tarjetas sin hijos tras cargar');
  }catch(e){errs.push('THROW: '+String(e.message).slice(0,170));}
  if(dom)try{dom.window.close()}catch(e){}
  const real=[...new Set(errs)].filter(e=>!SKIP.test(e));
  if(real.length)out.push([rel,real]);
}
fs.writeFileSync('/tmp/res.json',JSON.stringify(out,null,1));
console.log('páginas ejecutadas:',files.length,'| con errores reales:',out.length);
out.slice(0,25).forEach(([f,e])=>console.log('  '+f+'\n     '+e.join('\n     ')));
})();
