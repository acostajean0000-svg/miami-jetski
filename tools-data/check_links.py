# Comprueba enlaces internos de todas las páginas emulando Vercel (redirects -> archivos (cleanUrls) -> rewrites).
import json,re,glob,io,os,collections,sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V=json.load(open('vercel.json'))
def pat(src):
    s=re.escape(src)
    s=re.sub(r'\\\(\\\.\\\*\\\)','(.*)',s)          # (.*)
    s=re.sub(r':([a-zA-Z_]\w*)\\\*', r'(?P<\1>.*)', s)   # :path*
    s=re.sub(r':([a-zA-Z_]\w*)', r'(?P<\1>[^/]+)', s)
    return re.compile('^'+s+'$')
RED=[(pat(r['source']),r['destination']) for r in V.get('redirects',[])]
REW=[(pat(r['source']),r['destination']) for r in V.get('rewrites',[])]
FILES=set(f for f in glob.glob('**/*',recursive=True) if os.path.isfile(f))
def fs(path):
    p=path.lstrip('/')
    if p=='' : return 'index.html' in FILES
    return p in FILES or (p+'.html') in FILES or (p.rstrip('/')+'/index.html') in FILES
def resolve(path,depth=0):
    if depth>6: return 'loop'
    for rx,dst in RED:
        m=rx.match(path)
        if m:
            if dst.startswith('http'): return 'ext'
            d=dst
            for k,v in (m.groupdict() or {}).items(): d=d.replace(':'+k+'*',v).replace(':'+k,v)
            return resolve(d.split('?')[0].split('#')[0],depth+1)
    if fs(path): return 'ok'
    for rx,dst in REW:
        m=rx.match(path)
        if m:
            d=dst
            for k,v in (m.groupdict() or {}).items(): d=d.replace(':'+k+'*',v).replace(':'+k,v)
            if d.startswith('http'): return 'ext'
            return 'ok' if fs(d.split('?')[0]) else 'rewrite-roto'
    return 'roto'
HREF=re.compile(r'href="(/[^"#?]*)')
BLOCK=re.compile(r'<script\b[^>]*>.*?</script>',re.S)
res=collections.Counter(); broken=collections.defaultdict(set); total=0; cache={}
pages=[f for f in glob.glob('**/*.html',recursive=True) if not f.startswith('node_modules')]
for f in pages:
    t=BLOCK.sub('',io.open(f,encoding='utf-8',errors='replace').read())
    for h in set(HREF.findall(t)):
        if h.startswith('//'): continue
        h2=h.rstrip('/') or '/'
        if h2 not in cache: cache[h2]=resolve(h2)
        r=cache[h2]; res[r]+=1; total+=1
        if r not in ('ok','ext'): broken[h2].add(f)
print('páginas',len(pages),'| enlaces únicos por página',total,'|',dict(res))
for h,fs_ in sorted(broken.items(),key=lambda x:-len(x[1]))[:25]: print('  ',cache[h],h,'←',len(fs_),'páginas, ej.',sorted(fs_)[0])
