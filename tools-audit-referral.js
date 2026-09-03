const {JSDOM,VirtualConsole}=require('jsdom'),fs=require('fs'),path=require('path');
const ROOT='/sessions/serene-affectionate-euler/mnt/miami-jetski-main';
process.on('unhandledRejection',()=>{});process.on('uncaughtException',()=>{});
(async()=>{
let tot=0,bad=[],pages=0;
for(const rel of ['index.html','es/index.html','miami-jet-ski-rentals.html','west-florida-fishing-charters.html','austin-water-sports-rentals.html','miami-activities.html','es/cancun-activities.html','san-diego-boat-rentals.html']){
  let HTML=fs.readFileSync(path.join(ROOT,rel),'utf8').replace(/<script([^>]*?)\ssrc="(\/[^"]+\.js)"([^>]*)><\/script>/g,(m,a,src)=>{const fp=path.join(ROOT,src.slice(1));return fs.existsSync(fp)?'<script>'+fs.readFileSync(fp,'utf8').replace(/<\/script>/gi,'<\\/script>')+'</script>':m;});
  const dom=new JSDOM(HTML,{runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:new VirtualConsole(),url:'https://miamijetskiboatrentals.com/'+rel.replace(/\.html$/,''),
   beforeParse(w){w.dataLayer=[];w.matchMedia=q=>({matches:false,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}});class IO{observe(){}unobserve(){}disconnect(){}}w.IntersectionObserver=IO;w.ResizeObserver=IO;w.scrollTo=()=>{};
    const mk=()=>new Proxy(function(){},{get:(t,p)=>p==='then'?undefined:(p===Symbol.toPrimitive||p==='toString')?()=>'s':mk(),apply:()=>mk(),construct:()=>mk()});w.L=mk();
    w.fetch=u=>{let p=String(u).replace(/^https?:\/\/[^/]+/,'').replace(/^\.?\//,'').split('?')[0];const fp=path.join(ROOT,p);if(fs.existsSync(fp))return Promise.resolve({ok:true,json:()=>Promise.resolve(JSON.parse(fs.readFileSync(fp,'utf8')))});return Promise.reject(new Error('404'));};}});
  const w=dom.window; w.document.dispatchEvent(new w.Event('DOMContentLoaded',{bubbles:true})); w.dispatchEvent(new w.Event('load'));
  await new Promise(r=>setTimeout(r,500)); pages++;
  for(const a of w.document.querySelectorAll('a[href*="fareharbor.com/embeds/book/"]')){
    tot++; const u=new w.URL(a.href); const ks=[...u.searchParams.keys()];
    const e=[]; if(ks.length!==new Set(ks).size)e.push('DUP'); if(u.searchParams.get('branding')!=='no')e.push('sin branding');
    if(u.searchParams.get('ref')!=='miamistylerentals'||u.searchParams.get('asn-ref')!=='miamistylerentals')e.push('ref');
    if(e.length)bad.push([rel,e.join(','),a.href.slice(0,90)]);
  }
  try{w.close()}catch(e){}
}
console.log('páginas:',pages,'| enlaces generados en runtime:',tot,'| no conformes:',bad.length);
bad.slice(0,6).forEach(b=>console.log('  ',b.join(' | ')));
})();
