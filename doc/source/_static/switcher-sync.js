/**
 * switcher-sync.js
 *
 * Keeps the version-switcher in sync with the current deployment context so
 * that clicking a version entry stays within the same deploy root:
 *
 *   PR preview  → https://<cname>/pull/<N>/api/ansys/mechanical/stubs/v###/index.html
 *   dev branch  → https://<cname>/version/dev/api/ansys/mechanical/stubs/v###/index.html
 *   stable      → https://<cname>/version/stable/api/ansys/mechanical/stubs/v###/index.html
 *
 * How the pydata-sphinx-theme switcher works
 * ------------------------------------------
 * The theme builds each dropdown anchor href as:
 *
 *   href = versions_json_entry.url + current_pagename_path
 *
 * e.g. "https://cname/version/stable/api/ansys/mechanical/stubs/v252"
 *    + "api/ansys/mechanical/stubs/v261/index.html"
 *  →   "https://cname/version/stable/api/ansys/mechanical/stubs/v252api/..."  ← broken
 *
 * Its click handler (function S) does a HEAD request on that combined href,
 * then falls back to the bare entry URL — always landing on the stable root,
 * even when the user is browsing a PR preview.
 *
 * The fix
 * -------
 * We intercept clicks on switcher anchors in the *capture* phase (before the
 * theme's bubble-phase handler), read the target version from the anchor's
 * data-version attribute (set by the theme, e.g. "252"), build the correct
 * context-aware URL, and navigate directly.
 */
(function () {
  "use strict";

  // ── 1. Detect deployment context ──────────────────────────────────────────

  var pathname = window.location.pathname;

  // Returns "/pull/42", "/version/dev", "/version/stable", or "" (local)
  function getContextPrefix() {
    var pr = pathname.match(/^(\/pull\/\d+)/);
    if (pr) return pr[1];
    var ver = pathname.match(/^(\/version\/[^/]+)/);
    if (ver) return ver[1];
    return "";
  }

  var contextPrefix = getContextPrefix();

  // On a local build there is nothing to fix.
  if (contextPrefix === "") return;

  // ── 2. Build a context-aware URL for a given switcher anchor ──────────────

  /**
   * Returns the URL to navigate to, or null if this entry should be left
   * to the theme (e.g. "dev" or "0.1" entries without a 3-digit revn).
   *
   * The pydata-sphinx-theme sets data-version on every switcher anchor to
   * the "version" field from versions.json — e.g. "252", "dev", "0.1".
   * We only rewrite 3-digit Mechanical revision entries.
   */
  function buildTargetUrl(anchor) {
    var version = anchor.getAttribute("data-version"); // "252", "251", "dev", …
    if (!version || !/^\d{3}$/.test(version)) return null;

    return (
      window.location.origin +
      contextPrefix +
      "/api/ansys/mechanical/stubs/v" +
      version +
      "/index.html"
    );
  }

  // ── 3. Attach a capture-phase click interceptor to a switcher anchor ──────

  function attachInterceptor(anchor) {
    if (anchor.dataset.switcherSyncBound) return; // already handled
    anchor.dataset.switcherSyncBound = "1";

    anchor.addEventListener(
      "click",
      function (e) {
        var target = buildTargetUrl(anchor);
        if (!target) return; // let the theme handle non-v### entries normally

        e.preventDefault();
        e.stopImmediatePropagation(); // prevent the theme's own click handler
        window.location.href = target;
      },
      true // capture phase — fires before the theme's bubbling handler
    );
  }

  // ── 4. Process all current switcher anchors and watch for new ones ────────
  //
  // The theme populates the dropdown asynchronously after fetching
  // versions.json, so we use a MutationObserver to catch newly added anchors.

  function processAllSwitcherAnchors() {
    document
      .querySelectorAll(
        ".version-switcher__menu a, [id^='pst-version-switcher-list-'] a"
      )
      .forEach(attachInterceptor);
  }

  var observer = new MutationObserver(processAllSwitcherAnchors);

  function start() {
    observer.observe(document.body, { childList: true, subtree: true });
    processAllSwitcherAnchors(); // handle any anchors already in the DOM
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
