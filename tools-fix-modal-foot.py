#!/usr/bin/env python3
"""Corrige el pie del modal de reserva ("More in {zona}") en las páginas generadas.

tools-gen-localities.py y tools-gen-pagination.py copian el modal de sea-ray-46-miami.html,
cuyo pie dice "More in Miami". Ejecutar este script SIEMPRE después de regenerar:
    python3 tools-gen-localities.py && python3 tools-gen-pagination.py && python3 tools-fix-modal-foot.py
- Paginación /{zona}-activities/N  -> enlaza a /{zona}-activities con el nombre de la zona (h1 de la página 1).
- Localidades generadas            -> enlaza a la zona de su breadcrumb; si no tiene, quita el "More in".
"""
import io, re, glob, os
ROOT = os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT)
PFX = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport"'
FOOT = re.compile(r'(<div class="fh-modal-foot"[^>]*>)(.*?)(<a id="fhOpenNewTab")', re.S)
LNK = '<a href="/%s" style="color:#00d4c8;text-decoration:underline">More in %s</a> · '

def zone_name(zpage):
    try: t = io.open(zpage + '.html', encoding='utf-8', errors='replace').read()
    except OSError: return None
    h = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S)
    if not h: return None
    return re.sub(r'\s+(Activities|Tours).*$', '', re.sub(r'<[^>]+>', '', h.group(1)).strip())

files = glob.glob('*-activities/*.html') + [f for f in glob.glob('*-activities.html')
         if io.open(f, encoding='utf-8', errors='replace').read(120).startswith(PFX)]
changed = 0
for f in files:
    t = io.open(f, encoding='utf-8').read(); m = FOOT.search(t)
    if not m: continue
    if '/' in f:
        zp = f.split('/')[0]; name = zone_name(zp)
        target = (zp, name) if name else None
    else:
        b = re.search(r'<div class="bc">.*?<a href="/([a-z0-9-]+-activities)">([^<]+)</a>', t)
        target = (b.group(1), b.group(2)) if b else None
    mid = "Don't see availability? " + (LNK % target if target else '')
    t2 = t[:m.start(2)] + mid + t[m.end(2):]
    if t2 != t: io.open(f, 'w', encoding='utf-8').write(t2); changed += 1
print('pies de modal corregidos:', changed, 'de', len(files))
