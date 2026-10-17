# Quita secciones de plantilla inventadas en fichas: Highlights (todas), What's Included repetido (≥3 páginas), "Max Guests" = 8 (valor por defecto)
import glob,io,re,collections,sys,os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IN=re.compile(r'<div class="included-list">(.*?)</div>',re.S)
files=glob.glob('*.html')+glob.glob('es/*.html')
cnt=collections.Counter()
for f in files:
    for m in IN.finditer(io.open(f,encoding='utf-8',errors='replace').read()): cnt[m.group(1)]+=1
HLSEC=re.compile(r'\s*<div class="section">\s*<h2>[^<]*</h2>\s*<ul class="highlights-list">.*?</ul>\s*</div>',re.S)
INSEC=re.compile(r'\s*<div class="section">\s*<h2>[^<]*</h2>\s*<div class="included-list">(.*?)</div>\s*</div>',re.S)
MG=re.compile(r'<div class="fact"><div class="fact-val">8</div><div class="fact-lbl">Max Guests</div></div>')
st=collections.Counter(); left=collections.Counter()
for f in files:
    t=io.open(f,encoding='utf-8',errors='replace').read(); o=t
    t,a=HLSEC.subn('',t); st['highlights']+=a
    t,b=INSEC.subn(lambda m:'' if cnt[m.group(1)]>=3 else m.group(0),t); st['included']+=(o.count('included-list')-t.count('included-list'))
    t,c=MG.subn('',t); st['maxguests']+=c
    if 'highlights-list">' in t: left['highlights']+=1
    if t!=o and sys.argv[1:]==['run']: io.open(f,'w',encoding='utf-8').write(t)
print(dict(st),'restos:',dict(left))
