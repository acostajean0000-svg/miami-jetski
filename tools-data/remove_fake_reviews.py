# Quita reseñas de plantilla: bloque "What Recent Customers Say" de las fichas y "What Our Customers Say" de la home (EN/ES).
import glob,io,re,sys,os,collections
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN=sys.argv[1:]==['run']
def cut_div(t,start):
    depth=0
    for m in re.finditer(r'<div\b|</div>',t[start:]):
        depth+=1 if m.group(0)=='<div' else -1
        if depth==0: return start+m.end()
    return None
st=collections.Counter()
for f in glob.glob('**/*.html',recursive=True):
    t=io.open(f,encoding='utf-8',errors='replace').read(); o=t
    while True:
        i=t.find('<div class="section sp9-reviews">')
        if i<0: break
        j=cut_div(t,i)
        if not j: break
        s=i
        while s>0 and t[s-1] in ' \t': s-=1
        t=t[:s]+t[j:]; st['ficha']+=1
    if f in ('index.html','es/index.html'):
        t,k=re.subn(r'\s*<section class="testimonials" id="reviews">.*?</section>','',t,count=1,flags=re.S); st['home']+=k
        t,k=re.subn(r'\s*<a href="#reviews"[^>]*>[^<]*</a>','',t); st['nav']+=k
    if t!=o and RUN: io.open(f,'w',encoding='utf-8').write(t)
print(dict(st))
