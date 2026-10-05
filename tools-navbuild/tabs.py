import sys,io,re,html as H
sys.path.insert(0,'/tmp/navbuild'); from common import *
LANG=sys.argv[1]; F=sys.argv[2]; ES=LANG=='es'
t=io.open(F,encoding='utf-8').read()
KZ={'all','miami','broward','keys','westfl','orlando','hawaii','cancun'}
KC={'all','jetski','boat','yacht','sunset','fishing','watersports','snorkel'}
def compact(t,cont,btncls,fn,keep,sel_id,label):
    m=re.search(r'<div class="%s">'%cont,t); s=m.start(); e=balanced_end(t,s,'div'); blk=t[s:e]
    opts=[]
    def rp(mm):
        tag=mm.group(0); code=re.search(r"%s\('([a-z0-9_]+)'"%fn,tag)
        if not code or code.group(1) in keep: return tag
        full=t[s:e]; 
        return tag.replace('class="%s'%btncls,'class="%s %s-extra'%(btncls,btncls.split('-')[0]),1)
    blk2=re.sub(r'<button class="%s[^"]*"[^>]*>'%btncls,rp,blk)
    for bm in re.finditer(r'<button class="%s[^"]*%s-extra[^"]*"[^>]*%s\(\'([a-z0-9_]+)\'[^>]*>([\s\S]*?)</button>'%(btncls,btncls.split('-')[0],fn),blk2):
        lab=re.sub(r'<span class="cat-count">[^<]*</span>','',bm.group(2)); lab=re.sub(r'<[^>]+>',' ',lab); lab=re.sub(r'\s+',' ',H.unescape(lab)).strip()
        opts.append((bm.group(1),lab))
    sel=('<select class="more-sel" id="%s" aria-label="%s" onchange="if(!this.value)return;var b=document.querySelector(\'.%s[onclick*=&quot;\\\'\'+this.value+\'\\\'&quot;]\');if(b)b.click();this.classList.add(\'on\')">'
         '<option value="">%s</option>%s</select>')%(sel_id,H.escape(label),btncls,H.escape(label),''.join('<option value="%s">%s</option>'%(c,H.escape(l)) for c,l in opts))
    i=blk2.rfind('</div>')
    blk2=blk2[:i]+sel+blk2[i:]
    return t[:s]+blk2+t[e:], len(opts)
t2,nz=compact(t,'zone-tabs','zone-tab','filterZone',KZ,'zoneMore','Más destinos…' if ES else 'More destinations…')
ok,err=js_ok(t2); assert ok and ld_ok(t2),('zonas',err)
t3,nc=compact(t2,'cat-tabs','cat-tab','filterCat',KC,'catMore','Más categorías…' if ES else 'More categories…')
ok,err=js_ok(t3); assert ok and ld_ok(t3),('cats',err)
SYNC=('<script>(function(){function sync(cont,sel,extra){var c=document.querySelector(cont),s=document.getElementById(sel);if(!c||!s)return;'
 'var a=c.querySelector(".active");if(a&&a.classList.contains(extra)){var m=(a.getAttribute("onclick")||"").match(/\'([a-z0-9_]+)\'/);if(m){s.value=m[1];s.classList.add("on");}}'
 'else{s.value="";s.classList.remove("on");}}'
 'function all(){sync(".zone-tabs","zoneMore","zone-extra");sync(".cat-tabs","catMore","cat-extra");}'
 'document.addEventListener("click",function(e){if(e.target.closest&&e.target.closest(".zone-tab,.cat-tab"))setTimeout(all,0);});'
 'window.addEventListener("load",function(){setTimeout(all,1500);});})();</script>')
t3=t3.replace('</body>',SYNC+'</body>',1)
ok,err=js_ok(t3); assert ok and ld_ok(t3),('sync',err)
io.open(F,'w',encoding='utf-8').write(t3)
print(LANG,'| zonas a "Más":',nz,'| categorías a "Más":',nc)
