import json,glob,io,re,os,shutil,sys
ROOT='.'
def retire(ids, motivo):
    ids=set(ids)
    sm=io.open('slug-map.js',encoding='utf-8').read(); mp=json.loads(sm[sm.find('{"'):sm.rfind('}')+1])
    slugs={i:mp[i] for i in ids if i in mp}
    os.makedirs('/tmp/retired',exist_ok=True)
    rep={'datos':0,'slugmaps':0,'html':0,'links':0,'sitemap':0,'redirects':0}
    # 1) datos
    for f in ['operators.json','operators-slim.json','operators-top.json']+glob.glob('data/*.json')+glob.glob('data/cat/*.json'):
        try: d=json.load(open(f))
        except: continue
        ch=False
        if isinstance(d,list):
            n=len(d); d=[o for o in d if not (isinstance(o,dict) and o.get('id') in ids)]; ch=len(d)!=n; rep['datos']+=n-len(d)
        elif isinstance(d,dict):
            for k,v in d.items():
                if isinstance(v,list):
                    n=len(v); d[k]=[o for o in v if not (isinstance(o,dict) and o.get('id') in ids)]
                    if len(d[k])!=n: ch=True; rep['datos']+=n-len(d[k])
        if ch: json.dump(d,open(f,'w'),ensure_ascii=False,separators=(',',':'))
    # 2) slug maps
    for f in glob.glob('slug-map/*.js')+['slug-map.js']:
        s=io.open(f,encoding='utf-8').read(); i=s.find('{"'); j=s.rfind('}')
        d=json.loads(s[i:j+1]); n=len(d)
        for k in list(d):
            if k in ids: del d[k]
        if len(d)!=n:
            rep['slugmaps']+=n-len(d)
            io.open(f,'w',encoding='utf-8').write(s[:i]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[j+1:])
    # 3) zona destino + borrar html
    zona={}
    for i,s in slugs.items():
        p=s+'.html'
        if os.path.exists(p):
            t=io.open(p,encoding='utf-8',errors='replace').read()
            mb=re.search(r'BreadcrumbList[\s\S]{0,1200}',t)
            bc=re.findall(r'"item":\s*"https://miamijetskiboatrentals\.com/([a-z0-9-]+-activities)"',mb.group(0)) if mb else []
            m=re.search(r'href="/([a-z0-9-]+-activities)"',t)
            zona[s]=bc[0] if bc else (m.group(1) if m else 'miami-activities')
            shutil.move(p,'/tmp/retired/'+p); rep['html']+=1
    # 4) redirects 301
    v=json.load(open('vercel.json')); have={r['source'] for r in v['redirects']}
    for s,z in zona.items():
        if '/'+s not in have: v['redirects'].append({'source':'/'+s,'destination':'/'+z,'permanent':True}); rep['redirects']+=1
    json.dump(v,open('vercel.json','w'),indent=2,ensure_ascii=False)
    # 5) enlaces entrantes
    S=set(slugs.values())
    pat_card=re.compile(r'<a\b[^>]*href="/(%s)"[^>]*class="rel-card"[^>]*>.*?</a>'%'|'.join(map(re.escape,S)),re.S)
    pat_li=re.compile(r'<li>\s*<a\b[^>]*href="/(%s)"[^>]*>.*?</li>'%'|'.join(map(re.escape,S)),re.S)
    pat_inl=re.compile(r'(?:\s*·\s*)?<a\b[^>]*href="/(%s)"[^>]*>[^<]*</a>'%'|'.join(map(re.escape,S)))
    for f in glob.glob('*.html')+glob.glob('es/*.html')+glob.glob('blog/*.html'):
        t=io.open(f,encoding='utf-8',errors='replace').read()
        if not any('/'+s+'"' in t for s in S): continue
        o=t
        t=pat_card.sub('',t); t=pat_li.sub('',t); t=pat_inl.sub('',t)
        t=re.sub(r'<strong style="color:#9bb5d4">Related operators:</strong>\s*·\s*','<strong style="color:#9bb5d4">Related operators:</strong> ',t)
        if t!=o: io.open(f,'w',encoding='utf-8').write(t); rep['links']+=1
    # 6) sitemaps
    for f in glob.glob('sitemaps/*.xml'):
        t=io.open(f,encoding='utf-8').read(); o=t
        for s in S: t=re.sub(r'\s*<url>\s*<loc>https://miamijetskiboatrentals\.com/'+re.escape(s)+r'</loc>.*?</url>','',t,flags=re.S)
        if t!=o: io.open(f,'w',encoding='utf-8').write(t); rep['sitemap']+=1
    json.dump({'motivo':motivo,'ids':sorted(ids),'slugs':slugs,'zona':zona},open('/tmp/retired/_log_%s.json'%motivo,'w'),indent=1)
    return rep
if __name__=='__main__':
    ids=json.load(open(sys.argv[1])); print(retire(ids,sys.argv[2]))
