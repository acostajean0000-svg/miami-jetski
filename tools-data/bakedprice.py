import io,re,json,glob,sys,os,collections
os.chdir('/sessions/serene-affectionate-euler/mnt/miami-jetski-main')
d=json.load(open('/tmp/bkd/operators.json')); d=d if isinstance(d,list) else sum([v for v in d.values() if isinstance(v,list)],[])
UNK=set(json.load(open('/tmp/price_defaults.json'))['unknown_ids'])
sm=json.loads(re.search(r'=\s*(\{.*\})',open('slug-map.js').read(),re.S).group(1))
OP={o['id']:o for o in d}
def fp(o):
    try: return float(o.get('price'))
    except: return None
BYSLUG={s:i for i,s in sm.items()}
BYFH={}
for o in d:
    m=re.search(r'/embeds/book/([^/]+)/items/(\d+)',o['link'])
    if m: BYFH.setdefault(m.group(1)+'/'+m.group(2),o['id'])
REF=re.compile(r'href="(?:https://miamijetskiboatrentals\.com)?/(?:es/)?([a-z0-9][a-z0-9-]*)"|fareharbor\.com/embeds/book/([^/"\s]+)/items/(\d+)')
TOK=re.compile(r'(?P<pre>\b(?:From|from|Desde|desde)\s+)?\$(?P<n>\d{1,5}(?:\.\d{1,2})?)(?P<plus>\+)?(?![\d,.]\d)')
BLOCK=re.compile(r'<(script|style)\b[^>]*>.*?</\1>',re.S)
def refs(t):
    out=[]
    for m in REF.finditer(t):
        if m.group(1): i=BYSLUG.get(m.group(1))
        else: i=BYFH.get(m.group(2)+'/'+m.group(3))
        if i: out.append((m.start(),i))
    return out
def pick(R,p,n):
    best=None
    for pos,i in R:
        dd=p-pos if pos<=p else (pos-p)*1.3
        if dd>900: continue
        if fp(OP[i])!=n: continue
        if best is None or dd<best[0]: best=(dd,i)
    return best[1] if best else None
DEFV=set()
for _c,_v in json.load(open('/tmp/price_defaults.json'))['defaults'].items(): DEFV.update(_v)
DEFV.add('50')
def process(f,t):
    es=f.startswith('es/') or '<html lang="es"' in t[:400]
    S='Ver precios' if es else 'See prices'
    st=collections.Counter()
    own=BYSLUG.get(os.path.basename(f)[:-5])
    ownU= own in UNK
    # 1) JSON-LD
    def ld(m):
        try: j=json.loads(m.group(2))
        except: return m.group(0)
        ch=[0]
        def w(x):
            if isinstance(x,dict):
                of=x.get('offers')
                if isinstance(of,dict):
                    tp=of.get('@type')
                    if tp=='AggregateOffer': del x['offers']; ch[0]+=1; st['ld_aggoffer']+=1
                    elif tp=='Offer':
                        u=of.get('url','') ; mm=re.search(r'/embeds/book/([^/]+)/items/(\d+)',u)
                        i=BYFH.get(mm.group(1)+'/'+mm.group(2)) if mm else own
                        if i in UNK: del x['offers']; ch[0]+=1; st['ld_offer']+=1
                for v in list(x.values()): w(v)
            elif isinstance(x,list):
                for v in x: w(v)
        w(j)
        if not ch[0]: return m.group(0)
        compact=', ' not in m.group(2)[:200]
        return m.group(1)+(json.dumps(j,ensure_ascii=False,separators=(',',':')) if compact else json.dumps(j,ensure_ascii=False))+'</script>'
    t=re.sub(r'(<script type="application/ld\+json">)(.*?)</script>',ld,t,flags=re.S)
    # 2) ficha propia: facts, sidebar, meta
    if ownU:
        n=fp(OP[own]); ns=('%d'%n) if n==int(n) else str(n)
        t,k=re.subn(r'<div class="fact-val">\$%s</div><div class="fact-lbl">(?:From|Desde)</div>'%re.escape(ns),'<div class="fact-val">💲</div><div class="fact-lbl">%s</div>'%S,t); st['fact']+=k
        t,k=re.subn(r'(<div class="price-sub">)(?:Per person|Por persona)( · )',r'\1%s\2'%('Precio en el calendario' if es else 'Live price in calendar'),t); st['pricesub']+=k
        def meta(m):
            c=m.group(2); c2=re.sub(r' (?:from|desde) \$%s\b'%re.escape(ns),'',c)
            if c2!=c: st['meta']+=1
            return m.group(1)+c2+m.group(3)
        t=re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")([^"]*)(")',meta,t)
    # 3) tokens en nodos de texto cortos (fuera de script/style)
    R=refs(t)
    out=[];last=0
    spans=[(m.start(),m.end()) for m in BLOCK.finditer(t)]
    def inblock(p):
        for a,b in spans:
            if a<=p<b: return True
        return False
    def node_len(p):
        a=t.rfind('>',0,p); b=t.find('<',p)
        if a<0 or b<0: return 9999
        if t.rfind('<',0,p)>a: return 9999   # dentro de una etiqueta (atributo)
        return b-a
    res=[];last=0
    for m in TOK.finditer(t):
        p=m.start()
        if m.group('pre') and m.group('pre')[0].islower(): continue
        if inblock(p) or node_len(p)>48: continue
        n=float(m.group('n')); i=pick(R,p,n)
        if not i or i not in UNK: continue
        res.append(t[last:m.start()]); res.append(S); last=m.end(); st['tok']+=1
    res.append(t[last:]); t=''.join(res)
    # 4) páginas de listado (no fichas, no blog): quitar 'from $N' / 'desde $N' cuando N es un valor por defecto
    if not own and not f.startswith(('blog/','es/blog/')):
        def lp(m):
            nx=t2ctx[m.end():m.end()+6]
            if re.match(r'\s*(?:to|a|-|–)\s*\$',nx) or m.group(2) not in DEFV: return m.group(0)
            st['landing']+=1; return ''
        t2ctx=t
        t=re.sub(r' (from|desde) \$(\d+)(?![\d,]|\.\d)(?=[\s.—·"<|),;:]|$)',lp,t)
    return t,st
if __name__=='__main__':
    files=sys.argv[2:] or [f for f in glob.glob('**/*.html',recursive=True)]
    tot=collections.Counter(); nf=0
    for f in files:
        t=io.open(f,encoding='utf-8',errors='replace').read()
        if '$' not in t: continue
        t2,st=process(f,t)
        if t2!=t:
            nf+=1; tot+=st
            if sys.argv[1]=='run': io.open(f,'w',encoding='utf-8').write(t2)
    print('archivos',nf,dict(tot))
