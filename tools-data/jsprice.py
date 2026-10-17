import io,re,glob,sys
def sp(es): return 'Ver precios' if es else 'See prices'
def patch(t,es):
    S=sp(es); n=0
    reps=[
     ("<span class=\"pr\">$'+(o.price||100)+'</span>", "<span class=\"pr\">'+(o.price?'$'+o.price:'%s')+'</span>"%S),
     ("<span class=\"tag\">From $'+(o.price||100)+'</span>", "<span class=\"tag\">'+(o.price?'From $'+o.price:'%s')+'</span>"%S),
     ("<span class=\"tag\">Desde $'+(o.price||100)+'</span>", "<span class=\"tag\">'+(o.price?'Desde $'+o.price:'%s')+'</span>"%S),
     ('<div class="op-price"><div class="op-price-from">From</div><div class="op-price-num">$${op.price.toLocaleString()}</div></div>',
      '<div class="op-price">${op.price?`<div class="op-price-from">%s</div><div class="op-price-num">$${op.price.toLocaleString()}</div>`:`<div class="op-price-num" style="font-size:.85rem">%s</div>`}</div>'%('Desde' if es else 'From',S)),
     ('<div class="deal-price">$${op.price}</div>','<div class="deal-price">${op.price?\'$\'+op.price:\'%s\'}</div>'%S),
     ('<div class="ac-item-price">$${op.price}</div>','<div class="ac-item-price">${op.price?\'$\'+op.price:\'\'}</div>'),
     ('<span class="fav-op-price">From $${op.price}</span>','<span class="fav-op-price">${op.price?\'From $\'+op.price:\'%s\'}</span>'%S),
     ('<span class="fav-op-price">Desde $${op.price}</span>','<span class="fav-op-price">${op.price?\'Desde $\'+op.price:\'%s\'}</span>'%S),
     ('<div class="rv-card-price">From $${o.price}</div>','<div class="rv-card-price">${o.price?\'From $\'+o.price:\'%s\'}</div>'%S),
     ('<div class="rv-card-price">Desde $${o.price}</div>','<div class="rv-card-price">${o.price?\'Desde $\'+o.price:\'%s\'}</div>'%S),
     ("render:(op)=>op.price===minPrice?`<span class=\"cmp-best\">From $${op.price.toLocaleString()} 🏆</span>`:`From $${op.price.toLocaleString()}`}",
      "render:(op)=>!op.price?'%s':op.price===minPrice?`<span class=\"cmp-best\">From $${op.price.toLocaleString()} 🏆</span>`:`From $${op.price.toLocaleString()}`}"%S),
     ("render:(op)=>op.price===minPrice?`<span class=\"cmp-best\">Desde $${op.price.toLocaleString()} 🏆</span>`:`Desde $${op.price.toLocaleString()}`}",
      "render:(op)=>!op.price?'%s':op.price===minPrice?`<span class=\"cmp-best\">Desde $${op.price.toLocaleString()} 🏆</span>`:`Desde $${op.price.toLocaleString()}`}"%S),
     ("const minPrice=Math.min(...compareList.map(o=>o.price));","const minPrice=Math.min(...compareList.map(o=>o.price||Infinity));"),
     ("ops.sort((a,b) => a.price - b.price);","ops.sort((a,b) => (a.price||Infinity) - (b.price||Infinity));"),
     ("'\\nFrom $' + op.price +","(op.price ? '\\nFrom $' + op.price : '') +"),
    ]
    for a,b in reps:
        k=t.count(a)
        if k: t=t.replace(a,b); n+=k
    # $'+(X.price||'50')+'+  -> '+(X.price?'$'+X.price+'+':'See prices')+'
    t,k=re.subn(r"\$'\+\((\w+)\.price\|\|'50'\)\+'\+", lambda m:"'+(%s.price?'$'+%s.price+'+':'%s')+'"%(m.group(1),m.group(1),S), t); n+=k
    return t,n
if __name__=='__main__':
    files=[f for f in glob.glob('**/*.html',recursive=True)]
    tot=0;nf=0
    for f in files:
        t=io.open(f,encoding='utf-8',errors='replace').read()
        if 'price' not in t: continue
        es=f.startswith('es/') or '<html lang="es"' in t[:400]
        t2,n=patch(t,es)
        if n:
            nf+=1; tot+=n
            if sys.argv[1]=='run': io.open(f,'w',encoding='utf-8').write(t2)
    print('archivos',nf,'reemplazos',tot)
