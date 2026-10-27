# Socios destacados: sus productos van primero en los datos y llevan la etiqueta "⭐ Featured".
import json,glob,io,re,math,os,sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARTNERS=('bruschiboatrental','altamartrade')
BADGE='⭐ Featured'
def sn(o):
    m=re.search(r'(?:/embeds/book/)?([a-z0-9-]+)/(?:items/)?\d+',str(o.get('link') or ''))
    return m.group(1) if m else ''
def score(o): return float(o.get('rating') or 0)*math.log10(float(o.get('reviews') or 0)+1)
files=['operators.json','operators-slim.json','operators-top.json']+glob.glob('data/*.json')+glob.glob('data/cat/*.json')
tot=0
for f in files:
    raw=io.open(f,encoding='utf-8').read(); j=json.loads(raw); ch=[False]
    def fix_list(L):
        if not (isinstance(L,list) and L and isinstance(L[0],dict) and 'link' in L[0]): return L
        pin=[o for o in L if sn(o) in PARTNERS]; rest=[o for o in L if sn(o) not in PARTNERS]
        for o in pin:
            if o.get('badge')!=BADGE: o['badge']=BADGE; ch[0]=True
        pin.sort(key=score,reverse=True)
        new=pin+rest
        if [id(x) for x in new]!=[id(x) for x in L]: ch[0]=True
        return new
    if isinstance(j,list): j=fix_list(j)
    elif isinstance(j,dict):
        for k,v in list(j.items()): j[k]=fix_list(v)
    if ch[0]:
        compact='\n' not in raw.strip()[:2000]
        io.open(f,'w',encoding='utf-8').write(json.dumps(j,ensure_ascii=False,separators=(',',':')) if compact else json.dumps(j,ensure_ascii=False,indent=1)); tot+=1
print('archivos reordenados',tot)
