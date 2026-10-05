import sys,io,re,json
sys.path.insert(0,'/tmp/navbuild'); from common import *
LANG=sys.argv[1]; F=sys.argv[2]
ES = LANG=='es'
P  = '/es/' if ES else '/'
L = dict(
 dest   = 'Destinos' if ES else 'Destinations',
 fl     = 'Florida',
 us     = 'Resto de EE. UU.' if ES else 'Rest of the USA',
 mx     = 'México y Caribe' if ES else 'Mexico & Caribbean',
 all37  = 'Ver los 37 destinos →' if ES else 'All 37 destinations →',
 browse = 'Ver actividades →' if ES else 'Browse Activities →',
 secTag = 'Destinos' if ES else 'Destinations',
 secH2  = 'Explora por <span class="teal">destino</span>' if ES else 'Explore by <span class="teal">Destination</span>',
 secP   = '37 destinos con operadores verificados y reserva instantánea por FareHarbor.' if ES else '37 destinations with verified operators and instant FareHarbor booking.',
 more   = 'Más…' if ES else 'More…',
 moreZ  = 'Más destinos…' if ES else 'More destinations…',
 moreC  = 'Más categorías…' if ES else 'More categories…',
)
t=io.open(F,encoding='utf-8').read(); orig=t
log=[]
def step(name,newt):
    global t
    ok,err=js_ok(newt)
    if not ok or not ld_ok(newt): raise SystemExit('FALLA en %s: %s'%(name,err))
    log.append(name); t=newt

# ---------- 1) NAV: desplegable de destinos ----------
NAVPICK={'FL':['miami','keywest','broward','westfl','orlando','naples'],'US':['hawaii','sandiego','charleston','hiltonhead','laketahoe','savannah'],'MX':['cancun','puertorico','cabo','cozumel','tulum','puntacana']}
byz={d['zone']:d for d in TOP}
def col(reg,label): return '<div class="nav-dd-col"><h4>%s</h4>%s</div>'%(label,''.join('<a href="%s%s">%s %s</a>'%(P,byz[z]['slug'],EMO.get(z,'📍'),esc(byz[z]['name'])) for z in NAVPICK[reg] if z in byz))
dd=('<div class="nav-dd" id="navDest"><button type="button" class="nav-dd-btn" aria-haspopup="true" aria-expanded="false" '
    'onclick="var d=this.parentNode;var o=d.classList.toggle(\'open\');this.setAttribute(\'aria-expanded\',o)">%s ▾</button>'
    '<div class="nav-dd-panel" role="menu">%s%s%s<a class="nav-dd-all" href="#destinations">%s</a></div></div>')%(
    L['dest'],col('FL',L['fl']),col('US',L['us']),col('MX',L['mx']),L['all37'])
m=re.search(r'<div class="nav-links">([\s\S]*?)</div>',t)
inner=m.group(1)
keep=[a for a in re.findall(r'<a [^>]*>[\s\S]*?</a>',inner) if re.search(r'href="(?:/es)?/blog/?"|href="#reviews"|class="nav-cta"',a)]
miami='<a href="%smiami-activities">Miami</a>'%P
newnav='<div class="nav-links"> %s %s %s </div>'%(dd,miami,' '.join(keep))
CSS=('<style id="nav-dd-style">.nav-dd{position:relative}.nav-dd-btn{background:none;border:0;color:var(--text-muted);font-family:\'Montserrat\',sans-serif;font-size:.82rem;font-weight:600;letter-spacing:.5px;text-transform:uppercase;cursor:pointer;padding:0}'
     '.nav-dd-btn:hover,.nav-dd.open .nav-dd-btn{color:var(--teal)}'
     '.nav-dd-panel{display:none;position:absolute;top:calc(100% + 16px);left:50%;transform:translateX(-50%);background:#0b1a2e;border:1px solid rgba(0,210,255,.18);border-radius:14px;padding:18px 22px;box-shadow:0 18px 40px rgba(0,0,0,.55);z-index:1100;grid-template-columns:repeat(3,minmax(160px,1fr));gap:4px 28px;min-width:600px}'
     '.nav-dd-panel::before{content:"";position:absolute;top:-18px;left:0;right:0;height:18px}'
     '.nav-dd:hover .nav-dd-panel,.nav-dd:focus-within .nav-dd-panel,.nav-dd.open .nav-dd-panel{display:grid}'
     '.nav-dd-col h4{font-family:\'Montserrat\',sans-serif;font-size:.66rem;letter-spacing:1.2px;text-transform:uppercase;color:#7fa6c4;margin:0 0 8px}'
     '.nav-dd-col a{display:block;padding:5px 0;font-size:.86rem;font-weight:500;text-transform:none;letter-spacing:0;color:#e6f0fa}'
     '.nav-dd-col a:hover{color:var(--teal)}'
     '.nav-dd-all{grid-column:1/-1;border-top:1px solid rgba(255,255,255,.08);margin-top:10px;padding-top:12px;text-transform:none!important;letter-spacing:0!important;color:var(--teal)!important}'
     '.zone-tabs .zone-extra,.cat-tabs .cat-extra{display:none!important}'
     '.more-sel{background:rgba(0,210,255,.08);border:1px solid rgba(0,210,255,.25);color:#cfe6f7;border-radius:50px;padding:7px 12px;font-size:.8rem;font-weight:600;cursor:pointer;flex:0 0 auto}'
     '.more-sel.on{background:var(--teal);color:#040d1a;border-color:var(--teal)}'
     '.dest-group{margin-top:26px;text-align:left}.dest-group h3{font-family:\'Montserrat\',sans-serif;font-size:1.05rem;color:#fff;margin:0 0 12px}'
     '</style>')
step('nav', t.replace(m.group(0),newnav,1).replace('</head>',CSS+'</head>',1))
# cerrar el desplegable al pulsar fuera
step('nav-js', t.replace('</body>','<script>document.addEventListener("click",function(e){var d=document.getElementById("navDest");if(d&&!d.contains(e.target)){d.classList.remove("open");var b=d.querySelector(".nav-dd-btn");if(b)b.setAttribute("aria-expanded","false");}});</script></body>',1))

# menú móvil: sustituir los enlaces sueltos de destinos por grupos
mm=re.search(r'(<div class="mobile-menu" id="mobileMenu">)([\s\S]*?)(</div>)',t)
if mm:
    links=re.findall(r'<a [^>]*>[\s\S]*?</a>',mm.group(2))
    rest=[a for a in links if not re.search(r'-activities"',a)]
    def mcol(reg,label): return '<div style="padding:10px 4px 4px;font-size:.7rem;letter-spacing:1px;text-transform:uppercase;color:#7fa6c4">%s</div>'%label+''.join('<a href="%s%s" onclick="closeMobile()">%s %s</a>'%(P,byz[z]['slug'],EMO.get(z,'📍'),esc(byz[z]['name'])) for z in NAVPICK[reg][:4] if z in byz)
    newmm=mm.group(1)+mcol('FL',L['fl'])+mcol('US',L['us'])+mcol('MX',L['mx'])+'<a href="#destinations" onclick="closeMobile()">🗺️ %s</a>'%L['all37']+''.join(rest)+mm.group(3)
    step('menu-movil', t.replace(mm.group(0),newmm,1))

# ---------- 2) UNA sola sección de destinos ----------
def card(d):
    return ('<a href="%s%s" class="loc-card"><div class="loc-card-top"><span class="loc-card-emoji">%s</span><span class="loc-card-count">%d ops</span></div>'
            '<div class="loc-card-name">%s</div><div class="loc-card-cta">%s</div></a>')%(P,d['slug'],EMO.get(d['zone'],'📍'),d['n'],esc(d['name']),L['browse'])
grp=lambda reg,label: '<div class="dest-group"><h3>%s <span style="color:#7fa6c4;font-weight:500;font-size:.85rem">· %d</span></h3><div class="loc-grid">%s</div></div>'%(label,len(GROUPS[reg]),''.join(card(d) for d in GROUPS[reg]))
newsec=('<section class="loc-section" id="destinations"><div class="container text-center"><div class="section-tag">%s</div><h2 class="section-title">%s</h2>'
        '<p class="section-sub">%s</p>%s%s%s</div></section>')%(L['secTag'],L['secH2'],L['secP'],grp('FL',L['fl']),grp('US',L['us']),grp('MX',L['mx']))
s=t.find('<section class="loc-section"'); e=balanced_end(t,s,'section')
step('seccion-destinos', t[:s]+newsec+t[e:])
# quitar duplicados dentro de hpAuthority: h3 Top Destinations + grid, y la sección "Beyond/Más allá"
a=t.find('<section class="hp-authority"')
if a<0: a=None
if a is not None:
  b=balanced_end(t,a,'section'); ha=t[a:b]
  i=ha.find('<div class="hp-zones-grid"')
  if i>=0:
    j=balanced_end(ha,i,'div'); h3=ha.rfind('<h3>',0,i)
    ha=ha[:h3]+ha[j:]
  step('limpiar-hpAuthority', t[:a]+ha+t[b:])
# quitar las secciones "Beyond/Más allá de Florida" estén donde estén
for title in ['Beyond Florida','Más allá de Florida']:
    while title in t:
        i=t.find(title); s2=t.rfind('<section',0,i); e2=balanced_end(t,s2,'section')
        step('quitar-'+title[:6], t[:s2]+t[e2:])

# ---------- 4) FAQ única ----------
hpq={}
a=t.find('<section class="hp-authority"')
ha=''
if a>=0: b=balanced_end(t,a,'section'); ha=t[a:b]
for m2 in re.finditer(r'<summary class="hp-faq-q">([\s\S]*?)</summary><div class="hp-faq-a">([\s\S]*?)</div>',ha): hpq[re.sub(r'\s+',' ',m2.group(1)).strip()]=m2.group(2).strip()
i=ha.find('<div class="hp-faq-list"')
if i>=0:
    j=balanced_end(ha,i,'div'); h2=ha.rfind('<h2',0,i); ha=ha[:h2]+ha[j:]
    step('quitar-faq-hp', t[:a]+ha+t[b:])
# preguntas del JSON-LD
ldq={}
for sblk in re.findall(r'<script type="application/ld\+json">(.*?)</script>',t,re.S):
    jj=json.loads(sblk)
    if isinstance(jj,dict) and jj.get('@type')=='FAQPage':
        for q in jj['mainEntity']: ldq[q['name'].strip()]=q['acceptedAnswer']['text']
json.dump({'hp':hpq,'ld':ldq},open('/tmp/navbuild/faq_%s.json'%LANG,'w'),ensure_ascii=False,indent=1)
io.open(F,'w',encoding='utf-8').write(t)
print(LANG,'pasos OK:',log)
