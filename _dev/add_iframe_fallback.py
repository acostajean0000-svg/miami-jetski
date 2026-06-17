#!/usr/bin/env python3
"""
add_iframe_fallback.py — agrega detección de iframe vacío + fallback amigable
en el modal de booking de TODOS los operator pages.

Cuando un operador tiene catálogo FH vacío (zombie operator), en vez de
mostrar iframe blanco, mostramos mensaje con link a categorías relacionadas.
"""
from __future__ import annotations
import re, glob, sys

OLD_MODAL_LOGIC = '''iframe.onload=function(){if(iframe.src!=='about:blank')hideLoading();};
    setTimeout(hideLoading,4000); // fallback in case onload doesn't fire
    requestAnimationFrame(function(){iframe.src=url;});'''

NEW_MODAL_LOGIC = '''iframe.onload=function(){
      if(iframe.src==='about:blank'||iframe.src==='')return;
      hideLoading();
      // Detectar iframe vacío (operador zombie sin items): check después de render
      setTimeout(function(){
        try{
          var b=iframe.contentDocument&&iframe.contentDocument.body;
          var h=b?b.innerText.length:0;
          // Si el iframe tiene <500 chars de texto = catálogo vacío
          if(b&&h<500&&!/item|book|select|date/i.test(b.innerText)){showUnavailable();}
        }catch(e){/* cross-origin, no podemos chequear — no problem */}
      },3500);
    };
    setTimeout(hideLoading,4000);
    requestAnimationFrame(function(){iframe.src=url;});'''

UNAVAILABLE_HTML = '''  <div id="fhUnavailable" style="display:none;padding:40px 28px;text-align:center;color:#cdd9e8">
    <div style="font-size:3rem;margin-bottom:12px">😔</div>
    <h3 style="color:#fff;font-size:1.2rem;margin-bottom:10px">This operator is currently unavailable</h3>
    <p style="font-size:.95rem;line-height:1.6;margin-bottom:24px;color:#9bb5d4">
      The booking page is empty. The operator may be paused, closed, or out-of-season.
    </p>
    <a href="/" style="display:inline-block;background:linear-gradient(135deg,#00d4c8,#00eedd);color:#040d1a;padding:12px 28px;border-radius:50px;font-weight:700;text-decoration:none">
      Browse similar operators →
    </a>
  </div>'''

UNAVAILABLE_FN = '''  function showUnavailable(){
    var i=document.getElementById('fhModalIframe');var u=document.getElementById('fhUnavailable');
    if(i)i.style.display='none'; if(u)u.style.display='block';
  }'''

updated = 0
already_done = 0
not_applicable = 0

for fp in sorted(glob.glob('*.html')):
    try:
        html = open(fp).read()
    except: continue

    if 'fhModalIframe' not in html:
        not_applicable += 1
        continue

    if 'fhUnavailable' in html:
        already_done += 1
        continue

    new_html = html

    # 1. Reemplazar la lógica del iframe.onload
    if OLD_MODAL_LOGIC in new_html:
        new_html = new_html.replace(OLD_MODAL_LOGIC, NEW_MODAL_LOGIC)
    else:
        not_applicable += 1
        continue

    # 2. Insertar el div fallback dentro del modal-body, antes del </div> de fh-modal-body
    new_html = new_html.replace(
        '<iframe id="fhModalIframe" title="FareHarbor Booking" loading="eager" allow="payment"></iframe>',
        '<iframe id="fhModalIframe" title="FareHarbor Booking" loading="eager" allow="payment"></iframe>\n' + UNAVAILABLE_HTML
    )

    # 3. Agregar función showUnavailable antes de closeFhModal
    new_html = new_html.replace(
        '  window.closeFhModal=function(){',
        UNAVAILABLE_FN + '\n  window.closeFhModal=function(){var u=document.getElementById(\'fhUnavailable\');if(u)u.style.display=\'none\';var i=document.getElementById(\'fhModalIframe\');if(i)i.style.display=\'\';'
    )
    # Quitar el doble bloque inicial
    new_html = new_html.replace(
        'if(u)u.style.display=\'none\';var i=document.getElementById(\'fhModalIframe\');if(i)i.style.display=\'\';\n    var m=document.getElementById(\'fhModal\');',
        'if(u)u.style.display=\'none\';var i=document.getElementById(\'fhModalIframe\');if(i)i.style.display=\'\';\n    var m=document.getElementById(\'fhModal\');'
    )

    if new_html != html:
        with open(fp, 'w') as f:
            f.write(new_html)
        updated += 1

print(f'Actualizados:    {updated}')
print(f'Ya tenían fix:   {already_done}')
print(f'No aplicable:    {not_applicable}')
