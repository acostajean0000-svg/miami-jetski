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
 * No-op safe if no ref present.
 */
(function () {
  'use strict';

  // ── CONFIG ─────────────────────────────────────────────────
  // FareHarbor URL param used for per-host sub-tracking.
  // `ref` (Online Booking Reference) — confirmed by FareHarbor support.
  // Appears as a column in the FHDN Bookings report.
  var FH_SUB_PARAM = 'ref';

  // The distribution-partner shortname FareHarbor expects as the prefix.
  // Final value will be e.g.  ref=miamistylerentals-maria-x4k2
  var REF_BASE = 'miamistylerentals';

  // Where we store the ref slug locally
  var STORAGE_KEY = 'refstay_ref';
  // How long the attribution lasts (30 days = standard affiliate window)
  var REF_TTL_DAYS = 30;

  // FareHarbor URLs match this substring
  var FH_HOST_MATCH = 'fareharbor.com';

  // ── HELPERS ────────────────────────────────────────────────
  function safe(fn) { try { return fn(); } catch (e) { return null; } }

  function setRef(slug) {
    safe(function () {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        slug: slug,
        savedAt: Date.now()
      }));
    });
  }

  function getRef() {
    return safe(function () {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
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

  function injectSubIdIntoLink(a, slug) {
    if (!a || !a.href || a.href.indexOf(FH_HOST_MATCH) === -1) return;
    if (a.dataset.refstayInjected === '1') return; // idempotent
    try {
      var u = new URL(a.href);
      // Overwrite `ref` with `<REF_BASE>-<slug>`. We always rebuild from
      // REF_BASE rather than appending to whatever was there — this stays
      // correct even if the original href already had a slug suffix from
      // a previous render, or if some links were copied without the base.
      u.searchParams.set(FH_SUB_PARAM, REF_BASE + '-' + slug);
      a.href = u.toString();
      a.dataset.refstayInjected = '1';
    } catch (e) { /* ignore malformed URL */ }
  }

  function injectAll(slug) {
    if (!slug) return;
    var links = document.querySelectorAll('a[href*="' + FH_HOST_MATCH + '"]');
    for (var i = 0; i < links.length; i++) {
      injectSubIdIntoLink(links[i], slug);
    }
  }

  // ── STEP 1: capture ?ref= from URL on landing ─────────────
  var urlRef = safe(function () {
    var p = new URL(window.location.href).searchParams.get('ref');
    return sanitizeSlug(p);
  });

  if (urlRef) {
    setRef(urlRef);
    // Fire GA4 event (no-op safe if gtag isn't loaded yet)
    safe(function () {
      if (typeof window.gtag === 'function') {
        window.gtag('event', 'referred_visit', {
          refstay_slug: urlRef,
          page_path: location.pathname
        });
      }
    });
  }

  // ── STEP 2: on every page load, rewrite `ref` on FH links ──
  var activeSlug = urlRef || getRef();

  function init() {
    if (!activeSlug) return;
    injectAll(activeSlug);

    // Watch for dynamically-added links (defensive; the site is mostly static
    // but the booking modal logic uses delegated handlers)
    if ('MutationObserver' in window) {
      var t;
      var obs = new MutationObserver(function () {
        clearTimeout(t);
        t = setTimeout(function () { injectAll(activeSlug); }, 100);
      });
      obs.observe(document.body || document.documentElement, {
        childList: true,
        subtree: true
      });
    }
  }

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
    FH_SUB_PARAM: FH_SUB_PARAM,
    REF_BASE: REF_BASE
  };
})();
