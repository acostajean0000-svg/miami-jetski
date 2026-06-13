/*!
 * Refstay referral capture — for miamijetskiboatrentals.com
 * ─────────────────────────────────────────────────────────
 * Purpose: when a visitor arrives via a Refstay host link
 * (e.g. miamijetskiboatrentals.com/?ref=maria-x4k2), this script:
 *   1. Saves the referrer slug to localStorage (30-day TTL)
 *   2. Rewrites the FareHarbor `ref` (Online Booking Reference)
 *      parameter on every booking link to:
 *           miamistylerentals-<host_slug>
 *      The `miamistylerentals` prefix is preserved per FareHarbor
 *      support's recommendation so the overall distribution-partner
 *      tracking keeps working as a backup. The suffix attributes the
 *      booking to a specific Refstay host in the FHDN Bookings report
 *      (Online Booking Reference column).
 *   3. Fires a GA4 event so attribution shows in Analytics
 *
 * Designed to be loaded in <head> (no defer) so it runs BEFORE any
 * other script can clean the URL. Falls back to URL fragment (#ref=)
 * if query param is stripped.
 *
 * Debugging: open DevTools console — every step logs with [refstay] prefix.
 *
 * No-op safe if no ref present.
 */
(function () {
  'use strict';

  // ── CONFIG ─────────────────────────────────────────────────
  var FH_SUB_PARAM = 'ref';
  var REF_BASE = 'miamistylerentals';
  var STORAGE_KEY = 'refstay_ref';
  var REF_TTL_DAYS = 30;
  var FH_HOST_MATCH = 'fareharbor.com';
  var LOG_PREFIX = '[refstay]';
  var DEBUG = false; // set false in prod to silence logs

  // ── HELPERS ────────────────────────────────────────────────
  function log() {
    if (!DEBUG) return;
    try {
      var args = [LOG_PREFIX].concat(Array.prototype.slice.call(arguments));
      console.log.apply(console, args);
    } catch (e) {}
  }

  function safe(fn) { try { return fn(); } catch (e) { return null; } }

  function setRef(slug) {
    safe(function () {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        slug: slug,
        savedAt: Date.now()
      }));
    });
    // Also mirror to sessionStorage as a same-tab backup (some browsers
    // wipe localStorage in incognito after the window closes)
    safe(function () {
      sessionStorage.setItem(STORAGE_KEY, slug);
    });
  }

  function getRef() {
    return safe(function () {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        // Fallback to sessionStorage
        var s = sessionStorage.getItem(STORAGE_KEY);
        return s || null;
      }
      var parsed = JSON.parse(raw);
      if (!parsed || !parsed.slug) return null;
      var ageDays = (Date.now() - (parsed.savedAt || 0)) / 86400000;
      if (ageDays > REF_TTL_DAYS) {
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }
      return parsed.slug;
    });
  }

  function sanitizeSlug(s) {
    if (!s) return '';
    return String(s).toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 64);
  }

  // Read slug from query param OR fragment (e.g. #ref=jean-acosta)
  // Fragment is harder to strip — survives most URL cleaners.
  function readRefFromUrl() {
    var fromQuery = safe(function () {
      return new URL(window.location.href).searchParams.get('ref');
    });
    if (fromQuery) {
      log('found ref in query:', fromQuery);
      return fromQuery;
    }
    var fromFragment = safe(function () {
      var h = window.location.hash || '';
      if (!h) return null;
      // hash looks like "#ref=jean-acosta" or "#foo&ref=jean-acosta"
      var params = new URLSearchParams(h.replace(/^#/, ''));
      return params.get('ref');
    });
    if (fromFragment) {
      log('found ref in fragment:', fromFragment);
      return fromFragment;
    }
    return null;
  }

  function injectSubIdIntoLink(a, slug) {
    if (!a || !a.href || a.href.indexOf(FH_HOST_MATCH) === -1) return;
    if (a.dataset.refstayInjected === '1') return;
    try {
      var u = new URL(a.href);
      u.searchParams.set(FH_SUB_PARAM, REF_BASE + '-' + slug);
      a.href = u.toString();
      a.dataset.refstayInjected = '1';
    } catch (e) { /* ignore malformed URL */ }
  }

  function injectAll(slug) {
    if (!slug) return 0;
    var links = document.querySelectorAll('a[href*="' + FH_HOST_MATCH + '"]');
    var n = 0;
    for (var i = 0; i < links.length; i++) {
      if (links[i].dataset.refstayInjected !== '1') {
        injectSubIdIntoLink(links[i], slug);
        n++;
      }
    }
    if (n > 0) log('injected ref into', n, 'FareHarbor links');
    return n;
  }

  // Also patch any existing iframes (the FareHarbor booking modal uses an iframe
  // whose src is set programmatically — it doesn't go through our <a> injection).
  function injectIntoIframe(iframe, slug) {
    if (!iframe || !iframe.src) return false;
    if (iframe.src.indexOf(FH_HOST_MATCH) === -1) return false;
    if (iframe.dataset.refstayInjected === '1') return false;
    try {
      var u = new URL(iframe.src);
      var currentRef = u.searchParams.get(FH_SUB_PARAM) || '';
      var desiredRef = REF_BASE + '-' + slug;
      // Only rewrite if not already correct (avoids reload loops)
      if (currentRef !== desiredRef) {
        u.searchParams.set(FH_SUB_PARAM, desiredRef);
        iframe.src = u.toString();
        log('rewrote iframe.src — ref now:', desiredRef);
      }
      iframe.dataset.refstayInjected = '1';
      return true;
    } catch (e) { return false; }
  }

  function injectAllIframes(slug) {
    if (!slug) return 0;
    var iframes = document.querySelectorAll('iframe[src*="' + FH_HOST_MATCH + '"]');
    var n = 0;
    for (var i = 0; i < iframes.length; i++) {
      if (injectIntoIframe(iframes[i], slug)) n++;
    }
    if (n > 0) log('patched', n, 'FareHarbor iframe(s)');
    return n;
  }

  // Hijack the iframe.src setter so ANY FareHarbor iframe URL gets our ref
  // baked in at the moment it's assigned — even before the iframe loads.
  // This catches the modal-open path where openFhModal(url) sets iframe.src
  // with a URL that may not have our ref.
  function patchIframeSrcSetter() {
    try {
      var desc = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'src');
      if (!desc || !desc.set || desc.__refstayPatched) return;
      var origSet = desc.set;
      var origGet = desc.get;
      Object.defineProperty(HTMLIFrameElement.prototype, 'src', {
        configurable: true,
        get: origGet,
        set: function (value) {
          var v = value;
          try {
            if (typeof v === 'string' && v.indexOf(FH_HOST_MATCH) !== -1) {
              var slug = activeSlug || getRef();
              if (slug) {
                var u = new URL(v);
                var desired = REF_BASE + '-' + slug;
                if (u.searchParams.get(FH_SUB_PARAM) !== desired) {
                  u.searchParams.set(FH_SUB_PARAM, desired);
                  v = u.toString();
                  log('iframe.src setter — ref injected:', desired);
                }
              }
            }
          } catch (e) { /* if URL parse fails, just pass through original */ }
          origSet.call(this, v);
        }
      });
      // Mark as patched so we don't double-wrap on hot reload
      Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'src').__refstayPatched = true;
      log('iframe.src setter patched — all future FareHarbor iframes will get ref injected');
    } catch (e) {
      log('iframe.src setter patch failed (will rely on MutationObserver):', e.message);
    }
  }

  // ── STEP 1: capture ref from URL on landing ────────────────
  log('script loaded. URL parts:', {
    href: window.location.href,
    search: window.location.search,
    hash: window.location.hash,
    pathname: window.location.pathname
  });
  var raw = readRefFromUrl();
  var urlRef = sanitizeSlug(raw);

  if (urlRef) {
    setRef(urlRef);
    log('captured & saved slug:', urlRef);
    // Fire GA4 event (no-op safe if gtag isn't loaded yet)
    safe(function () {
      if (typeof window.gtag === 'function') {
        window.gtag('event', 'referred_visit', {
          refstay_slug: urlRef,
          page_path: location.pathname
        });
      }
    });
  } else {
    log('no ref in URL — will use cached slug if available');
  }

  // ── STEP 2: on every page load, rewrite ref on FH links ────
  var activeSlug = urlRef || getRef();
  if (activeSlug) {
    log('active slug for this session:', activeSlug);
  } else {
    log('no active slug — links will not be rewritten');
  }

  function init() {
    if (!activeSlug) return;
    injectAll(activeSlug);
    injectAllIframes(activeSlug);

    // Watch for dynamically-added links AND iframes (booking modal creates them on demand)
    if ('MutationObserver' in window) {
      var t;
      var obs = new MutationObserver(function () {
        clearTimeout(t);
        t = setTimeout(function () {
          injectAll(activeSlug);
          injectAllIframes(activeSlug);
        }, 100);
      });
      obs.observe(document.body || document.documentElement, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['src']  // watch iframe src changes too
      });
    }
  }

  // Patch iframe.src setter immediately — before any modal can open one
  patchIframeSrcSetter();

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose for debugging — visit the site, open DevTools, type:
  //   window.__refstay.getRef()
  window.__refstay = {
    getRef: getRef,
    setRef: setRef,
    sanitizeSlug: sanitizeSlug,
    readRefFromUrl: readRefFromUrl,
    injectAll: injectAll,
    activeSlug: function () { return activeSlug; },
    FH_SUB_PARAM: FH_SUB_PARAM,
    REF_BASE: REF_BASE,
    VERSION: '2026-05-25-v4-detailed-logs'
  };
  log('ready. type window.__refstay to inspect.');
})();
