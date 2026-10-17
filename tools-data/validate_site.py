# Valida JS inline (node --check, deduplicado) y JSON-LD de las páginas modificadas en los últimos N minutos.
import re,subprocess,io,hashlib,json,sys,os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
mins=sys.argv[1] if len(sys.argv)>1 else '240'
fs=subprocess.run("find . -name '*.html' -mmin -%s -not -path './node_modules/*'"%mins,shell=True,capture_output=True,text=True).stdout.split()
seen={};bad=set();badld=set()
for f in fs:
    t=io.open(f,encoding='utf-8').read()
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>',t,re.S):
        try: json.loads(b)
        except Exception: badld.add(f)
    for s in re.findall(r'<script(?![^>]*(?:src=|application/ld\+json))[^>]*>([\s\S]*?)</script>',t):
        h=hashlib.md5(s.encode()).hexdigest()
        if h not in seen:
            open('/tmp/_s.js','w').write(s); seen[h]=subprocess.run(['node','--check','/tmp/_s.js'],capture_output=True).returncode==0
        if not seen[h]: bad.add(f)
print('%d archivos | %d scripts únicos | JS con error: %s | JSON-LD inválido: %s'%(len(fs),len(seen),sorted(bad)[:4],sorted(badld)[:4]))
