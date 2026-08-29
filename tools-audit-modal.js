const {JSDOM,VirtualConsole}=require('jsdom'),fs=require('fs'),path=require('path');
const ROOT='/sessions/serene-affectionate-euler/mnt/miami-jetski-main';
const files=JSON.parse(fs.readFileSync('/tmp/sample.json','utf8'));
process.on('unhandledRejection',()=>{});process.on('uncaughtException',()=>{});
const out=[];
(async()=>{
for(const rel of files){
  const errs=[];
  let dom;
  try{
    dom=new JSDOM(fs.readFileSync(path.join(ROOT,rel),'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,
      virtualConsole:new VirtualConsole(),url:'https://miamijetskiboatrentals.com/'+rel.replace(/\.html$/,''),
      beforeParse(w){w.dataLayer=[];w.matchMedia=q=>({matches:false,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}});
        class IO{observe(){}unobserve(){}disconnect(){}}w.IntersectionObserver=IO;w.ResizeObserver=IO;w.scrollTo=()=>{};
        const mk=()=>new Proxy(function(){},{get:(t,p)=>p==='then'?undefined:(p===Symbol.toPrimitive||p==='toString')?()=>'s':mk(),apply:()=>mk(),construct:()=>mk()});w.L=mk();
        w.fetch=u=>{let p=String(u).replace(/^https?:\/\/[^/]+/,'').replace(/^\.?\//,'').split('?')[0];const fp=path.join(ROOT,p);
          if(fs.existsSync(fp))return Promise.resolve({ok:true,json:()=>Promise.resolve(JSON.parse(fs.readFileSync(fp,'utf8')))});return Promise.reject(new Error('404'));};}});
    const w=dom.window;
    w.document.dispatchEvent(new w.Event('DOMContentLoaded',{bubbles:true}));
    w.dispatchEvent(new w.Event('load'));
    await new Promise(r=>setTimeout(r,180));
    const a=w.document.querySelector('a[href*="fareharbor.com/embeds/book/"]');
    if(!a){ out.push([rel,['sin enlace FH']]); continue; }
    const orig=a.getAttribute('href');
    a.dispatchEvent(new w.MouseEvent('click',{bubbles:true,cancelable:true}));
    await new Promise(r=>setTimeout(r,120));
    const ifr=w.document.querySelector('#fhModalIframe,iframe[title*="FareHarbor"]');
    if(!ifr){ if(w.document.querySelector('#fhModal')) errs.push('MODAL: existe #fhModal pero no encuentro el iframe'); }
    else{
      const src=ifr.getAttribute('src')||'';
      if(!src||src==='about:blank') errs.push('MODAL: el iframe no cargó ninguna URL al pulsar');
      else{
        let u; try{u=new w.URL(src);}catch(e){errs.push('MODAL: src inválido '+src.slice(0,60));}
        if(u){
          if(!/fareharbor\.com$/.test(u.hostname)) errs.push('MODAL: dominio inesperado '+u.hostname);
          const ks=[...u.searchParams.keys()];
          if(ks.length!==new Set(ks).size) errs.push('MODAL: PARÁMETRO DUPLICADO en el iframe');
          if(u.searchParams.get('ref')!=='miamistylerentals') errs.push('MODAL: ref='+u.searchParams.get('ref'));
          if(u.searchParams.get('asn-ref')!=='miamistylerentals') errs.push('MODAL: asn-ref='+u.searchParams.get('asn-ref'));
          if(!(u.searchParams.get('asn')||'').startsWith('fhdn')) errs.push('MODAL: asn='+u.searchParams.get('asn'));
          if(/\/calendar\/\d{4}\/\d{2}\//.test(u.pathname)) errs.push('MODAL: CALENDARIO FIJO en el iframe');
          const o=new w.URL(orig,'https://x/');
          if(o.pathname!==u.pathname) errs.push('MODAL: cambió el item '+o.pathname+' -> '+u.pathname);
        }
      }
    }
  }catch(e){errs.push('THROW '+String(e.message).slice(0,90));}
  if(dom)try{dom.window.close()}catch(e){}
  if(errs.length)out.push([rel,errs]);
}
console.log('páginas probadas:',files.length,'| con problemas en el modal:',out.length);
out.slice(0,20).forEach(([f,e])=>console.log('  '+f+'\n     '+e.join('\n     ')));
})();
