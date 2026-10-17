# Recorta meta descriptions > 165 caracteres (visibles) a ≤160: por frase si es posible, si no por palabra + "…"
import glob,io,re,html,sys,os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D=re.compile(r'(<meta name="description" content=")([^"]*)(")')
def trim(s):
    if len(s)<=165: return s
    cut=s[:160]; k=max(cut.rfind('. '),cut.rfind('! '),cut.rfind('? '))
    if k>=110: return cut[:k+1]
    w=cut[:157].rsplit(' ',1)[0].rstrip(' ,;:—-–·.')
    while w.rsplit(' ',1)[-1].lower() in ('in','and','the','of','with','&amp;','&','a','to','for','on','at','or','y','en','de','con','la','el'):
        w=w.rsplit(' ',1)[0].rstrip(' ,;:—-–·.')
    return w+'…'
n=0;ex=[]
for f in glob.glob('**/*.html',recursive=True):
    t=io.open(f,encoding='utf-8',errors='replace').read(); m=D.search(t)
    if not m: continue
    s=html.unescape(m.group(2)); s2=trim(s)
    if s2!=s:
        n+=1; ex.append((f,s2))
        if sys.argv[1:]==['run']:
            t=t[:m.start(2)]+html.escape(s2,quote=True)+t[m.end(2):]; io.open(f,'w',encoding='utf-8').write(t)
print('recortadas',n)
for f,s in ex[:6]: print(' ',len(s),f[:35],'|',s)
