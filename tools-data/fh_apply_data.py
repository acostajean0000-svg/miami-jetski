# Aplica precios de FareHarbor (tools-data/fh-prices-*.json) a todos los JSON de datos.
# Regla: precio solo si viene de FareHarbor, en USD y >= 8; si no, 0 (= "See prices").
import json,glob,io,re,sys,os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P=json.load(open(sys.argv[1]))
good={k:round(float(v['price']),2) for k,v in P.items() if v.get('price') and v.get('currency')=='USD' and float(v['price'])>=8}
files=['operators.json','operators-slim.json','operators-top.json']+glob.glob('data/*.json')+glob.glob('data/cat/*.json')
tot=up=zero=0
for f in files:
    raw=io.open(f,encoding='utf-8').read(); j=json.loads(raw); ch=[0,0]
    def w(x):
        if isinstance(x,dict):
            if 'price' in x and 'link' in x:
                m=re.search(r'(?:/items/|^[^/:]+/)(\d+)',str(x.get('link') or ''))
                p=good.get(m.group(1)) if m else None
                newp=(int(p) if p and p==int(p) else p) if p else 0
                if x.get('price')!=newp:
                    x['price']=newp; ch[0 if newp else 1]+=1
            for v in x.values(): w(v)
        elif isinstance(x,list):
            for v in x: w(v)
    w(j)
    if ch[0] or ch[1]:
        compact='\n' not in raw.strip()[:2000]
        io.open(f,'w',encoding='utf-8').write(json.dumps(j,ensure_ascii=False,separators=(',',':')) if compact else json.dumps(j,ensure_ascii=False,indent=1))
        up+=ch[0]; zero+=ch[1]
print('archivos',len(files),'| precios puestos',up,'| puestos a 0',zero,'| items con precio FH',len(good))
