const {JSDOM,VirtualConsole}=require('jsdom'),fs=require('fs'),path=require('path');
const ROOT='/sessions/serene-affectionate-euler/mnt/miami-jetski-main';
process.on('unhandledRejection',()=>{});process.on('uncaughtException',()=>{});
const files=JSON.parse(fs.readFileSync('/tmp/zones.json','utf8'));
const red=new Set(); try{const v=JSON.parse(fs.readFileSync(path.join(ROOT,'vercel.json'),'utf8'));(v.redirects||[]).forEach(r=>red.add(String(r.source||'').replace(/^\//,'')));}catch(e){}
const exists=p=>{try{p=decodeURIComponent(p);}catch(e){} p=p.replace(/^\//,'').replace(/\/$/,'');if(!p)return true;
  return fs.existsSync(path.join(ROOT,p+'.html'))||fs.existsSync(path.join(ROOT,p))||red.has(p);};
(async()=>{
let tot=0, inlined=0; const bad={};
for(const rel of files){
  let dom;
  try{
    let HTML=fs.readFileSync(path.join(ROOT,rel),'utf8');
    HTML=HTML.replace(/<script([^>]*?)\ssrc="(\/[^"]+\.js)"([^>]*)><\/script>/g,(m,a,src)=>{
      const fp=path.join(ROOT,src.replace(/^\//,''));
      if(!fs.existsSync(fp)) return m;
      inlined++;
      return '<script>'+fs.readFileSync(fp,'utf8').replace(/<\/script>/gi,'<\\/script>')+'</script>';});
    dom=new JSDOM(HTML,{runScripts:'dangerously',pretendToBeVisual:true,
      virtualConsole:new VirtualConsole(),url:'https://miamijetskiboatrentals.com/'+rel.replace(/\.html$/,''),
      beforeParse(w){w.dataLayer=[];w.matchMedia=q=>({matches:false,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}});
        class IO{observe(){}unobserve(){}disconnect(){}}w.IntersectionObserver=IO;w.ResizeObserver=IO;w.scrollTo=()=>{};
        const mk=()=>new Proxy(function(){},{get:(t,p)=>p==='then'?undefined:(p===Symbol.toPrimitive||p==='toString')?()=>'s':mk(),apply:()=>mk(),construct:()=>mk()});w.L=mk();
        w.fetch=u=>{let p=String(u).replace(/^https?:\/\/[^/]+/,'').replace(/^\.?\//,'').split('?')[0];const fp=path.join(ROOT,p);
          if(fs.existsSync(fp))return Promise.resolve({ok:true,json:()=>Promise.resolve(JSON.parse(fs.readFileSync(fp,'utf8')))});return Promise.reject(new Error('404'));};}});
    const w=dom.window;
    w.document.dispatchEvent(new w.Event('DOMContentLoaded',{bubbles:true}));
    w.dispatchEvent(new w.Event('load'));
    await new Promise(r=>setTimeout(r,300));
    const as=[...w.document.querySelectorAll('a[href^="/"]')];
    as.forEach(a=>{const h=(a.getAttribute('href')||'').split('#')[0].split('?')[0];
      if(!h||h.startsWith('//')||/\.[a-z0-9]{2,4}$/i.test(h))return;
      tot++; if(!exists(h)) bad[h]=(bad[h]||0)+1;});
  }catch(e){}
  if(dom)try{dom.window.close()}catch(e){}
}
const ks=Object.keys(bad);
console.log('scripts locales insertados:',inlined);
console.log('enlaces internos generados revisados:',tot);
console.log('destinos inexistentes distintos:',ks.length,'| referencias:',ks.reduce((s,k)=>s+bad[k],0));
ks.slice(0,20).forEach(k=>console.log('   ',bad[k],'->',k));
})();
