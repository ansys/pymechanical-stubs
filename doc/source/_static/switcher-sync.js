/**
 * switcher-sync.js
 *
 * Rewrites version-switcher links so that each v### entry stays within the
 * same deployment context as the page currently being viewed:
 *
 *   PR preview  → https://<cname>/pull/<N>/api/ansys/mechanical/stubs/v###
 *   dev branch  → https://<cname>/version/dev/api/ansys/mechanical/stubs/v###
 *   stable      → https://<cname>/version/stable/api/ansys/mechanical/stubs/v###
 *                 (versions.json already contains stable URLs, so no rewrite
 *                  is needed there – but we normalise them for consistency)
 *
 * The script waits for the pydata-sphinx-theme to finish populating the
 * dropdown (it does so asynchronously after DOMContentLoaded), then patches
 * every anchor whose href contains "/api/ansys/mechanical/stubs/v".
 */
(function () {
  "use strict";

  // ── 1. Detect deployment context from window.location ──────────────────────

  var loc = window.location;
  var pathname = loc.pathname; // e.g. /pull/42/api/ansys/...  or  /version/stable/api/...

  /**
   * Returns the base prefix for the current deployment context, e.g.:
   *   "/pull/42"          for PR previews
   *   "/version/dev"      for the dev branch
   *   "/version/stable"   for stable releases
   *   ""                  for local / unknown builds
   */
  function getContextPrefix() {
    var prMatch = pathname.match(/^(\/pull\/\d+)/);
    if (prMatch) return prMatch[1];

    var versionMatch = pathname.match(/^(\/version\/[^/]+)/);
    if (versionMatch) return versionMatch[1];

    return ""; // local build or unknown – leave links untouched
  }

  var contextPrefix = getContextPrefix();

  // Nothing to patch on a plain local build.
  if (contextPrefix === "") return;

  // ── 2. Build a rewritten href for a given v### token ───────────────────────

  var STUBS_PATH = "/api/ansys/mechanical/stubs/";

  /**
   * Given any URL that contains "/api/ansys/mechanical/stubs/v###", return a
   * rewritten URL rooted at contextPrefix.
   * e.g. "https://cname/version/stable/api/ansys/mechanical/stubs/v252"
   *   →  "https://cname/pull/99/api/ansys/mechanical/stubs/v252"
   */
  function rewriteUrl(originalHref) {
    var stubsIdx = originalHref.indexOf(STUBS_PATH);
    if (stubsIdx === -1) return null; // not an API stubs link

    // Extract everything from /api/... onwards (may include a trailing path)
    var stubsSuffix = originalHref.slice(stubsIdx); // "/api/ansys/mechanical/stubs/v###..."
    return loc.origin + contextPrefix + stubsSuffix;
  }

  // ── 3. Patch all switcher anchors that point to a v### stubs page ──────────

  function patchSwitcher() {
    // The switcher dropdown is inside .version-switcher__menu or
    // #pst-version-switcher-list-* depending on theme version.
    var menus = document.querySelectorAll(
      ".version-switcher__menu a, [id^='pst-version-switcher-list-'] a"
    );

    menus.forEach(function (anchor) {
      var patched = rewriteUrl(anchor.href);
      if (patched) {
        anchor.href = patched;
      }
    });
  }

  // ── 4. Wait for the switcher to be populated, then patch ───────────────────
  //
  // pydata-sphinx-theme populates the dropdown asynchronously (fetch +
  // DOM insertion), so we use a MutationObserver on the navbar to catch the
  // moment the <a> elements appear, and also run once on DOMContentLoaded as
  // a best-effort fallback.

  function observeAndPatch() {
    var navbar = document.querySelector(".bd-header, header.bd-header, nav");

    if (navbar) {
      var observer = new MutationObserver(function (mutations) {
        // Check whether any switcher links have been added
        var hasSwitcherLink = mutations.some(function (m) {
          return Array.from(m.addedNodes).some(function (node) {
            return (
              node.nodeType === 1 &&
              (node.matches("a") || node.querySelector("a")) &&
              (node.closest
                ? node.closest(".version-switcher__menu, [id^='pst-version-switcher-list-']")
                : false)
            );
          });
        });

        if (hasSwitcherLink) {
          patchSwitcher();
          // Keep observing – the theme may re-render the list on navigation
        }
      });

      observer.observe(navbar, { childList: true, subtree: true });
    }

    // Also run after a short delay in case the switcher was already rendered
    // before our observer was attached (e.g. restored from bfcache).
    setTimeout(patchSwitcher, 500);
    setTimeout(patchSwitcher, 1500);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", observeAndPatch);
  } else {
    observeAndPatch();
  }
})();
