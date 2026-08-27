
(function(){
  // ───── Inject search bar + toolbar after .filters ─────
  function injectUX(){
    var filters=document.querySelector('.filters');
    if(!filters||document.querySelector('.ux-searchbar'))return;
    var search=document.createElement('div');
    search.className='ux-searchbar';
    search.innerHTML='<span class="ux-search-icon">🔎</span><input type="search" id="uxSearch" placeholder="Busca por nombre, tipo, ubicación..." autocomplete="off"><button type="button" class="ux-clear" id="uxClear" aria-label="Borrar">×</button>';
    var tools=document.createElement('div');
    tools.className='ux-toolbar';
    tools.innerHTML='<div class="ux-result-count" id="uxCount">Cargando…</div><div class="ux-sort"><label for="uxSort">Ordenar:</label><select id="uxSort"><option value="rec">Recomendados</option><option value="rating">⭐ Mejor valorados</option><option value="reviews">💬 Más reseñas</option><option value="price-asc">💰 Precio: menor a mayor</option><option value="price-desc">💰 Precio: mayor a menor</option><option value="name">A–Z</option></select></div>';
    // Insert in correct order: filters → search → toolbar → ...
    filters.insertAdjacentElement('afterend',search);
    search.insertAdjacentElement('afterend',tools);
    setupListeners();
  }

  // ───── Fuzzy match (lightweight) ─────
  function fuzzyMatch(op, q){
    if(!q)return true;
    q=q.toLowerCase().trim();
    var hay=(op.name+' '+(op.zl||'')+' '+(op.cat||'')).toLowerCase();
    // simple multi-token AND match with substring (typo-tolerant via prefix)
    return q.split(/\s+/).every(function(tok){
      if(tok.length<2)return true;
      if(hay.indexOf(tok)>=0)return true;
      // 1-char tolerance for tokens 4+
      if(tok.length>=4){
        for(var i=0;i<tok.length;i++){
          var partial=tok.slice(0,i)+tok.slice(i+1);
          if(hay.indexOf(partial)>=0)return true;
        }
      }
      return false;
    });
  }

  // ───── Hook into render with sort + search ─────
  var origGrid=null;
  var debounceT=null;
  function setupListeners(){
    var inp=document.getElementById('uxSearch');
    var clr=document.getElementById('uxClear');
    var sort=document.getElementById('uxSort');
    inp&&inp.addEventListener('input',function(){
      clearTimeout(debounceT);
      debounceT=setTimeout(applyUX,180);
    });
    clr&&clr.addEventListener('click',function(){inp.value='';applyUX()});
    sort&&sort.addEventListener('change',applyUX);
  }

  function applyUX(){
    if(!window.allOps&&!window._uxAllOps)return;
    var ops=window._uxAllOps||window.allOps||[];
    var q=(document.getElementById('uxSearch')||{}).value||'';
    var sort=(document.getElementById('uxSort')||{}).value||'rec';
    var activeCat=window.activeCat||'all';
    var filtered=ops.filter(function(o){
      if(activeCat!=='all'&&o.cat!==activeCat)return false;
      return fuzzyMatch(o,q);
    });
    if(sort==='rating')filtered.sort(function(a,b){return (b.rating||0)-(a.rating||0)});
    else if(sort==='reviews')filtered.sort(function(a,b){return (b.reviews||0)-(a.reviews||0)});
    else if(sort==='price-asc')filtered.sort(function(a,b){return (a.price||9999)-(b.price||9999)});
    else if(sort==='price-desc')filtered.sort(function(a,b){return (b.price||0)-(a.price||0)});
    else if(sort==='name')filtered.sort(function(a,b){return (a.name||'').localeCompare(b.name||'')});
    renderGrid(filtered, q);
    var cnt=document.getElementById('uxCount');
    if(cnt){
      cnt.innerHTML='<strong>'+filtered.length+'</strong> operator'+(filtered.length===1?'':'s')+(q?' matching "'+escapeHtml(q)+'"':'');
    }
    if(window.gtag&&q&&q.length>2){gtag('event','search',{search_term:q,results:filtered.length})}
  }
  function escapeHtml(s){return String(s).replace(/[&<>"']/g,function(c){return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]})}

  function renderGrid(list, query){
    var grid=document.getElementById('grid');
    if(!grid)return;
    if(!list.length){
      grid.innerHTML='<div class="ux-empty"><h3>🔍 Sin resultados</h3><p>Prueba otra búsqueda o categoría.</p>'+(query?'<button class="ux-empty-clear" onclick="document.getElementById(\'uxSearch\').value=\'\';document.getElementById(\'uxSearch\').dispatchEvent(new Event(\'input\'))">Limpiar búsqueda</button>':'')+'</div>';
      return;
    }
    var slugMap=window._OP_SLUG_MAP||{};
    var CAT_EMOJI=window.CAT_EMOJI||{};
    var CAT_LABELS=window.CAT_LABELS||{};
    var FALLBACK=window.FALLBACK_IMG||'';
    grid.innerHTML=list.slice(0,200).map(function(op,i){
      var slug=slugMap[op.id]||'';
      var href=slug?'/'+encodeURIComponent(slug):(op.link||'#');
      var priceText=(op.price&&op.price>0)?('desde $'+op.price):'Consultar precio';
      var photo=op.photo||FALLBACK;
      if(photo&&photo.includes('cdn.filestackcontent.com')){
        photo=photo.replace(/resize=width:\d+/,'resize=width:480');
      }
      var eager=i<4?'fetchpriority="high" loading="eager"':'loading="lazy" decoding="async"';
      return '<a class="card" href="'+href+'" data-op-id="'+op.id+'"><div class="img"><img src="'+photo+'" alt="'+escapeHtml(op.name)+'" '+eager+' width="480" height="320" onerror="this.src=FALLBACK_IMG"><span class="badge">'+(CAT_EMOJI[op.cat]||'🌊')+' '+(CAT_LABELS[op.cat]||op.cat)+'</span></div><div class="body"><div class="name">'+escapeHtml(op.name)+'</div><div class="zl">📍 '+escapeHtml(op.zl||'')+'</div><div class="price">'+priceText+'</div><div class="view-details">Ver detalles →</div></div></a>';
    }).join('');
    // Reveal animation via IntersectionObserver
    if('IntersectionObserver' in window){
      var io=new IntersectionObserver(function(es){
        es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('ux-revealed');io.unobserve(e.target)}});
      },{threshold:.1});
      grid.querySelectorAll('.card').forEach(function(c){io.observe(c)});
    } else {
      grid.querySelectorAll('.card').forEach(function(c){c.classList.add('ux-revealed')});
    }
  }

  // Hook cat-chip clicks to reapply UX
  document.addEventListener('click',function(e){
    var chip=e.target.closest('.cat-chip');
    if(chip){setTimeout(applyUX,30)}
  });

  // Wait for ops to load, then mirror to _uxAllOps
  var checkInt=setInterval(function(){
    if(window.allOps&&window.allOps.length){
      window._uxAllOps=window.allOps;
      clearInterval(checkInt);
      injectUX();
      setTimeout(applyUX,100);
    }
  },200);
  setTimeout(function(){clearInterval(checkInt)},20000);
  // First attempt
  document.addEventListener('DOMContentLoaded',injectUX);
  if(document.readyState!=='loading')injectUX();
})();


/* ─── SPRINT 12 MAP ENHANCEMENT ─── */
(function(){
  var radiusKm=null,radiusCircle=null,radiusCenter=null,satelliteLayer=null,streetLayer=null;
  var lastMapBounds=null,searchAreaPending=false;
  
  function $(s){return document.querySelector(s)}
  
  // Wait for map to initialize
  function waitForMap(cb,attempts){
    attempts=attempts||0;
    if(window.mapInstance){cb();return}
    if(attempts>60)return;
    setTimeout(function(){waitForMap(cb,attempts+1)},500);
  }
  
  // Inject controls overlay
  function injectControls(){
    var wrap=$('.map-wrap');
    if(!wrap||$('.map-controls-overlay'))return;
    
    // Top right: layer toggle + fullscreen
    var ov=document.createElement('div');
    ov.className='map-controls-overlay';
    ov.innerHTML=
      '<button class="map-control-btn" id="mapRadiusToggle">🎯 Radio</button>'+
      '<button class="map-control-btn" id="mapLayerToggle" data-mode="street">🛰️ Satélite</button>'+
      '<button class="map-control-btn" id="mapFullscreenToggle">⛶ Pantalla</button>';
    wrap.appendChild(ov);
    
    // Radius panel
    var rp=document.createElement('div');
    rp.className='map-radius-panel';
    rp.id='mapRadiusPanel';
    rp.innerHTML='<button data-r="0.047348">250 ft</button><button data-r="0.094697">500 ft</button><button data-r="0.189394">1,000 ft</button><button data-r="0.284091">1,500 ft</button><button data-r="0.473485">2,500 ft</button><button data-r="0.757576">4,000 ft</button><button data-r="0">Quitar</button>';
    wrap.appendChild(rp);
    
    // Search area button
    var sa=document.createElement('button');
    sa.className='map-search-area';
    sa.id='mapSearchArea';
    sa.innerHTML='🔍 Buscar en esta zona';
    wrap.appendChild(sa);
    
    // Visible count
    var vc=document.createElement('div');
    vc.className='map-visible-count';
    vc.id='mapVisibleCount';
    vc.innerHTML='<strong>0</strong> operadores a la vista';
    wrap.appendChild(vc);
    
    bindControls();
  }
  
  function bindControls(){
    // Radius toggle
    $('#mapRadiusToggle').onclick=function(){
      var p=$('#mapRadiusPanel');
      p.classList.toggle('show');
    };
    // Radius buttons
    $('#mapRadiusPanel').querySelectorAll('button').forEach(function(b){
      b.onclick=function(){
        var r=parseFloat(b.dataset.r);
        $('#mapRadiusPanel').querySelectorAll('button').forEach(function(x){x.classList.remove('active')});
        if(r){b.classList.add('active');applyRadius(r);}
        else clearRadius();
        if(window.gtag)gtag('event','map_radius_set',{radius_mi:r});
      };
    });
    
    // Layer toggle
    $('#mapLayerToggle').onclick=function(){
      toggleSatellite();
    };
    
    // Fullscreen
    $('#mapFullscreenToggle').onclick=function(){
      var wrap=$('.map-wrap');
      wrap.classList.toggle('fullscreen');
      this.innerHTML=wrap.classList.contains('fullscreen')?'✕ Salir':'⛶ Pantalla';
      setTimeout(function(){if(window.mapInstance)mapInstance.invalidateSize()},300);
      if(window.gtag)gtag('event','map_fullscreen_toggle');
    };
    
    // Search this area
    $('#mapSearchArea').onclick=function(){
      filterByMapBounds();
      this.classList.remove('show');
      if(window.gtag)gtag('event','map_search_area');
    };
    
    // ESC to exit fullscreen
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape'&&$('.map-wrap').classList.contains('fullscreen')){
        $('.map-wrap').classList.remove('fullscreen');
        $('#mapFullscreenToggle').innerHTML='⛶ Pantalla';
        setTimeout(function(){if(window.mapInstance)mapInstance.invalidateSize()},100);
      }
    });
    
    // Listen to map events
    waitForMap(function(){
      mapInstance.on('moveend',function(){
        updateVisibleCount();
        if(lastMapBounds){
          var newBounds=mapInstance.getBounds();
          if(!lastMapBounds.equals(newBounds)){
            $('#mapSearchArea').classList.add('show');
          }
        }
        lastMapBounds=mapInstance.getBounds();
      });
      mapInstance.on('click',function(e){
        if(radiusKm){
          radiusCenter=e.latlng;
          drawCircle();
          filterByRadius();
        }
      });
      lastMapBounds=mapInstance.getBounds();
      // Robust polling: retry until both allOps and map are ready
      var pollCount=0;
      var pollVC=setInterval(function(){
        pollCount++;
        if(window.allOps&&window.allOps.length&&window.mapInstance){
          updateVisibleCount();
          if(pollCount>3){clearInterval(pollVC)}
        }
        if(pollCount>40){clearInterval(pollVC)}
      },800);
    });
  }
  
  function toggleSatellite(){
    if(!window.mapInstance)return;
    var btn=$('#mapLayerToggle');
    if(satelliteLayer&&btn.dataset.mode==='satellite'){
      mapInstance.removeLayer(satelliteLayer);
      btn.dataset.mode='street';
      btn.innerHTML='🛰️ Satélite';
      btn.classList.remove('active');
    } else {
      if(!satelliteLayer){
        satelliteLayer=L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{
          maxZoom:18,attribution:'© Esri'
        });
      }
      satelliteLayer.addTo(mapInstance);
      satelliteLayer.bringToFront();
      btn.dataset.mode='satellite';
      btn.innerHTML='🗺️ Mapa';
      btn.classList.add('active');
    }
    if(window.gtag)gtag('event','map_layer_change',{layer:btn.dataset.mode});
  }
  
  function applyRadius(km){
    radiusKm=km;
    if(!radiusCenter)radiusCenter=mapInstance.getCenter();
    drawCircle();
    filterByRadius();
    $('#mapRadiusPanel').classList.remove('show');
  }
  function clearRadius(){
    radiusKm=null;
    if(radiusCircle){mapInstance.removeLayer(radiusCircle);radiusCircle=null}
    if(window.refreshMarkers)window.refreshMarkers();
  }
  function drawCircle(){
    if(radiusCircle)mapInstance.removeLayer(radiusCircle);
    radiusCircle=L.circle(radiusCenter,{radius:radiusKm*1609,className:'map-radius-circle'}).addTo(mapInstance);
    mapInstance.fitBounds(radiusCircle.getBounds(),{padding:[20,20]});
  }
  function filterByRadius(){
    if(!radiusCenter||!radiusKm||!window.allOps)return;
    var c=radiusCenter;
    var filtered=window.allOps.filter(function(o){
      if(!o.lat||!o.lng)return false;
      var d=haversine(c.lat,c.lng,o.lat,o.lng);
      return d<=radiusKm*1.60934;
    });
    // Update marker cluster (reusa marcadores ya construidos; fallback a makeMarker)
    var __cl=window.markerCluster||window.mapClusterGroup;
    if(__cl){
      __cl.clearLayers();
      var __by=window._markersById||{};
      filtered.forEach(function(o){
        var __m=__by[o.id]||(window.makeMarker?window.makeMarker(o):null);
        if(__m)__cl.addLayer(__m);
      });
    }
    updateVisibleCount(filtered.length);
  }
  function filterByMapBounds(){
    if(!window.mapInstance||!window.allOps)return;
    var b=mapInstance.getBounds();
    var filtered=window.allOps.filter(function(o){
      return o.lat&&o.lng&&b.contains([o.lat,o.lng]);
    });
    // Also update the cards grid below
    var grid=document.getElementById('grid');
    if(grid&&window.renderCards){
      window.renderCards(filtered);
    }
    updateVisibleCount(filtered.length);
  }
  function haversine(lat1,lon1,lat2,lon2){
    var R=6371;
    var dLat=(lat2-lat1)*Math.PI/180;
    var dLon=(lon2-lon1)*Math.PI/180;
    var a=Math.sin(dLat/2)*Math.sin(dLat/2)+Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)*Math.sin(dLon/2);
    return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
  }
  function updateVisibleCount(explicit){
    var el=$('#mapVisibleCount');
    if(!el)return;
    var count=explicit;
    if(count===undefined&&window.mapInstance&&window.allOps){
      var b=mapInstance.getBounds();
      count=window.allOps.filter(function(o){return o.lat&&o.lng&&b.contains([o.lat,o.lng])}).length;
    }
    if(count===undefined)count=0;
    el.innerHTML='<strong>'+count+'</strong> operator'+(count===1?'':'s')+' a la vista';
  }
  
  // Enable scroll wheel zoom on Ctrl+wheel or touch pinch
  waitForMap(function(){
    mapInstance.on('focus',function(){mapInstance.scrollWheelZoom.enable()});
    mapInstance.on('blur',function(){mapInstance.scrollWheelZoom.disable()});
    // Allow ctrl+wheel zoom
    document.getElementById('map').addEventListener('wheel',function(e){
      if(e.ctrlKey||e.metaKey){
        if(!mapInstance.scrollWheelZoom.enabled())mapInstance.scrollWheelZoom.enable();
      }
    });
  });
  
  // Init when DOM ready
  if(document.readyState!=='loading')injectControls();
  else document.addEventListener('DOMContentLoaded',injectControls);
})();
/* /SPRINT 12 MAP ENHANCEMENT */


/* ─── SPRINT 13 MAP PRO ─── */
(function(){
  // Detect which map var to use (jetskiMap for homepage, mapInstance for zones)
  function getMap(){return window.jetskiMap||window.mapInstance||null}
  function getOps(){return window.allOperators||window.allOps||window._uxAllOps||[]}
  function getSlug(op){var sm=window._OP_SLUG_MAP||{};return sm[op.id]||((op.name||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,80)+'-'+(op.zone||''))}
  function getMapContainer(){return document.querySelector('.map-panel')||document.querySelector('.map-wrap')||document.querySelector('#mapWrap')}
  
  // ─── Geolocation ─── (silent, no prompt)
  var userLoc=null;
  function tryGetLocation(){
    try{
      var cached=localStorage.getItem('mp_geo');
      if(cached){var c=JSON.parse(cached);if(Date.now()-c.t<86400000){userLoc=c.loc;return}}
      // Auto-prompt de ubicación eliminado: la ubicación solo se pide al pulsar "Cerca de mí" / "Near Me".
    }catch(e){}
  }
  tryGetLocation();
  
  function haversineMi(lat1,lon1,lat2,lon2){
    var R=3958.8;
    var dLat=(lat2-lat1)*Math.PI/180;
    var dLon=(lon2-lon1)*Math.PI/180;
    var a=Math.sin(dLat/2)*Math.sin(dLat/2)+Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)*Math.sin(dLon/2);
    return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
  }
  
  // ─── Favorites (localStorage) ─── 
  function getFavs(){try{return JSON.parse(localStorage.getItem('mp_favs')||'[]')}catch(e){return[]}}
  function setFavs(arr){localStorage.setItem('mp_favs',JSON.stringify(arr));updateFavBtn();}
  function toggleFav(opId){
    var f=getFavs();
    var i=f.indexOf(opId);
    if(i>-1)f.splice(i,1);else f.push(opId);
    setFavs(f);
    if(window.gtag)gtag('event','map_favorite_toggle',{op_id:opId,action:i>-1?'remove':'add'});
    return i===-1;
  }
  function isFav(opId){return getFavs().indexOf(opId)>-1}
  function updateFavBtn(){
    var btn=document.getElementById('mpFavBtn');
    if(!btn)return;
    var cnt=getFavs().length;
    var cntEl=btn.querySelector('.mp-fav-count');
    if(cnt>0){if(cntEl){cntEl.textContent=cnt}else{btn.innerHTML='❤️ Favoritos <span class="mp-fav-count">'+cnt+'</span>'}}
    else{btn.innerHTML='❤️ Favoritos'}
  }
  
  // ─── Compare list (session, max 3) ─── 
  var compareList=[];
  function addToCompare(opId){
    if(compareList.indexOf(opId)>-1)return;
    if(compareList.length>=3){alert('Máximo 3 operadores para comparar');return}
    compareList.push(opId);
    updateCompareBar();
    if(window.gtag)gtag('event','map_compare_add',{op_id:opId,total:compareList.length});
  }
  function clearCompare(){compareList=[];updateCompareBar()}
  function updateCompareBar(){
    var bar=document.getElementById('mpCompareBar');
    if(!bar){
      bar=document.createElement('div');
      bar.className='mp-compare-bar';
      bar.id='mpCompareBar';
      bar.innerHTML='<span class="mp-cmp-count" id="mpCmpCount">0</span><span style="color:#e8f4fd;font-size:.82rem">selected to compare</span><button id="mpCmpShow">Comparar →</button><button class="mp-cmp-clear" id="mpCmpClear">Limpiar</button>';
      document.body.appendChild(bar);
      document.getElementById('mpCmpShow').onclick=showCompareModal;
      document.getElementById('mpCmpClear').onclick=clearCompare;
    }
    var cnt=compareList.length;
    document.getElementById('mpCmpCount').textContent=cnt;
    if(cnt>=1)bar.classList.add('show');
    else bar.classList.remove('show');
  }
  function showCompareModal(){
    var ops=getOps().filter(function(o){return compareList.indexOf(o.id)>-1});
    var modal=document.getElementById('mpCmpModal');
    if(!modal){
      modal=document.createElement('div');
      modal.className='mp-modal-overlay';
      modal.id='mpCmpModal';
      modal.innerHTML='<div class="mp-modal"><button class="mp-modal-close" onclick="document.getElementById(\'mpCmpModal\').classList.remove(\'show\')" aria-label="Cerrar">×</button><h3>Comparar operadores</h3><div class="mp-cmp-grid" id="mpCmpGrid"></div></div>';
      document.body.appendChild(modal);
    }
    var grid=document.getElementById('mpCmpGrid');
    grid.innerHTML=ops.map(function(o){
      var photo=o.photo&&o.photo.includes('http')?o.photo:(o.photo?'https://cdn.filestackcontent.com/'+o.photo+'/convert?w=400&format=webp':'');
      var distanceHtml=userLoc&&o.lat?'<div class="mp-cmp-attr">📏 Distance <strong>'+haversineMi(userLoc.lat,userLoc.lng,o.lat,o.lng).toFixed(1)+' mi</strong></div>':'';
      return '<div class="mp-cmp-card"><img src="'+photo+'" alt="'+(o.name||'').replace(/"/g,'&quot;')+'" onerror="this.style.display=\'none\'"><div class="mp-cmp-body"><h4>'+(o.name||'').slice(0,60)+'</h4><div class="mp-cmp-attr">⭐ Rating <strong>'+(o.rating||'4.7')+'/5</strong></div><div class="mp-cmp-attr">💬 Reviews <strong>'+(o.reviews||'100')+'+</strong></div><div class="mp-cmp-attr">💰 Price <strong>$'+(o.price||'50')+'+</strong></div><div class="mp-cmp-attr">📍 Location <strong>'+(o.zl||o.zone||'').slice(0,20)+'</strong></div>'+distanceHtml+'<a href="/'+getSlug(o)+'" class="mp-cmp-book">Ver Detalles →</a></div></div>';
    }).join('');
    modal.classList.add('show');
    if(window.gtag)gtag('event','map_compare_view',{count:ops.length});
  }
  
  // ─── Geocoder (Nominatim) ─── 
  var searchTimer=null;
  var CAT_KEYWORDS={
    jetski:['jet ski','jetski','motos','moto de agua','wave runner','sea doo'],
    boat:['boat','lancha','yacht','catamaran','pontoon','speedboat'],
    fishing:['fishing','pesca','charter','offshore'],
    snorkel:['snorkel','snuba','dive','reef'],
    watersports:['deportes acuáticos','watersport','wakeboard','flyboard','parasail','jet pack','tube','banana boat','paddleboard','sup','kayak'],
    tour:['tour','sightseeing','excursion','sightsee','city tour'],
    yacht:['yacht','luxury'],
    atv:['atv','quad','buggy','utv','dune'],
    aerial:['aerial','helicopter','plane','seaplane','airplane','flight','parachute'],
    walking_tour:['walking','walk tour','ghost tour','food tour'],
    bikerental:['bike','bicycle','e-bike','cycling'],
    exotic:['exotic','lamborghini','ferrari','porsche','luxury car','supercar'],
    segway:['segway','scooter'],
    airboat:['airboat','everglades'],
    sunset:['sunset','sunset cruise','dinner cruise','sunset sail'],
    culinary:['food','wine','culinary','cooking','tasting'],
    villa:['villa','rental','accommodation'],
    wildlife:['wildlife','dolphin','whale','manatee','animal'],
    slingshot:['slingshot','sling shot','polaris'],
    golfcart:['golf cart','golf','cart'],
    jetcar:['jet car','jetcar'],
    nightlife:['nightlife','club','party','bar']
  };
  function matchOpsKeyword(q){
    var ops=getOps();
    var ql=q.toLowerCase().trim();
    if(!ql)return [];
    // Filter to current map viewport bounds — solo ops visibles
    var m=getMap();
    var bounds=null;
    if(m){try{bounds=m.getBounds()}catch(e){}}
    var matches=[];
    var seen={};
    ops.forEach(function(o){
      // Skip ops fuera del viewport del mapa
      if(bounds&&o.lat&&o.lng){
        if(!bounds.contains([o.lat,o.lng]))return;
      }
      if(seen[o.id])return;
      var score=0;
      var n=(o.name||'').toLowerCase();
      var z=(o.zl||'').toLowerCase();
      var c=(o.cat||'').toLowerCase();
      // Direct keyword match
      if(n.indexOf(ql)>-1)score+=10;
      if(z.indexOf(ql)>-1)score+=5;
      if(c.indexOf(ql)>-1)score+=8;
      // Category keyword match (cross-reference dictionary)
      Object.keys(CAT_KEYWORDS).forEach(function(catKey){
        var kws=CAT_KEYWORDS[catKey];
        for(var i=0;i<kws.length;i++){
          if(ql.indexOf(kws[i])>-1){
            if(o.cat===catKey)score+=15;
          }
        }
      });
      if(score>0){
        seen[o.id]=1;
        matches.push({op:o,score:score});
      }
    });
    matches.sort(function(a,b){
      // Sort: keyword score, then rating
      if(b.score!==a.score)return b.score-a.score;
      return (b.op.rating||0)-(a.op.rating||0);
    });
    return matches.slice(0,8).map(function(x){return x.op});
  }
  
  function renderSearchResults(opResults,placeResults){
    var box=document.getElementById('mpSearchResults');
    if(!box)return;
    var html='';
    if(opResults.length){
      html+='<div style="padding:6px 14px;color:#7ba3c0;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;background:rgba(0,210,255,.04)">🛥️ Operators</div>';
      opResults.forEach(function(o){
        var slug=getSlug(o);
        var emoji='🌊';
        var cat=(o.cat||'').toLowerCase();
        if(cat==='jetski')emoji='🛥️';else if(cat==='boat')emoji='⛵';else if(cat==='fishing')emoji='🎣';else if(cat==='snorkel')emoji='🤿';else if(cat==='atv')emoji='🏍️';else if(cat==='tour')emoji='🚌';else if(cat==='exotic')emoji='💎';else if(cat==='slingshot')emoji='🏎️';else if(cat==='aerial')emoji='✈️';else if(cat==='sunset')emoji='🌅';else if(cat==='watersports')emoji='🏄';
        html+='<a href="/'+slug+'" class="mp-result" style="display:block;text-decoration:none">'+emoji+' '+(o.name||'').slice(0,60)+'<span style="color:#7ba3c0;font-size:.72rem;margin-left:6px">⭐ '+(o.rating||'4.7')+' · $'+(o.price||'50')+'+</span></a>';
      });
    }
    if(placeResults.length){
      html+='<div style="padding:6px 14px;color:#7ba3c0;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;background:rgba(0,210,255,.04)">📍 Locations</div>';
      placeResults.forEach(function(r){
        html+='<div class="mp-result" data-lat="'+r.lat+'" data-lon="'+r.lon+'">📍 '+r.display_name.slice(0,80)+'</div>';
      });
    }
    if(!html){html='<div class="mp-result">Sin resultados</div>'}
    box.innerHTML=html;
    box.classList.add('show');
    // Bind clicks on location results
    box.querySelectorAll('.mp-result[data-lat]').forEach(function(el){
      el.onclick=function(){
        var lat=parseFloat(el.dataset.lat),lng=parseFloat(el.dataset.lon);
        var m=getMap();
        if(m){m.setView([lat,lng],14);if(window.gtag)gtag('event','map_search_result',{type:'place'})}
        box.classList.remove('show');
        document.getElementById('mpSearchInput').value='';
      };
    });
    box.querySelectorAll('a.mp-result').forEach(function(el){
      el.addEventListener('click',function(){if(window.gtag)gtag('event','map_search_result',{type:'operator'})});
    });
  }
  
  function isPureActivityQuery(q){
    var ql=q.toLowerCase().trim();
    // Pure activity words que no son ubicaciones
    var activities=['jet ski','jetski','slingshot','snorkel','snuba','atv','exotic','aerial','tour','boat','yacht','fishing','watersport','water sport','sunset','dolphin','whale','wildlife','airboat','segway','helicopter','culinary','food tour','bike','kayak','paddleboard','sup','parasail','ghost'];
    for(var i=0;i<activities.length;i++){if(ql===activities[i])return true}
    // If contains common location words, not pure activity
    var locWords=['beach','marina','bay','port','dock','harbor','park','island','street','avenue','road','plaza','hotel','airport','near','from'];
    for(var i=0;i<locWords.length;i++){if(ql.indexOf(locWords[i])>-1)return false}
    // Pure short activity-only queries
    return ql.split(' ').length<=2&&ql.length<10;
  }
  
  function searchPlaces(q){
    if(!q||q.length<2)return;
    var opResults=matchOpsKeyword(q);
    // Show op results immediately
    renderSearchResults(opResults,[]);
    // Skip location search for pure activity queries
    if(isPureActivityQuery(q)&&opResults.length>=3){
      return;
    }
    (function(){
      var m=getMap();var vb='';
      if(m){var b=m.getBounds();vb='&viewbox='+b.getWest()+','+b.getSouth()+','+b.getEast()+','+b.getNorth()+'&bounded=1'}
      // Restringir a países turísticos relevantes: US, MX, Dominican Rep, Puerto Rico, Bahamas, Canada
      var cc='&countrycodes=us,mx,do,pr,bs,ca';
      return fetch('https://nominatim.openstreetmap.org/search?q='+encodeURIComponent(q)+'&format=json&limit=4&addressdetails=1'+vb+cc);
    })()
      .then(function(r){return r.json()})
      .then(function(results){renderSearchResults(opResults,results||[])})
      .catch(function(){renderSearchResults(opResults,[])});
  }
  
  // ─── Smart filter chips ─── 
  var filters={cat:null,minRating:null,maxPrice:null};
  function applyFilters(){
    var ops=getOps().filter(function(o){
      if(filters.cat&&o.cat!==filters.cat)return false;
      if(filters.minRating&&(o.rating||0)<filters.minRating)return false;
      if(filters.maxPrice&&(o.price||9999)>filters.maxPrice)return false;
      return true;
    });
    // Detect cluster (zone uses window.markerCluster, homepage uses window.mapClusterGroup)
    var cluster=window.markerCluster||window.mapClusterGroup;
    var mkFn=window.makeMarker;
    if(cluster&&mkFn){
      cluster.clearLayers();
      ops.forEach(function(o){if(o.lat&&o.lng){try{cluster.addLayer(mkFn(o))}catch(e){}}});
    } else if(window.refreshMarkers){
      window.refreshMarkers();
    } else if(cluster) {
      // Fallback: just remove pins not matching, no re-add
      cluster.clearLayers();
    }
    // Update visible count
    var vc=document.getElementById('mapVisibleCount')||document.getElementById('hpVisibleCount');
    if(vc)vc.innerHTML='<strong>'+ops.length+'</strong> operator'+(ops.length===1?'':'s')+' a la vista';
    if(window.gtag)gtag('event','map_filter_apply',filters);
  }
  
  // ─── Inject UI ─── 
  function injectUI(){
    var wrap=getMapContainer();
    if(!wrap||document.getElementById('mpSearchInput'))return;
    
    // Search bar
    var sb=document.createElement('div');
    sb.className='mp-search-bar';
    sb.innerHTML='<span class="mp-search-icon">🔎</span><input type="search" id="mpSearchInput" placeholder="Busca moto de agua, lancha, marina, dirección..." autocomplete="off"><button id="mpSearchBtn">Ir</button>';
    wrap.appendChild(sb);
    
    var sr=document.createElement('div');
    sr.className='mp-search-results';
    sr.id='mpSearchResults';
    wrap.appendChild(sr);
    
    document.getElementById('mpSearchInput').addEventListener('input',function(e){
      clearTimeout(searchTimer);
      var val=e.target.value.trim();
      if(!val){
        // Empty input: hide dropdown immediately
        var box=document.getElementById('mpSearchResults');
        if(box){box.classList.remove('show');box.innerHTML='';}
        return;
      }
      searchTimer=setTimeout(function(){searchPlaces(val)},400);
    });
    // Hide results when clicking outside
    document.addEventListener('click',function(e){
      var box=document.getElementById('mpSearchResults');
      var bar=document.querySelector('.mp-search-bar');
      if(box&&bar&&!bar.contains(e.target)&&!box.contains(e.target)){
        box.classList.remove('show');
      }
    });
    // ESC key to clear
    document.getElementById('mpSearchInput').addEventListener('keydown',function(e){
      if(e.key==='Escape'){
        e.target.value='';
        var box=document.getElementById('mpSearchResults');
        if(box){box.classList.remove('show');box.innerHTML='';}
      }
    });
    document.getElementById('mpSearchBtn').onclick=function(){
      searchPlaces(document.getElementById('mpSearchInput').value);
    };
    document.getElementById('mpSearchInput').addEventListener('keydown',function(e){
      if(e.key==='Enter')searchPlaces(e.target.value);
    });
    
    // Filter chips
    var fc=document.createElement('div');
    fc.className='mp-filter-chips';
    fc.innerHTML='';fc.style.display='none';
    wrap.appendChild(fc);
    
    fc.querySelectorAll('.mp-chip').forEach(function(chip){
      chip.onclick=function(){
        var f=chip.dataset.filter,v=parseFloat(chip.dataset.val);
        var was=chip.classList.contains('active');
        // De-activate same-filter siblings
        fc.querySelectorAll('.mp-chip[data-filter="'+f+'"]').forEach(function(c){c.classList.remove('active')});
        if(!was){
          chip.classList.add('active');
          if(f==='rating')filters.minRating=v;
          else if(f==='price')filters.maxPrice=v;
        } else {
          if(f==='rating')filters.minRating=null;
          else if(f==='price')filters.maxPrice=null;
        }
        applyFilters();
      };
    });
    
    // Favorites button (junto a otros map controls)
    var controlsContainer=document.querySelector('.map-controls-overlay')||document.querySelector('.hp-map-controls');
    if(controlsContainer&&!document.getElementById('mpFavBtn')){
      var favBtn=document.createElement('button');
      favBtn.className='mp-fav-btn';
      favBtn.id='mpFavBtn';
      favBtn.innerHTML='❤️ Favoritos';
      favBtn.onclick=showFavoritesModal;
      controlsContainer.appendChild(favBtn);
      updateFavBtn();
    }
  }
  
  function showFavoritesModal(){
    var favs=getFavs();
    var ops=getOps().filter(function(o){return favs.indexOf(o.id)>-1});
    var modal=document.getElementById('mpFavModal');
    if(!modal){
      modal=document.createElement('div');
      modal.className='mp-modal-overlay';
      modal.id='mpFavModal';
      modal.innerHTML='<div class="mp-modal"><button class="mp-modal-close" onclick="document.getElementById(\'mpFavModal\').classList.remove(\'show\')" aria-label="Cerrar">×</button><h3>❤️ My Favorites</h3><div class="mp-cmp-grid" id="mpFavGrid"></div></div>';
      document.body.appendChild(modal);
    }
    var grid=document.getElementById('mpFavGrid');
    if(!ops.length){
      grid.innerHTML='<p style="color:#a8d4f0;grid-column:1/-1;text-align:center;padding:30px">Aún no tienes favoritos. Pulsa ❤️ en cualquier operador del mapa para guardarlo aquí.</p>';
    } else {
      grid.innerHTML=ops.map(function(o){
        var photo=o.photo&&o.photo.includes('http')?o.photo:(o.photo?'https://cdn.filestackcontent.com/'+o.photo+'/convert?w=400&format=webp':'');
        return '<div class="mp-cmp-card"><img src="'+photo+'" alt="'+(o.name||'').replace(/"/g,'&quot;')+'" onerror="this.style.display=\'none\'"><div class="mp-cmp-body"><h4>'+(o.name||'').slice(0,60)+'</h4><div class="mp-cmp-attr">⭐ <strong>'+(o.rating||'4.7')+'</strong> · 💰 $'+(o.price||'50')+'+</div><a href="/'+getSlug(o)+'" class="mp-cmp-book">Ver Detalles →</a></div></div>';
      }).join('');
    }
    modal.classList.add('show');
  }
  
  // ─── Override popup to be rich ─── 
  function enrichPopup(map){
    map.on('popupopen',function(e){
      var pop=e.popup;
      var marker=pop._source;
      if(!marker||!marker._opId)return;
      var op=getOps().find(function(o){return o.id===marker._opId});
      if(!op)return;
      
      var photo=op.photo&&op.photo.includes('http')?op.photo:(op.photo?'https://cdn.filestackcontent.com/'+op.photo+'/convert?w=400&format=webp&quality=80':'');
      var slug=getSlug(op);
      var __ll=userLoc||(window.mapInstance&&window.mapInstance.getCenter?window.mapInstance.getCenter():null);var __dmi=(__ll&&op.lat&&typeof haversineMi==='function')?haversineMi(__ll.lat,__ll.lng,op.lat,op.lng):null;var distance=(__dmi!=null)?('~'+Math.max(1,Math.round(__dmi*20))+' min a pie · '+__dmi.toFixed(1)+' mi'):'';
      var fav=isFav(op.id);
      var directionsUrl='https://www.google.com/maps/dir/?api=1&destination='+op.lat+','+op.lng;
      
      var html='<div class="mp-popup">'+
        (photo?'<img class="mp-popup-img" src="'+photo+'" alt="">':'')+
        '<div class="mp-popup-body">'+
        '<div class="mp-popup-name">'+(op.name||'').slice(0,80)+'</div>'+
        '<div class="mp-popup-meta"><span class="mp-popup-rating">⭐ '+(op.rating||'4.7')+' ('+(op.reviews||'100')+'+)</span><span class="mp-popup-price">$'+(op.price||'50')+'+</span></div>'+
        ((function(){var t=[];var em=(window.CAT_EMOJI&&window.CAT_EMOJI[op.cat])||'';if(op.badge)t.push((em?em+' ':'')+op.badge);if(op.zl)t.push('📍 '+op.zl);if(op.pax)t.push('👥 hasta '+op.pax);return t.length?'<div class="mp-popup-tags">'+t.join(' · ')+'</div>':'';})())+(distance?'<div class="mp-popup-distance">📍 '+distance+'</div>':'')+
        '<div class="mp-popup-actions">'+
        ((op.link&&op.link.indexOf('http')===0)?'<a href="'+op.link+'" target="_blank" rel="noopener" class="mp-popup-btn">⚡ Reservar</a>':'<a href="/'+slug+'" class="mp-popup-btn">Ver detalles</a>')+
        '<a href="'+directionsUrl+'" target="_blank" rel="noopener" class="mp-popup-btn secondary" onclick="if(window.gtag)gtag(\'event\',\'map_directions\',{op_id:\''+op.id+'\'})">🧭</a>'+
        '<button class="mp-popup-btn fav '+(fav?'active':'')+'" onclick="this.classList.toggle(\'active\');window.MPtoggle(\''+op.id+'\');if(!this.classList.contains(\'active\'))this.style.color=\'\'">'+(fav?'❤️':'🤍')+'</button>'+
        '</div>'+
        '<a href="/'+slug+'" class="mp-popup-btn secondary" style="width:100%;margin-top:6px">Ver detalles</a>'+
        '<button class="mp-popup-btn secondary" style="width:100%;margin-top:8px" onclick="window.MPcompare(\''+op.id+'\')">+ Comparar</button>'+
        '</div></div>';
      
      pop.setContent(html);
    });
  }
  
  // Expose for popup buttons
  window.MPtoggle=toggleFav;
  window.MPcompare=addToCompare;
  
  // Inject UI immediately (doesn't need map ready)
  function init(){
    injectUI();
    // Enrich popup waits for map
    waitForMapReady();
  }
  function waitForMapReady(attempts){
    attempts=attempts||0;
    var m=getMap();
    if(m){enrichPopup(m);return}
    if(attempts>120)return;
    setTimeout(function(){waitForMapReady(attempts+1)},500);
  }
  
  if(document.readyState!=='loading')setTimeout(init,800);
  else document.addEventListener('DOMContentLoaded',function(){setTimeout(init,800)});
})();
/* /SPRINT 13 MAP PRO */


/* ─── SPRINT 14 MAP CAT FILTER CHIPS ─── */
(function(){
  var selectedCats=new Set();
  
  function getMapLocal(){return window.jetskiMap||window.mapInstance||null}
  function getOpsLocal(){return window.allOperators||window.allOps||window._uxAllOps||[]}
  
  // Top categorías más comunes según datos
  var CAT_DISPLAY={
    tour:{label:'Tour',emoji:'🚌'},
    boat:{label:'Lancha',emoji:'⛵'},
    bikerental:{label:'Bici & E-Ride',emoji:'🚲'},
    kayak:{label:'Kayak & SUP',emoji:'🛶'},
    kayaksup:{label:'Kayak & SUP',emoji:'🛶'},
    fishing:{label:'Pesca',emoji:'🎣'},
    shuttle:{label:'Traslado',emoji:'🚐'},
    walking_tour:{label:'Tour a Pie',emoji:'🚶'},
    ghost:{label:'Fantasmas',emoji:'👻'},
    culinary:{label:'Gastronomía',emoji:'🍷'},
    airboat:{label:'Hidrodeslizador',emoji:'🐊'},
    yacht:{label:'Yate',emoji:'🛳️'},
    watersports:{label:'Deportes Acuáticos',emoji:'🏄'},
    hotel:{label:'Hotel',emoji:'🏨'},
    aerial:{label:'Tour Aéreo',emoji:'✈️'},
    sunset:{label:'Atardecer',emoji:'🌅'},
    jetski:{label:'Moto de Agua',emoji:'🛥️'},
    snorkel:{label:'Snorkel',emoji:'🤿'},
    golfcart:{label:'Carrito de Golf',emoji:'🛺'},
    jetcar:{label:'Jet Car',emoji:'🚗'},
    slingshot:{label:'Slingshot',emoji:'🏎️'},
    atv:{label:'ATV',emoji:'🏍️'},
    wildlife:{label:'Fauna',emoji:'🐋'},
    zipline:{label:'Tirolesa',emoji:'🪢'},
    mayan_cenote:{label:'Cenote',emoji:'🏛️'},
    golf:{label:'Golf',emoji:'⛳'},
    nightlife:{label:'Vida Nocturna',emoji:'🍸'},
    themepark:{label:'Parque Temático',emoji:'🎢'},
    segway:{label:'Segway',emoji:'🛴'},
    lei:{label:'Lei',emoji:'🌺'},
    staugustine:{label:'St. Augustine',emoji:'🏰'},
    sailing:{label:'Vela & Catamarán',emoji:'⛵'},
    surf:{label:'Clase de Surf',emoji:'🏄'},
    jacksonville:{label:'Jacksonville',emoji:'🌆'},
    exotic:{label:'Auto Exótico',emoji:'💎'},
    villa:{label:'Villa',emoji:'🏡'},
    flowers:{label:'Flores',emoji:'💐'}
  };
  
  function injectCatChips(){
    var wrap=document.querySelector('.map-wrap')||document.querySelector('.map-panel');
    if(!wrap||document.querySelector('.mp-cat-chips'))return;
    
    // Calcular qué cats existen en esta zona (con counts)
    var ops=getOpsLocal();
    var catCounts={};
    ops.forEach(function(o){if(o.cat){catCounts[o.cat]=(catCounts[o.cat]||0)+1}});
    
    // Solo mostrar cats con al menos 3 ops, ordenados por count
    var topCats=Object.keys(catCounts).filter(function(c){return catCounts[c]>=1&&CAT_DISPLAY[c]}).sort(function(a,b){return catCounts[b]-catCounts[a]});
    
    if(!topCats.length)return; // No mostrar si no hay cats
    
    var bar=document.createElement('div');
    bar.className='mp-cat-chips';
    
    var html='';
    topCats.forEach(function(c){
      var d=CAT_DISPLAY[c];
      html+='<button class="mp-cat-chip" data-cat="'+c+'">'+d.emoji+' '+d.label+' <span class="mp-cat-count">'+catCounts[c]+'</span></button>';
    });
    html+='<button class="mp-cat-chips-clear" id="mpCatChipsClear">✕ Limpiar</button>';
    
    bar.innerHTML=html;
    wrap.appendChild(bar);
    
    bar.querySelectorAll('.mp-cat-chip').forEach(function(chip){
      chip.onclick=function(){
        var cat=chip.dataset.cat;
        var wasActive=selectedCats.has(cat);
        // SINGLE-SELECT: clear all + activate this one
        selectedCats.clear();
        bar.querySelectorAll('.mp-cat-chip').forEach(function(c){c.classList.remove('active')});
        if(!wasActive){
          // Activate this chip (toggle off if clicking the active one)
          selectedCats.add(cat);
          chip.classList.add('active');
        }
        // Show/hide clear button
        var clearBtn=document.getElementById('mpCatChipsClear');
        if(clearBtn){
          if(selectedCats.size>0)clearBtn.classList.add('show');
          else clearBtn.classList.remove('show');
        }
        triggerMainCat(selectedCats.size>0?cat:'all');
        if(window.gtag)gtag('event','map_cat_chip_select',{cat:cat,active:selectedCats.has(cat)});
      };
    });
    
    document.getElementById('mpCatChipsClear').onclick=function(){
      selectedCats.clear();
      bar.querySelectorAll('.mp-cat-chip').forEach(function(c){c.classList.remove('active')});
      this.classList.remove('show');
      triggerMainCat('all');
      if(window.gtag)gtag('event','map_cat_chips_clear');
    };
  }
  
  function triggerMainCat(cat){
    // Reuse the proven main #filters handler (sets activeCat + render + refreshMarkers)
    var mainChip=document.querySelector('#filters .cat-chip[data-cat="'+cat+'"]');
    if(mainChip){mainChip.click();return;}
    // Fallback to globals if the main row isn't present
    window.activeCat=cat;
    if(typeof window.refreshMarkers==='function')window.refreshMarkers();
  }
  function applyMapCatFilter(){
    var ops=getOpsLocal();
    var cluster=window.markerCluster||window.mapClusterGroup;
    if(!cluster)return;
    
    cluster.clearLayers();
    
    var filtered=ops.filter(function(o){
      if(!o.lat||!o.lng)return false;
      if(selectedCats.size===0)return true; // sin filter = todos
      return selectedCats.has(o.cat);
    });
    
    // Inyectar markers con makeMarker si existe, sino crear inline simple
    var mkFn=window.makeMarker;
    if(mkFn){
      filtered.forEach(function(o){
        try{cluster.addLayer(mkFn(o))}catch(e){}
      });
    } else if(window.refreshMarkers){
      // Fallback: usar refreshMarkers — pero respeta activeCat global, no nuestro filter
      // Workaround: temporalmente cambiar window.allOps a filtered
      var origAllOps=window.allOps;
      window.allOps=filtered;
      window.refreshMarkers();
      window.allOps=origAllOps;
    }
    
    // Update visible count
    var vc=document.getElementById('mapVisibleCount')||document.getElementById('hpVisibleCount');
    if(vc){
      var label=selectedCats.size>0?' filtrados':' a la vista';
      vc.innerHTML='<strong>'+filtered.length+'</strong> operator'+(filtered.length===1?'':'s')+label;
    }
  }
  
  // Init when DOM + data ready
  var pollInit=setInterval(function(){
    if(getOpsLocal().length>0){
      clearInterval(pollInit);
      injectCatChips();
    }
  },500);
  setTimeout(function(){clearInterval(pollInit);if(getOpsLocal().length>0)injectCatChips()},25000);
})();
/* /SPRINT 14 MAP CAT FILTER CHIPS */


/* ─── SPRINT 15 MAP-CARD SYNC ─── */
(function(){
  var syncEnabled=false;
  var moveTimer=null;
  
  function getMapLocal(){return window.jetskiMap||window.mapInstance||null}
  function getOpsLocal(){return window.allOperators||window.allOps||window._uxAllOps||[]}
  function haversineMi2(lat1,lon1,lat2,lon2){
    var R=3958.8;
    var dLat=(lat2-lat1)*Math.PI/180;
    var dLon=(lon2-lon1)*Math.PI/180;
    var a=Math.sin(dLat/2)*Math.sin(dLat/2)+Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)*Math.sin(dLon/2);
    return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
  }
  
  function injectSyncBtn(){
    var wrap=document.querySelector('.map-wrap')||document.querySelector('.map-panel');
    if(!wrap||document.querySelector('.mp-sync-btn'))return;
    
    var btn=document.createElement('button');
    btn.className='mp-sync-btn';
    btn.id='mpSyncBtn';
    btn.innerHTML='<span class="mp-sync-icon">🔄</span> Ordenar por mapa';
    btn.title='Reordenar tarjetas por distancia al centro del mapa';
    wrap.appendChild(btn);
    
    btn.onclick=function(){
      syncEnabled=!syncEnabled;
      if(syncEnabled){
        btn.classList.add('active');
        btn.innerHTML='<span class="mp-sync-icon">✓</span> Ordenado por mapa';
        sortCardsByDistance();
        document.querySelectorAll('.card').forEach(function(c){c.classList.add('mp-show-distance')});
      } else {
        btn.classList.remove('active');
        btn.innerHTML='<span class="mp-sync-icon">🔄</span> Ordenar por mapa';
        // Clear distance attrs
        document.querySelectorAll('.card[data-mp-sync-distance]').forEach(function(c){
          c.removeAttribute('data-mp-sync-distance');
          c.classList.remove('mp-show-distance');
          c.style.order='';
        });
      }
      if(window.gtag)gtag('event','map_card_sync_toggle',{active:syncEnabled});
    };
  }
  
  function sortCardsByDistance(){
    var m=getMapLocal();
    if(!m)return;
    var center=m.getCenter();
    var ops=getOpsLocal();
    var slugMap=window._OP_SLUG_MAP||{};
    
    // Build op_id → distance map
    var opDist={};
    ops.forEach(function(o){
      if(!o.lat||!o.lng)return;
      opDist[o.id]={dist:haversineMi2(center.lat,center.lng,o.lat,o.lng),op:o};
    });
    
    var grid=document.getElementById('grid');
    if(!grid)return;
    
    // Apply CSS Grid order via inline styles (works with existing grid)
    grid.classList.add('mp-sync-transition');
    grid.style.display='flex';
    grid.style.flexWrap='wrap';
    
    var cards=grid.querySelectorAll('.card[data-op-id]');
    var cardsWithDist=[];
    cards.forEach(function(card){
      var opId=card.getAttribute('data-op-id');
      var d=opDist[opId];
      if(d){
        cardsWithDist.push({card:card,dist:d.dist});
        // Set distance label
        var distLabel=d.dist<1?Math.round(d.dist*5280)+' ft':d.dist.toFixed(1)+' mi';
        card.setAttribute('data-mp-sync-distance','📏 '+distLabel);
      } else {
        cardsWithDist.push({card:card,dist:99999});
      }
    });
    
    // Sort
    cardsWithDist.sort(function(a,b){return a.dist-b.dist});
    
    // Apply order via flexbox order or DOM reorder
    cardsWithDist.forEach(function(item,idx){
      item.card.style.order=idx;
    });
    
    if(window.gtag)gtag('event','map_card_sync_apply',{count:cardsWithDist.length});
  }
  
  // Listen to map movements (debounced)
  function listenToMap(){
    var m=getMapLocal();
    if(!m){setTimeout(listenToMap,1000);return}
    m.on('moveend',function(){
      if(!syncEnabled)return;
      clearTimeout(moveTimer);
      moveTimer=setTimeout(sortCardsByDistance,300);
    });
  }
  
  // Init when DOM + map ready
  var pollInit=setInterval(function(){
    var wrap=document.querySelector('.map-wrap')||document.querySelector('.map-panel');
    if(wrap){
      clearInterval(pollInit);
      injectSyncBtn();
      listenToMap();
    }
  },500);
  setTimeout(function(){clearInterval(pollInit)},25000);
})();
/* /SPRINT 15 MAP-CARD SYNC */

/* persist+share category state */
(function(){
  document.addEventListener('click',function(e){
    var c=e.target.closest&&e.target.closest('#filters .cat-chip');
    if(!c)return;
    try{var cat=c.dataset.cat;
      if(cat&&cat!=='all'){localStorage.setItem('mp_cat',cat);history.replaceState(null,'',location.pathname+'?cat='+encodeURIComponent(cat));}
      else{localStorage.removeItem('mp_cat');history.replaceState(null,'',location.pathname);}
    }catch(_){}
  });
  var applied=false;
  function apply(){
    if(applied)return; if(!(window.allOps&&window.allOps.length))return;
    applied=true;
    var saved=null;try{saved=new URLSearchParams(location.search).get('cat')||localStorage.getItem('mp_cat');}catch(_){}
    if(saved&&saved!=='all'){var chip=document.querySelector('#filters .cat-chip[data-cat="'+saved+'"]');if(chip)chip.click();}
  }
  var iv=setInterval(function(){apply();if(applied)clearInterval(iv);},300);
  setTimeout(function(){clearInterval(iv);},15000);
})();
