# Aplica los precios de FareHarbor al HTML ya generado (fichas y tarjetas).
# Uso: python3 tools-data/fh_apply_html.py [run]   (sin 'run' = simulación)
import io,re,json,glob,sys,os,collections
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = sys.argv[1:]==['run']
d=json.load(open('operators.json')); d=d if isinstance(d,list) else sum([v for v in d.values() if isinstance(v,list)],[])
OP={o['id']:o for o in d}
NEWP={o['id']:(float(o['price']) if o.get('price') else None) for o in d}
sm=json.loads(re.search(r'=\s*(\{.*\})',open('slug-map.js').read(),re.S).group(1))
BYSLUG={s:i for i,s in sm.items()}
BYFH={}
for o in d:
    m=re.search(r'/embeds/book/([^/]+)/items/(\d+)',o['link'])
    if m: BYFH.setdefault(m.group(1)+'/'+m.group(2),o['id'])
def fmt(p): return ('{:,.0f}'.format(p) if p==int(p) else '{:,.2f}'.format(p))
REF=re.compile(r'<a\b[^>]*href="(?:https://miamijetskiboatrentals\.com)?/(?:es/)?([a-z0-9][a-z0-9-]*)"|fareharbor\.com/embeds/book/([^/"\s]+)/items/(\d+)')
BLOCK=re.compile(r'<(script|style)\b[^>]*>.*?</\1>',re.S)
TOK=re.compile(r'See prices|Ver precios|(?:From|Desde) \$[\d,]+(?:\.\d{1,2})?|\$[\d,]+(?:\.\d{1,2})?\+')
def refs(t):
    out=[]
    for m in REF.finditer(t):
        i=BYSLUG.get(m.group(1)) if m.group(1) else BYFH.get(m.group(2)+'/'+m.group(3))
        if i: out.append((m.start(),m.end(),i,bool(m.group(1))))
    return out
def process(f,t):
    es=f.startswith('es/') or '<html lang="es"' in t[:400]
    FROM='Desde' if es else 'From'; S='Ver precios' if es else 'See prices'
    st=collections.Counter()
    own=BYSLUG.get(os.path.basename(f)[:-5])
    if own:
        p=NEWP.get(own)
        # dato de la ficha
        def fact(m):
            st['fact']+=1
            return ('<div class="fact-val">$%s</div><div class="fact-lbl">%s</div>'%(fmt(p),FROM)) if p else '<div class="fact-val">💲</div><div class="fact-lbl">%s</div>'%S
        t=re.sub(r'<div class="fact-val">(?:💲|\$[\d,.]+)</div><div class="fact-lbl">(?:See prices|Ver precios|From|Desde)</div>',fact,t)
        def side(m):
            st['side']+=1
            return '<div class="price">%s</div>'%(('%s $%s'%(FROM,fmt(p))) if p else S)
        t=re.sub(r'<div class="price">(?:See prices|Ver precios|Book online|Reserva online|(?:From|Desde) \$[\d,.]+)</div>',lambda m: side(m) if (p or 'Book online' not in m.group(0) and 'Reserva online' not in m.group(0)) else m.group(0),t)
        def mob(m):
            st['mobile']+=1
            return m.group(1)+(('%s $%s'%(FROM,fmt(p))) if p else S)+'</div>'
        t=re.sub(r'(<div class="mobile-book-bar">\s*<div>\s*<div style="[^"]*">)(?:See prices|Ver precios|(?:From|Desde) \$[\d,.]+|\$[\d,.]+)</div>',mob,t)
        # JSON-LD: Offer con precio real
        def ld(m):
            try: j=json.loads(m.group(2))
            except Exception: return m.group(0)
            ch=[0]
            def w(x):
                if isinstance(x,dict):
                    tp=x.get('@type'); tps=tp if isinstance(tp,list) else [tp]
                    if 'Product' in tps and x.get('aggregateRating') is not None or ('Product' in tps and x.get('url','').rstrip('/').endswith('/'+os.path.basename(f)[:-5])):
                        if p:
                            x['offers']={'@type':'Offer','priceCurrency':'USD','price':('%d'%p if p==int(p) else '%.2f'%p),'availability':'https://schema.org/InStock','url':OP[own]['link']}
                            ch[0]+=1
                        elif 'offers' in x: del x['offers']; ch[0]+=1
                    for v in list(x.values()): w(v)
                elif isinstance(x,list):
                    for v in x: w(v)
            w(j)
            if not ch[0]: return m.group(0)
            st['ld']+=1
            compact=', ' not in m.group(2)[:200]
            return m.group(1)+(json.dumps(j,ensure_ascii=False,separators=(',',':')) if compact else json.dumps(j,ensure_ascii=False))+'</script>'
        t=re.sub(r'(<script type="application/ld\+json">)(.*?)</script>',ld,t,flags=re.S)
    # tarjetas: atribución estricta
    R=refs(t); spans=[(m.start(),m.end()) for m in BLOCK.finditer(t)]
    def inblock(p): return any(a<=p<b for a,b in spans)
    def node_len(p):
        a=t.rfind('>',0,p); b=t.find('<',p)
        if a<0 or b<0 or t.rfind('<',0,p)>a: return 9999
        return b-a
    import bisect
    starts=[r[0] for r in R]
    res=[];last=0
    for m in TOK.finditer(t):
        p0=m.start()
        if inblock(p0) or node_len(p0)>60: continue
        k=bisect.bisect_left(starts,p0)
        b=R[k-1] if k>0 else None; fw=R[k] if k<len(R) else None
        op=None
        if b and p0-b[0]<900:
            if fw and fw[2]==b[2] and fw[0]-p0<700: op=b[2]
            elif b[3] and '</a>' not in t[b[1]:p0]: op=b[2]
        if not op or op==own and m.group(0) in (S,): pass
        if not op: continue
        p=NEWP.get(op); tok=m.group(0)
        if tok in ('See prices','Ver precios'):
            if not p: continue
            new='%s $%s'%(FROM,fmt(p))
        else:
            num=float(re.sub(r'[^\d.]','',tok))
            if p and abs(num-p)<0.01: continue
            new=('%s $%s'%(FROM,fmt(p)) if not tok.endswith('+') else '$%s+'%fmt(p)) if p else S
        res.append(t[last:m.start()]); res.append(new); last=m.end(); st['tok']+=1
    res.append(t[last:]); t=''.join(res)
    return t,st
if __name__=='__main__':
    files=[f for f in glob.glob('**/*.html',recursive=True) if not f.startswith(('blog/','es/blog/'))]
    tot=collections.Counter(); nf=0
    for f in files:
        t=io.open(f,encoding='utf-8',errors='replace').read()
        t2,st=process(f,t)
        if t2!=t:
            nf+=1; tot+=st
            if RUN: io.open(f,'w',encoding='utf-8').write(t2)
    print('archivos',nf,dict(tot))
