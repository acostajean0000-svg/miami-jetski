import sys,io,re,json,html as H
sys.path.insert(0,'/tmp/navbuild'); from common import *
LANG=sys.argv[1]; F=sys.argv[2]; ES=LANG=='es'
t=io.open(F,encoding='utf-8').read()
src=json.load(open('/tmp/navbuild/faq_%s.json'%LANG))
s=t.find('<section class="faq-section"'); e=balanced_end(t,s,'section'); sec=t[s:e]
vis=[(re.sub(r'\s+',' ',q).strip(), a.strip()) for q,a in re.findall(r'<div class="faq-q">([\s\S]*?)<span class="faq-icon">\+</span></div>\s*<div class="faq-a">([\s\S]*?)</div>\s*</div>',sec)]
print('visibles actuales:',len(vis)); [print('   ',q) for q,_ in vis]
def P(x): return '<p>%s</p>'%x if not x.lstrip().startswith('<p') else x
EXTRA = json.load(open('/tmp/navbuild/extra_%s.json'%LANG))   # [[q, a_html], ...] en el orden final, None = usar visible
final=[]
for q,a in EXTRA:
    if a is None:
        hit=[v for v in vis if v[0]==q]
        if not hit: raise SystemExit('no encuentro la visible: '+q)
        final.append((q,hit[0][1]))
    else: final.append((q,P(a)))
items=''.join('<div class="faq-item" onclick="toggleFaq(this)"><div class="faq-q">%s<span class="faq-icon">+</span></div><div class="faq-a">%s</div></div>'%(q,a) for q,a in final)
li=sec.find('<div class="faq-list">'); le=balanced_end(sec,li,'div')
newsec=sec[:li]+'<div class="faq-list">'+items+'</div>'+sec[le:]
t2=t[:s]+newsec+t[e:]
# JSON-LD FAQPage = exactamente lo visible
txt=lambda h: re.sub(r'\s+',' ',H.unescape(re.sub(r'<(?!/?a\b)[^>]+>','',h))).strip()
def rp(m):
    j=json.loads(m.group(2))
    if isinstance(j,dict) and j.get('@type')=='FAQPage':
        j['mainEntity']=[{'@type':'Question','name':H.unescape(re.sub(r'<[^>]+>','',q)).strip(),'acceptedAnswer':{'@type':'Answer','text':txt(a)}} for q,a in final]
        return m.group(1)+json.dumps(j,ensure_ascii=False)+m.group(3)
    return m.group(0)
t2=re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)',rp,t2,flags=re.S)
ok,err=js_ok(t2)
if not ok or not ld_ok(t2): raise SystemExit('FALLA '+err)
io.open(F,'w',encoding='utf-8').write(t2)
print('FAQ final:',len(final),'preguntas; JSON-LD sincronizado')
