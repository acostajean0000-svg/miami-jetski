# Sustituye promesas de "free cancellation" (no verificadas por operador) por textos neutros. Sin comillas ni barras en los reemplazos.
import glob,io,re,collections,sys,os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R=[
 (r'<strong>Free Cancellation</strong><span>On most bookings \d+h\+(?: ahead)?</span>', '<strong>Clear Policies</strong><span>Cancellation terms shown before you pay</span>'),
 (r'<strong>Cancelación gratuita</strong><span>En la mayoría de reservas[^<]*</span>', '<strong>Políticas claras</strong><span>Condiciones de cancelación antes de pagar</span>'),
 (r'🔄 Free cancellation · Instant confirmation', '🔄 Cancellation policy shown at checkout · Instant confirmation'),
 (r'🔄 Cancelación gratuita · Confirmación (?:instantánea|inmediata)', '🔄 Política de cancelación visible antes de pagar · Confirmación inmediata'),
 (r'<div class="fact-lbl">Free cancellation\*</div>', '<div class="fact-lbl">Cancellation terms at checkout</div>'),
 (r'<div class="fact-lbl">Cancelación gratuita\*?</div>', '<div class="fact-lbl">Cancelación: ver al reservar</div>'),
 (r' with real-time availability and free cancellation\.', ' with real-time availability.'),
 (r'\. Free cancellation on most bookings\.', '.'),
 (r'Reserve in minutes with free cancellation on most bookings and instant confirmation', 'Reserve in minutes with instant confirmation; cancellation terms are shown before you pay'),
 (r', free cancellation on most bookings\.', '; cancellation terms are shown before you pay.'),
 (r'with instant confirmation and free cancellation on most options\.', 'with instant confirmation; cancellation terms vary by operator.'),
 (r'✓ Free cancellation', '✓ Clear cancellation terms'),
 (r'Most operators offer free cancellation\.', 'Cancellation terms vary by operator.'),

 (r'<strong>Free Cancellation</strong><span>Most bookings \d+h\+</span>', '<strong>Clear Policies</strong><span>Cancellation terms shown before you pay</span>'),
 (r'Most operators offer free cancellation[^.;<"]*', 'Cancellation terms vary by operator'),
 (r'most operators offer free cancellation[^.;<"]*', 'cancellation terms vary by operator'),
 (r'La mayoría de los operadores (?:ofrecen|permiten) cancelación (?:gratis|gratuita)[^.;<"]*', 'Las condiciones de cancelación varían según el operador'),
 (r'la mayoría de los operadores (?:ofrecen|permiten) cancelación (?:gratis|gratuita)[^.;<"]*', 'las condiciones de cancelación varían según el operador'),
 (r' with free cancellation(?=[.<"])', ''),
 (r' con cancelación (?:gratuita|gratis)(?=[.<"])', ''),
 (r'✓ Cancelación gratis', '✓ Condiciones claras de cancelación'),
 (r' · Free cancellation · ', ' · '),
 (r' · Cancelación (?:gratis|gratuita) · ', ' · '),
 (r'🔄 Cancelación gratis', '🔄 Cancelación: ver condiciones al reservar'),
 (r', free cancellation(?= via|[.<"])', ''),
 (r' &amp; free cancellation', ''),
 (r' with cancelación gratis on most tours', ' with cancellation terms shown before you pay'),
 (r'\. Free cancellation on most [a-z]*(?=")', '.'),
 (r', cancelación (?:gratis|gratuita)(?=[.<"])', ''),
 (r' y cancelación (?:gratis|gratuita)(?=[.<"])', ''),
 (r' and free cancellation(?=[.<"])', ''),
 (r'(?<=\.) Free cancellation[a-z ]*(?=")', ''),
 (r'bc-cancel">✅ Free cancellation 24 hrs before', 'bc-cancel">📋 Cancellation terms shown at checkout'),
 (r'bc-cancel">🔄 Free cancellation · No hidden fees', 'bc-cancel">📋 Cancellation terms shown at checkout'),
 (r'Most bookings allow free cancellation up to \d+ hours in advance\.', 'Cancellation terms vary by operator and are shown before you pay.'),
 (r' con cancelación gratis en la mayoría\.', '.'),
 (r'<li>Free cancellation on most experiences</li>', '<li>Cancellation terms shown before you pay</li>'),
 (r'<strong>Free cancellation</strong> applies to most listings', '<strong>Cancellation terms</strong> vary by listing; most are'),
]
R=[(re.compile(a),b) for a,b in R]
GEN=[ # respaldo genérico, después de los específicos
 (re.compile(r'[Ff]ree cancellation on most (?:bookings|tours|options|rentals|trips)'), lambda m:('C' if m.group(0)[0]=='F' else 'c')+'ancellation terms shown before you pay'),
 (re.compile(r'🔄 Free cancellation'), lambda m:'🔄 Cancellation terms at checkout'),
 (re.compile(r'🔄 Cancelación gratuita'), lambda m:'🔄 Cancelación: ver condiciones al reservar'),
]
P=re.compile(r'(?i)free cancell?ation|cancelaci[oó]n gratu?i?t?a?|cancela gratis')
st=collections.Counter(); left=collections.Counter(); ex={}
for f in glob.glob('**/*.html',recursive=True):
    t=io.open(f,encoding='utf-8',errors='replace').read()
    if not P.search(t): continue
    o=t
    for i,(a,b) in enumerate(R): t,k=a.subn(b,t); st['r%d'%i]+=k
    for i,(a,b) in enumerate(GEN): t,k=a.subn(b,t); st['g%d'%i]+=k
    for m in P.finditer(t):
        k=re.sub(r'\d+','N',t[max(0,m.start()-45):m.end()+45]).replace('\n',' '); left[k]+=1; ex[k]=f
    if t!=o and sys.argv[1:]==['run']: io.open(f,'w',encoding='utf-8').write(t)
print(dict(st)); print('restos',sum(left.values()),'contextos',len(left))
for k,v in left.most_common(25): print(v,repr(k),ex[k])
