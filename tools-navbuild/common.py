import io,re,json,subprocess,html as H
DESTS=json.load(open('/tmp/dests.json'))
CLEAN={'Savannah GA':'Savannah','Galveston TX':'Galveston','Newport Beach CA':'Newport Beach','Newport RI':'Newport, RI','South Padre Island TX':'South Padre','Outer Banks NC':'Outer Banks','Cape May NJ':'Cape May','Park City UT':'Park City','Hilton Head Island':'Hilton Head','🏞️ Central Florida':'Central Florida','Daytona Beach':'NE Florida & Daytona'}
EMO={'miami':'🏖️','keywest':'🐠','westfl':'🌴','nefl':'🌊','broward':'⛵','naples':'🐚','space':'🚀','orlando':'🎢','palmbeach':'🌴','centralfl':'🏞️','everglades':'🐊',
 'sandiego':'🏄','hawaii':'🌺','hiltonhead':'🏌️','charleston':'🏛️','laketahoe':'🏔️','savannah':'🌳','austin':'🛶','seattle':'🌲','capecod':'🦞','galveston':'⚓','catalina':'🏝️','newportbeach':'🌅','newportri':'⛵','barharbor':'🦞','myrtle':'🏖️','southpadre':'🐢','outerbanks':'🏝️','capemay':'🏖️','parkcity':'⛰️',
 'puertorico':'🇵🇷','cancun':'🇲🇽','cabo':'🌵','cozumel':'🐠','tulum':'🏛️','puntacana':'🇩🇴','playadelcarmen':'🌊'}
for d in DESTS: d['name']=CLEAN.get(d['name'],d['name'])
TOP=[d for d in DESTS if d['n']>=40]           # = 37
GROUPS={'FL':[d for d in TOP if d['reg']=='FL'],'US':[d for d in TOP if d['reg']=='US'],'MX':[d for d in TOP if d['reg']=='MX']}
def esc(s): return H.escape(str(s),quote=True)
def js_ok(t):
    js=''.join(re.findall(r'<script(?![^>]*src=)(?![^>]*ld\+json)[^>]*>(.*?)</script>',t,re.S))
    io.open('/tmp/navbuild/c.js','w',encoding='utf-8').write(js)
    r=subprocess.run(['node','--check','/tmp/navbuild/c.js'],capture_output=True)
    return r.returncode==0, r.stderr.decode()[:120]
def ld_ok(t):
    for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',t,re.S):
        try: json.loads(s)
        except Exception as e: return False
    return True
def balanced_end(t,start,tag):
    """posición tras el cierre equilibrado del elemento <tag ...> que empieza en start"""
    d=0
    for m in re.finditer(r'<(/?)%s\b[^>]*>'%tag,t[start:]):
        d+= -1 if m.group(1) else 1
        if d==0: return start+m.end()
    return None
